import telebot
import time
import json 
import os
from telebot import types

bot = telebot.TeleBot('6137466158:AAFqIcQG4OUwyNB6W0_Ilrs2AwgDvIhO60w')
chat_id = 877378366

to_do = 'to_do.json'

def load_tasks():
    if os.path.exists(to_do):
        with open(to_do, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохранение задач в файл
def save_tasks(tasks):
    with open(to_do, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

@bot.message_handler(commands=['start'])
def start(command):
    print(f"[USER ACTION] New session started by user {command.chat.id}")
    bot.send_message(command.chat.id, 'Привет, напиши свое расписание на сегодня :)', reply_markup=menu(), parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == 'Добавить задачу')
def handle_add_task(message):
    msg = bot.send_message(message.chat.id, '📝 Введите новую задачу:')
    bot.register_next_step_handler(msg, process_add_task)

def process_add_task(message):
    try:
        tasks = load_tasks()
        user_id = str(message.from_user.id)
        
        if user_id not in tasks:
            tasks[user_id] = []
        
        task_text = message.text.strip()
        if task_text:
            new_task_id = len(tasks[user_id]) + 1
            tasks[user_id].append({
                'text': task_text,
                'completed': False,
                'id': new_task_id
            })
            save_tasks(tasks)
            bot.send_message(message.chat.id, "✅ Задача добавлена!", reply_markup=menu())
        else:
            bot.send_message(message.chat.id, "❌ Задача не может быть пустой!", reply_markup=menu())
    except Exception as e:
        print(f"Error adding task: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при добавлении задачи", reply_markup=menu())

@bot.message_handler(func=lambda message: message.text == 'Список задач')
def show_task(message):
    tasks = load_tasks()
    user_id = str(message.from_user.id)
    
    if user_id not in tasks or not tasks[user_id]:
        bot.send_message(message.chat.id, "📭 У вас нет задач!", reply_markup=menu())
        return
    
    task_list = "📋 *Ваши задачи:*\n\n"
    for task in tasks[user_id]:
        status = "✅" if task['completed'] else "⏳"
        task_list += f"{status} {task['id']}. {task['text']}\n"
    
    bot.send_message(message.chat.id, task_list, parse_mode='Markdown', reply_markup=menu())

@bot.message_handler(func=lambda message: message.text == 'Завершить задачу')
def complete_task_prompt(message):
    tasks = load_tasks()
    user_id = str(message.from_user.id)
    
    if user_id not in tasks or not tasks[user_id]:
        bot.send_message(message.chat.id, "📭 Нет задач для завершения!", reply_markup=menu())
        return
    
    # Создаем инлайн клавиатуру с задачами
    markup = types.InlineKeyboardMarkup()
    for task in tasks[user_id]:
        if not task['completed']:
            markup.add(types.InlineKeyboardButton(
                f"{task['id']}. {task['text'][:30]}...", 
                callback_data=f"complete_{task['id']}"
            ))
    
    if markup.keyboard:
        bot.send_message(message.chat.id, "✅ Выберите задачу для завершения:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "🎉 Все задачи уже выполнены!", reply_markup=menu())

@bot.message_handler(func=lambda message: message.text == 'Удалить задачу')
def delete_task_prompt(message):
    tasks = load_tasks()
    user_id = str(message.from_user.id)
    
    if user_id not in tasks or not tasks[user_id]:
        bot.send_message(message.chat.id, "📭 Нет задач для удаления!", reply_markup=menu())
        return
    
    markup = types.InlineKeyboardMarkup()
    for task in tasks[user_id]:
        status = "✅" if task['completed'] else "⏳"
        markup.add(types.InlineKeyboardButton(
            f"{status} {task['id']}. {task['text'][:30]}...", 
            callback_data=f"delete_{task['id']}"
        ))
    
    bot.send_message(message.chat.id, "🗑️ Выберите задачу для удаления:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Очистить все')
def clear_all_tasks(message):
    tasks = load_tasks()
    user_id = str(message.from_user.id)
    
    if user_id in tasks and tasks[user_id]:
        tasks[user_id] = []
        save_tasks(tasks)
        bot.send_message(message.chat.id, "🧹 Все задачи очищены!", reply_markup=menu())
    else:
        bot.send_message(message.chat.id, "📭 Нет задач для очистки!", reply_markup=menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    tasks = load_tasks()
    user_id = str(call.from_user.id)
    
    if user_id not in tasks:
        bot.answer_callback_query(call.id, "❌ Ошибка: задачи не найдены")
        return
    
    if call.data.startswith('complete_'):
        task_id = int(call.data.split('_')[1])
        for task in tasks[user_id]:
            if task['id'] == task_id:
                task['completed'] = True
                save_tasks(tasks)
                bot.answer_callback_query(call.id, f"✅ Задача '{task['text']}' выполнена!")
                bot.edit_message_text(
                    "✅ Задача завершена!",
                    call.message.chat.id,
                    call.message.message_id
                )
                break
    
    elif call.data.startswith('delete_'):
        task_id = int(call.data.split('_')[1])
        # Сохраняем текст задачи для сообщения
        task_text = ""
        for task in tasks[user_id]:
            if task['id'] == task_id:
                task_text = task['text']
                break
        
        # Удаляем задачу
        tasks[user_id] = [task for task in tasks[user_id] if task['id'] != task_id]
        
        # Перенумеровываем оставшиеся задачи
        for i, task in enumerate(tasks[user_id], 1):
            task['id'] = i
        
        save_tasks(tasks)
        bot.answer_callback_query(call.id, f"🗑️ Задача удалена: {task_text}")
        bot.edit_message_text(
            f"🗑️ Задача удалена: {task_text}",
            call.message.chat.id,
            call.message.message_id
        )

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
📋 *To-Do List Bot - Помощь*

*Команды:*
/start - Начать работу
/help - Показать помощь

*Кнопки:*
📝 Добавить задачу - Добавить новую задачу
📋 Список задач - Показать все задачи
✅ Завершить задачу - Отметить задачу выполненной
🗑️ Удалить задачу - Удалить задачу
🧹 Очистить все - Удалить все задачи
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown', reply_markup=menu())

@bot.message_handler(commands=['stats'])
def show_stats(message):
    tasks = load_tasks()
    user_id = str(message.from_user.id)
    
    if user_id not in tasks or not tasks[user_id]:
        bot.send_message(message.chat.id, "📊 У вас пока нет задач!", reply_markup=menu())
        return
    
    total = len(tasks[user_id])
    completed = sum(1 for task in tasks[user_id] if task['completed'])
    pending = total - completed
    
    stats_text = f"""
📊 *Статистика задач*

Всего задач: {total}
✅ Выполнено: {completed}
⏳ Осталось: {pending}
📈 Прогресс: {completed/total*100:.1f}%
"""
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown', reply_markup=menu())

def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Добавить задачу', 'Список задач')
    markup.add('Завершить задачу', 'Удалить задачу')
    markup.add('Очистить все')
    return markup

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text not in ['Добавить задачу', 'Список задач', 'Завершить задачу', 'Удалить задачу', 'Очистить все']:
        bot.send_message(message.chat.id, "🤔 Используйте кнопки меню для управления задачами", reply_markup=menu())

print("[SYSTEM] Starting bot...")
while True:
    try:
        print("[SYSTEM] Starting bot polling...")
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"[ERROR] Bot crashed: {e}")
        print("[SYSTEM] Restarting bot in 3 seconds...")
        time.sleep(3)
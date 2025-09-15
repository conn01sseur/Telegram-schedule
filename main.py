import telebot
import time
import json 
import os

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

@bot.message_handler(regexp='/start')
def start(command):
    print(f"[USER ACTION] New session started by user {command.chat.id}")
    bot.send_message(command.chat.id, 'Привет, напиши свое расписание на сегодня :)', reply_markup=menu(), parse_mode='Markdown')

@bot.message_handler(regexp='Добавить задачу')
def add_task(command):
    message = bot.send_message(command.chat.id, 'Вот ваше расписание')
    bot.register_next_step_handler(message, add_new_task)

def add_new_task(message):
    tasks = load_tasks
    user_id = str(message.from_user.id)
    
    if user_id not in tasks:
        tasks[user_id] = []
    
    task_text = message.text.strip()
    if task_text:
        tasks[user_id].append({
            'text': task_text,
            'completed': False,
            'id': len(tasks[user_id]) + 1
        })
        save_tasks(tasks)
        bot.send_message(message.chat.id, "Задача добавлена!", reply_markup=menu())
    else:
        bot.send_message(message.chat.id, "Задача не может быть пустой!")

@bot.message_handler(regexp='Список задач')
def show_task(command):
    tasks = load_tasks()
    user_id = str(command.from_user.id)
    
    if user_id not in tasks or not tasks[user_id]:
        bot.send_message(command.chat.id, "📭 У вас нет задач!", reply_markup=menu())
        return
    
    task_list = "*Ваши задачи:*\n\n"
    for task in tasks[user_id]:
        status = "✅" if task['completed'] else "⏳"
        task_list += f"{status} {task['id']}. {task['text']}\n"
    
    bot.send_message(command.chat.id, task_list, parse_mode='Markdown', reply_markup=menu())

@bot.message_handler(regexp='Завершить задачу')
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

def menu():
    button = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button.add('Добавить задачу', 'Список задач')
    button.add('Завершить задачу', 'Удалить задачу')
    button.add('Очистить все')
    return button

print("[SYSTEM] Starting bot...")
while True:
    try:
        print("[SYSTEM] Starting bot polling...")
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"[ERROR] Bot crashed: {e}")
        print("[SYSTEM] Restarting bot in 3 seconds...")
        time.sleep(3)
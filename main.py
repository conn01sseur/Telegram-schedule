import telebot
import time
import json 
import os

bot = telebot.TeleBot('6137466158:AAFqIcQG4OUwyNB6W0_Ilrs2AwgDvIhO60w')
chat_id = 877378366

@bot.message_handler(regexp='/start')
def start(command):
    print(f"[USER ACTION] New session started by user {command.chat.id}")
    bot.send_message(command.chat.id, 'Привет, напиши свое расписание на сегодня :)')

@bot.message_handler(regexp='расписание')
def schedule(command):
    bot.send_message(command.chat.id, 'Вот ваше расписание')

print("[SYSTEM] Starting bot...")
while True:
    try:
        print("[SYSTEM] Starting bot polling...")
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"[ERROR] Bot crashed: {e}")
        print("[SYSTEM] Restarting bot in 3 seconds...")
        time.sleep(3)
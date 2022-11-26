import subprocess

import requests
import telebot

API_TOKEN = "Your Bot Token"
bot = telebot.TeleBot(API_TOKEN)
users_files = {}


@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    if chat_id in users_files:
        users_files[chat_id].append(message.video.file_id)
        bot.send_message(chat_id, "Video qo'shildi.\n"
                                  "/merge - videolarni birlashtirish uchun.")
    else:
        users_files[chat_id] = [message.video.file_id]
        bot.send_message(chat_id, "Video qo'shildi.\n"
                                  "/merge - videolarni birlashtirish uchun.")


@bot.message_handler(commands=['merge'])
def merge(message):
    chat_id = message.chat.id

    if chat_id not in users_files:
        bot.send_message(chat_id, "Birlashtirish uchun hech qanday video yubormagansiz.")
        return None

    inputs = list()
    for i, file_id in enumerate(users_files[chat_id]):
        file_info = bot.get_file(file_id)

        response = requests.get(
            'https://api.telegram.org/file/bot{0}/{1}'.format(
                API_TOKEN, file_info.file_path
            )
        )
        inputs.append("file '{}'".format(i))
        with open(str(i), 'wb') as arq:
            arq.write(response.content)

    with open('inputs.txt', 'w') as arq:
        arq.write('\n'.join(inputs))

    subprocess.call(
        ['ffmpeg', '-f', 'concat', '-i', 'inputs.txt', '-c', 'copy', 'out.mp4']
    )

    with open('out.mp4', 'rb') as video:
        bot.send_video(chat_id, video)
    users_files[chat_id] = []


@bot.message_handler(func=lambda message: True)
def help(message):
    help_msg = (
        "Birlashtirmoqchi bo'lgan videolarni (afzalroq MP4 formatida) yuboring va "
        "birlashtirilgan videoni qabul qilish uchun /merge buyrug'idan foydalaning."
    )
    bot.send_message(message.chat.id, help_msg)


bot.polling()

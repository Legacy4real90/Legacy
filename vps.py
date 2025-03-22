import telebot
import subprocess
import os
import requests

BOT_TOKEN = '7789286725:AAHncH6RSYj5w8uSfNOdzsgHfy7ymiC6-hE'
bot = telebot.TeleBot(BOT_TOKEN)

ALLOWED_USER_ID = 8003600588
AUTHORIZED_CHAT_ID = None

def is_authorized(message):
    return message.from_user.id == ALLOWED_USER_ID

@bot.message_handler(commands=['start'])
def start(message):
    global AUTHORIZED_CHAT_ID
    if is_authorized(message):
        AUTHORIZED_CHAT_ID = message.chat.id

# Handle commands
@bot.message_handler(func=lambda message: True, content_types=['text'])
def execute(message):
    if is_authorized(message) and AUTHORIZED_CHAT_ID:
        command = message.text.strip()
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            response = result.stdout + (result.stderr if result.stderr else "")
            if len(response) > 4096:
                with open('output.txt', 'w') as f:
                    f.write(response)
                with open('output.txt', 'rb') as f:
                    bot.send_document(AUTHORIZED_CHAT_ID, f)
                os.remove('output.txt')
            else:
                bot.send_message(AUTHORIZED_CHAT_ID, response or "Done")
        except subprocess.TimeoutExpired:
            bot.send_message(AUTHORIZED_CHAT_ID, "Timeout")
        except Exception as e:
            bot.send_message(AUTHORIZED_CHAT_ID, str(e))

# Handle file uploads
@bot.message_handler(content_types=['document', 'photo', 'video', 'audio'])
def handle_files(message):
    if is_authorized(message) and AUTHORIZED_CHAT_ID:
        try:
            # Get file info
            if message.document:
                file_info = bot.get_file(message.document.file_id)
                file_name = message.document.file_name
            elif message.photo:
                file_info = bot.get_file(message.photo[-1].file_id)  # Get highest resolution photo
                file_name = f"photo_{message.photo[-1].file_id}.jpg"
            elif message.video:
                file_info = bot.get_file(message.video.file_id)
                file_name = message.video.file_name or f"video_{message.video.file_id}.mp4"
            elif message.audio:
                file_info = bot.get_file(message.audio.file_id)
                file_name = message.audio.file_name or f"audio_{message.audio.file_id}.mp3"
            else:
                return

            # Download file from Telegram
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
            response = requests.get(file_url)
            
            # Save file to VPS
            with open(file_name, 'wb') as f:
                f.write(response.content)
            
            bot.send_message(AUTHORIZED_CHAT_ID, f"File {file_name} VPS pe upload ho gaya!")
        
        except Exception as e:
            bot.send_message(AUTHORIZED_CHAT_ID, f"File upload mein error: {str(e)}")

if __name__ == "__main__":
    bot.polling(none_stop=True)
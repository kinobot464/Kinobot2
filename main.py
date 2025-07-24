import telebot
import json
import os
from flask import Flask, request
import threading

TOKEN = "8298456178:AAHeL9GxfYfnW7nXQLVTG8Rwd-KyYqbewnE"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 2097478310
MOVIES_FILE = "movies.json"

app = Flask(__name__)

# Kinolar ro'yxatini o'qish
def load_movies():
    if not os.path.exists(MOVIES_FILE):
        with open(MOVIES_FILE, "w") as f:
            json.dump({}, f)
    with open(MOVIES_FILE, "r") as f:
        return json.load(f)

# Kod bo'yicha kino olish
def get_movie_by_code(code):
    movies = load_movies()
    return movies.get(code)

# Yangi kino qo'shish
def add_movie(code, file_id):
    movies = load_movies()
    movies[code] = file_id
    with open(MOVIES_FILE, "w") as f:
        json.dump(movies, f)

# Start komandasi
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "🎬 Salom! Kino kodini yuboring, men sizga kinoni jo'nataman.")

# Kino kodi yuborilganda
@bot.message_handler(func=lambda message: message.content_type == 'text')
def handle_code(message):
    code = message.text.strip()
    movie = get_movie_by_code(code)
    if movie:
        bot.send_video(message.chat.id, movie)
    else:
        bot.send_message(message.chat.id, "❌ Bunday kodli kino topilmadi.")

# Admin fayl yuborganda
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "❌ Siz admin emassiz.")
    msg = bot.send_message(message.chat.id, "📝 Iltimos, bu kino uchun kod yozing:")
    bot.register_next_step_handler(msg, save_video, message.video.file_id)

def save_video(message, file_id):
    code = message.text.strip()
    add_movie(code, file_id)
    bot.send_message(message.chat.id, f"✅ Kino '{code}' kodi bilan saqlandi!")

# Flask sahifa (Render uxlamasligi uchun)
@app.route('/')
def index():
    return "Bot ishga tushdi!"

# Flaskni alohida threadda ishga tushuramiz
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# Botni alohida threadda ishga tushuramiz
def run_bot():
    bot.infinity_polling()

# Har ikkala xizmatni parallel ishga tushuramiz
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_bot).start()
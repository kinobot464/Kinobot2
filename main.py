import telebot
import json
import os

TOKEN = '8298456178:AAHeL9GxfYfnW7nXQLVTG8Rwd-KyYqbewnE'  # Bu yerga o'zingizning bot tokeningizni yozing
ADMIN_ID = 2097478310  # Bu yerga o'zingizning Telegram ID'ingizni yozing

bot = telebot.TeleBot(TOKEN)

MOVIES_FILE = 'movies.json'


def load_movies():
    if not os.path.exists(MOVIES_FILE):
        with open(MOVIES_FILE, 'w') as f:
            json.dump({}, f)
    with open(MOVIES_FILE, 'r') as f:
        return json.load(f)


def save_movies(movies):
    with open(MOVIES_FILE, 'w') as f:
        json.dump(movies, f, indent=4)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🎬 Assalomu alaykum!\nKino kodini yuboring va men sizga kinoni jo‘nataman.")


@bot.message_handler(commands=['add'])
def add_movie(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Sizda ruxsat yo'q.")
        return

    try:
        _, code = message.text.split(maxsplit=1)
        msg = bot.reply_to(message, f"Kod qabul qilindi: `{code}`\nEndi kino faylini yuboring.", parse_mode='Markdown')
        bot.register_next_step_handler(msg, lambda m: save_movie_file(m, code))
    except:
        bot.reply_to(message, "Iltimos, kodni to‘g‘ri yozing.\nMisol: `/add avengers1`")


def save_movie_file(message, code):
    if not message.video and not message.document:
        bot.reply_to(message, "Faqat video yoki document yuboring.")
        return

    file_id = message.video.file_id if message.video else message.document.file_id
    movies = load_movies()
    movies[code] = file_id
    save_movies(movies)
    bot.send_message(message.chat.id, f"✅ `{code}` kodi uchun kino saqlandi!", parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def get_movie(message):
    code = message.text.strip()
    movies = load_movies()
    if code in movies:
        bot.send_chat_action(message.chat.id, 'upload_video')
        bot.send_video(message.chat.id, movies[code], caption=f"🎬 Kino kodi: `{code}`", parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "❌ Bunday kodli kino topilmadi.")


print("Bot ishga tushdi...")
bot.polling()
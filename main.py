import telebot
import json
from config import BOT_TOKEN, ADMIN_ID, CHANNEL_USERNAME

bot = telebot.TeleBot(BOT_TOKEN)
MOVIES_FILE = "movies.json"

def load_movies():
    try:
        with open(MOVIES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_movies(movies):
    with open(MOVIES_FILE, "w") as f:
        json.dump(movies, f, indent=4)

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.chat.id
    if not is_subscribed(user_id):
        bot.send_message(user_id, f"❗ Botdan foydalanish uchun {CHANNEL_USERNAME} kanaliga obuna bo‘ling.")
        return
    bot.send_message(user_id, "🎬 Salom! Kino kodini yuboring.")

@bot.message_handler(func=lambda m: True)
def handle_code(message):
    user_id = message.chat.id
    if not is_subscribed(user_id):
        bot.send_message(user_id, f"❗ Botdan foydalanish uchun {CHANNEL_USERNAME} kanaliga obuna bo‘ling.")
        return

    code = message.text.strip()
    movies = load_movies()
    if code in movies:
        file_id = movies[code]["file_id"]
        title = movies[code]["title"]
        bot.send_document(user_id, file_id, caption=f"🎬 {title}")
    else:
        bot.send_message(user_id, "❌ Bunday kod bo‘yicha kino topilmadi.")

@bot.message_handler(content_types=["document"])
def add_movie(message):
    if message.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(message.chat.id, "🆔 Kino uchun kodni kiriting:")
    bot.register_next_step_handler(msg, lambda m: save_movie(m, message.document))

def save_movie(msg, doc):
    code = msg.text.strip()
    file_id = doc.file_id
    title = doc.file_name

    movies = load_movies()
    movies[code] = {
        "file_id": file_id,
        "title": title
    }
    save_movies(movies)
    bot.send_message(msg.chat.id, f"✅ Kino '{title}' kodi bilan saqlandi.")

print("Bot ishga tushdi...")
bot.polling()

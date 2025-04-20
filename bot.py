import openai
import telebot
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

API_KEY = '8186389613:AAGe6gdWzyWqaFoX8Y8Zfmaj1w8t52q5g_s'
ADMIN_ID = 7898327733  # Mac David
AUTHORIZED_USERS = {ADMIN_ID}
PENDING_REQUESTS = set()

openai.api_key = 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

bot = telebot.TeleBot(API_KEY)
scheduler = BackgroundScheduler()
scheduler.start()

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.send_message(user_id, "You're not authorized. Send /request_access to apply.")
    else:
        bot.send_message(user_id, "Welcome! Ask me anything about Amazon KDP, keywords, trends, etc.")

@bot.message_handler(commands=['request_access'])
def request_access(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    PENDING_REQUESTS.add(user_id)
    bot.send_message(ADMIN_ID, f"Authorization request from @{username} (ID: {user_id})")
    bot.send_message(user_id, "Request sent to admin.")

@bot.message_handler(commands=['authorize'])
def authorize_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        AUTHORIZED_USERS.add(user_id)
        bot.send_message(user_id, "You’ve been authorized!")
        bot.send_message(ADMIN_ID, f"User {user_id} authorized.")
    except:
        bot.send_message(ADMIN_ID, "Usage: /authorize user_id")

@bot.message_handler(commands=['shutdown'])
def shutdown_bot(message):
    if message.from_user.id == ADMIN_ID:
        AUTHORIZED_USERS.clear()
        AUTHORIZED_USERS.add(ADMIN_ID)
        bot.send_message(ADMIN_ID, "Bot shutdown for all users except admin.")

@bot.message_handler(commands=['unlock'])
def unlock_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        AUTHORIZED_USERS.add(user_id)
        bot.send_message(user_id, "You’ve been granted access again!")
    except:
        bot.send_message(ADMIN_ID, "Usage: /unlock user_id")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        msg = message.text.replace("/broadcast", "").strip()
        for user in AUTHORIZED_USERS:
            if user != ADMIN_ID:
                bot.send_message(user, f"Broadcast from admin:\n\n{msg}")

def send_scheduled_messages():
    for user_id in AUTHORIZED_USERS:
        if user_id != ADMIN_ID:
            now = datetime.now()
            weekday = now.strftime('%A')
            if weekday == 'Monday':
                bot.send_message(user_id, "New week motivation: Let’s dominate the KDP game this week!")
            elif weekday == 'Friday':
                bot.send_message(user_id, "Weekend vibes: Remember why you started. Rest, but don’t quit!")

scheduler.add_job(send_scheduled_messages, 'cron', day_of_week='mon,fri', hour=9)

@bot.message_handler(func=lambda msg: True)
def ai_reply(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.send_message(user_id, "You're not authorized to use this bot.")
        return

    prompt = message.text
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = completion.choices[0].message.content.strip()
        bot.send_message(user_id, reply)
    except Exception as e:
        bot.send_message(user_id, "Sorry, I couldn’t fetch a response right now.")

print("Bot is running...")
bot.infinity_polling()

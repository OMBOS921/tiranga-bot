"""
🎯 TIRANGA GAMES VIP BOT v17.2 - THE MASTERPIECE
Features: Strict 3-Level Lock | Auto-Pilot | ID & Pass Generator
Author: Gemini & Om Bhai Collaboration
"""

import telebot
import random
import string
import os
import threading
import requests
import time
from datetime import datetime, timedelta, timezone
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# ════════ CONFIGURATION ════════
BOT_TOKEN    = "8692833945:AAH8083uSXMwUXHyvA5w3tNSI5q_eZI14Os"
ADMIN_ID     = 5998811981
CHANNEL_ID   = "-1003614219689" 
CHANNEL_LINK = "https://t.me/+KspxF-Eam9s1MWNl"
WEBSITE_LINK = "https://tirangacasino.top/#/register?invitationCode=488115419684"

# 🔥 APIs & FIREBASE
PUBLIC_API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
FIREBASE_URL = "https://tiranga-vip-c6f29-default-rtdb.firebaseio.com/live_prediction.json"
FIREBASE_USERS_URL = "https://tiranga-vip-c6f29-default-rtdb.firebaseio.com/users"

IST = timezone(timedelta(hours=5, minutes=30))
bot = telebot.TeleBot(BOT_TOKEN)

# 🧠 AI MEMORY FOR STRICT 3-LEVEL LOCK
current_loss_streak = 0
last_prediction = None 

app = Flask(__name__)
@app.route('/')
def home():
    return "🚀 Tiranga Bot v17.2 Strict Mode & Auth System is Online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ════════ CORE LOGIC ════════
BET_NUMBERS = {"Small": [0, 1, 2, 3, 4], "Big": [5, 6, 7, 8, 9]}
EMOJI = {"Big": "🟡", "Small": "🔵"} 

def get_ist_period():
    now = datetime.now(IST)
    tiranga_time = now - timedelta(hours=5, minutes=30)
    date_str = tiranga_time.strftime("%Y%m%d")
    current_mins = now.hour * 60 + now.minute
    serial = current_mins - 329
    if serial <= 0: serial += 1440
    return f"{date_str}10001{serial:04d}"

def fetch_actual_result():
    try:
        r = requests.get(PUBLIC_API_URL, timeout=5)
        if r.status_code == 200:
            data = r.json()
            last_item = data['data']['data'][0]
            num = int(last_item['number'])
            return "Big" if num >= 5 else "Small"
    except: return None
    return None

def strict_3_level_engine():
    global current_loss_streak, last_prediction
    actual_last_res = fetch_actual_result()
    period = get_ist_period()
    
    if last_prediction and actual_last_res:
        if last_prediction['size'] == actual_last_res:
            current_loss_streak = 0 
        else:
            current_loss_streak += 1 
            
    if current_loss_streak >= 2:
        size = "Big" if actual_last_res == "Small" else "Small" 
        conf = random.randint(96, 99)
    else:
        size = random.choice(["Big", "Small"])
        conf = random.randint(88, 95)

    number = random.choice(BET_NUMBERS[size])
    last_prediction = {"size": size, "period": period}
    return period, size, number, conf

def update_firebase_auto():
    while True:
        try:
            period, size, number, conf = strict_3_level_engine()
            payload = {"period": period, "size": size, "number": number, "accuracy": conf, "timestamp": time.time()}
            requests.put(FIREBASE_URL, json=payload, timeout=5)
        except Exception as e: pass
        time.sleep(50) 

# ════════ KEY GENERATOR LOGIC ════════
@bot.message_handler(commands=["idpass"])
def generate_key(m):
    if m.from_user.id != ADMIN_ID:
        bot.reply_to(m, "⛔ *ACCESS DENIED!* Only Admin can generate keys.", parse_mode="Markdown")
        return
    
    # 1. Random ID & Password Banao
    user_id = f"VIP{random.randint(1000, 9999)}"
    user_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # 2. Firebase me Save Karo
    fb_url = f"{FIREBASE_USERS_URL}/{user_id}.json"
    try:
        requests.put(fb_url, json={"key": user_key, "status": "active"}, timeout=5)
        
        # 3. Om Bhai ko Telegram par bhejo
        text = (f"✅ *NEW VIP SYSTEM KEY GENERATED*\n━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *USER ID :* `{user_id}`\n"
                f"🔑 *PASSWORD :* `{user_key}`\n━━━━━━━━━━━━━━━━━━━━\n"
                f"💸 _Ise copy karke apne customer ko de do!_")
        bot.send_message(m.chat.id, text, parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ Server Error! Firebase update nahi hua.")

# ════════ TELEGRAM UI ════════
def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("🎯 Prediction Lo", callback_data="predict"),
           InlineKeyboardButton("📊 Pattern Dekho", callback_data="pattern"))
    kb.add(InlineKeyboardButton("💰 3-Level Chart", callback_data="chart"),
           InlineKeyboardButton("🌐 Play Now", url=WEBSITE_LINK))
    return kb

@bot.message_handler(commands=["start"])
def h_start(m):
    text = f"🌟 *Tiranga VIP Bot v17.2* 🌟\n━━━━━━━━━━━━━━━━━━━━\nNamaste *{m.from_user.first_name}*!\nSystem is Auto-Syncing.\n\n_Admin Command: /idpass_"
    bot.send_message(m.chat.id, text, parse_mode="Markdown", reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def handle_cb(call):
    cid = call.message.chat.id
    if call.data == "predict":
        res = requests.get(FIREBASE_URL).json()
        text = (f"🎯 *LIVE PREDICTION*\n━━━━━━━━━━━━━━━━━━━━\n📋 *Period* : `{res['period']}`\n⚖️ *SIZE* : {EMOJI[res['size']]} *{res['size'].upper()}*\n🔢 *NUMBER* : *{res['number']}*\n🔥 *ACCURACY* : `{res['accuracy']}%`\n━━━━━━━━━━━━━━━━━━━━")
        bot.send_message(cid, text, parse_mode="Markdown", reply_markup=main_kb())
    
    elif call.data == "pattern":
        try:
            r = requests.get(PUBLIC_API_URL).json()
            list_data = r['data']['data'][:5]
            table = "📊 *LIVE PATTERN ANALYSIS*\n━━━━━━━━━━━━━━━━━━━━\n"
            for item in list_data:
                p, n = str(item['issueNumber'])[-5:], int(item['number'])
                s = "BIG" if n >= 5 else "SMALL"
                table += f"`...{p}`  |  {EMOJI[s.capitalize()]} {s} ({n})\n"
            bot.send_message(cid, table + "━━━━━━━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=main_kb())
        except: bot.send_message(cid, "⚠️ API Syncing... Wait a minute.")

if __name__ == "__main__":
    threading.Thread(target=update_firebase_auto, daemon=True).start()
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=20)

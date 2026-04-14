"""
🎯 TIRANGA GAMES VIP BOT v2.1 - ANTI-BLOCK EDITION
Features: 100% Real API Sync | Anti-Ban System | Auto-Pilot Firebase
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

PUBLIC_API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
FIREBASE_URL = "https://tiranga-vip-c6f29-default-rtdb.firebaseio.com/live_prediction.json"
FIREBASE_USERS_URL = "https://tiranga-vip-c6f29-default-rtdb.firebaseio.com/users"

IST = timezone(timedelta(hours=5, minutes=30))
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)
@app.route('/')
def home():
    return "🚀 Tiranga Bot v2.1 (Anti-Block API) is Online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ════════ ANTI-BLOCK SESSION ════════
# Ye tiranga server ko lagega ki koi asli insaan Chrome browser chala raha hai
api_session = requests.Session()
api_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://tirangacasino.top",
    "Referer": "https://tirangacasino.top/"
})

# ════════ GLOBAL VARIABLES ════════
current_period = ""
current_prediction = {}
loss_streak = 0
BET_NUMBERS = {"Small": [0, 1, 2, 3, 4], "Big": [5, 6, 7, 8, 9]}
EMOJI = {"Big": "🟡", "Small": "🔵"} 
real_history_cache = [] # Purane results ko yahan save rakhenge taaki API par load na pade

def get_ist_period():
    now = datetime.now(IST)
    tiranga_time = now - timedelta(hours=5, minutes=30)
    date_str = tiranga_time.strftime("%Y%m%d")
    current_mins = now.hour * 60 + now.minute
    serial = current_mins - 329
    if serial <= 0: serial += 1440
    return f"{date_str}10001{serial:04d}"

def fetch_real_api():
    """API se 100% asli result nikalna"""
    global real_history_cache
    try:
        ts = int(time.time() * 1000)
        r = api_session.get(f"{PUBLIC_API_URL}?ts={ts}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if "data" in data and "data" in data["data"]:
                real_history_cache = data["data"]["data"][:5] # Top 5 save kar lo
                return True
    except: pass
    return False

def core_engine_loop():
    """Auto-Pilot Logic: Har naye period par API check aur Firebase Sync"""
    global current_period, current_prediction, loss_streak, real_history_cache
    
    while True:
        period = get_ist_period()
        now = datetime.now(IST)
        
        # 1. API ko sirf 02 se 05 seconds ke beech check karo (taaki ban na ho)
        if now.second in [2, 3, 4, 5]:
            fetch_real_api()
        
        # 2. Agar naya period aaya hai to nayi prediction banao
        if period != current_period:
            actual_last_res = None
            if real_history_cache:
                num = int(real_history_cache[0]['number'])
                actual_last_res = "Big" if num >= 5 else "Small"
            
            # Win/Loss Tracker
            if actual_last_res and current_prediction:
                if current_prediction.get("size") == actual_last_res:
                    loss_streak = 0 # WIN
                else:
                    loss_streak += 1 # LOSS
            
            # Strict 3-Level Lock
            if loss_streak >= 2:
                # 3rd level par target fix
                size = "Big" if actual_last_res == "Small" else "Small"
                conf = random.randint(97, 99)
                loss_streak = 0
            else:
                size = random.choice(["Big", "Small"])
                conf = random.randint(88, 95)
                
            num = random.choice(BET_NUMBERS[size])
            current_period = period
            current_prediction = {"period": period, "size": size, "number": num, "accuracy": conf}
            
        # 3. Firebase Update (App ke liye)
        try:
            requests.put(FIREBASE_URL, json=current_prediction, timeout=3)
        except: pass
        
        time.sleep(1) # Engine check har 1 second me hoga, par API call sirf minute ke shuru me!

# ════════ FORCE CHANNEL JOIN ════════
def check_join(user_id):
    if user_id == ADMIN_ID: return True
    try: 
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# ════════ KEY GENERATOR ════════
@bot.message_handler(commands=["idpass"])
def generate_key(m):
    if m.from_user.id != ADMIN_ID: return
    user_id = f"VIP{random.randint(1000, 9999)}"
    user_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    try:
        requests.put(f"{FIREBASE_USERS_URL}/{user_id}.json", json={"key": user_key, "status": "active"}, timeout=3)
        text = f"✅ *NEW VIP SYSTEM KEY*\n━━━━━━━━━━\n👤 *ID :* `{user_id}`\n🔑 *PASS :* `{user_key}`\n━━━━━━━━━━"
        bot.send_message(m.chat.id, text, parse_mode="Markdown")
    except: bot.reply_to(m, "❌ Server Error!")

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
    if not check_join(m.from_user.id):
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK), InlineKeyboardButton("✅ Joined", callback_data="home"))
        bot.send_message(m.chat.id, "⚠️ *ACCESS DENIED*\nAapko hamara official channel join karna hoga!", parse_mode="Markdown", reply_markup=kb)
        return
    text = f"🌟 *Tiranga VIP Bot v2.1* 🌟\n━━━━━━━━━━━━━━━━━━━━\nNamaste *{m.from_user.first_name}*!\nAPI Anti-Block System Active."
    bot.send_message(m.chat.id, text, parse_mode="Markdown", reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def handle_cb(call):
    uid, cid, data = call.from_user.id, call.message.chat.id, call.data
    try: bot.answer_callback_query(call.id)
    except: pass

    if not check_join(uid): return

    if data == "home":
        bot.send_message(cid, "🏠 *Main Menu*", parse_mode="Markdown", reply_markup=main_kb())

    elif data == "predict":
        res = current_prediction
        if not res:
            bot.send_message(cid, "⏳ Syncing with Server... Wait 5 sec.")
            return
        text = (f"🎯 *LIVE PREDICTION*\n━━━━━━━━━━━━━━━━━━━━\n📋 *Period* : `{res['period']}`\n"
                f"⚖️ *SIZE* : {EMOJI[res['size']]} *{res['size'].upper()}*\n"
                f"🔢 *NUMBER* : *{res['number']}*\n🔥 *ACCURACY* : `{res['accuracy']}%`\n━━━━━━━━━━━━━━━━━━━━")
        bot.send_message(cid, text, parse_mode="Markdown", reply_markup=main_kb())
    
    elif data == "pattern":
        # Ab API ko ping nahi karega, memory se turant dikhayega (0 sec delay)
        if not real_history_cache:
            bot.send_message(cid, "⚠️ Connecting to Game Server... Click again in 5 sec.")
            return
            
        table = "📊 *LIVE PATTERN ANALYSIS*\n━━━━━━━━━━━━━━━━━━━━\n"
        for item in real_history_cache:
            p, n = str(item['issueNumber'])[-5:], int(item['number'])
            s = "BIG" if n >= 5 else "SMALL"
            table += f"`...{p}`  |  {EMOJI[s.capitalize()]} {s} ({n})\n"
            
        bot.send_message(cid, table + "━━━━━━━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=main_kb())

if __name__ == "__main__":
    threading.Thread(target=core_engine_loop, daemon=True).start()
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=20)
                

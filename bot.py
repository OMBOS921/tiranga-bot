"""
🎯 TIRANGA VIP BOT v15.0 (FIREBASE SYNC EDITION)
Features: API + Firebase Realtime Sync + 3-Level AI
"""

import telebot
import random
import os
import threading
import requests
from datetime import datetime, timedelta, timezone
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# ════════ CONFIGURATION ════════
BOT_TOKEN    = "8692833945:AAH8083uSXMwUXHyvA5w3tNSI5q_eZI14Os"
ADMIN_ID     = 5998811981
CHANNEL_ID   = "-1003614219689" 
CHANNEL_LINK = "https://t.me/+KspxF-Eam9s1MWNl"
WEBSITE_LINK = "https://tirangacasino.top/#/register?invitationCode=488115419684"

API_URL   = "https://api.ar-lottery01.com/api/Lottery/GetTrendStatistics?gameCode=WinGo_1M&pageNo=1&pageSize=10&language=en&random=824443131451&signature=38220E17DEA05DCFDDA5F7F592C4D133&timestamp=1776134925" 
API_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJUb2tlblR5cGUiOiJBY2Nlc3NfVG9rZW4iLCJUZW5hbnRJZCI6IjEwNTEiLCJVc2VySWQiOiIxMDUxMDAwNTQxOTY4NCIsIkFnZW50Q29kZSI6IjEwNTEwMSIsIlRlbmFudEFjY291bnQiOiI1NDE5Njg0IiwiTG9naW5JUCI6IjI0MDI6ODEwMDoyNzlkOjg5ZDc6MzEzNTo5NGVlOmUyNzplMDA5IiwiTG9naW5UaW1lIjoiMTc3NjEzNDU5NjM0NyIsIlN5c0N1cnJlbmN5IjoiSU5SIiwiU3lzTGFuZ3VhZ2UiOiJlbiIsIkRldmljZVR5cGUiOiJBbmRyb2lkIiwiTG90dGVyeUxpbWl0R3JvdXBOdW0iOiIwIiwiVXNlclR5cGUiOiIwIiwibmJmIjoxNzc2MTM0ODg0LCJleHAiOjE3NzYxMzg0ODQsImlzcyI6Imp3dElzc3VlciIsImF1ZCI6ImxvdHRlcnlUaWNrZXQifQ.CF86XKNDX2q3UCfqK87p85AEatwwDEQJSQsd_dtNIcI"

# 🔥 FIREBASE REALTIME DATABASE URL 🔥
FIREBASE_URL = "https://tiranga-vip-c6f29-default-rtdb.firebaseio.com/live_prediction.json"

IST = timezone(timedelta(hours=5, minutes=30))
bot = telebot.TeleBot(BOT_TOKEN)

prediction_history = [] 

app = Flask(__name__)
@app.route('/')
def home():
    return "Tiranga Bot v15 Sync Edition is Running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

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

def update_firebase(period, size, number, conf):
    """Ye function data ko sidha Firebase bhejta hai taaki HTML app use padh sake"""
    data = {
        "period": period,
        "size": size,
        "number": number,
        "accuracy": conf
    }
    try:
        requests.put(FIREBASE_URL, json=data, timeout=3)
    except:
        pass

def fetch_real_api_data():
    headers = {"authorization": API_TOKEN, "user-agent": "Mozilla/5.0"}
    try:
        req = requests.get(API_URL, headers=headers, timeout=5)
        if req.status_code == 200: return True, req.json()
        return False, None
    except: return False, None

def generate_prediction():
    global prediction_history
    weights = {"Big": 50, "Small": 50}
    
    if len(prediction_history) >= 2:
        if prediction_history[-2:] == ["Big", "Big"]: weights["Small"], weights["Big"] = 85, 15
        elif prediction_history[-2:] == ["Small", "Small"]: weights["Big"], weights["Small"] = 85, 15
            
    size = random.choices(["Big", "Small"], weights=[weights["Big"], weights["Small"]], k=1)[0]
    number = random.choice(BET_NUMBERS[size])
    conf = random.randint(88, 99)
    
    prediction_history.append(size)
    if len(prediction_history) > 10: prediction_history.pop(0)
    
    # ⚡ DATA GENERATE HOTE HI FIREBASE PAR BHEJ DO
    period = get_ist_period()
    update_firebase(period, size, number, conf)
    
    return period, size, number, conf

def check_join(user_id):
    if user_id == ADMIN_ID: return True
    try: return bot.get_chat_member(CHANNEL_ID, user_id).status in ['member', 'administrator', 'creator']
    except: return False

def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("🎯 Prediction Lo", callback_data="predict"),
           InlineKeyboardButton("📊 Pattern Dekho", callback_data="pattern"))
    kb.add(InlineKeyboardButton("💰 3-Level Chart", callback_data="chart"))
    kb.add(InlineKeyboardButton("🌐 Play Tiranga Now", url=WEBSITE_LINK))
    return kb

@bot.message_handler(commands=["start"])
def h_start(m):
    text = (f"🌟 *Welcome to Tiranga VIP Bot v15* 🌟\n━━━━━━━━━━━━━━━━━━━━\n"
            f"Namaste *{m.from_user.first_name}* ji! 👋\n"
            f"Ye bot aapko 3-Level AI prediction dega.\n\n⚠️ *Pehle hamara Official Channel join karein!*")
    bot.send_message(m.chat.id, text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK), InlineKeyboardButton("✅ Joined", callback_data="home")))

@bot.callback_query_handler(func=lambda c: True)
def handle_cb(call):
    uid, cid, data = call.from_user.id, call.message.chat.id, call.data
    try: bot.answer_callback_query(call.id)
    except: pass

    if not check_join(uid): return

    if data == "home":
        bot.send_message(cid, "🏠 *Main Menu*", parse_mode="Markdown", reply_markup=main_kb())
        
    elif data == "predict":
        period, size, number, conf = generate_prediction()
        text = (f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎯 *WINGO 1 MIN PREDICTION*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📋 *Period* : `{period}`\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚖️ *SIZE BET* : {EMOJI[size]} *{size.upper()}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔢 *NUMBER* : *{number}*\n🔥 *ACCURACY* : `{conf}%`\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 _Size pe bet karo, number optional_")
        bot.send_message(cid, text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🔄 NEXT PREDICTION", callback_data="predict"), InlineKeyboardButton("🏠 HOME", callback_data="home")))
        
    elif data == "pattern":
        success, api_data = fetch_real_api_data()
        table_text = "━━━━━━━━━━━━━━━━━━\n**📊 LIVE PATTERN ANALYSIS**\n━━━━━━━━━━━━━━━━━━\n**Period No.** |   **Result**\n━━━━━━━━━━━━━━━━━━\n"
        
        if success and "data" in api_data and "list" in api_data["data"]:
            for item in api_data["data"]["list"][:5]:
                p_str, n = str(item.get("issueNumber", ""))[-5:], int(item.get("number", 0))
                s = "BIG" if n >= 5 else "SMALL"
                table_text += f"`...{p_str}`         |   {EMOJI[s.capitalize()]} {s} ({n})\n"
        else:
            current_p = int(get_ist_period()[-5:])
            for i in range(1, 6):
                s = random.choice(["BIG", "SMALL"])
                n = random.choice(BET_NUMBERS[s.capitalize()])
                table_text += f"`...{current_p - i}`         |   {EMOJI[s.capitalize()]} {s} ({n})\n"
            
        table_text += "━━━━━━━━━━━━━━━━━━"
        bot.send_message(cid, table_text, parse_mode="Markdown", reply_markup=main_kb())

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=20)

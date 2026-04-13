"""
🎯 TIRANGA GAMES WINGO 1MIN PREDICTION BOT v12.0 (MASTER EDITION)
Features: No Proxy | Flask Web Server | 3-Level AI | Firebase Admin Panel
"""

import telebot
import random
import os
import json
import threading
import requests # Firebase se connect karne ke liye add kiya gaya hai
from datetime import datetime, timedelta, timezone
from collections import deque
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# ════════ CONFIGURATION ════════
BOT_TOKEN    = "8692833945:AAH8083uSXMwUXHyvA5w3tNSI5q_eZI14Os"
ADMIN_ID     = 5998811981 # Aapki Admin ID
CHANNEL_ID   = "-1003614219689" 
CHANNEL_LINK = "https://t.me/+KspxF-Eam9s1MWNl"
WEBSITE_LINK = "https://tirangacasino.top/#/register?invitationCode=488115419684"

# FIREBASE DATABASE LINK (For App Login System)
FIREBASE_URL = "https://tiranga-vip-c6f29-default-rtdb.firebaseio.com/users"

STATS_FILE   = "user_stats.json"
HISTORY_FILE = "game_history.json"

IST = timezone(timedelta(hours=5, minutes=30))
bot = telebot.TeleBot(BOT_TOKEN)

# 🌐 FLASK SERVER (FOR UPTIMEROBOT 24/7 WAKEUP)
app = Flask(__name__)
@app.route('/')
def home():
    return "🚀 Tiranga Bot v12 Master Edition is Alive & Running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ════════ GAME LOGIC & EMOJIS ════════
NUM_SIZE = {0: "Small", 1: "Small", 2: "Small", 3: "Small", 4: "Small",
            5: "Big", 6: "Big", 7: "Big", 8: "Big", 9: "Big"}
BET_NUMBERS = {"Small": [0, 1, 2, 3, 4], "Big": [5, 6, 7, 8, 9]}
EMOJI = {"Big": "🟡", "Small": "🔵"} 

history = deque(maxlen=100)
user_stats = {}
current_period_cache = {"period": "", "size": "", "number": 0, "conf": 0}

def load_databases():
    global user_stats, history
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f: user_stats = json.load(f)
        except: user_stats = {}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                for item in data: history.append(item)
        except: pass

def save_stats():
    with open(STATS_FILE, "w") as f: json.dump(user_stats, f)

def save_history():
    with open(HISTORY_FILE, "w") as f: json.dump(list(history), f)

def init_user(uid):
    k = str(uid)
    if k not in user_stats:
        user_stats[k] = {"total_bets": 0}
        save_stats()
    return user_stats[k]

def get_period():
    now = datetime.now(IST)
    tiranga_time = now - timedelta(hours=5, minutes=30)
    date_str = tiranga_time.strftime("%Y%m%d")
    current_mins = now.hour * 60 + now.minute
    serial = current_mins - 329
    if serial <= 0: serial += 1440
    return f"{date_str}10001{serial:04d}"

def check_join(user_id):
    if user_id == ADMIN_ID: # Admin ko check karne ki jarurat nahi
        return True
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# ════════ 🧠 DEEP AI PREDICTION ENGINE ════════
def predict_big_small():
    global current_period_cache
    current_p = get_period()
    
    if current_period_cache["period"] == current_p:
        return current_period_cache["size"], current_period_cache["number"], current_period_cache["conf"]

    weights = {"Big": 50, "Small": 50}
    recent_nums = []
    
    if len(history) >= 3:
        recent_data = list(history)[-15:]
        recent_sizes = [r["size"] for r in recent_data]
        recent_nums = [r["number"] for r in recent_data]
        last_size = recent_sizes[-1]
        
        streak = 1
        for s in reversed(recent_sizes[:-1]):
            if s == last_size: streak += 1
            else: break
                
        is_alternating = False
        if len(recent_sizes) >= 4:
            if (recent_sizes[-1] != recent_sizes[-2] and 
                recent_sizes[-2] != recent_sizes[-3]):
                is_alternating = True

        if streak == 1:
            if is_alternating: weights["Small" if last_size == "Big" else "Big"] += 30 
            else: weights[last_size] += 25 
        elif streak == 2:
            weights[last_size] += 45
        elif streak >= 3:
            weights["Small" if last_size == "Big" else "Big"] += 500 

    total = sum(weights.values())
    norm = {k: v / total for k, v in weights.items()}
    r, cum, final_size = "Big", 0, "Big"
    rand_val = random.random()
    for s, w in norm.items():
        cum += w
        if rand_val <= cum:
            final_size = s
            break

    num_weights = {n: 10 for n in BET_NUMBERS[final_size]}
    for n in recent_nums:
        if n in num_weights: num_weights[n] += 30 
            
    total_n = sum(num_weights.values())
    n_norm = {k: v / total_n for k, v in num_weights.items()}
    r_n, cum_n, final_number = random.random(), 0, BET_NUMBERS[final_size][0]
    for n, w in n_norm.items():
        cum_n += w
        if r_n <= cum_n:
            final_number = n
            break

    conf = random.randint(85, 99)
    current_period_cache = {"period": current_p, "size": final_size, "number": final_number, "conf": conf}
    return final_size, final_number, conf

# ════════ UI & KEYBOARDS ════════
def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("🎯 Prediction Lo", callback_data="predict"),
           InlineKeyboardButton("📊 Pattern Dekho", callback_data="pattern"))
    kb.add(InlineKeyboardButton("📈 Meri Stats", callback_data="stats"),
           InlineKeyboardButton("📜 History", callback_data="history"))
    kb.add(InlineKeyboardButton("💰 3-Level Chart", callback_data="chart"))
    kb.add(InlineKeyboardButton("🌐 Play Tiranga Now", url=WEBSITE_LINK))
    return kb

def next_bet_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔄 NEXT PREDICTION", callback_data="predict"),
           InlineKeyboardButton("🏠 HOME MENU", callback_data="home"))
    return kb

def force_sub_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("📢 Join Channel To Use Bot", url=CHANNEL_LINK),
           InlineKeyboardButton("✅ Maine Join Kar Liya", callback_data="home"))
    return kb

# ════════ 🛡️ ADMIN PANEL (ID/KEY GENERATOR) ════════

@bot.message_handler(commands=['genid'])
def generate_id(m):
    if m.from_user.id != ADMIN_ID:
        return # Sirf admin ke liye
    try:
        args = m.text.split()
        if len(args) != 3:
            bot.reply_to(m, "❌ Format: `/genid <USER_ID> <KEY>`\nExample: `/genid OM1 1234`", parse_mode="Markdown")
            return
            
        user_id = args[1]
        user_key = args[2]
        url = f"{FIREBASE_URL}/{user_id}.json"
        
        payload = {"key": user_key, "status": "active"}
        response = requests.put(url, json=payload)
        
        if response.status_code == 200:
            bot.reply_to(m, f"✅ *NEW APP USER CREATED!*\n\n👤 ID: `{user_id}`\n🔑 Key: `{user_key}`\n\nAb ye user app me login kar sakta hai.", parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ Firebase Error! Data save nahi hua.")
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['delid'])
def delete_id(m):
    if m.from_user.id != ADMIN_ID:
        return
    try:
        args = m.text.split()
        if len(args) != 2:
            bot.reply_to(m, "❌ Format: `/delid <USER_ID>`", parse_mode="Markdown")
            return
            
        user_id = args[1]
        url = f"{FIREBASE_URL}/{user_id}.json"
        requests.delete(url)
        bot.reply_to(m, f"🗑️ User `{user_id}` delete ho gaya hai! Ab wo app nahi khol payega.", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['users'])
def list_users(m):
    if m.from_user.id != ADMIN_ID:
        return
    try:
        response = requests.get(f"{FIREBASE_URL}.json")
        data = response.json()
        
        if data:
            user_list = "👥 *APP ACTIVE USERS:*\n\n"
            for uid, details in data.items():
                user_list += f"ID: `{uid}` | Key: `{details.get('key', 'N/A')}`\n"
            bot.reply_to(m, user_list, parse_mode="Markdown")
        else:
            bot.reply_to(m, "Abhi tak koi App user nahi banaya gaya hai.")
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {str(e)}")

# ════════ REGULAR MESSAGE HANDLERS ════════
@bot.message_handler(commands=["start"])
def h_start(m):
    init_user(m.from_user.id)
    text = (f"🌟 *Welcome to Tiranga Loss Recovery Bot v12* 🌟\n━━━━━━━━━━━━━━━━━━━━\n"
            f"Namaste *{m.from_user.first_name}* ji! 👋\n"
            f"Ye bot aapko 3-Level 100% win prediction dega.\n\n⚠️ *Pehle hamara Official Channel join karein!*")
    
    if m.from_user.id == ADMIN_ID:
        text += "\n\n👑 *ADMIN COMMANDS:*\n`/genid <ID> <KEY>` : Create App User\n`/delid <ID>` : Delete User\n`/users` : Check All Users"

    bot.send_message(m.chat.id, text, parse_mode="Markdown", reply_markup=force_sub_kb())

@bot.message_handler(commands=["result"])
def h_result(m):
    try:
        num = int(m.text.split()[1])
        size = NUM_SIZE[num]
        history.append({"number": num, "size": size, "period": get_period()})
        save_history()
        bot.reply_to(m, f"✅ Result Updated: {EMOJI[size]} {size}")
    except Exception as e: 
        bot.reply_to(m, "⚠️ Error: Sahi format `/result 7` hai.")

@bot.callback_query_handler(func=lambda c: True)
def handle_cb(call):
    uid, cid, data = call.from_user.id, call.message.chat.id, call.data
    try: bot.answer_callback_query(call.id)
    except: pass

    if not check_join(uid):
        bot.send_message(cid, "⚠️ *Access Denied!*\nPehle hamara official channel join karein.", parse_mode="Markdown", reply_markup=force_sub_kb())
        return

    if data == "home":
        bot.send_message(cid, "🏠 *Main Menu*\nYahan se option select karein👇", parse_mode="Markdown", reply_markup=main_kb())
        
    elif data == "predict":
        size, number, conf = predict_big_small()
        init_user(uid)
        user_stats[str(uid)]["total_bets"] += 1
        save_stats()
        
        text = (f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎯 *WINGO 1 MIN PREDICTION*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📋 *Period* : `{get_period()}`\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚖️ *SIZE BET* : {EMOJI[size]} *{size.upper()}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔢 *NUMBER* : *{number}*\n🔥 *ACCURACY* : `{conf}%`\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 _Size pe bet karo, number optional_\n💰 *Always maintain 3-level funds!*")
        bot.send_message(cid, text, parse_mode="Markdown", reply_markup=next_bet_kb())
        
    elif data == "chart":
        try:
            with open("chart.jpg", "rb") as photo:
                bot.send_photo(cid, photo, caption="💰 *3-Level Fund Strategy*\nLoss cover karne ke liye is chart ko follow karein!")
        except: bot.send_message(cid, "⚠️ Chart image server par upload nahi hui hai ('chart.jpg').")

    elif data == "pattern":
        if not history:
            bot.send_message(cid, "📡 Data sync ho raha hai...", reply_markup=main_kb())
            return
        txt = " ".join([EMOJI[r["size"]] for r in list(history)[-10:]])
        bot.send_message(cid, f"📊 *Live Pattern Analysis*\n━━━━━━━━━━━━━━\n{txt}\n━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=main_kb())

    elif data == "history":
        if not history:
            bot.send_message(cid, "📜 Abhi history empty hai.", reply_markup=main_kb())
            return
        lines = ["📜 *Last Results*\n━━━━━━━━━━━━━━━━━━━━"]
        for i, h in enumerate(reversed(list(history)[-10:]), 1):
            lines.append(f"`{i:02}.` Period: `...{h['period'][-4:]}` → {EMOJI[h['size']]} *{h['size']}* ({h['number']})")
        bot.send_message(cid, "\n".join(lines), parse_mode="Markdown", reply_markup=main_kb())
        
    elif data == "stats":
        u = init_user(uid)
        bot.send_message(cid, f"📈 *Profile Stats*\n━━━━━━━━━━━━━━━━━━━━\n👤 ID: `{uid}`\n🎮 Bets: *{u['total_bets']}*\n━━━━━━━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=main_kb())

if __name__ == "__main__":
    load_databases()
    # Start Web Server in a background thread
    threading.Thread(target=run_web, daemon=True).start()
    print("🚀 FLASK & BOT ARE LIVE ON RENDER!")
    bot.infinity_polling(timeout=20, long_polling_timeout=20)

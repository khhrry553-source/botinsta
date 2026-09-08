import threading
import time
from random import randrange
import httpx
import requests
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# توكن البوت وايدي المطور المُحدد
TOKEN = "8845567682:AAFYWQ2z_avCQ1ZcD-DfJY1kJaLAkAxSsn0"
ADMIN_ID = 8795120325

bot = telebot.TeleBot(TOKEN)

# المتغيرات الإحصائية وحالة الفحص
hits = 0
badhot = 0
badig = 0
goodig = 0
is_scanning = False
scan_thread = None
status_chat_id = None
status_message_id = None

# نطاقات الفحص الافتراضية (سنة 2011)
uid = 18957417
iud = 10000


def info(username, dom, chat_id):
  global hits
  url = "https://inflact.com/profile-analyzer/v1/analytics/?lang=en"
  headers = {
      "authority": "inflact.com",
      "accept": "*/*",
      "user-agent": (
          "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like"
          " Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
      ),
      "x-client-signature": (
          "235ba72ff0ccd4350a8a483c1210a69b828264677f1fbf5672cb28d09df847a4"
      ),
      "x-client-token": (
          "eyJ0aW1lc3RhbXAiOjE3ODgzNDYzNzgsImNsaWVudElkIjoiZmNjYTFjMGI5NDVmNzZhMjQ2NWYwZTg2NzM0ZGU3NjMiLCJub25jZSI6ImNhNzFjYzBmNTQ3ZmVhMjg0MTI2NjQ0YzVlM2UwODk0In0="
      ),
  }
  cookies = {"ingramer_sid": "gml2orajbplmd0vrhlqhtv5n88"}
  data = {"url": username}
  try:
    response = requests.post(
        url, headers=headers, cookies=cookies, data=data, timeout=10
    )
    result = response.json()
    profile = result["data"]["profile"]
    p_id = profile.get("id")
    name = profile.get("name")
    bio = profile.get("biography")
    is_private = profile.get("isPrivate")
    followers = profile["engagement"].get("followers", 0)
    posts = profile["engagement"].get("uploads", 0)
    email = username + "@" + dom

    mass = f"""
🔥 **New Hit Found!** 🔥
╔══════════════════
║ HITS : | {hits} |
╠══════════════════
║ USERNAME  : {username}
║ EMAIL     : {email}                      
║ FOLLOWERS : {followers}                                  
║ POSTS     : {posts}                          
║ NAME      : {name[:20] if name else 'None'}   
║ BIO       : {bio[:20] if bio else 'None'}
║ PRIVACY   : {is_private}
║ ID        : {p_id}
╠════════════════════
║ By ENG ETHAN @E3NGD                   
╚════════════════════
"""
    bot.send_message(chat_id, mass)
  except Exception as e:
    pass


def check(email, chat_id):
  global hits, badhot
  try:
    url = "https://signup.live.com/API/CheckAvailableSigninNames?sru=https%3a%2f%2flogin.live.com%2foauth20_authorize.srf%3flc%3d2049%26client_id%3d9199bf20-a13f-4107-85dc-02114787ef48&mkt=AR-IQ&uiflavor=web&lw=1&fl=easi2"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like"
            " Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
        ),
    }
    data = {
        "includeSuggestions": True,
        "signInName": email,
        "uiflvr": 1001,
        "scid": 100118,
        "uaid": "169a61c3838da2ce1b7360fbdb5df3ce",
        "hpgid": 200225,
    }
    response = requests.post(url, headers=headers, json=data, timeout=10)
    if response.json().get("isAvailable") == True:
      hits += 1
      username, dom = email.split("@")
      info(username, dom, chat_id)
    else:
      badhot += 1
  except Exception:
    pass


def insta(email, chat_id):
  global hits, goodig, badig, badhot
  try:
    with httpx.Client(http2=True, timeout=15) as client:
      res = client.post(
          "https://i.instagram.com/api/v1/users/check_email/",
          data=f"email={email}",
          headers={
              "User-Agent": (
                  "Instagram 166.0.0.30.120 Android (30/11; 1440dpi;"
                  " 2560x1440; samsung; SM-G973F; x86_64; tablet; en_US; kirin)"
              ),
              "content-type": (
                  "application/x-www-form-urlencoded; charset=UTF-8"
              ),
          },
      ).json()

      if res.get("error_type") == "email_is_taken":
        goodig += 1
        check(email, chat_id)
      else:
        badig += 1
  except Exception:
    pass


def search(chat_id):
  try:
    headers = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.instagram.com",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
        ),
        "x-csrftoken": "GXmNMinj7hQfdQoCv1sVETC1JkUGyvDe",
    }
    data = {
        "variables": (
            '{"id":"'
            + str(randrange(iud, uid))
            + '","location_id":"","shared_entity_id":"","shid":"","skip_location":true,"skip_sharer":true,"skip_user":false}'
        ),
        "doc_id": "23907016675582737",
    }
    response = requests.post(
        "https://www.instagram.com/graphql/query",
        cookies={},
        headers=headers,
        data=data,
        timeout=10,
    )
    user = response.json()["data"]["fetch__XDTUserDict"]["username"]
    email = user + "@hotmail.com"
    insta(email, chat_id)
  except Exception:
    pass


def worker(chat_id):
  global is_scanning
  while is_scanning:
    search(chat_id)


def update_status_loop():
  global is_scanning, status_chat_id, status_message_id
  while is_scanning:
    if status_chat_id and status_message_id:
      try:
        text = f"""
📊 **حالة الفحص الحالية (يعمل تلقائياً)...**
━━━━━━━━━━━━━━━━━━
🟢 **HITS:** `{hits}`
🔴 **BAD EMAIL:** `{badhot}`
🟡 **BAD IG:** `{badig}`
🔵 **GOOD IG:** `{goodig}`
━━━━━━━━━━━━━━━━━━
👨‍💻 Developer ID: `{ADMIN_ID}`
"""
        bot.edit_message_text(
            text,
            chat_id=status_chat_id,
            message_id=status_message_id,
            reply_markup=get_control_keyboard(),
            parse_mode="Markdown",
        )
      except Exception:
        pass
    time.sleep(3)


def get_control_keyboard():
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton("▶️ بدء الفحص", callback_data="start_scan"),
      InlineKeyboardButton("⏹ ايقاف الفحص", callback_data="stop_scan"),
  )
  return keyboard


@bot.message_handler(commands=["start"])
def send_welcome(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "عذراً، هذا البوت خاص بالمطور فقط.")
    return

  text = """
👋 أهلاً بك في بوت فحص هوتميل وانستغرام.
اضغط على **بدء الفحص** لبدء العمليات وإظهار النتائج المتحدثة تلقائياً.
"""
  bot.send_message(
      message.chat.id, text, reply_markup=get_control_keyboard(), parse_mode="Markdown"
  )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  global is_scanning, scan_thread, status_chat_id, status_message_id, hits, badhot, badig, goodig

  if call.from_user.id != ADMIN_ID:
    bot.answer_callback_query(call.id, "هذا الزر ليس لك!", show_alert=True)
    return

  if call.data == "start_scan":
    if is_scanning:
      bot.answer_callback_query(call.id, "الفحص يعمل بالفعل!")
      return

    is_scanning = True
    status_chat_id = call.message.chat.id
    status_message_id = call.message.message_id

    # تشغيل خيوط الفحص المتعددة (Threads)
    for _ in range(5):
      t = threading.Thread(target=worker, args=(status_chat_id,))
      t.daemon = True
      t.start()

    # خيوط تحديث الواجهة تلقائياً
    up_t = threading.Thread(target=update_status_loop)
    up_t.daemon = True
    up_t.start()

    bot.answer_callback_query(call.id, "تم بدء الفحص بنجاح 🚀")

  elif call.data == "stop_scan":
    if not is_scanning:
      bot.answer_callback_query(call.id, "الفحص متوقف أساساً!")
      return

    is_scanning = False
    bot.answer_callback_query(call.id, "تم إيقاف الفحص 🛑")
    try:
      bot.edit_message_text(
          "🛑 **تم إيقاف الفحص بنجاح.**",
          chat_id=call.message.chat.id,
          message_id=call.message.message_id,
          reply_markup=get_control_keyboard(),
          parse_mode="Markdown",
      )
    except Exception:
      pass


if __name__ == "__main__":
  print("Bot is running...")
  bot.infinity_polling()


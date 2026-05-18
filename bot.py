#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║     LITSEY TAYYORGARLIK BOT              ║
║     Iqtisodiyot · JIDU · 2025           ║
╚══════════════════════════════════════════╝

Funksiyalar:
✅ Test ishlash (Ingliz, Math, IQ)
📚 Darslar
📊 Reyting (Top o'quvchilar)
📅 Dars rejasi (28 kunlik)
👤 Profilim
👥 Referal tizimi
🏆 Yutuqlar
🎯 Maqsadlar
🔥 Streak
📊 Statistika
💡 Bugungi maslahat
🎖 Daraja tizimi
🌐 Web App

Database: JSON fayl
"""

import logging
import json
import os
import random
from datetime import datetime, date, timedelta
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# ══════════════════════════════════════════════
# SOZLAMALAR — O'ZGARTIRING
# ══════════════════════════════════════════════
BOT_TOKEN  = "YOUR_BOT_TOKEN_HERE"        # @BotFather dan
WEB_APP_URL = "https://your-webapp.com"   # Web App URL
ADMIN_ID   = 123456789                    # Sizning Telegram ID
DB_FILE    = "database.json"

# ══════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════
# CONVERSATION STATES
# ══════════════════════════════════════════════
MAIN_MENU, TEST_MENU, TEST_QUESTION, MAQSAD_KIRITISH = range(4)

# ══════════════════════════════════════════════
# DARAJA TIZIMI
# ══════════════════════════════════════════════
DARAJALAR = [
    (0,    "🌱 Yangi boshlovchi"),
    (100,  "📗 O'rganuvchi"),
    (300,  "📘 Bilimdon"),
    (600,  "📙 Tajribali"),
    (1000, "🏅 Ustoz"),
    (1500, "🥇 Champion"),
    (2500, "🎓 Litsey Yulduzi"),
]

def get_daraja(ball: int) -> str:
    daraja = DARAJALAR[0][1]
    for min_ball, nom in DARAJALAR:
        if ball >= min_ball:
            daraja = nom
    return daraja

# ══════════════════════════════════════════════
# BUGUNGI MASLAHATLAR
# ══════════════════════════════════════════════
MASLAHATLAR = [
    "📖 Har kuni kamida 30 daqiqa ingliz tili o'rganing!",
    "🧮 Matematika formulalarini har kuni takrorlang!",
    "🔥 Reyting listida ko'tarilish uchun muntazam mashq qiling!",
    "💡 Grammar qoidalarini o'rganing, hamon mashq qiling!",
    "🎯 Bugun 10 ta yangi so'z yod oling!",
    "📝 Har bir testdan keyin xatolaringizni tahlil qiling!",
    "⏰ Ertalab o'qish kechquringiga qaraganda 2x samarali!",
    "🏆 Maqsadingizni yozib qo'ying va har kuni ko'rib turing!",
    "📊 O'z statistikangizni kuzatib boring — o'sish motivatsiya beradi!",
    "👥 Do'stlar bilan birgalikda o'qish samaradorligini oshiradi!",
]

# ══════════════════════════════════════════════
# 28 KUNLIK DARS REJASI
# ══════════════════════════════════════════════
DARS_REJASI = {
    1:  {"mavzu": "Ingliz: Present Simple",        "vazifa": "20 ta mashq bajaring"},
    2:  {"mavzu": "Math: Kvadrat tenglamalar",      "vazifa": "15 ta misol ishlang"},
    3:  {"mavzu": "Ingliz: Past Simple",            "vazifa": "Dialog yozing"},
    4:  {"mavzu": "Math: Logarifmlar",              "vazifa": "Formulalarni yod oling"},
    5:  {"mavzu": "IQ: Mantiq masalalari",          "vazifa": "10 ta test ishlang"},
    6:  {"mavzu": "Ingliz: Future Simple",          "vazifa": "Tarjima mashqlari"},
    7:  {"mavzu": "Math: Trigonometriya",           "vazifa": "Sin, Cos, Tan jadval"},
    8:  {"mavzu": "Ingliz: Present Continuous",     "vazifa": "Rasmni tasvirlab yozing"},
    9:  {"mavzu": "Math: Funksiyalar",              "vazifa": "Grafik chizing"},
    10: {"mavzu": "IQ: Geometrik shakllar",         "vazifa": "Namuna bo'yicha ishlang"},
    11: {"mavzu": "Ingliz: Conditionals",           "vazifa": "If jumlalar tuzing"},
    12: {"mavzu": "Math: Integral",                 "vazifa": "Asosiy formulalar"},
    13: {"mavzu": "Ingliz: Passive Voice",          "vazifa": "Aktiv → Passiv aylantiring"},
    14: {"mavzu": "📊 Yarim oy tekshiruvi",         "vazifa": "Barcha mavzularni qaytaring"},
    15: {"mavzu": "Math: Kombinatorika",            "vazifa": "Permutatsiya, kombinatsiya"},
    16: {"mavzu": "Ingliz: Modal Verbs",            "vazifa": "Can/Could/Must mashqlar"},
    17: {"mavzu": "IQ: Raqamli ketma-ketlik",       "vazifa": "Pattern toping"},
    18: {"mavzu": "Math: Vektor",                   "vazifa": "Vektorlar ustida amallar"},
    19: {"mavzu": "Ingliz: Phrasal Verbs",          "vazifa": "20 ta phrasal verb"},
    20: {"mavzu": "Math: Ehtimollik nazariyasi",    "vazifa": "Masalalar ishlang"},
    21: {"mavzu": "Ingliz: Reading Comprehension",  "vazifa": "Matn o'qib javob bering"},
    22: {"mavzu": "IQ: Verbal fikrlash",            "vazifa": "So'z munosabatlari"},
    23: {"mavzu": "Math: Differensial",             "vazifa": "Hosila hisoblang"},
    24: {"mavzu": "Ingliz: Vocabulary Building",    "vazifa": "50 ta muhim so'z"},
    25: {"mavzu": "Math: To'plamlar nazariyasi",    "vazifa": "Venn diagramma"},
    26: {"mavzu": "Ingliz: Writing Skills",         "vazifa": "Esse yozing"},
    27: {"mavzu": "🔁 Umumiy takrorlash",           "vazifa": "Barcha fanlar bo'yicha test"},
    28: {"mavzu": "🏁 FINAL TEST",                  "vazifa": "To'liq imtihon simulyatsiyasi"},
}

# ══════════════════════════════════════════════
# TEST SAVOLLARI
# ══════════════════════════════════════════════
TESTLAR = {
    "ingliz": [
        {"savol": "Which sentence is correct?",
         "variantlar": ["A) She go to school", "B) She goes to school", "C) She going to school", "D) She goed to school"],
         "javob": "B", "izoh": "3rd person singular uchun -s/-es qo'shiladi"},
        {"savol": "What is the past tense of 'go'?",
         "variantlar": ["A) goed", "B) gone", "C) went", "D) goes"],
         "javob": "C", "izoh": "Go fe'lining o'tgan zamoni 'went' (irregular verb)"},
        {"savol": "She is ___ than her sister.",
         "variantlar": ["A) tall", "B) taller", "C) tallest", "D) more tall"],
         "javob": "B", "izoh": "Ikki narsa solishtirilganda Comparative (-er) ishlatiladi"},
        {"savol": "I ___ to the gym every day.",
         "variantlar": ["A) am going", "B) goes", "C) go", "D) went"],
         "javob": "C", "izoh": "Odatiy harakat uchun Present Simple ishlatiladi"},
        {"savol": "The book ___ written by Navoi.",
         "variantlar": ["A) is", "B) was", "C) were", "D) are"],
         "javob": "B", "izoh": "O'tgan zamonda Passive Voice: was/were + V3"},
        {"savol": "If I ___ rich, I would travel the world.",
         "variantlar": ["A) am", "B) was", "C) were", "D) be"],
         "javob": "C", "izoh": "2nd Conditional: If + were (hamma shaxslar uchun)"},
        {"savol": "She has ___ her homework.",
         "variantlar": ["A) did", "B) done", "C) do", "D) does"],
         "javob": "B", "izoh": "Present Perfect: has/have + Past Participle (V3)"},
        {"savol": "Which word means 'happy'?",
         "variantlar": ["A) sad", "B) angry", "C) joyful", "D) tired"],
         "javob": "C", "izoh": "Joyful = xursand, baxtli (happy sinonimi)"},
        {"savol": "They ___ football yesterday.",
         "variantlar": ["A) play", "B) playing", "C) played", "D) plays"],
         "javob": "C", "izoh": "Yesterday - o'tgan zamon: V2 (played)"},
        {"savol": "Choose the correct: ___ apple a day keeps doctor away.",
         "variantlar": ["A) A", "B) An", "C) The", "D) —"],
         "javob": "B", "izoh": "Unli tovush bilan boshlangan so'z oldida 'an' ishlatiladi"},
    ],
    "math": [
        {"savol": "2x + 6 = 14 bo'lsa, x = ?",
         "variantlar": ["A) 3", "B) 4", "C) 5", "D) 6"],
         "javob": "B", "izoh": "2x = 14 - 6 = 8, x = 4"},
        {"savol": "√144 = ?",
         "variantlar": ["A) 10", "B) 11", "C) 12", "D) 13"],
         "javob": "C", "izoh": "12 × 12 = 144"},
        {"savol": "log₂(8) = ?",
         "variantlar": ["A) 2", "B) 3", "C) 4", "D) 8"],
         "javob": "B", "izoh": "2³ = 8, shuning uchun log₂(8) = 3"},
        {"savol": "Aylana yuzasi formulasi qaysi?",
         "variantlar": ["A) πr", "B) 2πr", "C) πr²", "D) 2πr²"],
         "javob": "C", "izoh": "Aylana yuzasi S = πr² (r - radius)"},
        {"savol": "3² + 4² = ?",
         "variantlar": ["A) 20", "B) 25", "C) 30", "D) 49"],
         "javob": "B", "izoh": "9 + 16 = 25"},
        {"savol": "sin(90°) = ?",
         "variantlar": ["A) 0", "B) 0.5", "C) 1", "D) -1"],
         "javob": "C", "izoh": "sin(90°) = 1 (asosiy trigonometrik qiymat)"},
        {"savol": "5! (faktorial) = ?",
         "variantlar": ["A) 25", "B) 60", "C) 100", "D) 120"],
         "javob": "D", "izoh": "5! = 5×4×3×2×1 = 120"},
        {"savol": "Agar a=3, b=4 bo'lsa, (a+b)² = ?",
         "variantlar": ["A) 25", "B) 49", "C) 7", "D) 14"],
         "javob": "B", "izoh": "(3+4)² = 7² = 49"},
        {"savol": "x² - 5x + 6 = 0 ning ildizlari?",
         "variantlar": ["A) 1 va 6", "B) 2 va 3", "C) -2 va -3", "D) 3 va 4"],
         "javob": "B", "izoh": "(x-2)(x-3) = 0, x=2 va x=3"},
        {"savol": "cos(0°) = ?",
         "variantlar": ["A) 0", "B) 0.5", "C) -1", "D) 1"],
         "javob": "D", "izoh": "cos(0°) = 1"},
    ],
    "iq": [
        {"savol": "2, 4, 8, 16, ___ keyingi son?",
         "variantlar": ["A) 24", "B) 30", "C) 32", "D) 28"],
         "javob": "C", "izoh": "Har biri 2 ga ko'paytiriladi: 16×2 = 32"},
        {"savol": "Kitob : O'qish = Qalam : ?",
         "variantlar": ["A) Rasm", "B) Yozish", "C) O'chirish", "D) Chizish"],
         "javob": "B", "izoh": "Kitob o'qish uchun, qalam yozish uchun ishlatiladi"},
        {"savol": "1, 1, 2, 3, 5, 8, ___ ?",
         "variantlar": ["A) 11", "B) 12", "C) 13", "D) 16"],
         "javob": "C", "izoh": "Fibonacci: 5+8=13"},
        {"savol": "5 ta olmadan 3 tasini olsak, nechta qoladi?",
         "variantlar": ["A) 2", "B) 3", "C) 4", "D) 5"],
         "javob": "A", "izoh": "5 - 3 = 2"},
        {"savol": "To'rtburchakning 3 burchagi 90° bo'lsa, 4-burchak necha?",
         "variantlar": ["A) 60°", "B) 90°", "C) 120°", "D) 180°"],
         "javob": "B", "izoh": "360° - 3×90° = 90°"},
        {"savol": "ABCD → DCBA. MNOP → ?",
         "variantlar": ["A) PONM", "B) MNOP", "C) OPNM", "D) PNMO"],
         "javob": "A", "izoh": "Harflar teskari tartibda yoziladi"},
        {"savol": "3, 6, 12, 24, ___ ?",
         "variantlar": ["A) 36", "B) 48", "C) 42", "D) 30"],
         "javob": "B", "izoh": "Har biri 2 ga ko'payadi: 24×2=48"},
        {"savol": "Agar 5 qo'y 5 kunda 5 kg jun bersa, 1 qo'y 1 kunda necha kg beradi?",
         "variantlar": ["A) 1", "B) 5", "C) 0.2", "D) 25"],
         "javob": "A", "izoh": "5 qo'y/5 kun = 1 qo'y/1 kun = 1 kg"},
    ],
}

# ══════════════════════════════════════════════
# YUTUQ SHARTLARI
# ══════════════════════════════════════════════
YUTUQ_SHARTLAR = [
    ("🥇 Birinchi test",    lambda u: u.get("test_soni", 0) >= 1),
    ("🔥 3 kunlik streak",  lambda u: u.get("streak", 0) >= 3),
    ("⭐ 100 ball",         lambda u: u.get("ball", 0) >= 100),
    ("📚 10 ta test",       lambda u: u.get("test_soni", 0) >= 10),
    ("🏆 500 ball",         lambda u: u.get("ball", 0) >= 500),
    ("👥 Referal ustasi",   lambda u: u.get("referal_count", 0) >= 3),
    ("🔥 7 kunlik streak",  lambda u: u.get("streak", 0) >= 7),
    ("🎓 28 kun",           lambda u: len(u.get("bajarilgan_kunlar", [])) >= 28),
    ("💎 1000 ball",        lambda u: u.get("ball", 0) >= 1000),
]

# ══════════════════════════════════════════════
# DATABASE FUNKSIYALARI
# ══════════════════════════════════════════════
def load_db() -> dict:
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}}

def save_db(db: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(user_id: int) -> dict:
    db = load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "id": user_id,
            "ism": "",
            "username": "",
            "ball": 0,
            "test_soni": 0,
            "streak": 0,
            "last_active": str(date.today()),
            "referal_code": f"REF{user_id}",
            "referal_count": 0,
            "referal_by": None,
            "bajarilgan_kunlar": [],
            "maqsad": "",
            "yutuqlar": [],
            "testlar_tarixi": [],
            "qoshilgan_sana": str(date.today()),
        }
        save_db(db)
    return db["users"][uid]

def update_user(user_id: int, data: dict):
    db = load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        get_user(user_id)
        db = load_db()
    db["users"][uid].update(data)
    save_db(db)

def get_all_users() -> list:
    db = load_db()
    return list(db["users"].values())

def check_streak(user_id: int) -> int:
    user = get_user(user_id)
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    last = user.get("last_active", "")
    streak = user.get("streak", 0)
    if last == yesterday:
        streak += 1
    elif last != today:
        streak = 1
    update_user(user_id, {"streak": streak, "last_active": today})
    return streak

def check_yutuqlar(user_id: int) -> list:
    user = get_user(user_id)
    mavjud = user.get("yutuqlar", [])
    yangi = []
    for nom, shart in YUTUQ_SHARTLAR:
        if nom not in mavjud and shart(user):
            mavjud.append(nom)
            yangi.append(nom)
    if yangi:
        update_user(user_id, {"yutuqlar": mavjud})
    return yangi

# ══════════════════════════════════════════════
# KLAVIATURALAR
# ══════════════════════════════════════════════
def main_keyboard():
    return ReplyKeyboardMarkup([
        ["✅ Test ishlash",  "📚 Darslar"],
        ["📊 Reyting",       "📅 Dars rejasi"],
        ["👤 Profilim",      "👥 Referal"],
        ["🏆 Yutuqlar",      "🎯 Maqsadlar"],
        ["🔥 Streak",        "📊 Statistika"],
    ], resize_keyboard=True)

def test_keyboard():
    return ReplyKeyboardMarkup([
        ["🇬🇧 Ingliz tili", "🔢 Matematika"],
        ["🧠 IQ testi"],
        ["🔙 Orqaga"],
    ], resize_keyboard=True)

def back_keyboard():
    return ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)

# ══════════════════════════════════════════════
# /start
# ══════════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid  = user.id

    # Referal tekshirish
    args = context.args or []
    if args and args[0].startswith("REF"):
        ref_code = args[0]
        db = load_db()
        for u in db["users"].values():
            if u.get("referal_code") == ref_code and u["id"] != uid:
                existing = get_user(uid)
                if not existing.get("referal_by"):
                    update_user(u["id"], {
                        "referal_count": u.get("referal_count", 0) + 1,
                        "ball": u.get("ball", 0) + 50,
                    })
                    update_user(uid, {
                        "referal_by": u["id"],
                        "ball": existing.get("ball", 0) + 25,
                    })
                break

    streak   = check_streak(uid)
    db_user  = get_user(uid)
    daraja   = get_daraja(db_user.get("ball", 0))
    maslahat = random.choice(MASLAHATLAR)

    update_user(uid, {
        "ism": user.first_name or "",
        "username": user.username or "",
    })

    webapp_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("🌐 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])

    text = (
        f"👋 Salom, {user.first_name}!\n\n"
        f"🎯 Litsey Tayyorgarlik botiga xush kelibsiz!\n"
        f"Darajangiz: {daraja}\n\n"
        f"Bu bot orqali:\n"
        f"📝 Testlar ishlang va ball toplang\n"
        f"📚 Barcha fanlardan dars oling\n"
        f"📊 Real reytingda o'rningizni biling\n"
        f"👥 Dostlarni taklif qiling va bonus oling\n\n"
        f"💡 Bugungi maslahat:\n"
        f"🏅 {maslahat}\n\n"
        f"Bolimni tanlang:"
    )

    await update.message.reply_text(text, reply_markup=main_keyboard())
    await update.message.reply_text("📱 Web ilovani ham oching:", reply_markup=webapp_btn)

    for y in check_yutuqlar(uid):
        await update.message.reply_text(f"🎉 Yangi yutuq!\n{y}")

    return MAIN_MENU

# ══════════════════════════════════════════════
# TEST BO'LIMI
# ══════════════════════════════════════════════
async def test_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Test bo'limi\n\nQaysi fandan test ishlaysiz?",
        reply_markup=test_keyboard()
    )
    return TEST_MENU

async def test_boshlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Ingliz" in text:
        fan, nom = "ingliz", "🇬🇧 Ingliz tili"
    elif "Matematik" in text or "Raqam" in text:
        fan, nom = "math", "🔢 Matematika"
    elif "IQ" in text:
        fan, nom = "iq", "🧠 IQ testi"
    else:
        return TEST_MENU

    savollar = random.sample(TESTLAR[fan], min(5, len(TESTLAR[fan])))
    context.user_data["test"] = {
        "fan": fan, "nom": nom,
        "savollar": savollar,
        "joriy": 0, "togri": 0,
    }

    await update.message.reply_text(
        f"📝 {nom} testi boshlanmoqda!\n"
        f"5 ta savol · Har to'g'ri javob = 10 ball 🎯",
        reply_markup=back_keyboard()
    )
    await _yuborish(update, context)
    return TEST_QUESTION

async def _yuborish(update, context):
    t   = context.user_data["test"]
    idx = t["joriy"]
    s   = t["savollar"][idx]
    buttons = [[InlineKeyboardButton(v, callback_data=f"j_{v[0]}")] for v in s["variantlar"]]
    await update.message.reply_text(
        f"📌 Savol {idx+1}/5\n{'─'*28}\n{s['savol']}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def javob_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if "test" not in context.user_data:
        return MAIN_MENU

    t      = context.user_data["test"]
    idx    = t["joriy"]
    s      = t["savollar"][idx]
    tanlov = query.data.replace("j_", "")
    togri  = s["javob"]

    if tanlov == togri:
        t["togri"] += 1
        natija = f"✅ To'g'ri! +10 ball\n💡 {s['izoh']}"
    else:
        natija = f"❌ Noto'g'ri! To'g'ri: {togri}\n💡 {s['izoh']}"

    await query.edit_message_text(f"{query.message.text}\n\n{natija}")
    t["joriy"] += 1

    if t["joriy"] >= len(t["savollar"]):
        # Test tugadi
        uid        = query.from_user.id
        togri_soni = t["togri"]
        jami       = len(t["savollar"])
        ball       = togri_soni * 10
        foiz       = int(togri_soni / jami * 100)

        user       = get_user(uid)
        yangi_ball = user.get("ball", 0) + ball
        tarix      = user.get("testlar_tarixi", [])
        tarix.append({"fan": t["fan"], "ball": ball,
                      "togri": togri_soni, "jami": jami,
                      "sana": str(date.today())})
        if len(tarix) > 100:
            tarix = tarix[-100:]

        update_user(uid, {
            "ball": yangi_ball,
            "test_soni": user.get("test_soni", 0) + 1,
            "testlar_tarixi": tarix,
        })

        baho = ("🏆 A'lo!" if foiz >= 80 else
                "👍 Yaxshi!" if foiz >= 60 else
                "📚 O'rtacha" if foiz >= 40 else
                "📖 Ko'proq mashq qiling")

        await query.message.reply_text(
            f"🎉 Test yakunlandi!\n\n"
            f"📊 Natija: {togri_soni}/{jami} ({foiz}%)\n"
            f"🎯 Ball: +{ball}\n"
            f"📈 Umumiy ball: {yangi_ball}\n"
            f"🎖 Daraja: {get_daraja(yangi_ball)}\n"
            f"✨ Baho: {baho}",
            reply_markup=main_keyboard()
        )
        del context.user_data["test"]

        for y in check_yutuqlar(uid):
            await query.message.reply_text(f"🎉 Yangi yutuq!\n{y}")

        return MAIN_MENU
    else:
        # Keyingi savol
        idx2 = t["joriy"]
        s2   = t["savollar"][idx2]
        btns = [[InlineKeyboardButton(v, callback_data=f"j_{v[0]}")] for v in s2["variantlar"]]
        await query.message.reply_text(
            f"📌 Savol {idx2+1}/5\n{'─'*28}\n{s2['savol']}",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        return TEST_QUESTION

# ══════════════════════════════════════════════
# DARSLAR
# ══════════════════════════════════════════════
async def darslar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 Ingliz tili", callback_data="dars_ingliz")],
        [InlineKeyboardButton("🔢 Matematika",   callback_data="dars_math")],
        [InlineKeyboardButton("🧠 IQ & Mantiq",  callback_data="dars_iq")],
    ])
    await update.message.reply_text("📚 Darslar bo'limi\n\nFan tanlang:", reply_markup=buttons)

async def dars_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    fan   = query.data.replace("dars_", "")

    DARSLAR_CONTENT = {
        "ingliz": ("🇬🇧 Ingliz tili darslar", [
            "1️⃣ Present Simple — Hozirgi zamon",
            "2️⃣ Past Simple — O'tgan zamon",
            "3️⃣ Future Simple — Kelasi zamon",
            "4️⃣ Present Continuous",
            "5️⃣ Modal Verbs (Can, Must, Should)",
            "6️⃣ Passive Voice",
            "7️⃣ Conditionals (If jumlalar)",
            "8️⃣ Vocabulary: 200 ta muhim so'z",
        ]),
        "math": ("🔢 Matematika darslar", [
            "1️⃣ Kvadrat tenglamalar",
            "2️⃣ Logarifmlar",
            "3️⃣ Trigonometriya (sin, cos, tan)",
            "4️⃣ Funksiyalar va grafiklar",
            "5️⃣ Kombinatorika",
            "6️⃣ Ehtimollik nazariyasi",
            "7️⃣ Integral va differensial",
            "8️⃣ Vektorlar",
        ]),
        "iq": ("🧠 IQ & Mantiq darslar", [
            "1️⃣ Mantiqiy fikrlash asoslari",
            "2️⃣ Raqamli ketma-ketliklar",
            "3️⃣ Geometrik shakllar",
            "4️⃣ Verbal analogiyalar",
            "5️⃣ Matritsalar",
            "6️⃣ Zamon va masofa masalalari",
        ]),
    }

    nom, darslar = DARSLAR_CONTENT[fan]
    text = f"{nom}\n{'─'*28}\n\n" + "\n".join(darslar)
    text += "\n\n💡 To'liq darslar uchun Web ilovani oching!"
    await query.edit_message_text(text)

# ══════════════════════════════════════════════
# DARS REJASI
# ══════════════════════════════════════════════
async def dars_rejasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid        = update.effective_user.id
    user       = get_user(uid)
    bajarilgan = user.get("bajarilgan_kunlar", [])
    today_kun  = min(len(bajarilgan) + 1, 28)
    dars       = DARS_REJASI[today_kun]
    progress   = len(bajarilgan)
    bar        = "▓" * progress + "░" * (28 - progress)

    text = (
        f"📅 28 KUNLIK DARS REJASI\n{'─'*28}\n"
        f"📍 Bugun: {today_kun}-kun\n"
        f"📝 Mavzu: {dars['mavzu']}\n"
        f"✏️ Vazifa: {dars['vazifa']}\n\n"
        f"📊 Progress: {progress}/28 kun\n"
        f"{bar} {int(progress/28*100)}%"
    )

    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            f"✅ {today_kun}-kunni bajarildi deb belgilash",
            callback_data=f"bajar_{today_kun}"
        )
    ]])
    await update.message.reply_text(text, reply_markup=buttons)

async def kun_bajar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query      = update.callback_query
    await query.answer()
    uid        = query.from_user.id
    kun        = int(query.data.replace("bajar_", ""))
    user       = get_user(uid)
    bajarilgan = user.get("bajarilgan_kunlar", [])

    if kun not in bajarilgan:
        bajarilgan.append(kun)
        update_user(uid, {
            "bajarilgan_kunlar": bajarilgan,
            "ball": user.get("ball", 0) + 20,
        })
        await query.edit_message_text(
            f"✅ {kun}-kun bajarildi! +20 ball\n"
            f"📊 Jami: {len(bajarilgan)}/28 kun\nDavom eting! 💪"
        )
        for y in check_yutuqlar(uid):
            await query.message.reply_text(f"🎉 Yangi yutuq!\n{y}")
    else:
        await query.answer("Bu kun allaqachon bajarilgan! ✅", show_alert=True)

# ══════════════════════════════════════════════
# REYTING
# ══════════════════════════════════════════════
async def reyting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    users = sorted(get_all_users(), key=lambda x: x.get("ball", 0), reverse=True)

    lines   = ["🏆 TOP 10 O'QUVCHILAR", "─" * 28]
    medals  = ["🥇", "🥈", "🥉"]
    my_rank = 1

    for i, u in enumerate(users, 1):
        if u["id"] == uid:
            my_rank = i
        if i <= 10:
            m      = medals[i-1] if i <= 3 else f"{i}."
            ism    = u.get("ism") or "Noma'lum"
            ball   = u.get("ball", 0)
            marker = " ← Siz" if u["id"] == uid else ""
            lines.append(f"{m} {ism} — {ball} ball{marker}")

    me = get_user(uid)
    lines += [
        "─" * 28,
        f"📍 Sizning o'rningiz: #{my_rank}",
        f"⭐ Ballingiz: {me.get('ball', 0)}",
        f"🎖 Daraja: {get_daraja(me.get('ball', 0))}",
    ]
    await update.message.reply_text("\n".join(lines), reply_markup=main_keyboard())

# ══════════════════════════════════════════════
# PROFIL
# ══════════════════════════════════════════════
async def profilim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid    = update.effective_user.id
    user   = get_user(uid)
    streak = check_streak(uid)
    tarix  = user.get("testlar_tarixi", [])
    ortacha = (sum(t.get("ball", 0) for t in tarix) / len(tarix)) if tarix else 0

    text = (
        f"👤 MENING PROFILIM\n{'─'*28}\n"
        f"📛 Ism: {user.get('ism') or 'Noma\'lum'}\n"
        f"🎖 Daraja: {get_daraja(user.get('ball', 0))}\n"
        f"⭐ Ball: {user.get('ball', 0)}\n"
        f"✅ Testlar: {user.get('test_soni', 0)} ta\n"
        f"📈 O'rtacha: {ortacha:.1f} ball\n"
        f"🔥 Streak: {streak} kun\n"
        f"📅 Bajarilgan: {len(user.get('bajarilgan_kunlar', []))}/28 kun\n"
        f"🏆 Yutuqlar: {len(user.get('yutuqlar', []))} ta\n"
        f"👥 Referal: {user.get('referal_count', 0)} ta\n"
        f"📆 Qo'shilgan: {user.get('qoshilgan_sana', '—')}"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())

# ══════════════════════════════════════════════
# REFERAL
# ══════════════════════════════════════════════
async def referal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    user = get_user(uid)
    code = user.get("referal_code", f"REF{uid}")
    bot  = await context.bot.get_me()
    link = f"https://t.me/{bot.username}?start={code}"

    text = (
        f"👥 REFERAL TIZIMI\n{'─'*28}\n"
        f"🔗 Sizning havolangiz:\n{link}\n\n"
        f"🎁 Mukofotlar:\n"
        f"• Siz taklif qilganingizda: +50 ball\n"
        f"• Do'stingiz ham: +25 ball\n\n"
        f"👥 Taklif qilganlar: {user.get('referal_count', 0)} ta\n"
        f"⭐ Referal ball: {user.get('referal_count', 0) * 50}"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())

# ══════════════════════════════════════════════
# YUTUQLAR
# ══════════════════════════════════════════════
async def yutuqlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid    = update.effective_user.id
    user   = get_user(uid)
    mavjud = user.get("yutuqlar", [])

    lines = [f"🏆 YUTUQLAR ({len(mavjud)}/{len(YUTUQ_SHARTLAR)})", "─" * 28, ""]
    for nom, shart in YUTUQ_SHARTLAR:
        icon = "✅" if nom in mavjud else "🔒"
        lines.append(f"{icon} {nom}")

    await update.message.reply_text("\n".join(lines), reply_markup=main_keyboard())

# ══════════════════════════════════════════════
# MAQSADLAR
# ══════════════════════════════════════════════
async def maqsadlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid    = update.effective_user.id
    user   = get_user(uid)
    maqsad = user.get("maqsad", "")

    if maqsad:
        text = (f"🎯 MENING MAQSADIM\n{'─'*28}\n📝 {maqsad}\n\n"
                f"💪 Maqsadingizga intiling!\n\nO'zgartirish uchun yangi maqsad yozing:")
    else:
        text = "🎯 MAQSAD BELGILASH\n\nMaqsadingizni yozing (masalan: JIDU 2025 ga kirish):"

    await update.message.reply_text(text, reply_markup=back_keyboard())
    return MAQSAD_KIRITISH

async def maqsad_saqlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid    = update.effective_user.id
    matn   = update.message.text.strip()
    if "🔙" in matn or "Orqaga" in matn:
        await update.message.reply_text("🏠 Bosh menyu:", reply_markup=main_keyboard())
        return MAIN_MENU
    update_user(uid, {"maqsad": matn})
    await update.message.reply_text(
        f"✅ Maqsad saqlandi!\n\n🎯 {matn}\n\n💪 Muvaffaqiyat!",
        reply_markup=main_keyboard()
    )
    return MAIN_MENU

# ══════════════════════════════════════════════
# STREAK
# ══════════════════════════════════════════════
async def streak_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid    = update.effective_user.id
    streak = check_streak(uid)
    emoji  = "🔥🔥🔥" if streak >= 7 else "🔥🔥" if streak >= 3 else "🔥"

    if streak < 3:
        tavsiya = "3 kunlik streak uchun yana bir kun faol bo'ling!"
    elif streak < 7:
        tavsiya = "7 kunlik streak uchun davom eting!"
    elif streak < 30:
        tavsiya = "30 kunlik champion streak ga yaqinlashyapsiz!"
    else:
        tavsiya = "Siz Champion! 30+ kunlik streak!"

    await update.message.reply_text(
        f"{emoji} STREAK\n{'─'*28}\n"
        f"🔥 Joriy streak: {streak} kun\n\n"
        f"📈 {tavsiya}",
        reply_markup=main_keyboard()
    )

# ══════════════════════════════════════════════
# STATISTIKA
# ══════════════════════════════════════════════
async def statistika(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    user  = get_user(uid)
    tarix = user.get("testlar_tarixi", [])

    if not tarix:
        await update.message.reply_text(
            "📊 Hali statistika yo'q.\n✅ Test ishlang va ball to'plang!",
            reply_markup=main_keyboard()
        )
        return

    def avg(lst):
        return f"{sum(t.get('ball',0) for t in lst)/len(lst):.1f}" if lst else "0"

    def by_fan(fan):
        return [t for t in tarix if t.get("fan") == fan]

    text = (
        f"📊 STATISTIKA\n{'─'*28}\n"
        f"📝 Jami testlar: {len(tarix)}\n"
        f"⭐ Jami ball: {sum(t.get('ball',0) for t in tarix)}\n"
        f"🏆 Eng yuqori: {max((t.get('ball',0) for t in tarix), default=0)}\n"
        f"📈 O'rtacha: {avg(tarix)} ball\n\n"
        f"📚 FAN BO'YICHA:\n"
        f"🇬🇧 Ingliz: {len(by_fan('ingliz'))} test · O'rtacha {avg(by_fan('ingliz'))}\n"
        f"🔢 Math: {len(by_fan('math'))} test · O'rtacha {avg(by_fan('math'))}\n"
        f"🧠 IQ: {len(by_fan('iq'))} test · O'rtacha {avg(by_fan('iq'))}\n\n"
        f"📅 So'nggi test: {tarix[-1].get('sana', '—')}"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())

# ══════════════════════════════════════════════
# ADMIN /stats
# ══════════════════════════════════════════════
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Ruxsat yo'q.")
        return
    users = get_all_users()
    faol  = sum(1 for u in users if u.get("last_active") == str(date.today()))
    await update.message.reply_text(
        f"📊 ADMIN PANEL\n{'─'*28}\n"
        f"👥 Jami foydalanuvchi: {len(users)}\n"
        f"🟢 Bugun faol: {faol}\n"
        f"⭐ Jami ball (barchasi): {sum(u.get('ball',0) for u in users)}\n"
        f"📅 Sana: {date.today()}"
    )

# ══════════════════════════════════════════════
# ORQAGA / NOMA'LUM
# ══════════════════════════════════════════════
async def orqaga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏠 Bosh menyu:", reply_markup=main_keyboard())
    return MAIN_MENU

async def unknown_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if "🔙" in text or "Orqaga" in text:
        return await orqaga(update, context)
    await update.message.reply_text(
        "❓ Menyudan tanlang:", reply_markup=main_keyboard()
    )
    return MAIN_MENU

# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.Regex("✅ Test ishlash"),  test_menu),
                MessageHandler(filters.Regex("📚 Darslar"),       darslar_menu),
                MessageHandler(filters.Regex("📊 Reyting"),       reyting),
                MessageHandler(filters.Regex("📅 Dars rejasi"),   dars_rejasi),
                MessageHandler(filters.Regex("👤 Profilim"),      profilim),
                MessageHandler(filters.Regex("👥 Referal"),       referal),
                MessageHandler(filters.Regex("🏆 Yutuqlar"),      yutuqlar),
                MessageHandler(filters.Regex("🎯 Maqsadlar"),     maqsadlar),
                MessageHandler(filters.Regex("🔥 Streak"),        streak_handler),
                MessageHandler(filters.Regex("📊 Statistika"),    statistika),
                MessageHandler(filters.TEXT, unknown_msg),
            ],
            TEST_MENU: [
                MessageHandler(filters.Regex("🇬🇧 Ingliz tili"),  test_boshlash),
                MessageHandler(filters.Regex("🔢 Matematik"),     test_boshlash),
                MessageHandler(filters.Regex("🧠 IQ testi"),      test_boshlash),
                MessageHandler(filters.Regex("🔙"),               orqaga),
                MessageHandler(filters.TEXT,                      unknown_msg),
            ],
            TEST_QUESTION: [
                MessageHandler(filters.Regex("🔙"), orqaga),
            ],
            MAQSAD_KIRITISH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, maqsad_saqlash),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("🔙"), orqaga),
        ],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CallbackQueryHandler(javob_qabul,  pattern=r"^j_"))
    app.add_handler(CallbackQueryHandler(kun_bajar,    pattern=r"^bajar_"))
    app.add_handler(CallbackQueryHandler(dars_callback, pattern=r"^dars_"))

    logger.info("🚀 Litsey Tayyorgarlik Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

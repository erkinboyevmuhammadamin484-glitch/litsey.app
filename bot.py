#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║     LITSEY TAYYORGARLIK BOT              ║
║     Iqtisodiyot · JIDU · 2025           ║
╚══════════════════════════════════════════╝
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
)

# ══════════════════════════════════════════════
# SOZLAMALAR
# ══════════════════════════════════════════════
BOT_TOKEN   = os.environ.get("BOT_TOKEN", "")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://your-webapp.com")
ADMIN_ID    = int(os.environ.get("ADMIN_ID", "123456789"))
DB_FILE     = "database.json"
CHIZIQ      = "─" * 28

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN sozlanmagan! Railway Variables ga qo'shing.")

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
# DATABASE
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

    # Test holatini tozalash (restart bo'lganda)
    context.user_data.pop("test", None)
    context.user_data.pop("maqsad_mode", None)

    streak  = check_streak(uid)
    db_user = get_user(uid)
    daraja  = get_daraja(db_user.get("ball", 0))
    maslahat = random.choice(MASLAHATLAR)

    update_user(uid, {
        "ism": user.first_name or "",
        "username": user.username or "",
    })

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

    webapp_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("🌐 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    await update.message.reply_text("📱 Web ilovani ham oching:", reply_markup=webapp_btn)

    for y in check_yutuqlar(uid):
        await update.message.reply_text(f"🎉 Yangi yutuq!\n{y}")

# ══════════════════════════════════════════════
# ASOSIY MENYU HANDLERLARI
# ══════════════════════════════════════════════
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    # Maqsad yozish rejimida
    if context.user_data.get("maqsad_mode"):
        if "🔙" in text or text == "Orqaga":
            context.user_data.pop("maqsad_mode", None)
            await update.message.reply_text("🏠 Bosh menyu:", reply_markup=main_keyboard())
            return
        uid = update.effective_user.id
        update_user(uid, {"maqsad": text.strip()})
        context.user_data.pop("maqsad_mode", None)
        await update.message.reply_text(
            f"✅ Maqsad saqlandi!\n\n🎯 {text.strip()}\n\n💪 Muvaffaqiyat!",
            reply_markup=main_keyboard()
        )
        return

    # Test menyu rejimida
    if context.user_data.get("test_menu_mode"):
        if "🔙" in text or "Orqaga" in text:
            context.user_data.pop("test_menu_mode", None)
            await update.message.reply_text("🏠 Bosh menyu:", reply_markup=main_keyboard())
            return
        if "Ingliz" in text:
            fan, nom = "ingliz", "🇬🇧 Ingliz tili"
        elif "Matematik" in text or "Raqam" in text:
            fan, nom = "math", "🔢 Matematika"
        elif "IQ" in text:
            fan, nom = "iq", "🧠 IQ testi"
        else:
            await update.message.reply_text("Fan tanlang:", reply_markup=test_keyboard())
            return

        context.user_data.pop("test_menu_mode", None)
        await _test_boshlash(update, context, fan, nom)
        return

    # Test savol rejimida — faqat Orqaga ishlaydi (javoblar inline button orqali)
    if context.user_data.get("test"):
        if "🔙" in text or "Orqaga" in text:
            context.user_data.pop("test", None)
            await update.message.reply_text("🏠 Bosh menyu:", reply_markup=main_keyboard())
        else:
            await update.message.reply_text(
                "⬆️ Yuqoridagi tugmalardan javob tanlang!", reply_markup=back_keyboard()
            )
        return

    # Bosh menyu
    if "✅ Test ishlash" in text:
        context.user_data["test_menu_mode"] = True
        await update.message.reply_text(
            "✅ Test bo'limi\n\nQaysi fandan test ishlaysiz?",
            reply_markup=test_keyboard()
        )
    elif "📚 Darslar" in text:
        await darslar_menu(update, context)
    elif "📊 Reyting" in text:
        await reyting(update, context)
    elif "📅 Dars rejasi" in text:
        await dars_rejasi(update, context)
    elif "👤 Profilim" in text:
        await profilim(update, context)
    elif "👥 Referal" in text:
        await referal(update, context)
    elif "🏆 Yutuqlar" in text:
        await yutuqlar(update, context)
    elif "🎯 Maqsadlar" in text:
        await maqsadlar(update, context)
    elif "🔥 Streak" in text:
        await streak_handler(update, context)
    elif "📊 Statistika" in text:
        await statistika(update, context)
    elif "🔙" in text or "Orqaga" in text:
        await update.message.reply_text("🏠 Bosh menyu:", reply_markup=main_keyboard())
    else:
        await update.message.reply_text("❓ Menyudan tanlang:", reply_markup=main_keyboard())

# ══════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════
async def _test_boshlash(update: Update, context: ContextTypes.DEFAULT_TYPE, fan: str,

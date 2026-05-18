import logging
import json
import os
import random
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes,
)

# ======================== SOZLAMALAR ========================
BOT_TOKEN = "8916754154:AAF2Xz3iU8b6g7D8rdVoszCbrx0s8Hk9l_4"
ADMIN_IDS = [123456789]  # O'z Telegram ID'ingizni kiriting
DATA_FILE = "data.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======================== DARAJALAR ========================
LEVELS = [
    (0,    "🌱 Yangi boshlovchi"),
    (100,  "📗 O'rganuvchi"),
    (300,  "📘 Bilimdon"),
    (600,  "📙 Tajribali"),
    (1000, "🥇 Ekspert"),
    (1500, "🏆 Master"),
    (2500, "💎 Legend"),
]

def get_level(score):
    level = LEVELS[0][1]
    for threshold, name in LEVELS:
        if score >= threshold:
            level = name
    return level

def get_next_level(score):
    for threshold, name in LEVELS:
        if score < threshold:
            return threshold, name
    return None, None

# ======================== KUNLIK MASLAHATLAR ========================
DAILY_TIPS = [
    "📖 Grammar qoidalarini o'rganing, hamon mashq qiling!",
    "🔢 Matematika formulalarini yodlang va misollar ishlang!",
    "🌍 Tarix sanalarini kartochkalarga yozing, qaytaring!",
    "🧠 IQ testlarini har kuni ishlang, mantiqni rivojlantiring!",
    "⏰ Har kuni 30 daqiqa o'qish odatga aylantiring!",
    "📝 Yozgan narsalaringizni qaytadan o'qib chiqing!",
    "🎯 Bugun kamida 2 ta test ishlang!",
    "💪 Qiyin savollardan qo'rqmang — xato qilish ham o'rganish!",
    "🏅 Reyting listida ko'tarilish uchun muntazam mashq qiling!",
    "📚 Har bir fanga teng vaqt ajrating!",
]

# ======================== 28 KUNLIK DARS REJASI ========================
DARS_REJASI = [
    {"kun": 1,  "fan": "Ingliz tili", "mavzu": "Present Simple & Continuous", "emoji": "🇬🇧"},
    {"kun": 2,  "fan": "Matematika", "mavzu": "Algebra asoslari", "emoji": "🔢"},
    {"kun": 3,  "fan": "IQ", "mavzu": "Mantiqiy ketma-ketlik", "emoji": "🧠"},
    {"kun": 4,  "fan": "Ingliz tili", "mavzu": "Past Simple & Perfect", "emoji": "🇬🇧"},
    {"kun": 5,  "fan": "Matematika", "mavzu": "Kvadrat tenglamalar", "emoji": "🔢"},
    {"kun": 6,  "fan": "Tarix", "mavzu": "O'zbekiston tarixi", "emoji": "📜"},
    {"kun": 7,  "fan": "IQ", "mavzu": "Fazoviy fikrlash", "emoji": "🧠"},
    {"kun": 8,  "fan": "Ingliz tili", "mavzu": "Future tenses", "emoji": "🇬🇧"},
    {"kun": 9,  "fan": "Matematika", "mavzu": "Funksiyalar va grafiklar", "emoji": "🔢"},
    {"kun": 10, "fan": "Tarix", "mavzu": "Jahon tarixi - Antik davr", "emoji": "📜"},
    {"kun": 11, "fan": "IQ", "mavzu": "Raqamlar qonuniyati", "emoji": "🧠"},
    {"kun": 12, "fan": "Ingliz tili", "mavzu": "Modal fe'llar", "emoji": "🇬🇧"},
    {"kun": 13, "fan": "Matematika", "mavzu": "Trigonometriya", "emoji": "🔢"},
    {"kun": 14, "fan": "Barcha fanlar", "mavzu": "Haftalik takrorlash", "emoji": "📚"},
    {"kun": 15, "fan": "Ingliz tili", "mavzu": "Passive Voice", "emoji": "🇬🇧"},
    {"kun": 16, "fan": "Matematika", "mavzu": "Logarifmlar", "emoji": "🔢"},
    {"kun": 17, "fan": "Tarix", "mavzu": "O'rta asrlar tarixi", "emoji": "📜"},
    {"kun": 18, "fan": "IQ", "mavzu": "So'z analogiyalari", "emoji": "🧠"},
    {"kun": 19, "fan": "Ingliz tili", "mavzu": "Conditionals (If gaplari)", "emoji": "🇬🇧"},
    {"kun": 20, "fan": "Matematika", "mavzu": "Geometriya asoslari", "emoji": "🔢"},
    {"kun": 21, "fan": "Barcha fanlar", "mavzu": "Oraliq sinovga tayyorgarlik", "emoji": "📚"},
    {"kun": 22, "fan": "Ingliz tili", "mavzu": "Reported Speech", "emoji": "🇬🇧"},
    {"kun": 23, "fan": "Matematika", "mavzu": "Ehtimollik nazariyasi", "emoji": "🔢"},
    {"kun": 24, "fan": "Tarix", "mavzu": "Yangi davr tarixi", "emoji": "📜"},
    {"kun": 25, "fan": "IQ", "mavzu": "Murakkab mantiq masalalari", "emoji": "🧠"},
    {"kun": 26, "fan": "Ingliz tili", "mavzu": "Academic vocabulary", "emoji": "🇬🇧"},
    {"kun": 27, "fan": "Matematika", "mavzu": "Arifmetik progressiya", "emoji": "🔢"},
    {"kun": 28, "fan": "Barcha fanlar", "mavzu": "Yakuniy takrorlash va test", "emoji": "🎓"},
]

# ======================== SAVOLLAR ========================
DEFAULT_QUESTIONS = {
    "ingliz_tili": [
        {"q": "'Apple' o'zbek tilida nima?", "options": ["Nok", "Olma", "Banan", "Uzum"], "correct": 1},
        {"q": "'Hello' o'zbek tilida nima?", "options": ["Xayr", "Salom", "Rahmat", "Iltimos"], "correct": 1},
        {"q": "I ___ a student. (to'g'ri variant)", "options": ["is", "are", "am", "be"], "correct": 2},
        {"q": "'Beautiful' antonimi nima?", "options": ["Pretty", "Ugly", "Nice", "Lovely"], "correct": 1},
        {"q": "She ___ to school every day.", "options": ["go", "goes", "going", "gone"], "correct": 1},
        {"q": "'Difficult' sinonimi qaysi?", "options": ["Easy", "Hard", "Simple", "Clear"], "correct": 1},
        {"q": "They ___ watching TV now.", "options": ["is", "was", "are", "were"], "correct": 2},
        {"q": "I have ___ to Tashkent.", "options": ["go", "went", "gone", "going"], "correct": 2},
        {"q": "The book ___ on the table.", "options": ["are", "is", "am", "be"], "correct": 1},
        {"q": "'Quickly' qaysi so'z turkumiga kiradi?", "options": ["Sifat", "Ot", "Ravish", "Fe'l"], "correct": 2},
    ],
    "matematika": [
        {"q": "2 + 2 = ?", "options": ["3", "4", "5", "6"], "correct": 1},
        {"q": "5 x 5 = ?", "options": ["20", "25", "30", "10"], "correct": 1},
        {"q": "kv.ildiz(16) = ?", "options": ["2", "3", "4", "5"], "correct": 2},
        {"q": "3^2 = ?", "options": ["6", "8", "9", "12"], "correct": 2},
        {"q": "15 / 3 = ?", "options": ["3", "4", "5", "6"], "correct": 2},
        {"q": "x^2 - 5x + 6 = 0 ildizlari?", "options": ["1 va 6", "2 va 3", "3 va 4", "1 va 5"], "correct": 1},
        {"q": "log(100) = ? (asos 10)", "options": ["1", "2", "3", "10"], "correct": 1},
        {"q": "sin(90) = ?", "options": ["0", "0.5", "1", "-1"], "correct": 2},
        {"q": "2^3 = ?", "options": ["6", "8", "9", "12"], "correct": 1},
        {"q": "a=3, b=4 bo'lsa, a^2+b^2=?", "options": ["14", "25", "49", "7"], "correct": 1},
    ],
    "iq": [
        {"q": "2, 4, 8, 16, ___ ? Keyingi son?", "options": ["24", "28", "32", "36"], "correct": 2},
        {"q": "Kitob : Kutubxona = Rasm : ?", "options": ["Bo'yoq", "Muzey", "Artist", "Ramka"], "correct": 1},
        {"q": "5 ta olmadan 2 tasini olsak, nechta qoladi?", "options": ["2", "3", "5", "7"], "correct": 1},
        {"q": "ABCD : DCBA = 1234 : ?", "options": ["1234", "4321", "2143", "3412"], "correct": 1},
        {"q": "1, 1, 2, 3, 5, 8, ___ ?", "options": ["11", "12", "13", "14"], "correct": 2},
        {"q": "3 mushuk 3 daqiqada 3 sichqon tutsa, 9 mushuk 9 daqiqada nechta?", "options": ["9", "27", "81", "3"], "correct": 1},
        {"q": "Qaysi son boshqacha?: 2, 3, 5, 7, 9, 11", "options": ["3", "5", "9", "11"], "correct": 2},
        {"q": "Bir kunda 24 soat, bir haftada necha soat?", "options": ["148", "162", "168", "172"], "correct": 2},
        {"q": "Qaysi shakl boshqacha?: Doira, Ellips, Kvadrat, Oval", "options": ["Doira", "Ellips", "Kvadrat", "Oval"], "correct": 2},
        {"q": "10, 9, 7, 4, ___ ?", "options": ["0", "1", "2", "3"], "correct": 0},
    ],
    "tarix": [
        {"q": "O'zbekiston mustaqillikka qaysi yilda erishdi?", "options": ["1989", "1990", "1991", "1992"], "correct": 2},
        {"q": "Amir Temur qaysi yilda tug'ilgan?", "options": ["1330", "1336", "1340", "1350"], "correct": 1},
        {"q": "Buyuk Ipak yo'li qaysi shahardan o'tgan?", "options": ["Buxoro", "Samarqand", "Xiva", "Hammasi"], "correct": 3},
        {"q": "Birinchi jahon urushi qachon boshlangan?", "options": ["1912", "1914", "1916", "1918"], "correct": 1},
        {"q": "Ikkinchi jahon urushi qachon tugagan?", "options": ["1943", "1944", "1945", "1946"], "correct": 2},
        {"q": "Al-Xorazmiy algebra faniga asos solgan asari?", "options": ["Qomus", "Al-Jabr", "Kitob ul-hind", "Zij"], "correct": 1},
        {"q": "Temuriylar davlatining poytaxti?", "options": ["Buxoro", "Xiva", "Samarqand", "Toshkent"], "correct": 2},
        {"q": "Ulug'bek rasadxonasi qaysi shaharda?", "options": ["Buxoro", "Samarqand", "Toshkent", "Xiva"], "correct": 1},
        {"q": "Amerika qachon kashf etilgan?", "options": ["1390", "1492", "1500", "1520"], "correct": 1},
        {"q": "Fransuz inqilobi qaysi yilda bo'lgan?", "options": ["1776", "1789", "1800", "1815"], "correct": 1},
    ],
}

SUBJECT_EMOJIS = {
    "ingliz_tili": "🇬🇧",
    "matematika":  "🔢",
    "iq":          "🧠",
    "tarix":       "📜",
}

SUBJECT_NAMES = {
    "ingliz_tili": "Ingliz tili",
    "matematika":  "Matematika",
    "iq":          "IQ",
    "tarix":       "Tarix",
}

# ======================== YUTUQLAR ========================
BADGES = {
    "birinchi_test": {"name": "🎯 Birinchi test", "desc": "Birinchi testni yakunlading", "condition": lambda u: u["total_tests"] >= 1},
    "mukammal":      {"name": "💯 Mukammal", "desc": "Bitta testda 100% to'g'ri javob", "condition": lambda u: u.get("perfect_tests", 0) >= 1},
    "ball_100":      {"name": "🏅 100 ball", "desc": "Jami 100 ball to'plading", "condition": lambda u: u["total_score"] >= 100},
    "ball_500":      {"name": "🥈 500 ball", "desc": "Jami 500 ball to'plading", "condition": lambda u: u["total_score"] >= 500},
    "referal":       {"name": "👥 Referal", "desc": "1 ta do'st taklif qilding", "condition": lambda u: u.get("referrals", 0) >= 1},
    "haftalik":      {"name": "🔥 Haftalik chempion", "desc": "7 kun ketma-ket o'yndingiz", "condition": lambda u: u.get("streak", 0) >= 7},
}

# ======================== DATA ========================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    if "questions" not in data:
        data["questions"] = DEFAULT_QUESTIONS
    if "users" not in data:
        data["users"] = {}
    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, user_id):
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "name": "",
            "username": "",
            "total_score": 0,
            "total_tests": 0,
            "perfect_tests": 0,
            "badges": [],
            "streak": 0,
            "last_play_date": None,
            "referrals": 0,
            "referred_by": None,
            "goals": [],
            "subject_stats": {},
            "joined": str(date.today()),
        }
    return data["users"][uid]

def check_badges(user):
    new_badges = []
    for badge_id, badge in BADGES.items():
        if badge_id not in user["badges"]:
            try:
                if badge["condition"](user):
                    user["badges"].append(badge_id)
                    new_badges.append(badge["name"])
            except:
                pass
    return new_badges

def update_streak(user):
    today = str(date.today())
    last = user.get("last_play_date")
    if last is None:
        user["streak"] = 1
    elif last == today:
        pass
    elif last == str(date.today() - timedelta(days=1)):
        user["streak"] = user.get("streak", 0) + 1
    else:
        user["streak"] = 1
    user["last_play_date"] = today

def get_today_tip():
    day_of_year = date.today().timetuple().tm_yday
    return DAILY_TIPS[day_of_year % len(DAILY_TIPS)]

def get_user_rank(data, user_id):
    users_sorted = sorted(data["users"].items(), key=lambda x: x[1]["total_score"], reverse=True)
    for i, (uid, _) in enumerate(users_sorted):
        if uid == str(user_id):
            return i + 1
    return "-"

# ======================== KLAVIATURA ========================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Test ishlash", callback_data="start_test"),
            InlineKeyboardButton("📚 Darslar", callback_data="darslar"),
        ],
        [
            InlineKeyboardButton("📊 Reyting", callback_data="leaderboard"),
            InlineKeyboardButton("📅 Dars rejasi", callback_data="dars_rejasi"),
        ],
        [
            InlineKeyboardButton("👤 Profilim", callback_data="profil"),
            InlineKeyboardButton("👥 Referal", callback_data="referral"),
        ],
        [
            InlineKeyboardButton("🏆 Yutuqlar", callback_data="badges"),
            InlineKeyboardButton("🎯 Maqsadlar", callback_data="goals"),
        ],
        [
            InlineKeyboardButton("🔥 Streak", callback_data="streak"),
            InlineKeyboardButton("📈 Statistika", callback_data="stats"),
        ],
    ])

def subjects_keyboard(data):
    subjects = list(data["questions"].keys())
    buttons = []
    for subj in subjects:
        emoji = SUBJECT_EMOJIS.get(subj, "📖")
        name = SUBJECT_NAMES.get(subj, subj.replace("_", " ").title())
        buttons.append([InlineKeyboardButton(f"{emoji} {name}", callback_data=f"subject_{subj}")])
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def answer_keyboard(options, q_index):
    letters = ["A", "B", "C", "D"]
    buttons = []
    for i, opt in enumerate(options):
        buttons.append([InlineKeyboardButton(f"{letters[i]}) {opt}", callback_data=f"answer_{q_index}_{i}")])
    return InlineKeyboardMarkup(buttons)

def back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")]])

# ======================== START ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = update.effective_user.id
    user = get_user(data, user_id)
    user["name"] = update.effective_user.first_name or "Foydalanuvchi"
    user["username"] = update.effective_user.username or ""

    args = context.args
    if args and args[0].startswith("ref_"):
        ref_id = args[0][4:]
        if ref_id != str(user_id) and ref_id in data["users"] and not user.get("referred_by"):
            user["referred_by"] = ref_id
            ref_user = data["users"][ref_id]
            ref_user["referrals"] = ref_user.get("referrals", 0) + 1
            ref_user["total_score"] = ref_user.get("total_score", 0) + 20
            check_badges(ref_user)

    save_data(data)

    level = get_level(user["total_score"])
    tip = get_today_tip()

    text = (
        f"Salom, {user['name']}!\n\n"
        f"🎯 Litsey Tayyorgarlik botiga xush kelibsiz!\n"
        f"Darajangiz: {level}\n\n"
        f"Bu bot orqali:\n"
        f"📝 Testlar ishlang va ball toplang\n"
        f"📚 Barcha fanlardan dars oling\n"
        f"📊 Real reytingda o'rningizni biling\n"
        f"👥 Dostlarni taklif qiling va bonus oling\n\n"
        f"💡 Bugungi maslahat:\n{tip}\n\n"
        f"Bolimni tanlang:"
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard())
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard())

async def main_menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

# ======================== DARSLAR ========================
async def show_darslar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "📚 Darslar bo'limi\n\n"
        "Fan tanlang va o'rganing:\n\n"
        "🇬🇧 Ingliz tili — Grammar, Vocabulary, Reading\n"
        "🔢 Matematika — Algebra, Geometriya, Analiz\n"
        "🧠 IQ — Mantiq, Analogiya, Ketma-ketlik\n"
        "📜 Tarix — O'zbekiston va Jahon tarixi\n\n"
        "Testlarni ishlash orqali bilimingizni mustahkamlang!"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 Ingliz tili testi", callback_data="subject_ingliz_tili")],
        [InlineKeyboardButton("🔢 Matematika testi", callback_data="subject_matematika")],
        [InlineKeyboardButton("🧠 IQ testi", callback_data="subject_iq")],
        [InlineKeyboardButton("📜 Tarix testi", callback_data="subject_tarix")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")],
    ])
    await query.edit_message_text(text, reply_markup=keyboard)

# ======================== DARS REJASI ========================
async def show_dars_rejasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_data()
    user = get_user(data, query.from_user.id)
    joined = user.get("joined", str(date.today()))
    try:
        joined_date = date.fromisoformat(joined)
        current_day = (date.today() - joined_date).days + 1
        current_day = max(1, min(current_day, 28))
    except:
        current_day = 1

    text = f"📅 28 Kunlik Dars Rejasi\n"
    text += f"Siz hozir: {current_day}-kun\n\n"

    start_idx = max(0, current_day - 2)
    end_idx = min(28, current_day + 3)

    for lesson in DARS_REJASI[start_idx:end_idx]:
        k = lesson["kun"]
        if k == current_day:
            text += f"▶️ {k}-kun (BUGUN)\n"
        elif k < current_day:
            text += f"✅ {k}-kun\n"
        else:
            text += f"⏳ {k}-kun\n"
        text += f"   {lesson['emoji']} {lesson['fan']}: {lesson['mavzu']}\n\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Barcha kunlar", callback_data="rejasi_all")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")],
    ])
    await query.edit_message_text(text, reply_markup=keyboard)

async def show_all_rejasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = "📅 Barcha 28 kunlik reja:\n\n"
    for lesson in DARS_REJASI:
        text += f"{lesson['emoji']} {lesson['kun']}-kun: {lesson['fan']} — {lesson['mavzu']}\n"

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="dars_rejasi")]])
    )

# ======================== TEST ========================
async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    await query.edit_message_text(
        "✅ Fan tanlang:\n\nQaysi fandan test ishlashni xohlaysiz?",
        reply_markup=subjects_keyboard(data)
    )

async def choose_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    subject = query.data.replace("subject_", "")
    data = load_data()

    questions = data["questions"].get(subject, [])
    if not questions:
        await query.edit_message_text("Bu fan uchun savollar yo'q.", reply_markup=main_menu_keyboard())
        return

    selected = random.sample(questions, min(10, len(questions)))
    context.user_data["test"] = {
        "subject": subject,
        "questions": selected,
        "current": 0,
        "score": 0,
    }
    await send_question(query, context)

async def send_question(query, context):
    test = context.user_data["test"]
    q_index = test["current"]
    total = len(test["questions"])
    q = test["questions"][q_index]

    filled = int((q_index / total) * 10)
    bar = "█" * filled + "░" * (10 - filled)
    pct = q_index * 100 // total

    subject = test["subject"]
    emoji = SUBJECT_EMOJIS.get(subject, "📖")
    name = SUBJECT_NAMES.get(subject, subject)

    text = (
        f"{emoji} {name}\n"
        f"---\n"
        f"Savol {q_index + 1}/{total}  [{bar}] {pct}%\n"
        f"---\n\n"
        f"{q['q']}"
    )
    await query.edit_message_text(text, reply_markup=answer_keyboard(q["options"], q_index))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    q_index = int(parts[1])
    chosen = int(parts[2])

    if "test" not in context.user_data:
        await query.edit_message_text("Test topilmadi. /start bilan boshlang.")
        return

    test = context.user_data["test"]
    if q_index != test["current"]:
        return

    q = test["questions"][q_index]
    correct = q["correct"]
    is_correct = chosen == correct

    if is_correct:
        test["score"] += 1
        feedback = "✅ To'g'ri!"
    else:
        feedback = f"❌ Noto'g'ri!\nTo'g'ri javob: {q['options'][correct]}"

    test["current"] += 1

    if test["current"] >= len(test["questions"]):
        await finish_test(query, context, feedback)
    else:
        total = len(test["questions"])
        ni = test["current"]
        filled = int((ni / total) * 10)
        bar = "█" * filled + "░" * (10 - filled)
        nq = test["questions"][ni]
        subject = test["subject"]
        emoji = SUBJECT_EMOJIS.get(subject, "📖")
        name = SUBJECT_NAMES.get(subject, subject)

        text = (
            f"{feedback}\n\n"
            f"{emoji} {name}\n"
            f"---\n"
            f"Savol {ni + 1}/{total}  [{bar}] {ni * 100 // total}%\n"
            f"---\n\n"
            f"{nq['q']}"
        )
        await query.edit_message_text(text, reply_markup=answer_keyboard(nq["options"], ni))

async def finish_test(query, context, last_feedback):
    test = context.user_data["test"]
    score = test["score"]
    total = len(test["questions"])
    subject = test["subject"]
    percentage = score * 100 // total
    points = score * 10

    if percentage == 100:
        grade = "🏆 Mukammal!"
    elif percentage >= 80:
        grade = "🥇 A'lo!"
    elif percentage >= 60:
        grade = "🥈 Yaxshi"
    elif percentage >= 40:
        grade = "🥉 Qoniqarli"
    else:
        grade = "😔 Ko'proq mashq qiling"

    data = load_data()
    user = get_user(data, query.from_user.id)
    user["total_score"] += points
    user["total_tests"] += 1
    if percentage == 100:
        user["perfect_tests"] = user.get("perfect_tests", 0) + 1

    ss = user["subject_stats"]
    if subject not in ss:
        ss[subject] = {"tests": 0, "correct": 0, "total": 0}
    ss[subject]["tests"] += 1
    ss[subject]["correct"] += score
    ss[subject]["total"] += total

    update_streak(user)

    goal_msg = ""
    for goal in user.get("goals", []):
        if not goal.get("done") and user["total_score"] >= goal["target"]:
            goal["done"] = True
            goal_msg = f"\n\n🎯 Maqsadga yetdingiz: {goal['target']} ball! 🎉"

    new_badges = check_badges(user)
    badge_msg = ""
    if new_badges:
        badge_msg = "\n\n🎖 Yangi yutuqlar:\n" + "\n".join(new_badges)

    level = get_level(user["total_score"])
    save_data(data)

    bar = "█" * 10
    text = (
        f"{last_feedback}\n\n"
        f"---\n"
        f"🏁 Test yakunlandi!\n"
        f"[{bar}] 100%\n"
        f"---\n\n"
        f"Fan: {SUBJECT_NAMES.get(subject, subject)}\n"
        f"To'g'ri: {score}/{total} ({percentage}%)\n"
        f"Ball: +{points}\n"
        f"Natija: {grade}\n"
        f"Daraja: {level}"
        f"{goal_msg}"
        f"{badge_msg}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Yana test", callback_data="start_test"),
            InlineKeyboardButton("📈 Statistika", callback_data="stats"),
        ],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")],
    ])
    await query.edit_message_text(text, reply_markup=keyboard)
    context.user_data.pop("test", None)

# ======================== PROFIL ========================
async def show_profil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    user = get_user(data, query.from_user.id)

    level = get_level(user["total_score"])
    next_thresh, next_level = get_next_level(user["total_score"])
    rank = get_user_rank(data, query.from_user.id)

    progress_text = ""
    if next_thresh:
        needed = next_thresh - user["total_score"]
        progress_text = f"\nKeyingi: {next_level} — {needed} ball qoldi"

    joined = user.get("joined", "Noma'lum")
    text = (
        f"👤 Profilim\n"
        f"---\n"
        f"Ism: {user['name']}\n"
        f"Qo'shilgan: {joined}\n"
        f"---\n"
        f"🏆 Jami ball: {user['total_score']}\n"
        f"📝 Testlar: {user['total_tests']}\n"
        f"💯 Mukammal: {user.get('perfect_tests', 0)}\n"
        f"🔥 Streak: {user.get('streak', 0)} kun\n"
        f"🏅 O'rin: #{rank}\n"
        f"🎖 Yutuqlar: {len(user['badges'])}/{len(BADGES)}\n"
        f"---\n"
        f"Daraja: {level}"
        f"{progress_text}"
    )
    await query.edit_message_text(text, reply_markup=back_keyboard())

# ======================== STATISTIKA ========================
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    user = get_user(data, query.from_user.id)

    text = f"📈 {user['name']} statistikasi\n---\n"
    text += f"🏆 Jami ball: {user['total_score']}\n"
    text += f"📝 Testlar: {user['total_tests']}\n"
    text += f"💯 Mukammal: {user.get('perfect_tests', 0)}\n"
    text += f"🔥 Streak: {user.get('streak', 0)} kun\n\n"

    ss = user.get("subject_stats", {})
    if ss:
        text += "📚 Fan bo'yicha natija:\n\n"
        for subj, s in ss.items():
            avg = s["correct"] * 100 // s["total"] if s["total"] else 0
            emoji = SUBJECT_EMOJIS.get(subj, "📖")
            name = SUBJECT_NAMES.get(subj, subj)
            filled = avg // 10
            bar = "█" * filled + "░" * (10 - filled)
            text += f"{emoji} {name}\n[{bar}] {avg}% ({s['tests']} test)\n\n"
    else:
        text += "Hali test ishlanmagan."

    await query.edit_message_text(text, reply_markup=back_keyboard())

# ======================== YUTUQLAR ========================
async def show_badges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    user = get_user(data, query.from_user.id)

    text = f"🏆 Yutuqlar ({len(user['badges'])}/{len(BADGES)})\n---\n\n"
    for bid, badge in BADGES.items():
        if bid in user["badges"]:
            text += f"✅ {badge['name']}\n   {badge['desc']}\n\n"
        else:
            text += f"🔒 {badge['name']}\n   {badge['desc']}\n\n"

    await query.edit_message_text(text, reply_markup=back_keyboard())

# ======================== MAQSADLAR ========================
async def show_goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    user = get_user(data, query.from_user.id)

    text = f"🎯 Maqsadlar\nHozirgi ball: {user['total_score']}\n---\n\n"
    goals = user.get("goals", [])
    if goals:
        for g in goals:
            if g.get("done"):
                text += f"✅ {g['target']} ball — Bajarildi!\n"
            else:
                remaining = g["target"] - user["total_score"]
                text += f"⏳ {g['target']} ball — yana {remaining} ball kerak\n"
    else:
        text += "Hech qanday maqsad qo'yilmagan.\n"

    text += "\nMaqsad tanlang:"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 100 ball", callback_data="addgoal_100"),
            InlineKeyboardButton("🎯 300 ball", callback_data="addgoal_300"),
        ],
        [
            InlineKeyboardButton("🎯 500 ball", callback_data="addgoal_500"),
            InlineKeyboardButton("🎯 1000 ball", callback_data="addgoal_1000"),
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")],
    ])
    await query.edit_message_text(text, reply_markup=keyboard)

async def add_goal_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    target = int(query.data.replace("addgoal_", ""))
    data = load_data()
    user = get_user(data, query.from_user.id)

    for g in user.get("goals", []):
        if g["target"] == target and not g.get("done"):
            await query.answer("Bu maqsad allaqachon mavjud!", show_alert=True)
            return

    user.setdefault("goals", []).append({"target": target, "done": False})
    save_data(data)
    await query.answer(f"{target} ball maqsad qo'shildi!", show_alert=True)
    await show_goals(update, context)

# ======================== STREAK ========================
async def show_streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    user = get_user(data, query.from_user.id)

    streak = user.get("streak", 0)
    flames = "🔥" * min(streak, 10) if streak > 0 else "❄️"

    text = f"🔥 Ketma-ket kunlar\n---\n{flames}\n\nSiz {streak} kun ketma-ket mashq qildingiz!\n\n"
    if streak == 0:
        text += "Bugun test ishlang va streakni boshlang! 💪"
    elif streak < 7:
        text += f"7 kunlik yutuq uchun yana {7 - streak} kun kerak."
    else:
        text += "Haftalik chempionsiz! Davom eting! 🏆"

    await query.edit_message_text(text, reply_markup=back_keyboard())

# ======================== REYTING ========================
async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()

    user_id = str(query.from_user.id)
    all_users = sorted(data["users"].items(), key=lambda x: x[1]["total_score"], reverse=True)

    text = "📊 Top 10 o'quvchilar\n---\n\n"
    medals = ["🥇", "🥈", "🥉"]

    user_rank = "-"
    user_score = 0

    for i, (uid, u) in enumerate(all_users):
        if uid == user_id:
            user_rank = i + 1
            user_score = u["total_score"]
        if i < 10:
            medal = medals[i] if i < 3 else f"{i+1}."
            level = get_level(u["total_score"])
            text += f"{medal} {u['name']} — {u['total_score']} ball\n   {level}\n\n"

    if not all_users:
        text += "Hali hech kim yo'q."

    text += f"---\nSizning o'rningiz: #{user_rank} — {user_score} ball"

    await query.edit_message_text(text, reply_markup=back_keyboard())

# ======================== REFERAL ========================
async def show_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    bot_info = await context.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"

    data = load_data()
    user = get_user(data, user_id)

    text = (
        f"👥 Do'st taklif qilish\n"
        f"---\n"
        f"Havolangiz:\n{link}\n\n"
        f"Taklif qilganlar: {user.get('referrals', 0)}\n\n"
        f"Bonus:\n"
        f"— Do'stingiz botga kirsa siz +20 ball olasiz\n"
        f"— Referal badge qo'lga kiritasiz\n\n"
        f"Havolani nusxalab do'stlaringizga yuboring! 🚀"
    )
    await query.edit_message_text(text, reply_markup=back_keyboard())

# ======================== ADMIN ========================
async def addq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Siz admin emassiz!")
        return

    data = load_data()
    subjects = list(data["questions"].keys())
    buttons = []
    for s in subjects:
        name = SUBJECT_NAMES.get(s, s)
        buttons.append([InlineKeyboardButton(f"{SUBJECT_EMOJIS.get(s, '📖')} {name}", callback_data=f"adm_subj_{s}")])

    await update.message.reply_text(
        "👑 Admin: Savol qo'shish\nFan tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def admin_choose_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id not in ADMIN_IDS:
        return
    subject = query.data.replace("adm_subj_", "")
    context.user_data["adm_subject"] = subject
    context.user_data["adm_state"] = "waiting_question"
    await query.edit_message_text(
        f"{SUBJECT_NAMES.get(subject, subject)} uchun savol matnini yuboring:"
    )

async def admin_stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Siz admin emassiz!")
        return
    data = load_data()
    total_users = len(data["users"])
    total_tests = sum(u.get("total_tests", 0) for u in data["users"].values())
    await update.message.reply_text(
        f"👑 Admin statistika\n\n"
        f"Jami foydalanuvchilar: {total_users}\n"
        f"Jami testlar: {total_tests}"
    )

async def general_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "adm_state" not in context.user_data:
        return
    if update.effective_user.id not in ADMIN_IDS:
        return

    state = context.user_data["adm_state"]
    text = update.message.text

    if state == "waiting_question":
        context.user_data["adm_question"] = text
        context.user_data["adm_options"] = []
        context.user_data["adm_state"] = "waiting_options"
        await update.message.reply_text("4 ta variant yuboring (har birini alohida):\n1-variant:")

    elif state == "waiting_options":
        context.user_data["adm_options"].append(text)
        count = len(context.user_data["adm_options"])
        if count < 4:
            await update.message.reply_text(f"{count + 1}-variant:")
        else:
            context.user_data["adm_state"] = "waiting_correct"
            opts = context.user_data["adm_options"]
            opts_text = "\n".join([f"{i}) {o}" for i, o in enumerate(opts)])
            await update.message.reply_text(f"To'g'ri javob raqamini yuboring (0-3):\n\n{opts_text}")

    elif state == "waiting_correct":
        try:
            correct = int(text)
            assert 0 <= correct <= 3
        except:
            await update.message.reply_text("0 dan 3 gacha raqam kiriting!")
            return

        data = load_data()
        subject = context.user_data["adm_subject"]
        new_q = {
            "q": context.user_data["adm_question"],
            "options": context.user_data["adm_options"],
            "correct": correct,
        }
        data["questions"].setdefault(subject, []).append(new_q)
        save_data(data)

        for key in ["adm_state", "adm_question", "adm_options", "adm_subject"]:
            context.user_data.pop(key, None)

        await update.message.reply_text(
            f"Savol qo'shildi!\n\n"
            f"Fan: {SUBJECT_NAMES.get(subject, subject)}\n"
            f"Savol: {new_q['q']}"
        )

# ======================== HELP ========================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 Yordam\n---\n\n"
        "/start — Botni boshlash\n"
        "/help — Yordam\n"
        "/goal [raqam] — Maqsad qo'shish\n"
        "/addq — Savol qo'shish (admin)\n"
        "/adminstats — Bot statistikasi (admin)\n\n"
        "Fanlar:\n"
        "🇬🇧 Ingliz tili\n"
        "🔢 Matematika\n"
        "🧠 IQ\n"
        "📜 Tarix\n\n"
        "Testlarni ishlang, ball to'plang, reytingda o'rningizni egallang!"
    )
    await update.message.reply_text(text)

async def goal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Ishlatish: /goal 500")
        return
    try:
        target = int(context.args[0])
        assert target > 0
    except:
        await update.message.reply_text("To'g'ri raqam kiriting. Masalan: /goal 500")
        return
    data = load_data()
    user = get_user(data, update.effective_user.id)
    user.setdefault("goals", []).append({"target": target, "done": False})
    save_data(data)
    await update.message.reply_text(f"{target} ball maqsad qo'shildi!")

# ======================== MAIN ========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("goal", goal_command))
    app.add_handler(CommandHandler("addq", addq_command))
    app.add_handler(CommandHandler("adminstats", admin_stats_cmd))

    app.add_handler(CallbackQueryHandler(main_menu_cb,         pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(show_darslar,         pattern="^darslar$"))
    app.add_handler(CallbackQueryHandler(show_dars_rejasi,     pattern="^dars_rejasi$"))
    app.add_handler(CallbackQueryHandler(show_dars_rejasi,     pattern="^rejasi_prev_"))
    app.add_handler(CallbackQueryHandler(show_dars_rejasi,     pattern="^rejasi_next_"))
    app.add_handler(CallbackQueryHandler(show_all_rejasi,      pattern="^rejasi_all$"))
    app.add_handler(CallbackQueryHandler(start_test,           pattern="^start_test$"))
    app.add_handler(CallbackQueryHandler(choose_subject,       pattern="^subject_"))
    app.add_handler(CallbackQueryHandler(handle_answer,        pattern="^answer_"))
    app.add_handler(CallbackQueryHandler(show_profil,          pattern="^profil$"))
    app.add_handler(CallbackQueryHandler(show_stats,           pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(show_badges,          pattern="^badges$"))
    app.add_handler(CallbackQueryHandler(show_goals,           pattern="^goals$"))
    app.add_handler(CallbackQueryHandler(add_goal_cb,          pattern="^addgoal_"))
    app.add_handler(CallbackQueryHandler(show_streak,          pattern="^streak$"))
    app.add_handler(CallbackQueryHandler(show_leaderboard,     pattern="^leaderboard$"))
    app.add_handler(CallbackQueryHandler(show_referral,        pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(admin_choose_subject, pattern="^adm_subj_"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, general_message_handler))

    print("Litsey Tayyorgarlik boti ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

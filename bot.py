        import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://litsey-app.vercel.app")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "0").split(",") if x.strip()]

users_db = {}
pending_question = {}  # admin savol qo'shish uchun

questions_db = {
    "matematika": [
        {"savol": "2 + 2 = ?", "v": ["3", "4", "5", "6"], "t": 1},
        {"savol": "5 x 5 = ?", "v": ["20", "25", "30", "35"], "t": 1},
        {"savol": "10 - 3 = ?", "v": ["5", "6", "7", "8"], "t": 2},
        {"savol": "3 ning kvadrati = ?", "v": ["6", "9", "12", "8"], "t": 1},
        {"savol": "16 ning ildizi = ?", "v": ["2", "4", "6", "8"], "t": 1},
        {"savol": "15 / 3 = ?", "v": ["3", "4", "5", "6"], "t": 2},
        {"savol": "2 ning kubi = ?", "v": ["6", "8", "10", "12"], "t": 1},
        {"savol": "100 / 4 = ?", "v": ["20", "25", "30", "40"], "t": 1},
        {"savol": "7 x 8 = ?", "v": ["54", "56", "58", "60"], "t": 1},
        {"savol": "144 ning ildizi = ?", "v": ["10", "11", "12", "13"], "t": 2},
        {"savol": "0.5 x 10 = ?", "v": ["4", "5", "6", "7"], "t": 1},
        {"savol": "2 darajasi 10 = ?", "v": ["512", "1024", "2048", "256"], "t": 1},
        {"savol": "sin 90 = ?", "v": ["0", "0.5", "1", "-1"], "t": 2},
        {"savol": "cos 0 = ?", "v": ["0", "0.5", "1", "-1"], "t": 2},
        {"savol": "Pi sonining taxminiy qiymati?", "v": ["3.14", "2.71", "1.41", "1.73"], "t": 0},
    ],
    "ingliz": [
        {"savol": "Apple - ozbekcha?", "v": ["Olma", "Nok", "Uzum", "Shaftoli"], "t": 0},
        {"savol": "I am a student - tarjimasi?", "v": ["O'qituvchi", "O'quvchi", "Shifokor", "Muhandis"], "t": 1},
        {"savol": "Beautiful sinoniimi?", "v": ["Ugly", "Pretty", "Bad", "Slow"], "t": 1},
        {"savol": "To be - Past Simple?", "v": ["is/are", "was/were", "be", "been"], "t": 1},
        {"savol": "They ___ students.", "v": ["is", "am", "are", "be"], "t": 2},
        {"savol": "Book - kopligi?", "v": ["Books", "Bookes", "Bookies", "Book"], "t": 0},
        {"savol": "Run - Past Simple?", "v": ["Runned", "Ran", "Run", "Runs"], "t": 1},
        {"savol": "She ___ to school every day.", "v": ["go", "goes", "going", "went"], "t": 1},
        {"savol": "Water - ozbekcha?", "v": ["Suv", "Havo", "Olov", "Yer"], "t": 0},
        {"savol": "I ___ a doctor in the future.", "v": ["am", "is", "will be", "was"], "t": 2},
        {"savol": "Biggest - superlativi?", "v": ["Big", "Bigger", "Biggest", "Most big"], "t": 2},
        {"savol": "What ___ you doing?", "v": ["is", "am", "are", "be"], "t": 2},
        {"savol": "Yesterday - tarjimasi?", "v": ["Bugun", "Ertaga", "Kecha", "Hozir"], "t": 2},
        {"savol": "Speak - sinonimi?", "v": ["Listen", "Talk", "Write", "Read"], "t": 1},
        {"savol": "Happy - antonimi?", "v": ["Glad", "Joyful", "Sad", "Cheerful"], "t": 2},
    ],
    "fizika": [
        {"savol": "Yoruglik tezligi?", "v": ["200000 km/s", "300000 km/s", "400000 km/s", "100000 km/s"], "t": 1},
        {"savol": "Nyuton 1-qonuni?", "v": ["Kuch", "Inersiya", "Ishqalanish", "Tortishish"], "t": 1},
        {"savol": "Suv necha gradusda qaynaydi?", "v": ["90", "95", "100", "105"], "t": 2},
        {"savol": "Elektr toki birligi?", "v": ["Volt", "Amper", "Vatt", "Om"], "t": 1},
        {"savol": "Massa birligi SI da?", "v": ["Gramm", "Kilogramm", "Tonna", "Litr"], "t": 1},
        {"savol": "Kuch birligi?", "v": ["Joule", "Nyuton", "Paskal", "Vatt"], "t": 1},
        {"savol": "Energiya birligi?", "v": ["Nyuton", "Vatt", "Joule", "Amper"], "t": 2},
        {"savol": "Erkin tushish tezlanishi?", "v": ["8 m/s2", "9.8 m/s2", "10.5 m/s2", "11 m/s2"], "t": 1},
        {"savol": "Ovoz tezligi havoda?", "v": ["200 m/s", "343 m/s", "500 m/s", "1000 m/s"], "t": 1},
        {"savol": "Qaysi jism eng ko'p nur qaytaradi?", "v": ["Qora", "Ko'k", "Oq", "Yashil"], "t": 2},
    ],
    "kimyo": [
        {"savol": "Suv formulasi?", "v": ["CO2", "H2O", "NaCl", "O2"], "t": 1},
        {"savol": "Oltin belgisi?", "v": ["Ag", "Fe", "Au", "Cu"], "t": 2},
        {"savol": "Davriy jadval kim tuzgan?", "v": ["Nyuton", "Mendeleyev", "Einstein", "Darvin"], "t": 1},
        {"savol": "Osh tuzi formulasi?", "v": ["KCl", "NaCl", "CaCl2", "MgCl2"], "t": 1},
        {"savol": "Kislorod belgisi?", "v": ["O", "K", "Os", "Og"], "t": 0},
        {"savol": "Vodorod belgisi?", "v": ["He", "H", "Ho", "Hf"], "t": 1},
        {"savol": "Temir belgisi?", "v": ["Ti", "Te", "Fe", "Fr"], "t": 2},
        {"savol": "Uglerod belgisi?", "v": ["Ca", "Co", "Cr", "C"], "t": 3},
        {"savol": "Azot formulasi gaz holatda?", "v": ["N", "N2", "N3", "NO"], "t": 1},
        {"savol": "Eng engil element?", "v": ["Geliy", "Vodorod", "Litiy", "Berilliy"], "t": 1},
    ],
    "biologiya": [
        {"savol": "Fotosintez qayerda boladi?", "v": ["Ildizda", "Bargda", "Gulda", "Mevada"], "t": 1},
        {"savol": "Odam tanasida nechta suyak?", "v": ["186", "206", "226", "246"], "t": 1},
        {"savol": "DNK nima?", "v": ["Oqsil", "Irsiyat moddasi", "Vitamin", "Ferment"], "t": 1},
        {"savol": "Qon guruhlar soni?", "v": ["2", "3", "4", "5"], "t": 2},
        {"savol": "Eng katta hujayra?", "v": ["Qon", "Tuxum", "Nerv", "Muskul"], "t": 1},
        {"savol": "Odam yuragining normal urish chastotasi?", "v": ["40-50", "60-80", "100-120", "20-30"], "t": 1},
        {"savol": "Fotosintez uchun nima kerak?", "v": ["CO2 va suv", "O2 va suv", "N2 va suv", "H2 va suv"], "t": 0},
        {"savol": "Eng kichik tirik organizm?", "v": ["Bakteriya", "Virus", "Zamburug", "Suv otlari"], "t": 1},
        {"savol": "Qaysi organ qon tozalaydi?", "v": ["Yurak", "O'pka", "Buyrak", "Jigar"], "t": 2},
        {"savol": "Odam tanasidagi eng uzun suyak?", "v": ["Qovurg'a", "Son suyagi", "Orqa suyak", "Qo'l suyagi"], "t": 1},
    ],
    "tarix": [
        {"savol": "O'zbekiston mustaqillikka qachon erishdi?", "v": ["1990", "1991", "1992", "1993"], "t": 1},
        {"savol": "Amir Temur qachon tug'ilgan?", "v": ["1326", "1336", "1346", "1356"], "t": 1},
        {"savol": "Samarqand qachon qurilgan?", "v": ["eramizdan avvalgi 700", "eramizdan avvalgi 500", "eramizdan avvalgi 300", "eramizdan avvalgi 100"], "t": 0},
        {"savol": "Birinchi jahon urushi qachon boshlandi?", "v": ["1912", "1914", "1916", "1918"], "t": 1},
        {"savol": "Ikkinchi jahon urushi qachon tugadi?", "v": ["1943", "1944", "1945", "1946"], "t": 2},
    ],
}

FANLAR = {
    "matematika": "📐 Matematika",
    "fizika": "⚡ Fizika",
    "kimyo": "🧪 Kimyo",
    "biologiya": "🌿 Biologiya",
    "ingliz": "🇬🇧 Ingliz tili",
    "tarix": "📜 Tarix",
}

DARAJALAR = [
    (0, "🌱 Yangi boshlovchi"),
    (50, "📚 Oquvchi"),
    (150, "⭐ Bilimdon"),
    (300, "🔥 Ustoz"),
    (500, "🏆 Champion"),
    (1000, "👑 Mutaxassis"),
]

YUTUQLAR = [
    ("first_test", "🎯 Birinchi qadam", "Birinchi testni ishlash"),
    ("perfect_5", "💯 Mukammal", "5 ta testda 100% natija"),
    ("ball_100", "💰 Yuz ball", "100 ball toplash"),
    ("ball_500", "🏅 Besh yuz", "500 ball toplash"),
    ("referal_5", "👥 Targ'ibotchi", "5 ta referal jalb qilish"),
    ("daily_7", "📅 Haftalik", "7 kun ketma-ket test ishlash"),
]

DARS_REJASI = [
    ("Dushanba", "📐 Matematika + 🇬🇧 Ingliz tili"),
    ("Seshanba", "⚡ Fizika + 📖 Ona tili"),
    ("Chorshanba", "🧪 Kimyo + 📐 Matematika"),
    ("Payshanba", "🌿 Biologiya + 🇬🇧 Ingliz tili"),
    ("Juma", "📜 Tarix + ⚡ Fizika"),
    ("Shanba", "🔄 Barcha fanlardan takrorlash"),
    ("Yakshanba", "💪 Dam olish + Zaif fanlar"),
]

DARS_MATERIALLARI = {
    "matematika": "📐 Matematika darslari:\n\n1. Algebra asoslari\n2. Geometriya\n3. Trigonometriya\n4. Logarifmlar\n5. Integrallar\n\nHar kuni kamida 10 ta misol ishlang!",
    "ingliz": "🇬🇧 Ingliz tili darslari:\n\n1. Grammar asoslari\n2. Vocabulary\n3. Reading\n4. Listening\n5. Writing\n\nHar kuni 10 ta yangi soz organing!",
    "fizika": "⚡ Fizika darslari:\n\n1. Mexanika\n2. Termodinamika\n3. Elektr va magnetizm\n4. Optika\n5. Kvant fizika\n\nFormulalarni yod oling!",
    "kimyo": "🧪 Kimyo darslari:\n\n1. Atom tuzilishi\n2. Kimyoviy bog\n3. Oksidlanish-qaytarilish\n4. Organik kimyo\n5. Eritmalar\n\nDavriy jadval elementlarini organing!",
    "biologiya": "🌿 Biologiya darslari:\n\n1. Hujayra tuzilishi\n2. Genetika\n3. Evolyutsiya\n4. Ekologiya\n5. Odam anatomiyasi\n\nSxemalarni chizib organing!",
    "tarix": "📜 Tarix darslari:\n\n1. Qadimgi davr\n2. O'rta asrlar\n3. Yangi davr\n4. O'zbekiston tarixi\n5. Jahon tarixi\n\nSanalarni yod oling!",
}


def get_daraja(ball):
    daraja = DARAJALAR[0][1]
    for min_ball, nom in DARAJALAR:
        if ball >= min_ball:
            daraja = nom
    return daraja


def get_user(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            "ball": 0, "testlar": 0, "togri": 0,
            "full_name": "", "username": "",
            "referallar": 0, "kunlik_test": 0,
            "oxirgi_kun": datetime.now().date().isoformat(),
            "maqsad": 0,
            "yutuqlar": [],
            "ketma_ket_kun": 0,
            "fan_statistika": {},
            "perfect_count": 0,
        }
    return users_db[user_id]


def update_kunlik(user_id):
    user = get_user(user_id)
    bugun = datetime.now().date().isoformat()
    if user["oxirgi_kun"] != bugun:
        user["kunlik_test"] = 0
        user["ketma_ket_kun"] = user.get("ketma_ket_kun", 0) + 1
        user["oxirgi_kun"] = bugun


def check_yutuqlar(user_id, context=None):
    user = get_user(user_id)
    yangi_yutuqlar = []

    if user["testlar"] >= 1 and "first_test" not in user["yutuqlar"]:
        user["yutuqlar"].append("first_test")
        yangi_yutuqlar.append("🎯 Birinchi qadam")

    if user.get("perfect_count", 0) >= 5 and "perfect_5" not in user["yutuqlar"]:
        user["yutuqlar"].append("perfect_5")
        yangi_yutuqlar.append("💯 Mukammal")

    if user["ball"] >= 100 and "ball_100" not in user["yutuqlar"]:
        user["yutuqlar"].append("ball_100")
        yangi_yutuqlar.append("💰 Yuz ball")

    if user["ball"] >= 500 and "ball_500" not in user["yutuqlar"]:
        user["yutuqlar"].append("ball_500")
        yangi_yutuqlar.append("🏅 Besh yuz ball")

    if user.get("referallar", 0) >= 5 and "referal_5" not in user["yutuqlar"]:
        user["yutuqlar"].append("referal_5")
        yangi_yutuqlar.append("👥 Targibotchi")

    if user.get("ketma_ket_kun", 0) >= 7 and "daily_7" not in user["yutuqlar"]:
        user["yutuqlar"].append("daily_7")
        yangi_yutuqlar.append("📅 Haftalik")

    return yangi_yutuqlar


def get_reyting():
    return sorted(users_db.items(), key=lambda x: x[1]["ball"], reverse=True)[:10]


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Test ishlash", callback_data="test"),
         InlineKeyboardButton("📚 Darslar", callback_data="darslar")],
        [InlineKeyboardButton("📊 Reyting", callback_data="reyting"),
         InlineKeyboardButton("📅 Dars rejasi", callback_data="reja")],
        [InlineKeyboardButton("👤 Profilim", callback_data="profil"),
         InlineKeyboardButton("🏅 Yutuqlar", callback_data="yutuqlar")],
        [InlineKeyboardButton("🎯 Maqsad", callback_data="maqsad"),
         InlineKeyboardButton("👥 Referal", callback_data="referal")],
        [InlineKeyboardButton("🌐 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))],
    ])


async def send_savol(query, context, fan, index):
    savol_data = questions_db[fan][index]
    jami = len(questions_db[fan])
    togri_son = context.user_data.get("togri_javoblar", 0)
    harflar = ["A", "B", "C", "D"]
    keyboard = [
        [InlineKeyboardButton(harflar[i] + ") " + v, callback_data="q_" + str(i))]
        for i, v in enumerate(savol_data["v"])
    ]
    fan_nomi = FANLAR.get(fan, fan)
    progress = "▓" * index + "░" * (jami - index)
    await query.edit_message_text(
        fan_nomi + " — " + str(index + 1) + "/" + str(jami) + "\n"
        + progress + "\n"
        "Togri: " + str(togri_son) + "\n\n"
        "❓ " + savol_data["savol"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_user(user.id)
    db_user["full_name"] = user.full_name or ""
    db_user["username"] = user.username or ""

    if context.args:
        ref_id = context.args[0]
        if ref_id.isdigit() and int(ref_id) != user.id and int(ref_id) in users_db:
            ref_user = users_db[int(ref_id)]
            ref_user["referallar"] = ref_user.get("referallar", 0) + 1
            ref_user["ball"] += 20
            yangi = check_yutuqlar(int(ref_id))
            msg = "Referal havolangiz orqali yangi foydalanuvchi qoshildi! +20 ball oldiniz!"
            if yangi:
                msg += "\n\nYangi yutuq: " + ", ".join(yangi)
            try:
                await context.bot.send_message(int(ref_id), msg)
            except Exception:
                pass

    daraja = get_daraja(db_user["ball"])
    maqsad_text = ""
    if db_user.get("maqsad", 0) > 0:
        foiz = min(100, int((db_user["ball"] / db_user["maqsad"]) * 100))
        maqsad_text = "\n🎯 Maqsad: " + str(db_user["ball"]) + "/" + str(db_user["maqsad"]) + " (" + str(foiz) + "%)"

    await update.message.reply_text(
        "Salom, " + (user.first_name or "foydalanuvchi") + "!\n\n"
        "🎯 Litsey Tayyorgarlik botiga xush kelibsiz!\n"
        "Darajangiz: " + daraja + maqsad_text + "\n\n"
        "Bu bot orqali:\n"
        "📝 Testlar ishlang va ball toplang\n"
        "📚 Barcha fanlardan dars oling\n"
        "📊 Real reytingda orningizni biling\n"
        "🏅 Yutuqlar toplang\n"
        "👥 Dostlarni taklif qiling va bonus oling\n\n"
        "Bolimni tanlang:",
        reply_markup=main_menu()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user
    db_user = get_user(user.id)
    update_kunlik(user.id)

    if data == "menu":
        daraja = get_daraja(db_user["ball"])
        await query.edit_message_text(
            "🏠 Bosh menyu\nDarajangiz: " + daraja + "\n\nBolimni tanlang:",
            reply_markup=main_menu()
        )

    elif data == "test":
        keyboard = [[InlineKeyboardButton(v, callback_data="fan_" + k)] for k, v in FANLAR.items()]
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="menu")])
        await query.edit_message_text(
            "📝 Test ishlash\n\n"
            "Bugungi testlar: " + str(db_user["kunlik_test"]) + "\n"
            "Jami ball: " + str(db_user["ball"]) + "\n\n"
            "Qaysi fandan test ishlaysiz?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("fan_"):
        fan = data[4:]
        if fan not in questions_db:
            await query.answer("Bu fan hali qoshilmagan!", show_alert=True)
            return
        context.user_data["fan"] = fan
        context.user_data["savol_index"] = 0
        context.user_data["togri_javoblar"] = 0
        await send_savol(query, context, fan, 0)

    elif data.startswith("q_"):
        fan = context.user_data.get("fan", "")
        savol_index = context.user_data.get("savol_index", 0)
        togri_javoblar = context.user_data.get("togri_javoblar", 0)
        javob = int(data[2:])

        if fan and fan in questions_db:
            savol = questions_db[fan][savol_index]
            if javob == savol["t"]:
                togri_javoblar += 1
                context.user_data["togri_javoblar"] = togri_javoblar
                await query.answer("Togri!", show_alert=False)
            else:
                togri_javob = savol["v"][savol["t"]]
                await query.answer("Xato! Togri javob: " + togri_javob, show_alert=True)

            savol_index += 1
            context.user_data["savol_index"] = savol_index

            if savol_index < len(questions_db[fan]):
                await send_savol(query, context, fan, savol_index)
            else:
                jami = len(questions_db[fan])
                ball = togri_javoblar * 10
                db_user["ball"] += ball
                db_user["testlar"] += 1
                db_user["togri"] += togri_javoblar
                db_user["kunlik_test"] += 1

                if togri_javoblar == jami:
                    db_user["perfect_count"] = db_user.get("perfect_count", 0) + 1

                if fan not in db_user["fan_statistika"]:
                    db_user["fan_statistika"][fan] = {"testlar": 0, "togri": 0}
                db_user["fan_statistika"][fan]["testlar"] += 1
                db_user["fan_statistika"][fan]["togri"] += togri_javoblar

                daraja = get_daraja(db_user["ball"])
                yangi_yutuqlar = check_yutuqlar(user.id)

                maqsad_text = ""
                if db_user.get("maqsad", 0) > 0:
                    foiz = min(100, int((db_user["ball"] / db_user["maqsad"]) * 100))
                    maqsad_text = "\n🎯 Maqsad: " + str(foiz) + "%"
                    if db_user["ball"] >= db_user["maqsad"]:
                        maqsad_text += " - BAJARILDI!"

                yutuq_text = ""
                if yangi_yutuqlar:
                    yutuq_text = "\n\nYangi yutuq: " + ", ".join(yangi_yutuqlar)

                xabar = "Ajoyib! Mukammal natija!" if togri_javoblar == jami else "Davom eting!"
                await query.edit_message_text(
                    "🏁 Test yakunlandi!\n\n"
                    "Natija: " + str(togri_javoblar) + "/" + str(jami) + "\n"
                    "Olgan ball: +" + str(ball) + "\n"
                    "Jami ball: " + str(db_user["ball"]) + "\n"
                    "Daraja: " + daraja + maqsad_text + yutuq_text + "\n\n" + xabar,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Yana ishlash", callback_data="fan_" + fan)],
                        [InlineKeyboardButton("📝 Boshqa fan", callback_data="test")],
                        [InlineKeyboardButton("🏠 Bosh menu", callback_data="menu")],
                    ])
                )

    elif data == "darslar":
        keyboard = [[InlineKeyboardButton(v, callback_data="dars_" + k)] for k, v in FANLAR.items()]
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="menu")])
        await query.edit_message_text(
            "📚 Darslar\n\nQaysi fandan dars olasiz?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("dars_"):
        fan = data[5:]
        matn = DARS_MATERIALLARI.get(fan, "Tez orada!")
        await query.edit_message_text(
            matn,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="darslar")]])
        )

    elif data == "reyting":
        medals = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        rows = get_reyting()
        text = "📊 Top 10 Reyting\n\n"
        for i, (uid, u) in enumerate(rows):
            name = u.get("full_name", "Noma'lum")
            ball = u["ball"]
            daraja = get_daraja(ball)
            text += medals[i] + ". " + name + " — " + str(ball) + " ball " + daraja + "\n"
        if not rows:
            text += "Hali hech kim test ishlamagan!\n"
        my_ball = db_user["ball"]
        text += "\nSiz: " + str(my_ball) + " ball | " + get_daraja(my_ball)
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]])
        )

    elif data == "reja":
       

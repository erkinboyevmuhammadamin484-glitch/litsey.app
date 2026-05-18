import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://litsey-app.vercel.app")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "0").split(",") if x.strip()]

users_db = {}

questions_db = {
    "matematika": [
        {"savol": "2 + 2 = ?", "v": ["3", "4", "5", "6"], "t": 1},
        {"savol": "5 x 5 = ?", "v": ["20", "25", "30", "35"], "t": 1},
        {"savol": "10 - 3 = ?", "v": ["5", "6", "7", "8"], "t": 2},
        {"savol": "3 ning kvadrati = ?", "v": ["6", "9", "12", "8"], "t": 1},
        {"savol": "16 ning ildizi = ?", "v": ["2", "4", "6", "8"], "t": 1},
        {"savol": "15 / 3 = ?", "v": ["3", "4", "5", "6"], "t": 2},
        {"savol": "2 ning kubi = ?", "v": ["6", "8", "10", "12"], "t": 1},
    ],
    "ingliz": [
        {"savol": "Apple - ozbekcha?", "v": ["Olma", "Nok", "Uzum", "Shaftoli"], "t": 0},
        {"savol": "I am a student - tarjimasi?", "v": ["O'qituvchi", "O'quvchi", "Shifokor", "Muhandis"], "t": 1},
        {"savol": "Beautiful sinoniimi?", "v": ["Ugly", "Pretty", "Bad", "Slow"], "t": 1},
        {"savol": "To be - Past Simple?", "v": ["is/are", "was/were", "be", "been"], "t": 1},
        {"savol": "They ___ students.", "v": ["is", "am", "are", "be"], "t": 2},
        {"savol": "Book - kopligi?", "v": ["Books", "Bookes", "Bookies", "Book"], "t": 0},
        {"savol": "Run - Past Simple?", "v": ["Runned", "Ran", "Run", "Runs"], "t": 1},
    ],
    "fizika": [
        {"savol": "Yoruglik tezligi?", "v": ["200000 km/s", "300000 km/s", "400000 km/s", "100000 km/s"], "t": 1},
        {"savol": "Nyuton 1-qonuni?", "v": ["Kuch", "Inersiya", "Ishqalanish", "Tortishish"], "t": 1},
        {"savol": "Suv necha gradusda qaynaydi?", "v": ["90", "95", "100", "105"], "t": 2},
        {"savol": "Elektr toki birligi?", "v": ["Volt", "Amper", "Vatt", "Om"], "t": 1},
        {"savol": "Massa birligi SI da?", "v": ["Gramm", "Kilogramm", "Tonna", "Litr"], "t": 1},
    ],
    "kimyo": [
        {"savol": "Suv formulasi?", "v": ["CO2", "H2O", "NaCl", "O2"], "t": 1},
        {"savol": "Oltin belgisi?", "v": ["Ag", "Fe", "Au", "Cu"], "t": 2},
        {"savol": "Davriy jadval kim tuzgan?", "v": ["Nyuton", "Mendeleyev", "Einstein", "Darvin"], "t": 1},
        {"savol": "Osh tuzi formulasi?", "v": ["KCl", "NaCl", "CaCl2", "MgCl2"], "t": 1},
        {"savol": "Kislorod belgisi?", "v": ["O", "K", "Os", "Og"], "t": 0},
    ],
    "biologiya": [
        {"savol": "Fotosintez qayerda boladi?", "v": ["Ildizda", "Bargda", "Gulda", "Mevada"], "t": 1},
        {"savol": "Odam tanasida nechta suyak?", "v": ["186", "206", "226", "246"], "t": 1},
        {"savol": "DNK nima?", "v": ["Oqsil", "Irsiyat moddasi", "Vitamin", "Ferment"], "t": 1},
        {"savol": "Qon guruhlar soni?", "v": ["2", "3", "4", "5"], "t": 2},
        {"savol": "Eng katta hujayra?", "v": ["Qon", "Tuxum", "Nerv", "Muskul"], "t": 1},
    ],
}

FANLAR = {
    "matematika": "📐 Matematika",
    "fizika": "⚡ Fizika",
    "kimyo": "🧪 Kimyo",
    "biologiya": "🌿 Biologiya",
    "ingliz": "🇬🇧 Ingliz tili",
}

DARAJALAR = [
    (0, "🌱 Yangi boshlovchi"),
    (50, "📚 Oquvchi"),
    (150, "⭐ Bilimdon"),
    (300, "🔥 Ustoz"),
    (500, "🏆 Champion"),
    (1000, "👑 Mutaxassis"),
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
        }
    return users_db[user_id]


def update_kunlik(user_id):
    user = get_user(user_id)
    bugun = datetime.now().date().isoformat()
    if user["oxirgi_kun"] != bugun:
        user["kunlik_test"] = 0
        user["oxirgi_kun"] = bugun


def get_reyting():
    return sorted(users_db.items(), key=lambda x: x[1]["ball"], reverse=True)[:10]


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Test ishlash", callback_data="test"),
         InlineKeyboardButton("📚 Darslar", callback_data="darslar")],
        [InlineKeyboardButton("📊 Reyting", callback_data="reyting"),
         InlineKeyboardButton("📅 Dars rejasi", callback_data="reja")],
        [InlineKeyboardButton("👤 Profilim", callback_data="profil"),
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
    await query.edit_message_text(
        fan_nomi + " — " + str(index + 1) + "/" + str(jami) + " savol\n"
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
            try:
                await context.bot.send_message(int(ref_id),
                    "Referal havolangiz orqali yangi foydalanuvchi qoshildi! +20 ball oldiniz!")
            except Exception:
                pass

    daraja = get_daraja(db_user["ball"])
    await update.message.reply_text(
        "Salom, " + (user.first_name or "foydalanuvchi") + "!\n\n"
        "🎯 Litsey Tayyorgarlik botiga xush kelibsiz!\n"
        "Darajangiz: " + daraja + "\n\n"
        "Bu bot orqali:\n"
        "📝 Testlar ishlang va ball toplang\n"
        "📚 Barcha fanlardan dars oling\n"
        "📊 Real reytingda orningizni biling\n"
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
            "Bugungi testlar: " + str(db_user["kunlik_test"]) + "\n\n"
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
                daraja = get_daraja(db_user["ball"])
                xabar = "Ajoyib!" if togri_javoblar == jami else "Davom eting!"
                await query.edit_message_text(
                    "🏁 Test yakunlandi!\n\n"
                    "Natija: " + str(togri_javoblar) + "/" + str(jami) + "\n"
                    "Olgan ball: +" + str(ball) + "\n"
                    "Jami ball: " + str(db_user["ball"]) + "\n"
                    "Daraja: " + daraja + "\n\n" + xabar,
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
        my_daraja = get_daraja(my_ball)
        text += "\nSiz: " + str(my_ball) + " ball | " + my_daraja
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]])
        )

    elif data == "reja":
        kunlar = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
        bugun_index = datetime.now().weekday()
        text = "📅 Haftalik dars rejasi\n\n"
        for i, (kun, dars) in enumerate(DARS_REJASI):
            belgi = "👉 " if i == bugun_index else "    "
            text += belgi + kun + ": " + dars + "\n"
        text += "\nBugun: " + kunlar[bugun_index]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]])
        )

    elif data == "profil":
        ball = db_user["ball"]
        testlar = db_user["testlar"]
        togri = db_user["togri"]
        foiz = round((togri / (testlar * 5)) * 100) if testlar > 0 else 0
        daraja = get_daraja(ball)
        xabar = "Zor natija!" if foiz >= 80 else "Davom eting!"
        await query.edit_message_text(
            "👤 Profilingiz\n\n"
            "Ism: " + (user.full_name or "") + "\n"
            "Daraja: " + daraja + "\n"
            "Ball: " + str(ball) + "\n"
            "Testlar: " + str(testlar) + "\n"
            "Togri javoblar: " + str(togri) + "\n"
            "Aniqlik: " + str(foiz) + "%\n"
            "Referallar: " + str(db_user.get("referallar", 0)) + "\n"
            "Bugungi testlar: " + str(db_user["kunlik_test"]) + "\n\n" + xabar,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]])
        )

    elif data == "referal":
        bot_me = await context.bot.get_me()
        ref_link = "https://t.me/" + bot_me.username + "?start=" + str(user.id)
        referallar = db_user.get("referallar", 0)
        await query.edit_message_text(
            "👥 Referal tizimi\n\n"
            "Dostlarni taklif qiling — har biri uchun +20 ball!\n\n"
            "Sizning havolangiz:\n" + ref_link + "\n\n"
            "Jami referallar: " + str(referallar) + "\n"
            "Referal bonuslari: " + str(referallar * 20) + " ball",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]])
        )


async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Ruxsat yoq!")
        return
    jami_testlar = sum(u.get("testlar", 0) for u in users_db.values())
    await update.message.reply_text(
        "👑 Admin panel\n\n"
        "Foydalanuvchilar: " + str(len(users_db)) + "\n"
        "Jami testlar: " + str(jami_testlar)
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("Ishlatish: /broadcast <xabar>")
        return
    matn = " ".join(context.args)
    yuborildi = 0
    for uid in users_db:
        try:
            await context.bot.send_message(uid, "Yangilik:\n\n" + matn)
            yuborildi += 1
        except Exception:
            pass
    await update.message.reply_text(str(yuborildi) + " ta foydalanuvchiga yuborildi!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Yordam:\n\n"
        "/start — Botni boshlash\n"
        "/help — Yordam\n\n"
        "Ilova: " + WEB_APP_URL
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()

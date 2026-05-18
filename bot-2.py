import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://litsey-app.vercel.app")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "0").split(",") if x.strip()]

# ======= DATABASE (xotira) =======
users_db = {}

questions_db = {
    "matematika": [
        {"savol": "2 + 2 = ?", "variantlar": ["3", "4", "5", "6"], "togri": 1},
        {"savol": "5 x 5 = ?", "variantlar": ["20", "25", "30", "35"], "togri": 1},
        {"savol": "10 - 3 = ?", "variantlar": ["5", "6", "7", "8"], "togri": 2},
        {"savol": "3² = ?", "variantlar": ["6", "9", "12", "8"], "togri": 1},
        {"savol": "√16 = ?", "variantlar": ["2", "4", "6", "8"], "togri": 1},
        {"savol": "15 ÷ 3 = ?", "variantlar": ["3", "4", "5", "6"], "togri": 2},
        {"savol": "2³ = ?", "variantlar": ["6", "8", "10", "12"], "togri": 1},
    ],
    "ingliz": [
        {"savol": "'Apple' o'zbekcha?", "variantlar": ["Olma", "Nok", "Uzum", "Shaftoli"], "togri": 0},
        {"savol": "'I am a student' tarjimasi?", "variantlar": ["Men o'qituvchiman", "Men o'quvchiman", "Men shifokorman", "Men muhandisaman"], "togri": 1},
        {"savol": "'Beautiful' so'zining sinonimi?", "variantlar": ["Ugly", "Pretty", "Bad", "Slow"], "togri": 1},
        {"savol": "To be fe'lining Past Simple shakli?", "variantlar": ["is/are", "was/were", "be", "been"], "togri": 1},
        {"savol": "'They ___ students.'", "variantlar": ["is", "am", "are", "be"], "togri": 2},
        {"savol": "'Book' so'zining ko'pligi?", "variantlar": ["Books", "Bookes", "Bookies", "Book"], "togri": 0},
        {"savol": "'Run' fe'lining Past Simple?", "variantlar": ["Runned", "Ran", "Run", "Runs"], "togri": 1},
    ],
    "fizika": [
        {"savol": "Yorug'lik tezligi?", "variantlar": ["200,000 km/s", "300,000 km/s", "400,000 km/s", "100,000 km/s"], "togri": 1},
        {"savol": "Nyutonning 1-qonuni?", "variantlar": ["Kuch", "Inersiya", "Ishqalanish", "Tortishish"], "togri": 1},
        {"savol": "Suv necha gradusda qaynaydi?", "variantlar": ["90°C", "95°C", "100°C", "105°C"], "togri": 2},
        {"savol": "Elektr toki birligi?", "variantlar": ["Volt", "Amper", "Vatt", "Om"], "togri": 1},
        {"savol": "Massa birligi SI da?", "variantlar": ["Gramm", "Kilogramm", "Tonna", "Litr"], "togri": 1},
    ],
    "kimyo": [
        {"savol": "Suvning formulasi?", "variantlar": ["CO2", "H2O", "NaCl", "O2"], "togri": 1},
        {"savol": "Oltin belgisi?", "variantlar": ["Ag", "Fe", "Au", "Cu"], "togri": 2},
        {"savol": "Davriy jadval kim tuzgan?", "variantlar": ["Nyuton", "Mendeleyev", "Einstein", "Darvin"], "togri": 1},
        {"savol": "Osh tuzi formulasi?", "variantlar": ["KCl", "NaCl", "CaCl2", "MgCl2"], "togri": 1},
        {"savol": "Kislorod belgisi?", "variantlar": ["O", "K", "Os", "Og"], "togri": 0},
    ],
    "biologiya": [
        {"savol": "Fotosintez qayerda?", "variantlar": ["Ildizda", "Bargda", "Gulda", "Mevada"], "togri": 1},
        {"savol": "Odam tanasida nechta suyak?", "variantlar": ["186", "206", "226", "246"], "togri": 1},
        {"savol": "DNK nima?", "variantlar": ["Oqsil", "Irsiyat moddasi", "Vitamin", "Ferment"], "togri": 1},
        {"savol": "Qon guruhlar soni?", "variantlar": ["2", "3", "4", "5"], "togri": 2},
        {"savol": "Eng katta hujayra?", "variantlar": ["Qon", "Tuxum", "Nerv", "Muskul"], "togri": 1},
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
    (50, "📚 O'quvchi"),
    (150, "⭐ Bilimdon"),
    (300, "🔥 Ustoz"),
    (500, "🏆 Champion"),
    (1000, "👑 Mutaxassis"),
]

DARS_REJASI = {
    "Dushanba": "📐 Matematika + 🇬🇧 Ingliz tili",
    "Seshanba": "⚡ Fizika + 📖 Ona tili",
    "Chorshanba": "🧪 Kimyo + 📐 Matematika",
    "Payshanba": "🌿 Biologiya + 🇬🇧 Ingliz tili",
    "Juma": "📜 Tarix + ⚡ Fizika",
    "Shanba": "Barcha fanlardan takrorlash 🔄",
    "Yakshanba": "Dam olish + Zaif fanlarni mustahkamlash 💪",
}

DARS_MATERIALLARI = {
    "matematika": (
        "📐 Matematika darslari:\n\n"
        "1️⃣ Algebra asoslari\n"
        "2️⃣ Geometriya\n"
        "3️⃣ Trigonometriya\n"
        "4️⃣ Logarifmlar\n"
        "5️⃣ Integrallar\n\n"
        "📌 Har kuni kamida 10 ta misol ishlang!"
    ),
    "ingliz": (
        "🇬🇧 Ingliz tili darslari:\n\n"
        "1️⃣ Grammar asoslari\n"
        "2️⃣ So'z boyligi (Vocabulary)\n"
        "3️⃣ Reading comprehension\n"
        "4️⃣ Listening\n"
        "5️⃣ Writing\n\n"
        "📌 Har kuni 10 ta yangi so'z o'rganing!"
    ),
    "fizika": (
        "⚡ Fizika darslari:\n\n"
        "1️⃣ Mexanika\n"
        "2️⃣ Termodinamika\n"
        "3️⃣ Elektr va magnetizm\n"
        "4️⃣ Optika\n"
        "5️⃣ Kvant fizika\n\n"
        "📌 Formulalarni yod oling!"
    ),
    "kimyo": (
        "🧪 Kimyo darslari:\n\n"
        "1️⃣ Atom tuzilishi\n"
        "2️⃣ Kimyoviy bog'\n"
        "3️⃣ Oksidlanish-qaytarilish\n"
        "4️⃣ Organik kimyo\n"
        "5️⃣ Eritmalar\n\n"
        "📌 Davriy jadval elementlarini o'rganing!"
    ),
    "biologiya": (
        "🌿 Biologiya darslari:\n\n"
        "1️⃣ Hujayra tuzilishi\n"
        "2️⃣ Genetika\n"
        "3️⃣ Evolyutsiya\n"
        "4️⃣ Ekologiya\n"
        "5️⃣ Odam anatomiyasi\n\n"
        "📌 Sxemalarni chizib o'rganing!"
    ),
}

# ======= YORDAMCHI FUNKSIYALAR =======

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

async def send_question(query, context, fan, index):
    savol_data = questions_db[fan][index]
    jami = len(questions_db[fan])
    togri = context.user_data.get("togri_javoblar", 0)
    harflar = ["A", "B", "C", "D"]
    keyboard = [
        [InlineKeyboardButton(f"{harflar[i]}) {v}", callback_data=f"test_q_{i}")]
        for i, v in enumerate(savol_data["variantlar"])
    ]
    await query.edit_message_text(
        f"📝 {FANLAR.get(fan, fan)} — {index + 1}/{jami} savol\n"
        f"✅ To'g'ri: {togri}\n\n"
        f"❓ {savol_data['savol']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ======= HANDLERS =======

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
                    "🎉 Referal havolangiz orqali yangi foydalanuvchi qo'shildi!\n+20 ball oldiniz!")
            except:
                pass

    daraja = get_daraja(db_user["ball"])
    await update.message.reply_text(
        f"👋 Salom, {user.first_name}!\n\n"
        f"🎯 Litsey Tayyorgarlik botiga xush kelibsiz!\n"
        f"🎖 Darajangiz: {daraja}\n\n"
        f"Bu bot orqali:\n"
        f"• 📝 Testlar ishlang va ball to'plang\n"
        f"• 📚 Barcha fanlardan dars oling\n"
        f"• 📊 Real reytingda o'z o'rningizni biling\n"
        f"• 👥 Do'stlarni taklif qiling va bonus oling\n\n"
        f"⬇️ Bo'limni tanlang:",
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
        await query.edit_message_text(
            f"🏠 Bosh menyu\n🎖 Darajangiz: {get_daraja(db_user['ball'])}\n\nBo'limni tanlang:",
            reply_markup=main_menu()
        )

    elif data == "test":
        keyboard = [[InlineKeyboardButton(v, callback_data=f"test_{k}")] for k, v in FANLAR.items()]
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="menu")])
        await query.edit_message_text(
            f"📝 Test ishlash\n\n"
            f"📅 Bugungi testlar: {db_user['kunlik_test']}\n\n"
            f"Qaysi fandan test ishlaysiz?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("test_") and "_q_" not in data:
        fan = data[5:]
        if fan not in questions_db:
            await query.answer("Bu fan hali qo'shilmagan!", show_alert=True)
            return
        context.user_data.update({"fan": fan, "savol_index": 0, "togri_javoblar": 0})
        await send_question(query, context, fan, 0)

    elif "_q_" in data:
        fan = context.user_data.get("fan", "")
        savol_index = context.user_data.get("savol_index", 0)
        togri_javoblar = context.user_data.get("togri_javoblar", 0)
        javob = int(data.split("_q_")[1])

        if fan and fan in questions_db:
            savol = questions_db[fan][savol_index]
            if javob == savol["togri"]:
                togri_javoblar += 1
                context.user_data["togri_javoblar"] = togri_javoblar
                await query.answer("✅ To'g'ri!", show_alert=False)
            else:
                await query.answer(f"❌ Xato! To'g'ri: {savol['variantlar'][savol['togri']]}", show_alert=True)

            savol_index += 1
            context.user_data["savol_index"] = savol_index

            if savol_index < len(questions_db[fan]):
                await send_question(query, context, fan, savol_index)
            else:
                jami = len(questions_db[fan])
                ball = togri_javoblar * 10
                db_user["ball"] += ball
                db_user["testlar"] += 1
                db_user["togri"] += togri_javoblar
                db_user["kunlik_test"] += 1
                daraja = get_daraja(db_user["ball"])
                await query.edit_message_text(
                    f"🏁 Test yakunlandi!\n\n"
                    f"📊 Natija: {togri_javoblar}/{jami}\n"
                    f"⭐ Olgan ball: +{ball}\n"
                    f"💰 Jami ball: {db_user['ball']}\n"
                    f"🎖 Daraja: {daraja}\n\n"
                    f"{'🔥 Ajoyib!' if togri_javoblar == jami else '💪 Davom eting!'}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Yana ishlash", callback_data=f"test_{fan}")],
                        [InlineKeyboardButton("📝 Boshqa fan", callback_data="test")],
                        [InlineKeyboardButton("🏠 Bosh menu", callback_data="menu")],
                    ])
                )

    elif data == "darslar":
        keyboard = [[InlineKeyboardButton(v, callback_data=f"dars_{k}")] for k, v in FANLAR.items()]
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="menu")])
        await query.edit_message_text("📚 Darslar\n\nQaysi fandan dars olasiz?",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("dars_"):
        fan = data[5:]
        matn = DARS_MATERIALLARI.get(fan, "🔜 Tez orada!")
        await query.edit_message_text(matn,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="darslar")]]))

    elif data == "reyting":
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        rows = get_reyting()
        text = "📊 Top 10 Reyting\n\n"
        for i, (uid, u) in enumerate(rows):
            text += f"{medals[i]} {u.get('full_name', 'Noma\'lum')} — {u['ball']} ball {get_daraja(u['ball'])}\n"
        text += f"\n👤 Siz: {db_user['ball']} ball | {get_daraja(db_user['ball'])}"
        await query.edit_message_text(text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]]))

    elif data == "reja":
        kunlar = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
        bugun_index = datetime.now().weekday()
        text = "📅 Haftalik dars rejasi\n\n"
        for i, (kun, dars) in enumerate(DARS_REJASI.items()):
            belgi = "👉 " if i == bugun_index else "    "
            text += f"{belgi}{kun}: {dars}\n"
        text += f"\n📌 Bugun: {kunlar[bugun_index]}"
        await query.edit_message_text(text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]]))

    elif data == "profil":
        ball = db_user["ball"]
        testlar = db_user["testlar"]
        togri = db_user["togri"]
        foiz = round((togri / (testlar * 5)) * 100) if testlar > 0 else 0
        await query.edit_message_text(
            f"👤 Profilingiz\n\n"
            f"👤 Ism: {user.full_name}\n"
            f"🎖 Daraja: {get_daraja(ball)}\n"
            f"⭐ Ball: {ball}\n"
            f"📝 Testlar: {testlar}\n"
            f"✅ To'g'ri javoblar: {togri}\n"
            f"📈 Aniqlik: {foiz}%\n"
            f"👥 Referallar: {db_user.get('referallar', 0)}\n"
            f"📅 Bugungi testlar: {db_user['kunlik_test']}\n\n"
            f"{'🔥 Zo\'r natija!' if foiz >= 80 else '💪 Davom eting!'}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]]))

    elif data == "referal":
        bot_me = await context.bot.get_me()
        ref_link = f"https://t.me/{bot_me.username}?start={user.id}"
        await query.edit_message_text(
            f"👥 Referal tizimi\n\n"
            f"Do'stlarni taklif qiling — har biri uchun +20 ball!\n\n"
            f"🔗 Sizning havolangiz:\n{ref_link}\n\n"
            f"👥 Jami referallar: {db_user.get('referallar', 0)}\n"
            f"⭐ Referal bonuslari: {db_user.get('referallar', 0) * 20} ball",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]]))

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Ruxsat yo'q!")
        return
    jami_testlar = sum(u.get("testlar", 0) for u in users_db.values())
    await update.message.reply_text(
        f"👑 Admin panel\n\n"
        f"👥 Foydalanuvchilar: {len(users_db)}\n"
        f"📝 Jami testlar: {jami_testlar}\n"
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
            await context.bot.send_message(uid, f"📢 Yangilik:\n\n{matn}")
            yuborildi += 1
        except:
            pass
    await update.message.reply_text(f"✅ {yuborildi} ta foydalanuvchiga yuborildi!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Yordam:\n\n"
        "/start — Botni boshlash\n"
        "/help — Yordam\n\n"
        f"🌐 Ilova: {WEB_APP_URL}"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()

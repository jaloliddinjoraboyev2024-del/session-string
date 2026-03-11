import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired
import os
from dotenv import load_dotenv

# .env faylidan ma'lumotlarni o'qish
load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Botni yaratish
app = Client(
    "public_session_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# Foydalanuvchi ma'lumotlarini vaqtincha saqlash
user_sessions = {}

# /start komandasi - HAMMA UCHUN OCHIQ
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Foydalanuvchi"
    
    welcome_text = f"""
🌐 **Assalomu alaykum, {first_name}!**

Telegram Session String Botiga xush kelibsiz!

📌 **Bu bot orqali:**
• O'z Telegram hisobingiz uchun **session string** olishingiz mumkin
• Session string - bu sizning hisobingizga dasturlar orqali kirish imkonini beruvchi maxfiy kod

⚠️ **DIQQAT!**
• Session stringni hech kimga bermang!
• Bu kod orqali hisobingizga to'liq kirish mumkin
• Session stringni xavfsiz joyda saqlang

🔽 **Davom etish uchun tugmani bosing:**
    """
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Session String olish", callback_data="get_session")],
        [InlineKeyboardButton("📚 Qanday ishlaydi?", callback_data="help")],
        [InlineKeyboardButton("👨‍💻 Bot haqida", callback_data="about")]
    ])
    
    await message.reply_text(
        welcome_text,
        reply_markup=buttons,
        parse_mode=ParseMode.MARKDOWN
    )

# Callback handler
@app.on_callback_query()
async def handle_callbacks(client: Client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    if data == "get_session":
        await callback_query.message.edit_text(
            "🔐 **Session string olish**\n\n"
            "📱 Iltimos, telefon raqamingizni kiriting:\n"
            "Format: Xalqaro formatda (+998901234567)\n"
            "Misol: `+998901234567`\n\n"
            "⚠️ Telefon raqamingiz xavfsiz saqlanadi va faqat session yaratish uchun ishlatiladi.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")
            ]])
        )
        
        # Foydalanuvchini kutish holatiga o'tkazish
        user_sessions[user_id] = {"step": "waiting_phone"}
        
    elif data == "help":
        help_text = """
📚 **Qanday ishlaydi?**

1️⃣ **Telefon raqamni kiriting:**
   • Xalqaro formatda (+998901234567)
   • To'g'ri raqam kiritish muhim

2️⃣ **Kodni tasdiqlang:**
   • Telegramdan SMS yoki app orqali kod keladi
   • 5 xonali kodni kiriting

3️⃣ **Session stringni oling:**
   • Bot sizga tayyor session stringni yuboradi
   • Kodni xavfsiz joyda saqlang

⚠️ **Muhim eslatmalar:**
• Agar 2FA (ikki bosqichli tasdiqlash) yoqilgan bo'lsa, parol ham so'raladi
• Jarayon 5 daqiqa ichida tugatilmasa, qaytadan boshlash kerak
• Session string faqat sizga ko'rsatiladi
        """
        
        await callback_query.message.edit_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")
            ]])
        )
        
    elif data == "about":
        about_text = """
👨‍💻 **Bot haqida:**

• **Versiya:** 2.0.0 (Ochiq)
• **Kutubxona:** Pyrogram
• **Til:** Python 3.9+

✅ **Imkoniyatlar:**
• Hamma foydalanuvchilar uchun ochiq
• Xavfsiz session string yaratish
• 2FA qo'llab-quvvatlash
• Tezkor va ishonchli

📞 **Muammo bo'lsa:** @jaloliddinee bilan bog'laning
        """
        
        await callback_query.message.edit_text(
            about_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")
            ]])
        )
        
    elif data == "back_to_main":
        user_id = callback_query.from_user.id
        first_name = callback_query.from_user.first_name or "Foydalanuvchi"
        
        welcome_text = f"""
🌐 **Assalomu alaykum, {first_name}!**

Telegram Session String Botiga xush kelibsiz!

📌 **Bu bot orqali:**
• O'z Telegram hisobingiz uchun **session string** olishingiz mumkin

⚠️ **DIQQAT!**
• Session stringni hech kimga bermang!
• Bu kod orqali hisobingizga to'liq kirish mumkin

🔽 **Davom etish uchun tugmani bosing:**
        """
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔐 Session String olish", callback_data="get_session")],
            [InlineKeyboardButton("📚 Qanday ishlaydi?", callback_data="help")],
            [InlineKeyboardButton("👨‍💻 Bot haqida", callback_data="about")]
        ])
        
        await callback_query.message.edit_text(
            welcome_text,
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN
        )
        
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    await callback_query.answer()

# Xabarlarni qabul qilish - HAMMA UCHUN
@app.on_message(filters.text & filters.private)
async def handle_messages(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Foydalanuvchi session olish jarayonidami?
    if user_id in user_sessions:
        step = user_sessions[user_id].get("step")
        
        if step == "waiting_phone":
            # Telefon raqamni qabul qilish
            phone = text
            
            # Telefon raqam formatini tekshirish
            if not phone.startswith("+") or not phone[1:].isdigit():
                await message.reply_text(
                    "❌ **Xato format!**\n\n"
                    "Telefon raqam + bilan boshlanishi va faqat raqamlardan iborat bo'lishi kerak.\n"
                    "Misol: `+998901234567`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            await message.reply_text("⏳ **Telegram serverlariga ulanmoqda...**\n\nIltimos, biroz kuting...")
            
            try:
                # Yangi client yaratish
                temp_client = Client(
                    f"temp_{user_id}",
                    api_id=API_ID,
                    api_hash=API_HASH,
                    in_memory=True
                )
                
                await temp_client.connect()
                
                # Kod yuborish
                sent_code = await temp_client.send_code(phone)
                
                # Ma'lumotlarni saqlash
                user_sessions[user_id].update({
                    "step": "waiting_code",
                    "phone": phone,
                    "client": temp_client,
                    "phone_code_hash": sent_code.phone_code_hash
                })
                
                await message.reply_text(
                    "📨 **Telegramdan kod yuborildi!**\n\n"
                    "Iltimos, SMS yoki Telegram ilovasida kelgan **5 xonali kod**ni kiriting:\n"
                    "Format: `12345`",
                    parse_mode=ParseMode.MARKDOWN
                )
                
            except Exception as e:
                await message.reply_text(f"❌ Xatolik: {str(e)}")
                if user_id in user_sessions:
                    del user_sessions[user_id]
        
        elif step == "waiting_code":
            # Kodni qabul qilish
            code = text.strip()
            
            if not code.isdigit() or len(code) != 5:
                await message.reply_text(
                    "❌ **Xato format!**\n\n"
                    "Kod 5 xonali raqamdan iborat bo'lishi kerak.\n"
                    "Misol: `12345`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            temp_client = user_sessions[user_id].get("client")
            phone = user_sessions[user_id].get("phone")
            phone_code_hash = user_sessions[user_id].get("phone_code_hash")
            
            try:
                # Kodni tasdiqlash
                await temp_client.sign_in(
                    phone,
                    phone_code_hash,
                    code
                )
                
                # Session stringni olish
                session_string = await temp_client.export_session_string()
                
                # Session stringni yuborish
                await message.reply_text(
                    "✅ **SESSION STRING TAYYOR!**\n\n"
                    f"📝 **Sizning session stringingiz:**\n`{session_string}`\n\n"
                    "⚠️ **MUHIM!**\n"
                    "• Bu kodni hech kimga bermang\n"
                    "• Xavfsiz joyda saqlang\n"
                    "• Kerak bo'lmaganda o'chirib tashlang\n\n"
                    "📋 **Kodni nusxalash uchun ustiga bosing!**",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Clientni to'xtatish
                await temp_client.disconnect()
                
                # Ma'lumotlarni tozalash
                del user_sessions[user_id]
                
            except SessionPasswordNeeded:
                # 2FA parol so'rash
                user_sessions[user_id]["step"] = "waiting_2fa"
                await message.reply_text(
                    "🔐 **Ikki bosqichli tasdiqlash (2FA) yoqilgan!**\n\n"
                    "Iltimos, hisobingiz uchun o'rnatilgan **parol**ni kiriting:",
                    parse_mode=ParseMode.MARKDOWN
                )
                
            except PhoneCodeInvalid:
                await message.reply_text(
                    "❌ **Noto'g'ri kod!**\n\n"
                    "Qaytadan urinib ko'ring. Agar kod kelmagan bo'lsa, /start bosing."
                )
                
            except PhoneCodeExpired:
                await message.reply_text(
                    "❌ **Kod eskirgan!**\n\n"
                    "Yangi kod olish uchun /start bosing."
                )
                
            except Exception as e:
                await message.reply_text(f"❌ Xatolik: {str(e)}")
                del user_sessions[user_id]
        
        elif step == "waiting_2fa":
            # 2FA parolni qabul qilish
            password = text
            
            temp_client = user_sessions[user_id].get("client")
            
            try:
                # Parol bilan kirish
                await temp_client.check_password(password)
                
                # Session stringni olish
                session_string = await temp_client.export_session_string()
                
                # Session stringni yuborish
                await message.reply_text(
                    "✅ **SESSION STRING TAYYOR!**\n\n"
                    f"📝 **Sizning session stringingiz:**\n`{session_string}`\n\n"
                    "⚠️ **MUHIM!**\n"
                    "• Bu kodni hech kimga bermang\n"
                    "• Xavfsiz joyda saqlang\n\n"
                    "📋 **Kodni nusxalash uchun ustiga bosing!**",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Clientni to'xtatish
                await temp_client.disconnect()
                
                # Ma'lumotlarni tozalash
                del user_sessions[user_id]
                
            except Exception as e:
                await message.reply_text(f"❌ Xatolik: {str(e)}")
                del user_sessions[user_id]
    
    else:
        # Agar /start bosilmagan bo'lsa
        await message.reply_text(
            "❌ Iltimos, avval /start komandasini bosing!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")
            ]])
        )

# Botni ishga tushirish
if __name__ == "__main__":
    print("🚀 Public Session String Bot ishga tushmoqda...")
    print("✅ Bot HAMMA foydalanuvchilar uchun OCHIQ!")
    print(f"🤖 Bot token: {BOT_TOKEN[:10]}...")
    print("📡 Bot faol...")
    app.run()
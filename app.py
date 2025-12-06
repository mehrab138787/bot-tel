from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, CallbackQuery # <-- اصلاح شده
from typing import Union # <-- اضافه شده برای سازگاری با پایتون < 3.10
from datetime import datetime, timedelta
import logging
import os
import random
import re 
import asyncio 

# --- تنظیمات اولیه و متغیرها ---

# توکن تأیید شده شما
TOKEN = '8551310379:AAGpE01aL05hENbsrwBYkD63WzRsBClV9mw' 

# 🚨 نام کاربری ربات شما 
BOT_USERNAME = "Chat_Nashnaas_bot" 

# --- تنظیمات سکه‌ها و جوایز ---
CHAT_FEE = 2              # هزینه هر جستجوی هدفمند (هم استانی، همسن و...)
REFERRAL_REWARD = 20      
INITIAL_COINS = 20        

# --- محدودیت‌های زمانی چت ---
GIF_STICKER_BAN_MINUTES = 2 
ENGLISH_WORD_BAN_MINUTES = 3 

# --- شناسه‌های عکس‌های پیش‌فرض و مسیرهای محلی ---
MALE_DEFAULT_PATH = os.path.join("static", "1.png")
FEMALE_DEFAULT_PATH = os.path.join("static", "2.png")
MALE_DEFAULT_PHOTO_ID = None   
FEMALE_DEFAULT_PHOTO_ID = None 

# --- دیتابیس جامع استان‌ها و شهرهای اصلی ایران (شهرستان‌ها) ---
IRANIAN_GEOGRAPHY = {
    'آذربایجان شرقی': ['تبریز', 'مرند', 'مراغه', 'اهر', 'بناب', 'شبستر', 'میانه', 'سایر'],
    'آذربایجان غربی': ['ارومیه', 'خوی', 'مهاباد', 'بوکان', 'پیرانشهر', 'سلماس', 'نقده', 'سایر'],
    'اردبیل': ['اردبیل', 'پارس‌آباد', 'مشگین‌شهر', 'خلخال', 'گرمی', 'نمین', 'سایر'],
    'اصفهان': ['اصفهان', 'کاشان', 'خمینی‌شهر', 'نجف‌آباد', 'شاهین‌شهر', 'شهرضا', 'نطنز', 'سایر'],
    'البرز': ['کرج', 'فردیس', 'نظرآباد', 'ساوجبلاغ', 'طالقان', 'اشتهارد', 'سایر'],
    'ایلام': ['ایلام', 'دهلران', 'آبدانان', 'مهران', 'دره‌شهر', 'ایوان', 'سایر'],
    'بوشهر': ['بوشهر', 'برازجان', 'گناوه', 'کنگان', 'جم', 'عسلویه', 'دیر', 'سایر'],
    'تهران': ['تهران', 'اسلام‌شهر', 'شهریار', 'قدس', 'ملارد', 'رباط‌کریم', 'پردیس', 'دماوند', 'سایر'],
    'چهارمحال و بختیاری': ['شهرکرد', 'بروجن', 'لردگان', 'فارسان', 'کوهرنگ', 'کیار', 'اردل', 'سایر'],
    'خراسان جنوبی': ['بیرجند', 'قاین', 'فردوس', 'طبس', 'نهبندان', 'سربیشه', 'بشرویه', 'سایر'],
    'خراسان رضوی': ['مشهد', 'سبزوار', 'نیشابور', 'تربت حیدریه', 'کاشمر', 'قوچان', 'تربت جام', 'تایباد', 'سایر'],
    'خراسان شمالی': ['بجنورد', 'شیروان', 'اسفراین', 'آشخانه', 'جاجرم', 'مانه و سملقان', 'گرمه', 'سایر'],
    'خوزستان': ['اهواز', 'دزفول', 'آبادان', 'خرمشهر', 'اندیمشک', 'ایذه', 'بهبهان', 'شوشتر', 'سایر'],
    'زنجان': ['زنجان', 'ابهر', 'خرمدره', 'قیدار', 'طارم', 'ماه نشان', 'ایجرود', 'سایر'],
    'سمنان': ['سمنان', 'شاهرود', 'دامغان', 'گرمسار', 'مهدی‌شهر', 'میامی', 'سرخه', 'آرادان', 'سایر'],
    'سیستان و بلوچستان': ['زاهدان', 'چابهار', 'ایرانشهر', 'سراوان', 'زابل', 'کنارک', 'نیک‌شهر', 'خاش', 'سایر'],
    'فارس': ['شیراز', 'مرودشت', 'جهرم', 'فسا', 'کازرون', 'لارستان', 'داراب', 'اقلید', 'آباده', 'سایر'],
    'قزوین': ['قزوین', 'تاکستان', 'الوند', 'آبیک', 'بوئین‌زهرا', 'آوج', 'سایر'],
    'قم': ['قم', 'سایر'],
    'کردستان': ['سنندج', 'سقز', 'مریوان', 'بانه', 'قروه', 'کامیاران', 'دیواندره', 'بیجار', 'سایر'],
    'کرمان': ['کرمان', 'سیرجان', 'رفسنجان', 'جیرفت', 'بم', 'بافت', 'کهنوج', 'زرند', 'سایر'],
    'کرمانشاه': ['کرمانشاه', 'اسلام‌آباد غرب', 'هرسین', 'کنگاور', 'سنقر', 'جوانرود', 'گیلانغرب', 'صحنه', 'سایر'],
    'کهگیلویه و بویراحمد': ['یاسوج', 'گچساران', 'دهدشت', 'لیکک', 'باشت', 'چرام', 'لنده', 'بهمئی', 'سایر'],
    'گلستان': ['گرگان', 'گنبد کاووس', 'علی‌آباد کتول', 'آزادشهر', 'کردکوی', 'بندر ترکمن', 'مینودشت', 'سایر'],
    'گیلان': ['رشت', 'بندر انزلی', 'لاهیجان', 'لنگرود', 'تالش', 'آستانه اشرفیه', 'رودسر', 'صومعه‌سرا', 'سایر'],
    'لرستان': ['خرم‌آباد', 'بروجرد', 'دورود', 'کوهدشت', 'الیگودرز', 'ازنا', 'دلفان', 'سلسله', 'سایر'],
    'مازندران': ['ساری', 'بابل', 'آمل', 'قائم‌شهر', 'بهشهر', 'تنکابن', 'چالوس', 'بابلسر', 'سایر'],
    'مرکزی': ['اراک', 'ساوه', 'خمین', 'محلات', 'دلیجان', 'شازند', 'تفرش', 'آشتیان', 'سایر'],
    'هرمزگان': ['بندرعباس', 'میناب', 'قشم', 'کیش', 'بندر لنگه', 'جاسک', 'رودان', 'حاجی‌آباد', 'سایر'],
    'همدان': ['همدان', 'ملایر', 'نهاوند', 'تویسرکان', 'اسدآباد', 'بهار', 'کبودرآهنگ', 'رزن', 'سایر'],
    'یزد': ['یزد', 'میبد', 'اردکان', 'تفت', 'بافق', 'ابرقو', 'خاتم', 'مهریز', 'سایر'],
}
IRANIAN_PROVINCES = list(IRANIAN_GEOGRAPHY.keys()) 
# ------------------------------------


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- تعاریف وضعیت‌ها (States) ---
MENU, SEARCHING, CHATTING = range(3)
MAIN_MENU_SELECT, CHAT_OPTIONS_SELECT, SEARCH_PEOPLE_SELECT, NEARBY_SELECT = range(3, 7)
EDITING_PROFILE_MENU, EDITING_PROFILE_NAME, EDITING_PROFILE_AGE, EDITING_PROFILE_PROVINCE, EDITING_PROFILE_GENDER, EDITING_PROFILE_CITY = range(7, 13)
GET_MANDATORY_CITY = 13 

# --- وضعیت‌های جدید برای سیستم Matchmaking ---
SELECTING_TARGET_GENDER = 14
DISPLAYING_SEARCH_LIST = 15
WAITING_FOR_CHAT_REQUEST = 16 # کسی که درخواست چت داده
WAITING_FOR_CHAT_RESPONSE = 17 # کسی که منتظر قبول/رد درخواست است

# --- متغیرهای جهانی برای مدیریت صف و اتصال ---
WAITING_QUEUE = []
ACTIVE_CHATS = {} 
CHAT_START_TIMES = {} 
PENDING_REQUESTS = {} # {recipient_id: requester_id, ...}

# --- دکمه‌ها و کیبوردها ---

# کیبورد منوی اصلی
MAIN_MENU_KEYBOARD = [
    ['👤 به ناشناس وصلم کن'], 
    ['🗺️ افراد نزدیک', '🔎 جستجوی کاربران'],
    ['❓ راهنما', '👥 پروفایل من', '💰 سکه‌های من'],
    ['📢 معرفی به دوستان (سکه رایگان)']
]
MENU_MARKUP = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False)

# کیبورد چت 
CHATTING_KEYBOARD = [
    ['❌ پایان چت', '👁️ مشاهده پروفایل']
]
CHATTING_MARKUP = ReplyKeyboardMarkup(CHATTING_KEYBOARD, resize_keyboard=True, one_time_keyboard=False)

# کیبورد تأیید قطع چت (Inline Keyboard)
DISCONNECT_KEYBOARD = [
    [
        InlineKeyboardButton("🛑 پایان چت", callback_data="confirm_disconnect"),
        InlineKeyboardButton("✅ ادامه چت", callback_data="cancel_disconnect")
    ]
]
DISCONNECT_MARKUP = InlineKeyboardMarkup(DISCONNECT_KEYBOARD)

# کیبوردهای کمکی (جدید)
GENDER_MARKUP_MANDATORY = ReplyKeyboardMarkup([['پسر 🧑', 'دختر 👧']], resize_keyboard=True, one_time_keyboard=True)

PROFILE_MENU_KEYBOARD = [
    ['✍️ ویرایش نام', '🎂 ویرایش سن'],
    ['🗺️ ویرایش استان/شهر', '📷 ویرایش عکس پروفایل'],
    ['⬅️ بازگشت به منوی اصلی']
]
PROFILE_MENU_MARKUP = ReplyKeyboardMarkup(PROFILE_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=True)

CHAT_OPTIONS_KEYBOARD = [
    ['🎲 جستجوی شانسی'],
    ['👩 جستجوی دختر', '👨 جستجوی پسر'],
    ['❌ توقف چت / لغو جستجو'],
    ['⬅️ بازگشت به منوی اصلی']
]
CHAT_OPTIONS_MARKUP = ReplyKeyboardMarkup(CHAT_OPTIONS_KEYBOARD, resize_keyboard=True, one_time_keyboard=True)

NEARBY_KEYBOARD = [
    ['5 کیلومتر', '10 کیلومتر', '20 کیلومتر'],
    [KeyboardButton('📍 ارسال موقعیت مکانی فعلی', request_location=True)],
    ['⬅️ بازگشت به منوی اصلی']
]
NEARBY_MARKUP = ReplyKeyboardMarkup(NEARBY_KEYBOARD, resize_keyboard=True, one_time_keyboard=True)


# کیبورد انتخاب جنسیت هدف برای جستجو (Reply Keyboard)
TARGET_GENDER_KEYBOARD = [
    ['پسر 🧑', 'دختر 👧'],
    ['⬅️ بازگشت به منوی اصلی']
]
TARGET_GENDER_MARKUP = ReplyKeyboardMarkup(TARGET_GENDER_KEYBOARD, resize_keyboard=True, one_time_keyboard=True)

# کیبورد جستجوی کاربران
SEARCH_PEOPLE_MARKUP = ReplyKeyboardMarkup([['🏘️ هم استانی‌ها', '🎂 همسن‌ها'], ['🌟 کاربران جدید', '🔇 بدون چت‌ها'], ['⬅️ بازگشت به منوی اصلی']], resize_keyboard=True)


# --- توابع کمکی ---

def contains_link_or_id(text):
    """بررسی می‌کند که آیا متن حاوی لینک، آیدی یا شماره تلفن است."""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    username_pattern = r'@[\w_]{5,}'
    phone_pattern = r'\b(\+98|0)?9\d{9}\b'
    
    if re.search(url_pattern, text) or re.search(username_pattern, text) or re.search(phone_pattern, text):
        return True
    return False

def contains_english(text):
    """بررسی می‌کند که آیا متن حاوی کلمات انگلیسی است."""
    return bool(re.search(r'[a-zA-Z]', text))

def generate_province_markup(is_mandatory: bool, current_state: int) -> InlineKeyboardMarkup:
    """ساخت Inline Keyboard برای انتخاب استان."""
    keyboard = []
    provinces = sorted(list(IRANIAN_GEOGRAPHY.keys()))
    
    for i in range(0, len(provinces), 2):
        row = []
        row.append(InlineKeyboardButton(provinces[i], callback_data=f"prov_sel:{provinces[i]}"))
        if i + 1 < len(provinces):
            row.append(InlineKeyboardButton(provinces[i+1], callback_data=f"prov_sel:{provinces[i+1]}"))
        keyboard.append(row)
        
    if not is_mandatory:
        keyboard.append([InlineKeyboardButton("⬅️ بازگشت به پروفایل", callback_data="profile_back")])

    return InlineKeyboardMarkup(keyboard)

def generate_city_markup(province_name: str, is_mandatory: bool, current_state: int) -> InlineKeyboardMarkup:
    """ساخت Inline Keyboard برای انتخاب شهر بر اساس استان."""
    keyboard = []
    cities = IRANIAN_GEOGRAPHY.get(province_name, [])
    
    for i in range(0, len(cities), 3):
        row = []
        for j in range(3):
            if i + j < len(cities):
                city_name = cities[i+j]
                row.append(InlineKeyboardButton(city_name, callback_data=f"city_sel:{city_name}"))
        if row:
            keyboard.append(row)
            
    keyboard.append([InlineKeyboardButton("❌ انتخاب استان دیگر", callback_data="province_reselect")])
    
    if not is_mandatory:
        keyboard.append([InlineKeyboardButton("⬅️ بازگشت به پروفایل", callback_data="profile_back")])
    
    return InlineKeyboardMarkup(keyboard)

async def check_mandatory_profile(context: ContextTypes.DEFAULT_TYPE) -> bool:
    """بررسی می‌کند که آیا همه فیلدهای اجباری پر شده‌اند."""
    profile = context.user_data.get('profile', {})
    required_fields = ['gender', 'name', 'age', 'province', 'city']
    
    for field in required_fields:
        if profile.get(field) in [None, '[ثبت‌نشده]', '[تنظیم‌نشده]']:
            return False
    return True

async def start_mandatory_profile_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """کاربر را به اولین فیلد اجباری هدایت می‌کند."""
    if 'profile' not in context.user_data:
         context.user_data['profile'] = {
            'name': '[ثبت‌نشده]', 'age': '[تنظیم‌نشده]', 'province': '[تنظیم‌نشده]',
            'city': '[تنظیم‌نشده]', 'location': 'ندارد', 'photo_id': None, 'gender': None 
        }
    
    profile = context.user_data['profile']
    
    # اطمینان از خروج از حالت‌های Matchmaking هنگام شروع
    user_id = update.effective_user.id
    if user_id in PENDING_REQUESTS: 
        del PENDING_REQUESTS[user_id]
        
    if profile['gender'] is None:
        await context.bot.send_message(user_id, "👋 خوش آمدید!\nبرای شروع چت ناشناس، ابتدا باید **جنسیت** خود را ثبت کنید (اجباری):", reply_markup=GENDER_MARKUP_MANDATORY, parse_mode='Markdown')
        return EDITING_PROFILE_GENDER 
    
    if profile['name'] in [None, '[ثبت‌نشده]']:
        await context.bot.send_message(user_id, "لطفاً **نام** (یا نام مستعار) خود را وارد کنید (اجباری):", reply_markup=ReplyKeyboardRemove())
        return EDITING_PROFILE_NAME 

    if profile['age'] in [None, '[تنظیم‌نشده]']:
        await context.bot.send_message(user_id, "لطفاً **سن** خود را به صورت عدد وارد کنید (اجباری - بین ۹ تا ۶۰ سال):", reply_markup=ReplyKeyboardRemove())
        return EDITING_PROFILE_AGE 

    if profile['province'] in [None, '[تنظیم‌نشده]']:
        await context.bot.send_message(user_id, "لطفاً **استان** خود را از لیست انتخاب کنید (اجباری):", reply_markup=generate_province_markup(is_mandatory=True, current_state=EDITING_PROFILE_PROVINCE), parse_mode='Markdown')
        return EDITING_PROFILE_PROVINCE
        
    if profile['city'] in [None, '[تنظیم‌نشده]']:
        context.user_data['temp_province'] = profile['province']
        await context.bot.send_message(user_id, f"استان شما **{profile['province']}** ثبت شد.\nلطفاً **شهر** خود را از لیست انتخاب کنید (اجباری):", reply_markup=generate_city_markup(profile['province'], is_mandatory=True, current_state=GET_MANDATORY_CITY), parse_mode='Markdown')
        return GET_MANDATORY_CITY
    
    return await go_to_main_menu(update, context)

async def go_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """کاربر را به منوی اصلی هدایت می‌کند."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name if update.effective_user else "کاربر"

    if user_id in ACTIVE_CHATS: await disconnect_users(user_id, context)
    if user_id in WAITING_QUEUE: WAITING_QUEUE.remove(user_id)
    if user_id in PENDING_REQUESTS: del PENDING_REQUESTS[user_id]
    
    # 💰 پاک کردن هرگونه هزینه در انتظار در صورت بازگشت به منو
    context.user_data.pop('pending_fee', None)

    try:
        await context.bot.send_message(user_id, f"سلام {user_name}! 👋\nبه منوی اصلی خوش آمدید.", reply_markup=MENU_MARKUP)
    except Exception:
        await update.message.reply_text(f"سلام {user_name}! 👋\nبه منوی اصلی خوش آمدید.", reply_markup=MENU_MARKUP)
        
    return MAIN_MENU_SELECT


async def edit_message_safely(query: CallbackQuery, new_text: str, new_markup: Union[InlineKeyboardMarkup, None]):
    """تابع کمکی برای ویرایش امن پیام‌های حاوی عکس یا متن."""
    try:
        if query.message.photo or query.message.animation or query.message.video_note:
            # اگر پیام اصلی عکس، گیف یا پیام ویدیویی باشد، کپشن ویرایش شود
            await query.edit_message_caption(caption=new_text, reply_markup=new_markup, parse_mode='Markdown')
        else:
            # اگر پیام اصلی متن باشد، متن آن ویرایش می‌شود
            await query.edit_message_text(new_text, reply_markup=new_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"خطا در ویرایش پیام توسط CallbackQuery: {e}")
        # در صورت شکست ویرایش، می‌توان یک پیام جدید ارسال کرد
        await query.message.reply_text(new_text, reply_markup=new_markup, parse_mode='Markdown')


async def display_profile(user_id: int, profile: dict, context: ContextTypes.DEFAULT_TYPE, chat_id_to_send: int, show_request_button: bool = False, custom_caption: str = None):
    """تابع کمکی برای نمایش پروفایل."""
    global MALE_DEFAULT_PHOTO_ID, FEMALE_DEFAULT_PHOTO_ID
    
    gender = profile.get('gender', '[تنظیم‌نشده]')
    
    profile_info = (
        custom_caption if custom_caption else "👤 **پروفایل**\n"
        "--------------------------------------\n"
        f"  جنسیت: {gender}\n" 
        f"  نام: {profile.get('name', '[ثبت‌نشده]')}\n"
        f"  سن: {profile.get('age', '[تنظیم‌نشده]')}\n"
        f"  استان: {profile.get('province', '[تنظیم‌نشده]')}\n"
        f"  شهر: {profile.get('city', '[تنظیم‌نشده]')}\n" 
        "--------------------------------------\n"
    )
    
    photo_to_send = profile.get('photo_id')
    photo_is_local_file = False
    
    if not photo_to_send:
        if gender == 'پسر':
            if MALE_DEFAULT_PHOTO_ID: photo_to_send = MALE_DEFAULT_PHOTO_ID
            else: photo_to_send = MALE_DEFAULT_PATH; photo_is_local_file = True
        elif gender == 'دختر':
            if FEMALE_DEFAULT_PHOTO_ID: photo_to_send = FEMALE_DEFAULT_PHOTO_ID
            else: photo_to_send = FEMALE_DEFAULT_PATH; photo_is_local_file = True
    
    reply_markup = None
    if show_request_button:
        target_user_id = user_id 
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("💌 درخواست چت", callback_data=f"request_chat:{target_user_id}")]])
        
    if photo_to_send:
        try:
            if photo_is_local_file:
                with open(photo_to_send, 'rb') as photo_file:
                    message = await context.bot.send_photo(
                        chat_id=chat_id_to_send, photo=photo_file, caption=profile_info, parse_mode='Markdown', reply_markup=reply_markup
                    )
                new_file_id = message.photo[-1].file_id
                if gender == 'پسر': MALE_DEFAULT_PHOTO_ID = new_file_id
                elif gender == 'دختر': FEMALE_DEFAULT_PHOTO_ID = new_file_id
            else:
                await context.bot.send_photo(
                    chat_id=chat_id_to_send, photo=photo_to_send, caption=profile_info, parse_mode='Markdown', reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"خطا در ارسال عکس پروفایل: {e}")
            await context.bot.send_message(chat_id=chat_id_to_send, text=profile_info, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=chat_id_to_send, text=profile_info, parse_mode='Markdown', reply_markup=reply_markup)


async def display_profile_and_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تابع نمایش پروفایل و منوی ویرایش."""
    user_id = update.effective_user.id
    if 'profile' not in context.user_data:
        await context.bot.send_message(user_id, "در حال بارگیری پروفایل...", reply_markup=ReplyKeyboardRemove())
        return await start_mandatory_profile_setup(update, context) 
        
    profile = context.user_data['profile']
    
    await display_profile(user_id, profile, context, user_id, show_request_button=False, 
                          custom_caption="👤 **پروفایل شما**\n--------------------------------------\n")
    
    await context.bot.send_message(user_id, "برای ویرایش، گزینه‌ی زیر را انتخاب کنید:", reply_markup=PROFILE_MENU_MARKUP)
        
    return EDITING_PROFILE_MENU


async def display_partner_profile(user_id: int, partner_id: int, context: ContextTypes.DEFAULT_TYPE, show_request_button: bool = False):
    """نمایش مشخصات شریک چت (یا کاربر جستجو شده) به یک کاربر دیگر."""
    # اصلاح شده: استفاده از context.application.user_data برای دسترسی به دیتای کاربران دیگر
    partner_profile = context.application.user_data.get(partner_id, {}).get('profile', {})
    
    custom_caption = "🔥 **مشخصات شریک چت** 🔥\n" if not show_request_button else "👀 **مشاهده پروفایل**\n"
    
    await display_profile(partner_id, partner_profile, context, user_id, 
                          show_request_button=show_request_button, 
                          custom_caption=custom_caption)


async def connect_users(user1_id: int, user2_id: int, context: ContextTypes.DEFAULT_TYPE):
    """دو کاربر را به هم متصل کرده و وضعیت چت را آغاز می‌کند."""
    ACTIVE_CHATS[user1_id] = user2_id
    ACTIVE_CHATS[user2_id] = user1_id
    CHAT_START_TIMES[user1_id] = datetime.now()
    CHAT_START_TIMES[user2_id] = datetime.now()
    
    if user1_id in WAITING_QUEUE: WAITING_QUEUE.remove(user1_id)
    if user2_id in WAITING_QUEUE: WAITING_QUEUE.remove(user2_id)
    
    if user1_id in PENDING_REQUESTS: del PENDING_REQUESTS[user1_id]
    if user2_id in PENDING_REQUESTS: del PENDING_REQUESTS[user2_id]
    
    # 💰 منطق کسر سکه برای جستجوی ساده پولی (اینجا فقط یکی از دو کاربر باید pending_fee داشته باشد)
    user1_context = context.application.user_data.get(user1_id)
    user2_context = context.application.user_data.get(user2_id)
    
    if user1_context and 'pending_fee' in user1_context:
        fee = user1_context.pop('pending_fee')
        user1_context['coins'] -= fee
        await context.bot.send_message(user1_id, f"✅ **{fee} سکه** برای اتصال کسر شد. موجودی جدید: **{user1_context['coins']} سکه**.", parse_mode='Markdown')
        
    if user2_context and 'pending_fee' in user2_context:
        fee = user2_context.pop('pending_fee')
        user2_context['coins'] -= fee
        await context.bot.send_message(user2_id, f"✅ **{fee} سکه** برای اتصال کسر شد. موجودی جدید: **{user2_context['coins']} سکه**.", parse_mode='Markdown')
    
    
    await display_partner_profile(user1_id, user2_id, context)
    await display_partner_profile(user2_id, user1_id, context)
    
    chat_message = "🎉 با موفقیت به یک کاربر جدید متصل شدید! چت را شروع کنید.\n\n⚠️ **تذکر مهم:** ارسال گیف/استیکر تا ۲ دقیقه و استفاده از الفاظ انگلیسی تا ۳ دقیقه ممنوع است."
    await context.bot.send_message(chat_id=user1_id, text=chat_message, reply_markup=CHATTING_MARKUP)
    await context.bot.send_message(chat_id=user2_id, text=chat_message, reply_markup=CHATTING_MARKUP)
    
    logger.info(f"اتصال جدید: {user1_id} و {user2_id}.")
    
# --- منطق جستجوی شانسی (قدیمی) ---
async def find_partner_and_connect(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """جستجوی جفت در صف انتظار و برقراری اتصال در صورت وجود."""
    potential_partners = [uid for uid in WAITING_QUEUE if uid != user_id]
    if potential_partners:
        partner_id = random.choice(potential_partners)
        await connect_users(user_id, partner_id, context)
        return partner_id
    return None

async def disconnect_users(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    """کاربر را از چت جدا کرده و او و جفتش را به منوی اصلی برمی‌گرداند."""
    partner_id = ACTIVE_CHATS.pop(user_id, None)
    CHAT_START_TIMES.pop(user_id, None)
    
    await context.bot.send_message(chat_id=user_id, text="❌ چت متوقف شد. برای شروع دوباره، از منوی زیر استفاده کنید.", reply_markup=MENU_MARKUP)
    
    if partner_id and partner_id in ACTIVE_CHATS:
        ACTIVE_CHATS.pop(partner_id, None) 
        CHAT_START_TIMES.pop(partner_id, None)
        await context.bot.send_message(chat_id=partner_id, text="🚨 کاربر مقابل چت را ترک کرد. برای شروع دوباره، از منوی زیر استفاده کنید.", reply_markup=MENU_MARKUP)
        logger.info(f"قطع اتصال بین: {user_id} و {partner_id}")
    return MAIN_MENU_SELECT 

# --- هندلرهای اصلی ---

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """نقطه ورود."""
    user_id = update.effective_user.id
    
    is_new_user = 'coins' not in context.user_data
    is_new_user_profile = 'profile' not in context.user_data
    
    if is_new_user:
        context.user_data['coins'] = INITIAL_COINS
        # منطق ارجاع (Referral)
        if context.args and context.args[0].isdigit():
            referrer_id = int(context.args[0])
            if referrer_id != user_id and 'referred' not in context.user_data:
                context.user_data['referred'] = True
                # استفاده صحیح از context.application.user_data
                referrer_data = context.application.user_data.get(referrer_id)
                if referrer_data:
                    referrer_data['coins'] = referrer_data.get('coins', 0) + REFERRAL_REWARD
                    try:
                        await context.bot.send_message(referrer_id, f"🎁 تبریک! دوست شما چت ناشناس را با لینک شما شروع کرد و **{REFERRAL_REWARD} سکه** به حساب شما افزوده شد. موجودی جدید: **{referrer_data['coins']} سکه**.", parse_mode='Markdown')
                    except Exception as e:
                        logger.error(f"خطا در ارسال جایزه ارجاع به {referrer_id}: {e}")
                        
    if is_new_user_profile or not await check_mandatory_profile(context):
        if update.message:
            return await start_mandatory_profile_setup(update, context)
        await context.bot.send_message(user_id, "لطفاً برای شروع پروفایل خود را تکمیل کنید.")
        return await start_mandatory_profile_setup(update, context)

    return await go_to_main_menu(update, context) 

async def menu_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """هندلر فرمان /menu برای بازگشت سریع به منوی اصلی."""
    return await go_to_main_menu(update, context)


async def main_menu_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت انتخاب‌های منوی اصلی."""
    
    if not await check_mandatory_profile(context):
        await update.message.reply_text("⛔️ ابتدا باید پروفایل خود را تکمیل کنید.", reply_markup=ReplyKeyboardRemove())
        return await start_mandatory_profile_setup(update, context)
    
    user_message = update.message.text
    user_id = update.effective_user.id
    
    if user_message == '👤 به ناشناس وصلم کن':
        await update.message.reply_text("حالت مورد نظر برای اتصال ناشناس را انتخاب کنید:", reply_markup=CHAT_OPTIONS_MARKUP)
        return CHAT_OPTIONS_SELECT
    elif user_message == '🔎 جستجوی کاربران':
        await update.message.reply_text("چه کسانی رو نشونت بدم؟ امتحان کن ⬇️", reply_markup=SEARCH_PEOPLE_MARKUP)
        return SEARCH_PEOPLE_SELECT
    elif user_message == '🗺️ افراد نزدیک':
        await update.message.reply_text("محدوده مورد نظر بر حسب کیلومتر را انتخاب کنید:", reply_markup=NEARBY_MARKUP)
        return NEARBY_SELECT
    elif user_message == '👥 پروفایل من':
        return await display_profile_and_menu(update, context) 
        
    elif user_message == '💰 سکه‌های من':
        coins = context.user_data.get('coins', 0)
        await update.message.reply_text(f"💳 موجودی سکه‌های شما: **{coins} سکه**.", reply_markup=MENU_MARKUP, parse_mode='Markdown')
        return MAIN_MENU_SELECT
        
    elif user_message == '📢 معرفی به دوستان (سکه رایگان)':
        referral_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        message_text = (
            "📢 <b>معرفی و کسب سکه رایگان</b> 🎁\n\n"
            f"با دعوت هر دوست، دوست شما <b>{INITIAL_COINS} سکه</b> هدیه می‌گیرد و شما <b>{REFERRAL_REWARD} سکه</b> جایزه می‌گیرید!\n\n"
            "لینک اختصاصی شما:\n"
            f"<code>{referral_link}</code>\n\n"
            "همین الان این پیام رو برای دوستات بفرست:\n\n"
            "<b>متن دعوت:</b>\n"
            "چت کده هستم! با من میتونی افراد نزدیک یا همسن خودت رو پیدا کنی و به صورت ناشناس چت کنی. همین الان رو لینک زیر کلیک کن:\n"
            f"{referral_link}"
        )
        await update.message.reply_text(message_text, parse_mode='HTML', reply_markup=MENU_MARKUP)
        return MAIN_MENU_SELECT

    elif user_message == '❓ راهنما':
        GUIDE_TEXT = (
            "راهنمای استفاده از ربات ❓\n"
            "1. **به ناشناس وصلم کن:** سریع‌ترین راه برای چت ناشناس. جستجوی شانسی رایگان است.\n"
            "2. **جستجوی کاربران:** فیلترهای هدفمند (هم‌استانی/همسن) با هزینه **۲ سکه** که **پس از اتصال موفق** کسر می‌شود. پس از پیدا شدن لیست، می‌توانید درخواست چت دهید.\n"
            "3. **محدودیت‌های چت:** ارسال لینک، آیدی و شماره تماس ممنوع است. همچنین ارسال گیف و استیکر در ۲ دقیقه اول و کلمات انگلیسی در ۳ دقیقه اول چت مجاز نیست.\n"
            "4. **کسب سکه:** از طریق معرفی دوستان (📢) می‌توانید سکه رایگان دریافت کنید."
        )
        await update.message.reply_text(GUIDE_TEXT, reply_markup=MENU_MARKUP, parse_mode='Markdown')
        return MAIN_MENU_SELECT
        
    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود در منو استفاده کنید.", reply_markup=MENU_MARKUP)
        return MAIN_MENU_SELECT


async def chat_options_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت جستجوهای شانسی، دختر و پسر (با کسر سکه در صورت اتصال موفق)."""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if user_message == '⬅️ بازگشت به منوی اصلی':
        await update.message.reply_text("به منوی اصلی بازگشتید.", reply_markup=MENU_MARKUP)
        return MAIN_MENU_SELECT
    
    elif user_message == '🎲 جستجوی شانسی':
        # رایگان، بدون کسر سکه
        if user_id not in WAITING_QUEUE: WAITING_QUEUE.append(user_id)
        partner_id = await find_partner_and_connect(user_id, context)
        if partner_id: 
            return CHATTING
        else:
            await update.message.reply_text("⏳ در حال جستجوی جفت... برای لغو، **❌ توقف چت / لغو جستجو** را بزنید.", reply_markup=ReplyKeyboardRemove())
            return SEARCHING 
            
    elif user_message in ['👩 جستجوی دختر', '👨 جستجوی پسر']:
        current_coins = context.user_data.get('coins', 0)
        
        if current_coins < CHAT_FEE:
            await update.message.reply_text(f"❌ موجودی سکه شما کافی نیست! برای این نوع جستجو به **{CHAT_FEE} سکه** نیاز دارید. موجودی فعلی شما: **{current_coins} سکه**.", reply_markup=CHAT_OPTIONS_MARKUP, parse_mode='Markdown')
            return CHAT_OPTIONS_SELECT
            
        # 🟢 تغییر: سکه کسر نمی‌شود، پرچم هزینه در انتظار تنظیم می‌شود
        context.user_data['pending_fee'] = CHAT_FEE
        
        await update.message.reply_text(f"⏳ در حال جستجوی جفت با فیلتر **{user_message}**... لطفاً صبر کنید.\n"
                                        f"**توجه:** هزینه **{CHAT_FEE} سکه** پس از اتصال کسر خواهد شد.\nبرای لغو، /cancel را بزنید.", 
                                        reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')

        if user_id not in WAITING_QUEUE: WAITING_QUEUE.append(user_id)
        partner_id = await find_partner_and_connect(user_id, context)
        
        if partner_id: 
            # connect_users، کسر سکه را انجام می‌دهد
            return CHATTING
        else:
            # اگر در صف قرار گرفت، در SEARCHING می‌ماند و در صورت لغو، pending_fee پاک می‌شود.
            return SEARCHING 

    elif user_message == '❌ توقف چت / لغو جستجو':
        if user_id in WAITING_QUEUE: WAITING_QUEUE.remove(user_id)
        # 💰 پاک کردن پرچم هزینه در انتظار
        context.user_data.pop('pending_fee', None)
        await update.message.reply_text("شما نه در چت هستید و نه در صف انتظار. به منوی اصلی بازگشتید.", reply_markup=MENU_MARKUP)
        return MAIN_MENU_SELECT
    
    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود در منوی اتصال به ناشناس استفاده کنید:", reply_markup=CHAT_OPTIONS_MARKUP)
        return CHAT_OPTIONS_SELECT

async def search_people_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت انتخاب‌های جستجوی هدفمند (شروع Matchmaking)."""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    if user_message == '⬅️ بازگشت به منوی اصلی':
        await update.message.reply_text("به منوی اصلی بازگشتید.", reply_markup=MENU_MARKUP)
        return MAIN_MENU_SELECT
    
    elif user_message == '🏘️ هم استانی‌ها':
        current_coins = context.user_data.get('coins', 0)
        if current_coins < CHAT_FEE:
            await update.message.reply_text(f"❌ موجودی سکه شما کافی نیست! برای جستجوی هم استانی به **{CHAT_FEE} سکه** نیاز دارید. موجودی فعلی شما: **{current_coins} سکه**.", reply_markup=SEARCH_PEOPLE_MARKUP, parse_mode='Markdown')
            return SEARCH_PEOPLE_SELECT
            
        # 🟢 تغییر: سکه کسر نمی‌شود، پرچم هزینه در انتظار تنظیم می‌شود
        context.user_data['pending_fee'] = CHAT_FEE
        context.user_data['search_type'] = 'province'
        
        await update.message.reply_text(f"لطفاً جنسیت فردی را که می‌خواهید با او چت کنید، انتخاب کنید:\n"
                                        f"**توجه:** هزینه **{CHAT_FEE} سکه** پس از قبول درخواست چت توسط طرف مقابل کسر خواهد شد.", 
                                        reply_markup=TARGET_GENDER_MARKUP, parse_mode='Markdown')
        
        return SELECTING_TARGET_GENDER
    
    # 🎂 همسن‌ها، 🌟 کاربران جدید، 🔇 بدون چت‌ها (رفتار مشابه جستجوی ساده پولی)
    elif user_message in ['🎂 همسن‌ها', '🌟 کاربران جدید', '🔇 بدون چت‌ها']:
        current_coins = context.user_data.get('coins', 0)
        if current_coins < CHAT_FEE:
            await update.message.reply_text(f"❌ موجودی سکه شما کافی نیست! برای این نوع جستجو به **{CHAT_FEE} سکه** نیاز دارید. موجودی فعلی شما: **{current_coins} سکه**.", reply_markup=SEARCH_PEOPLE_MARKUP, parse_mode='Markdown')
            return SEARCH_PEOPLE_SELECT
            
        # 🟢 تغییر: سکه کسر نمی‌شود، پرچم هزینه در انتظار تنظیم می‌شود
        context.user_data['pending_fee'] = CHAT_FEE
        
        await update.message.reply_text(f"⏳ در حال جستجوی جفت با فیلتر **{user_message}**... لطفاً صبر کنید.\n"
                                        f"**توجه:** هزینه **{CHAT_FEE} سکه** پس از اتصال کسر خواهد شد.\nبرای لغو، /cancel را بزنید.", 
                                        reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
        if user_id not in WAITING_QUEUE: WAITING_QUEUE.append(user_id)
        
        partner_id = await find_partner_and_connect(user_id, context)
        
        if partner_id: 
            # connect_users، کسر سکه را انجام می‌دهد
            return CHATTING
        else:
            return SEARCHING
    
    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود در منوی جستجوی کاربران استفاده کنید:", reply_markup=SEARCH_PEOPLE_MARKUP)
        return SEARCH_PEOPLE_SELECT


def get_available_users(context: ContextTypes.DEFAULT_TYPE, user_id: int, province: str, target_gender: str) -> list[int]:
    """لیست کاربرانی که آنلاین، موجود و منطبق با فیلتر هستند را برمی‌گرداند."""
    
    available_users = []
    
    # استفاده صحیح از context.application.user_data
    for uid, data in context.application.user_data.items(): 
        if uid == user_id: continue
        # بررسی وضعیت آنلاین بودن (درگیر چت یا انتظار نباشد)
        if uid in ACTIVE_CHATS: continue
        if uid in WAITING_QUEUE: continue
        if uid in PENDING_REQUESTS: continue 
        
        profile = data.get('profile')
        if not profile: continue 

        # فیلتر هم‌استانی و جنسیت
        if profile.get('province') == province and profile.get('gender') == target_gender:
            available_users.append(uid)
            
    return available_users


def generate_search_list_markup(user_ids: list[int], context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    """ساخت Inline Keyboard برای نمایش لیست کاربران پیدا شده."""
    keyboard = []
    
    # حداکثر ۵ کاربر نمایش داده شود
    users_to_show = user_ids[:5]
    
    for uid in users_to_show:
        # استفاده صحیح از context.application.user_data
        profile = context.application.user_data.get(uid, {}).get('profile', {})
        name = profile.get('name', 'ناشناس')
        age = profile.get('age', '؟')
        city = profile.get('city', '؟')
        
        button_text = f"👁️ {name} ({age}) از {city}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_prof:{uid}")])
        
    keyboard.append([InlineKeyboardButton("❌ لغو جستجو و بازگشت", callback_data="cancel_search")])
    
    return InlineKeyboardMarkup(keyboard)


async def get_target_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت جنسیت مورد نظر برای جستجو و نمایش لیست."""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    if user_message == '⬅️ بازگشت به منوی اصلی':
        # 🟢 تغییر: فقط پرچم هزینه پاک می‌شود، چون هنوز سکه‌ای کسر نشده.
        if context.user_data.pop('pending_fee', 0) > 0:
             await update.message.reply_text(f"✅ جستجوی هدفمند لغو شد. سکه‌ای کسر نشده است.", parse_mode='Markdown')
        return await go_to_main_menu(update, context)

    if user_message in ['پسر 🧑', 'دختر 👧']:
        target_gender = 'پسر' if user_message == 'پسر 🧑' else 'دختر'
        
        user_profile = context.user_data['profile']
        province = user_profile['province']
        
        found_users = get_available_users(context, user_id, province, target_gender)
        
        if not found_users:
            # 🟢 تغییر: فقط پرچم هزینه پاک می‌شود، چون هنوز سکه‌ای کسر نشده.
            context.user_data.pop('pending_fee', None) 
            
            await update.message.reply_text(f"😔 متأسفانه در استان شما، کاربر **{target_gender}** با مشخصات مورد نظر در دسترس نبود.\n"
                                            f"✅ جستجو لغو شد. سکه‌ای کسر نشده است.", 
                                            reply_markup=MENU_MARKUP, parse_mode='Markdown')
            return MAIN_MENU_SELECT
            
        context.user_data['search_results'] = found_users
        
        await update.message.reply_text(f"🥳 **{len(found_users)}** نفر **{target_gender}** هم‌استانی شما پیدا شد. (فقط ۵ نفر نمایش داده می‌شوند)\n"
                                        "برای مشاهده پروفایل و ارسال درخواست چت، روی دکمه کلیک کنید:",
                                        reply_markup=generate_search_list_markup(found_users, context))
        
        return DISPLAYING_SEARCH_LIST
    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود استفاده کنید:", reply_markup=TARGET_GENDER_MARKUP)
        return SELECTING_TARGET_GENDER


async def matchmaking_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت تمامی Callbackهای سیستم Matchmaking: مشاهده، درخواست، قبول و رد."""
    query = update.callback_query
    await query.answer() 
    
    data = query.data
    user_id = query.from_user.id
    
    # 1. لغو جستجو (از لیست جستجو)
    if data == 'cancel_search':
        # 🟢 تغییر: پاک کردن پرچم هزینه در انتظار
        context.user_data.pop('pending_fee', None)
        await edit_message_safely(query, "❌ جستجو لغو شد. به منوی اصلی بازگشتید.", None)
        await context.bot.send_message(user_id, "منوی اصلی:", reply_markup=MENU_MARKUP)
        return MAIN_MENU_SELECT
        
    # 2. مشاهده پروفایل (در لیست جستجو)
    if data.startswith('view_prof:'):
        target_id = int(data.split(':')[1])
        
        await edit_message_safely(query, "⏳ در حال بارگیری پروفایل...", None)
        await display_partner_profile(user_id, target_id, context, show_request_button=True)
        
        await context.bot.send_message(user_id, "برای بازگشت به منو اصلی یا لیست، /menu را بزنید. یا درخواست چت دهید.", reply_markup=ReplyKeyboardRemove())
        
        context.user_data['target_user_id'] = target_id
        return WAITING_FOR_CHAT_REQUEST 
        
    # 3. ارسال درخواست چت (از صفحه مشاهده پروفایل)
    elif data.startswith('request_chat:'):
        target_id = int(data.split(':')[1])
        requester_id = user_id
        
        if target_id in ACTIVE_CHATS or target_id in WAITING_QUEUE or target_id in PENDING_REQUESTS:
            await edit_message_safely(query, "❌ کاربر مورد نظر در حال حاضر در دسترس نیست یا درگیر چت دیگری است.", None)
            await context.bot.send_message(requester_id, "منوی اصلی:", reply_markup=MENU_MARKUP)
            return MAIN_MENU_SELECT
            
        PENDING_REQUESTS[target_id] = requester_id
        
        requester_profile = context.user_data['profile']
        response_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ قبول چت", callback_data=f"accept_chat:{requester_id}")],
            [InlineKeyboardButton("❌ رد چت", callback_data=f"reject_chat:{requester_id}")]
        ])
        
        # نمایش پروفایل درخواست‌دهنده به فرد هدف
        await display_profile(requester_id, requester_profile, context, target_id, 
                              custom_caption="🔔 **درخواست چت جدید!**\n\nاین شخص می‌خواهد با شما چت کند. مشخصات او را مشاهده کنید و تصمیم بگیرید:", 
                              show_request_button=False)

        await context.bot.send_message(target_id, "چه می‌کنید؟", reply_markup=response_markup)
        
        # 🟢 رفع خطا: ویرایش امن پیام حاوی عکس یا متن
        await edit_message_safely(query, f"✅ درخواست چت برای کاربر ارسال شد. منتظر پاسخ او بمانید...\n"
                                      "برای لغو درخواست، /menu را بزنید.", None)
                                      
        return WAITING_FOR_CHAT_RESPONSE
        
    # 4. قبول درخواست
    elif data.startswith('accept_chat:'):
        requester_id = int(data.split(':')[1])
        recipient_id = user_id
        
        if PENDING_REQUESTS.get(recipient_id) == requester_id:
            del PENDING_REQUESTS[recipient_id]
            
            # 🟢 تغییر: کسر سکه از درخواست‌دهنده (Requester) در لحظه قبول شدن درخواست
            requester_context = context.application.user_data.get(requester_id)
            if requester_context and 'pending_fee' in requester_context:
                 fee = requester_context.pop('pending_fee')
                 requester_context['coins'] -= fee
                 await context.bot.send_message(requester_id, f"✅ **{fee} سکه** برای اتصال کسر شد. موجودی جدید: **{requester_context['coins']} سکه**.", parse_mode='Markdown')
            
            # 🟢 رفع خطا: ویرایش امن پیام
            await edit_message_safely(query, "✅ درخواست قبول شد. در حال اتصال...", None)
            await context.bot.send_message(requester_id, "🎉 کاربر مقابل درخواست شما را قبول کرد. در حال اتصال...", reply_markup=ReplyKeyboardRemove())
            
            await connect_users(requester_id, recipient_id, context)
            return CHATTING 
        else:
            # 🟢 رفع خطا: ویرایش امن پیام
            await edit_message_safely(query, "❌ اعتبار درخواست به پایان رسیده یا قبلاً پاسخ داده شده است.", None)
            await context.bot.send_message(recipient_id, "منوی اصلی:", reply_markup=MENU_MARKUP)
            return MAIN_MENU_SELECT
            
    # 5. رد درخواست
    elif data.startswith('reject_chat:'):
        requester_id = int(data.split(':')[1])
        recipient_id = user_id
        
        if PENDING_REQUESTS.get(recipient_id) == requester_id:
            del PENDING_REQUESTS[recipient_id]
            
            # 💰 پاک کردن پرچم هزینه در انتظار از درخواست‌دهنده (چون سکه‌ای کسر نشده است)
            requester_context = context.application.user_data.get(requester_id)
            if requester_context:
                requester_context.pop('pending_fee', None)
            
            # 🟢 رفع خطا: ویرایش امن پیام
            await edit_message_safely(query, "❌ درخواست رد شد. به منوی اصلی بازگشتید.", None)
            await context.bot.send_message(requester_id, "😔 متأسفانه کاربر مقابل درخواست چت شما را رد کرد. به منوی اصلی بازگشتید.", reply_markup=MENU_MARKUP)
            
            await context.bot.send_message(recipient_id, "منوی اصلی:", reply_markup=MENU_MARKUP)
            
            return MAIN_MENU_SELECT
            
        else:
            # 🟢 رفع خطا: ویرایش امن پیام
            await edit_message_safely(query, "❌ اعتبار درخواست به پایان رسیده یا قبلاً پاسخ داده شده است.", None)
            await context.bot.send_message(recipient_id, "منوی اصلی:", reply_markup=MENU_MARKUP)
            return MAIN_MENU_SELECT
    
    return await geography_callback_handler(update, context)

# --- هندلرهای ویرایش پروفایل ---
# ... (توابع ویرایش پروفایل بدون تغییر باقی می‌مانند) ...

async def get_mandatory_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت جنسیت اجباری."""
    gender = update.message.text.split(' ')[0] 
    if gender not in ['پسر', 'دختر']:
        await update.message.reply_text("❌ لطفاً جنسیت خود را از دکمه‌ها انتخاب کنید.")
        return EDITING_PROFILE_GENDER
        
    context.user_data['profile']['gender'] = gender
    await update.message.reply_text(f"✅ جنسیت شما **{gender}** ثبت شد.", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    
    await update.message.reply_text("لطفاً **نام** (یا نام مستعار) خود را وارد کنید (اجباری):", reply_markup=ReplyKeyboardRemove())
    return EDITING_PROFILE_NAME 

async def get_mandatory_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت نام اجباری/ویرایش نام."""
    name = update.message.text.strip()
    if not name or len(name) < 2 or len(name) > 30:
        await update.message.reply_text("❌ نام معتبر نیست. لطفاً یک نام یا نام مستعار (بین ۲ تا ۳۰ کاراکتر) وارد کنید.")
        return EDITING_PROFILE_NAME

    context.user_data['profile']['name'] = name
    await update.message.reply_text(f"✅ نام شما **{name}** ثبت شد.", parse_mode='Markdown')
    
    # تعیین گام بعدی
    if context.user_data['profile']['age'] in [None, '[تنظیم‌نشده]']:
        await update.message.reply_text("لطفاً **سن** خود را به صورت عدد وارد کنید (اجباری - بین ۹ تا ۶۰ سال):", reply_markup=ReplyKeyboardRemove())
        return EDITING_PROFILE_AGE
    else:
        return await display_profile_and_menu(update, context)

async def get_mandatory_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت سن اجباری/ویرایش سن."""
    try:
        age = int(update.message.text.strip())
        if not (9 <= age <= 60):
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ سن باید یک عدد صحیح بین ۹ تا ۶۰ باشد. لطفاً دوباره وارد کنید.")
        return EDITING_PROFILE_AGE
        
    context.user_data['profile']['age'] = age
    await update.message.reply_text(f"✅ سن شما **{age}** سال ثبت شد.", parse_mode='Markdown')
    
    # تعیین گام بعدی
    if context.user_data['profile']['province'] in [None, '[تنظیم‌نشده]']:
        await update.message.reply_text("لطفاً **استان** خود را از لیست انتخاب کنید (اجباری):", 
                                        reply_markup=generate_province_markup(is_mandatory=True, current_state=EDITING_PROFILE_PROVINCE), parse_mode='Markdown')
        return EDITING_PROFILE_PROVINCE
    else:
        return await display_profile_and_menu(update, context)

async def geography_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت انتخاب استان و شهر با دکمه‌های شیشه‌ای."""
    query = update.callback_query
    await query.answer() 
    
    data = query.data
    user_id = query.from_user.id
    
    if data == 'profile_back':
        await edit_message_safely(query, "بازگشت به منوی پروفایل.", None)
        await context.bot.send_message(user_id, "منوی پروفایل:", reply_markup=PROFILE_MENU_MARKUP)
        return EDITING_PROFILE_MENU

    if data.startswith('prov_sel:'):
        province = data.split(':')[1]
        is_mandatory = (context.user_data['profile']['province'] in [None, '[تنظیم‌نشده]'])
        
        context.user_data['temp_province'] = province
        
        await edit_message_safely(query, f"✅ استان شما **{province}** انتخاب شد.\n\nلطفاً **شهر** خود را از لیست انتخاب کنید:", 
                                      generate_city_markup(province, is_mandatory, GET_MANDATORY_CITY))
        
        return GET_MANDATORY_CITY 
            
    elif data.startswith('city_sel:'):
        city = data.split(':')[1]
        province = context.user_data.get('temp_province')
        
        context.user_data['profile']['province'] = province
        context.user_data['profile']['city'] = city
        
        await edit_message_safely(query, f"✅ شهر شما **{city}** از استان **{province}** با موفقیت ثبت شد.", None)
        
        # تعیین گام بعدی
        if not await check_mandatory_profile(context):
            return await start_mandatory_profile_setup(update, context)
        else:
            await context.bot.send_message(user_id, "منوی پروفایل:", reply_markup=PROFILE_MENU_MARKUP)
            return EDITING_PROFILE_MENU
            
    elif data == 'province_reselect':
        is_mandatory = (context.user_data['profile']['province'] in [None, '[تنظیم‌نشده]'])
        
        await edit_message_safely(query, "❌ لغو شد. لطفاً دوباره **استان** خود را انتخاب کنید:", 
                                      generate_province_markup(is_mandatory, EDITING_PROFILE_PROVINCE))
        
        return EDITING_PROFILE_PROVINCE

    return MAIN_MENU_SELECT 

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره عکس پروفایل."""
    photo_file_id = update.message.photo[-1].file_id 
    context.user_data['profile']['photo_id'] = photo_file_id
    
    await update.message.reply_text("✅ عکس پروفایل شما با موفقیت به‌روز شد.", reply_markup=PROFILE_MENU_MARKUP)
    return EDITING_PROFILE_MENU

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره موقعیت مکانی (اختیاری) و بازگشت به منوی صحیح."""
    location = update.message.location
    lat, lon = location.latitude, location.longitude
    context.user_data['profile']['location'] = f"{lat},{lon}"
    
    # اگر کاربر در منوی جستجوی نزدیک بود
    if context.user_data.get('current_state') == NEARBY_SELECT:
        await update.message.reply_text("✅ موقعیت مکانی شما برای جستجوی افراد نزدیک ذخیره شد. محدوده جستجو را انتخاب کنید:", reply_markup=NEARBY_MARKUP)
        return NEARBY_SELECT
    # اگر کاربر در منوی ویرایش پروفایل بود
    else:
        await update.message.reply_text("✅ موقعیت مکانی شما ذخیره شد.", reply_markup=PROFILE_MENU_MARKUP)
        return EDITING_PROFILE_MENU

async def profile_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت انتخاب‌های منوی ویرایش پروفایل."""
    user_message = update.message.text
    
    if user_message == '⬅️ بازگشت به منوی اصلی':
        return await go_to_main_menu(update, context)
        
    elif user_message == '✍️ ویرایش نام':
        await update.message.reply_text("لطفاً نام جدید (یا نام مستعار) خود را وارد کنید:", reply_markup=ReplyKeyboardRemove())
        return EDITING_PROFILE_NAME
        
    elif user_message == '🎂 ویرایش سن':
        await update.message.reply_text("لطفاً سن جدید خود را به صورت عدد وارد کنید:", reply_markup=ReplyKeyboardRemove())
        return EDITING_PROFILE_AGE
        
    elif user_message == '🗺️ ویرایش استان/شهر':
        await update.message.reply_text("لطفاً استان جدید خود را از لیست انتخاب کنید:", 
                                        reply_markup=generate_province_markup(is_mandatory=False, current_state=EDITING_PROFILE_PROVINCE), parse_mode='Markdown')
        return EDITING_PROFILE_PROVINCE
        
    elif user_message == '📷 ویرایش عکس پروفایل':
        await update.message.reply_text("لطفاً یک عکس جدید برای پروفایل خود ارسال کنید:", reply_markup=ReplyKeyboardRemove())
        return EDITING_PROFILE_MENU 
    
    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود در منو استفاده کنید.", reply_markup=PROFILE_MENU_MARKUP)
        return EDITING_PROFILE_MENU

async def nearby_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """هندلر جستجوی افراد نزدیک."""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    if update.message.location:
        return await handle_location(update, context) 
        
    if user_message == '⬅️ بازگشت به منوی اصلی':
        return await go_to_main_menu(update, context)
        
    if not context.user_data['profile'].get('location') or context.user_data['profile'].get('location') == 'ندارد':
        await update.message.reply_text("❌ ابتدا باید موقعیت مکانی خود را برای ربات ارسال کنید (از دکمه زیر استفاده کنید).", reply_markup=NEARBY_MARKUP)
        return NEARBY_SELECT
        
    if user_message in ['5 کیلومتر', '10 کیلومتر', '20 کیلومتر']:
        current_coins = context.user_data.get('coins', 0)
        
        if current_coins < CHAT_FEE:
            await update.message.reply_text(f"❌ موجودی سکه شما کافی نیست! برای این نوع جستجو به **{CHAT_FEE} سکه** نیاز دارید. موجودی فعلی شما: **{current_coins} سکه**.", reply_markup=NEARBY_MARKUP, parse_mode='Markdown')
            return NEARBY_SELECT

        # 🟢 تغییر: سکه کسر نمی‌شود، پرچم هزینه در انتظار تنظیم می‌شود
        context.user_data['pending_fee'] = CHAT_FEE
        
        await update.message.reply_text(f"⏳ در حال جستجوی کاربران در محدوده **{user_message}**... لطفاً صبر کنید.\n"
                                        f"**توجه:** هزینه **{CHAT_FEE} سکه** پس از اتصال کسر خواهد شد.\nبرای لغو، /cancel را بزنید.", 
                                        reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
        return SEARCHING
        
    await update.message.reply_text("لطفاً محدوده مورد نظر را انتخاب کنید یا موقعیت خود را ارسال نمایید.", reply_markup=NEARBY_MARKUP)
    return NEARBY_SELECT

async def searching_cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """هندلر لغو جستجو یا چت در وضعیت‌های مختلف."""
    user_id = update.effective_user.id
    
    # 1. اگر در صف انتظار است (جستجوی ساده پولی یا شانسی)
    if user_id in WAITING_QUEUE:
        WAITING_QUEUE.remove(user_id)
        # 🟢 تغییر: پاک کردن پرچم هزینه در انتظار و ارسال پیام مناسب
        if context.user_data.pop('pending_fee', 0) > 0:
            await context.bot.send_message(user_id, "✅ جستجوی پولی شما لغو شد. سکه‌ای کسر نشده است.", reply_markup=MENU_MARKUP)
        else:
            await context.bot.send_message(user_id, "✅ جستجوی شانسی شما لغو شد.", reply_markup=MENU_MARKUP)
        return MAIN_MENU_SELECT
    
    # 2. اگر در چت است (با /cancel یا /stop)
    elif user_id in ACTIVE_CHATS:
        await context.bot.send_message(user_id, "⚠️ مطمئنی میخوای چت رو تموم کنی؟؟؟", reply_markup=DISCONNECT_MARKUP)
        return CHATTING
    
    # 3. اگر در Matchmaking منتظر پاسخ است
    elif context.user_data.get('current_state') == WAITING_FOR_CHAT_RESPONSE:
        # لغو درخواست داده شده
        target_id = context.user_data.pop('target_user_id', None)
        # 💰 پاک کردن پرچم هزینه در انتظار از درخواست‌دهنده
        context.user_data.pop('pending_fee', None)
        
        if target_id and PENDING_REQUESTS.get(target_id) == user_id:
            del PENDING_REQUESTS[target_id]
            try:
                await context.bot.send_message(target_id, "❌ درخواست چت توسط فرستنده لغو شد.", reply_markup=MENU_MARKUP)
            except: pass
            
        await context.bot.send_message(user_id, "✅ درخواست چت شما لغو شد.", reply_markup=MENU_MARKUP)
        return MAIN_MENU_SELECT
        
    else:
        await context.bot.send_message(user_id, "شما نه در چت هستید، نه در صف انتظار و نه در حال انتظار برای پاسخ چت. به منوی اصلی بازگشتید.", reply_markup=MENU_MARKUP)
        return MAIN_MENU_SELECT

async def disconnect_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """هندلر برای دکمه‌های تأیید قطع چت (Inline Keyboard)."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'confirm_disconnect':
        await edit_message_safely(query, "در حال قطع اتصال...", None)
        return await disconnect_users(user_id, context)
    elif query.data == 'cancel_disconnect':
        await edit_message_safely(query, "✅ چت ادامه یافت. می‌توانید پیام‌های خود را ارسال کنید.", None)
        await context.bot.send_message(user_id, "منوی چت:", reply_markup=CHATTING_MARKUP)
        return CHATTING
    return CHATTING

async def chat_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    partner_id = ACTIVE_CHATS.get(user_id)
    chat_start_time = CHAT_START_TIMES.get(user_id)
    
    if not partner_id:
        await update.message.reply_text("⚠️ وضعیت چت شما نامنظم است. به منو بازگشتید.")
        return await disconnect_users(user_id, context)
        
    if update.message.text == '❌ پایان چت' or update.message.text == '/stop':
        await update.message.reply_text("⚠️ مطمئنی میخوای چت رو تموم کنی؟؟؟", reply_markup=DISCONNECT_MARKUP)
        return CHATTING 

    if update.message.text == '👁️ مشاهده پروفایل':
        await display_partner_profile(user_id, partner_id, context, show_request_button=False)
        await update.message.reply_text("همچنان در حال چت هستید. می‌توانید پیام دهید یا چت را تمام کنید.", reply_markup=CHATTING_MARKUP)
        return CHATTING

    # --- اعمال محدودیت‌های چت ---
    time_elapsed: timedelta = datetime.now() - chat_start_time if chat_start_time else timedelta(seconds=0)
    
    if update.message.sticker or update.message.animation or update.message.video_note:
        if time_elapsed < timedelta(minutes=GIF_STICKER_BAN_MINUTES):
            remaining_seconds = max(0, int(timedelta(minutes=GIF_STICKER_BAN_MINUTES).total_seconds() - time_elapsed.total_seconds()))
            remaining_minutes = remaining_seconds / 60
            await update.message.reply_text(f"❌ ارسال گیف، استیکر یا پیام ویدیویی تا **{GIF_STICKER_BAN_MINUTES} دقیقه** اول ممنوع است. (**{remaining_minutes:.1f} دقیقه باقی مانده**)", parse_mode='Markdown', reply_markup=CHATTING_MARKUP)
            return CHATTING 
        
    if update.message.text:
        if contains_link_or_id(update.message.text):
            await update.message.reply_text("❌ ارسال لینک، آیدی و شماره تلفن در چت ناشناس **ممنوع** است.", parse_mode='Markdown', reply_markup=CHATTING_MARKUP)
            return CHATTING 

        if contains_english(update.message.text):
            if time_elapsed < timedelta(minutes=ENGLISH_WORD_BAN_MINUTES):
                remaining_seconds = max(0, int(timedelta(minutes=ENGLISH_WORD_BAN_MINUTES).total_seconds() - time_elapsed.total_seconds()))
                remaining_minutes = remaining_seconds / 60
                await update.message.reply_text(f"❌ استفاده از الفاظ انگلیسی تا **{ENGLISH_WORD_BAN_MINUTES} دقیقه** اول ممنوع است. (**{remaining_minutes:.1f} دقیقه باقی مانده**)", parse_mode='Markdown', reply_markup=CHATTING_MARKUP)
                return CHATTING 
            
    # --- ارسال پیام در صورت عبور از فیلتر ---
    try:
        await update.message.copy(chat_id=partner_id)
    except Exception as e:
        logger.error(f"خطا در ارسال پیام از {user_id} به {partner_id}: {e}")
        await update.message.reply_text("🚨 متأسفانه پیام شما به دلیل مشکل فنی ارسال نشد. چت قطع شد.", reply_markup=CHATTING_MARKUP)
        return await disconnect_users(user_id, context)
        
    return CHATTING

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a traceback to the developer (or user in this case)."""
    logger.error("Update '%s' caused error '%s'", update, context.error)
    try:
        if update and update.effective_chat:
            await context.bot.send_message(update.effective_chat.id, "🚨 یک خطای فنی رخ داد. لطفاً با /start یا /menu دوباره شروع کنید.")
    except Exception as e:
        logger.error(f"Failed to send error message to user: {e}")


def main():
    
    proxy_info = os.environ.get('ALL_PROXY') or os.environ.get('HTTP_PROXY')
    
    # 🟢 تغییر: کاهش poll_interval برای سرعت بالاتر
    application_builder = Application.builder().token(TOKEN).concurrent_updates(True).read_timeout(60).write_timeout(60) 
    
    if proxy_info:
        logger.info(f"✅ تلاش برای اتصال با پروکسی از طریق CMD: {proxy_info}")
        application = application_builder.build(
            request_kwargs={'proxy_url': proxy_info} 
        )
    else:
        logger.warning("⚠️ هیچ پروکسی‌ای تنظیم نشده است. اتصال ممکن است شکست بخورد.")
        application = application_builder.build()
        
    # 3. تعریف ConversationHandler
    conv_handler = ConversationHandler(
        
        entry_points=[
            CommandHandler("start", start_handler),
            CommandHandler("menu", menu_command_handler),
        ],
        
        states={
            MAIN_MENU_SELECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_select_handler),
            ],
            
            CHAT_OPTIONS_SELECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat_options_handler),
            ],

            SEARCH_PEOPLE_SELECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_people_handler),
            ],
            
            # --- وضعیت‌های Matchmaking جدید ---
            SELECTING_TARGET_GENDER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_target_gender),
            ],
            DISPLAYING_SEARCH_LIST: [
                CallbackQueryHandler(matchmaking_callback_handler),
            ],
            WAITING_FOR_CHAT_REQUEST: [
                CallbackQueryHandler(matchmaking_callback_handler),
                CommandHandler("menu", menu_command_handler),
            ],
            WAITING_FOR_CHAT_RESPONSE: [
                CallbackQueryHandler(matchmaking_callback_handler),
                CommandHandler("menu", menu_command_handler),
            ],
            # ------------------------------------

            NEARBY_SELECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND | filters.LOCATION, nearby_handler),
            ],
            
            # --- وضعیت‌های پروفایل (ویرایش) ---
            EDITING_PROFILE_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.LOCATION & ~filters.PHOTO, profile_menu_handler),
                MessageHandler(filters.LOCATION, handle_location), 
                MessageHandler(filters.PHOTO, handle_photo) 
            ],
            
            EDITING_PROFILE_PROVINCE: [
                CallbackQueryHandler(geography_callback_handler),
            ],
            GET_MANDATORY_CITY: [
                CallbackQueryHandler(geography_callback_handler),
            ],
            EDITING_PROFILE_CITY: [
                CallbackQueryHandler(geography_callback_handler),
            ],
            
            EDITING_PROFILE_GENDER: [ 
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_mandatory_gender),
            ],
            
            EDITING_PROFILE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_mandatory_name),
            ],
            
            EDITING_PROFILE_AGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_mandatory_age),
            ],
            
            SEARCHING: [
                MessageHandler(filters.ALL & ~filters.COMMAND, searching_cancel_handler),
                CommandHandler("cancel", searching_cancel_handler),
            ],
            
            CHATTING: [
                MessageHandler(filters.ALL & ~filters.COMMAND, chat_message_handler), 
                CommandHandler("stop", chat_message_handler),
            ]
        },
        
        fallbacks=[
            CommandHandler("start", start_handler),
            CommandHandler("menu", menu_command_handler),
            MessageHandler(filters.ALL, lambda update, context: start_handler(update, context)) 
        ],
        per_user=True 
    )

    # 4. اضافه کردن هندلرهای CallbackQuery
    # 🟢 فیلترگذاری اختصاصی برای جلوگیری از تداخل و رفع خطاهای ویرایش پیام
    application.add_handler(CallbackQueryHandler(disconnect_confirmation_handler, pattern="^(confirm_disconnect|cancel_disconnect)$")) 
    
    # 🟢 فیلترگذاری برای Matchmaking
    application.add_handler(CallbackQueryHandler(matchmaking_callback_handler, pattern="^(view_prof:|request_chat:|accept_chat:|reject_chat:|cancel_search)$"))
    
    # فیلترگذاری برای انتخاب موقعیت
    application.add_handler(CallbackQueryHandler(geography_callback_handler, pattern="^(prov_sel:|city_sel:|province_reselect|profile_back)$"))

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    print("✨ ربات در حال اجرا و گوش دادن به پیام‌ها است...")
    
    try:
        # 🟢 تغییر: کاهش poll_interval برای سرعت بالاتر
        application.run_polling(poll_interval=1.0) 
    except Exception as e:
        print(f"\n❌ خطای اتصال: {e}.")


if __name__ == '__main__':
    if not os.path.exists("static"):
        os.makedirs("static")
        print("⚠️ پوشه 'static' ایجاد شد. لطفاً عکس‌های پیش‌فرض (1.png و 2.png) را در آن قرار دهید.")
        
    main()
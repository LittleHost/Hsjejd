import asyncio
import logging
import random
import sqlite3
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Optional
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup,
    KeyboardButton, CallbackQuery, Message, BotCommand,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ========== КОНФИГ ==========
BOT_TOKEN = "import asyncio
import logging
import random
import sqlite3
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Optional
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup,
    KeyboardButton, CallbackQuery, Message, BotCommand,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ========== КОНФИГ ==========
BOT_TOKEN = "7932790272:AAHvHvVR0ysdJ8VUoWCnsDmfNgzDK3Tw_3U"
CRYPTOBOT_TOKEN = "594394:AAqYLgin8OMpwWvpBXCDiNGcpnGHJ5NDXPn"
ADMIN_IDS = [7966949924]
BOT_USERNAME = "SecondCasBOT"
CHAT_LINK = "https://t.me/SecondProjectChat"
REQUIRED_CHANNEL_ID = -1003948376817

MIN_BET = 0.10
MIN_WITHDRAW = 1.10
COOLDOWN = 3
MIN_TRANSFER = 0.10

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === ID ПРЕМИУМ ЭМОДЗИ ДЛЯ КНОПОК (НЕ ТРОГАЕМ) ===
PREMIUM_BUTTONS = {
    "game": "5258508428212445001",
    "profile": "5879770735999717115",
    "deposit": "5258043150110301407",
    "withdraw": "5258336354642697821",
    "gift": "5226731292334235524",
    "ref": "5879770735999717115",
    "send": "5258336354642697821",
    "back": "5258336354642697821",
    "chat": "5258501105293205250",
    "crypto": "5377820717024842074",
    "star": "5958376256788502078",
    "check": "5238078046174456159",
    "cross": "5238078046174456159",
}

# ========== ФУНКЦИЯ ДЛЯ ПРЕМИУМ ЭМОДЗИ В ТЕКСТАХ ==========
def p(text: str) -> str:
    """Заменяет обычные эмодзи на премиум в текстах"""
    replacements = {
        "💰": '<tg-emoji emoji-id="5377452788651429834">💰</tg-emoji>',
        "💵": '<tg-emoji emoji-id="5377452788651429834">💵</tg-emoji>',
        "⚡️": '<tg-emoji emoji-id="5377444769947490089">⚡️</tg-emoji>',
        "🎮": '<tg-emoji emoji-id="5258508428212445001">🎮</tg-emoji>',
        "👤": '<tg-emoji emoji-id="5879770735999717115">👤</tg-emoji>',
        "⏰": '<tg-emoji emoji-id="5778605968208170641">⏰</tg-emoji>',
        "💳": '<tg-emoji emoji-id="5258043150110301407">💳</tg-emoji>',
        "🎁": '<tg-emoji emoji-id="5226731292334235524">🎁</tg-emoji>',
        "👥": '<tg-emoji emoji-id="5879770735999717115">👥</tg-emoji>',
        "⭐️": '<tg-emoji emoji-id="5958376256788502078">⭐️</tg-emoji>',
        "💎": '<tg-emoji emoji-id="5377820717024842074">💎</tg-emoji>',
        "✅": '<tg-emoji emoji-id="5238078046174456159">✅</tg-emoji>',
        "❌": '<tg-emoji emoji-id="5238078046174456159">❌</tg-emoji>',
        "⚠️": '<tg-emoji emoji-id="5238078046174456159">⚠️</tg-emoji>',
        "🔙": '<tg-emoji emoji-id="5258336354642697821">🔙</tg-emoji>',
        "🏆": '<tg-emoji emoji-id="5235702276424737428">🏆</tg-emoji>',
        "🎉": '<tg-emoji emoji-id="5238078046174456159">🎉</tg-emoji>',
        "📤": '<tg-emoji emoji-id="5258336354642697821">📤</tg-emoji>',
        "💬": '<tg-emoji emoji-id="5258501105293205250">💬</tg-emoji>',
        "🗼": '<tg-emoji emoji-id="5377444769947490089">🗼</tg-emoji>',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# ========== КЛАВИАТУРЫ (НЕ ТРОГАЕМ) ==========
def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text=" Игры в боте", icon_custom_emoji_id=PREMIUM_BUTTONS["game"]),
            KeyboardButton(text=" Профиль", icon_custom_emoji_id=PREMIUM_BUTTONS["profile"])
        ]],
        resize_keyboard=True
    )

def games_kb():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="🎲", callback_data="game_dice"),
        InlineKeyboardButton(text="⚽️", callback_data="game_football"),
        InlineKeyboardButton(text="🎯", callback_data="game_target"),
        InlineKeyboardButton(text="🗼", callback_data="game_tower")
    )
    b.row(InlineKeyboardButton(text=" Чат", url=CHAT_LINK, icon_custom_emoji_id=PREMIUM_BUTTONS["chat"]))
    b.row(InlineKeyboardButton(text=" Назад", callback_data="back_main", icon_custom_emoji_id=PREMIUM_BUTTONS["back"]))
    return b.as_markup()

def profile_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Пополнить", callback_data="deposit", icon_custom_emoji_id=PREMIUM_BUTTONS["deposit"]),
         InlineKeyboardButton(text=" Вывести", callback_data="withdraw", icon_custom_emoji_id=PREMIUM_BUTTONS["withdraw"])],
        [InlineKeyboardButton(text=" Промокоды", callback_data="promo", icon_custom_emoji_id=PREMIUM_BUTTONS["gift"]),
         InlineKeyboardButton(text=" Рефералы", callback_data="ref", icon_custom_emoji_id=PREMIUM_BUTTONS["ref"])],
        [InlineKeyboardButton(text=" Перевод", callback_data="transfer", icon_custom_emoji_id=PREMIUM_BUTTONS["send"]),
         InlineKeyboardButton(text=" Назад", callback_data="back_main", icon_custom_emoji_id=PREMIUM_BUTTONS["back"])]
    ])

def deposit_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" CryptoBot", callback_data="dep_crypto", icon_custom_emoji_id=PREMIUM_BUTTONS["crypto"])],
        [InlineKeyboardButton(text=" Stars", callback_data="dep_stars", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" Назад", callback_data="back_profile", icon_custom_emoji_id=PREMIUM_BUTTONS["back"])]
    ])

def stars_amount_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" 50 Stars ($0.55)", callback_data="stars_50", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" 100 Stars ($1.10)", callback_data="stars_100", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" 250 Stars ($2.75)", callback_data="stars_250", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" 500 Stars ($5.50)", callback_data="stars_500", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" 1000 Stars ($11.00)", callback_data="stars_1000", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" Назад", callback_data="back_deposit", icon_custom_emoji_id=PREMIUM_BUTTONS["back"])]
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Назад", callback_data="back_profile", icon_custom_emoji_id=PREMIUM_BUTTONS["back"])]
    ])

def cancel_kb(callback_data: str = "cancel"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Отмена", callback_data=callback_data, icon_custom_emoji_id=PREMIUM_BUTTONS["cross"])]
    ])

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        uid INTEGER PRIMARY KEY,
        balance REAL DEFAULT 0,
        reg TEXT,
        deposit REAL DEFAULT 0,
        wagered REAL DEFAULT 0,
        lost REAL DEFAULT 0,
        ref_id INTEGER,
        ref_earn REAL DEFAULT 0,
        ref_cnt INTEGER DEFAULT 0,
        ref_dep_cnt INTEGER DEFAULT 0,
        last_bet REAL DEFAULT 0,
        subscribed INTEGER DEFAULT 0,
        username TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS withdraws (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER,
        amount REAL,
        status TEXT DEFAULT 'pending',
        created TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS promos (
        code TEXT PRIMARY KEY,
        reward REAL,
        max_act INTEGER,
        activated INTEGER DEFAULT 0,
        expires TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS promo_used (
        code TEXT,
        uid INTEGER
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_uid INTEGER,
        to_uid INTEGER,
        amount REAL,
        created TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS duels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        player1 INTEGER,
        player2 INTEGER,
        amount REAL,
        status TEXT DEFAULT 'waiting',
        created TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def get_user(uid: int) -> Dict:
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE uid = ?", (uid,))
    u = cur.fetchone()
    conn.close()
    if not u:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users (uid, reg, last_bet, subscribed) VALUES (?, ?, 0, 0)", (uid, datetime.now()))
        conn.commit()
        conn.close()
        return {"uid": uid, "balance": 0, "reg": datetime.now(), "wagered": 0, "lost": 0,
                "ref_cnt": 0, "ref_earn": 0, "last_bet": 0, "subscribed": 0, "username": None}
    return {"uid": u[0], "balance": u[1], "reg": datetime.strptime(u[2], "%Y-%m-%d %H:%M:%S.%f"),
            "wagered": u[4], "lost": u[5], "ref_id": u[6], "ref_earn": u[7],
            "ref_cnt": u[8], "ref_dep_cnt": u[9], "last_bet": u[10], "subscribed": u[11], "username": u[12]}

def upd_bal(uid: int, amt: float):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE uid = ?", (amt, uid))
    conn.commit()
    conn.close()

def upd_username(uid: int, username: str):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET username = ? WHERE uid = ?", (username, uid))
    conn.commit()
    conn.close()

def upd_wagered(uid: int, amt: float):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET wagered = wagered + ? WHERE uid = ?", (amt, uid))
    conn.commit()
    conn.close()

def upd_lost(uid: int, amt: float):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET lost = lost + ? WHERE uid = ?", (amt, uid))
    conn.commit()
    conn.close()

def upd_last_bet(uid: int):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_bet = ? WHERE uid = ?", (datetime.now().timestamp(), uid))
    conn.commit()
    conn.close()

def upd_subscribed(uid: int, val: int = 1):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET subscribed = ? WHERE uid = ?", (val, uid))
    conn.commit()
    conn.close()

def can_bet(uid: int):
    u = get_user(uid)
    now = datetime.now().timestamp()
    if now - u["last_bet"] < COOLDOWN:
        return False, COOLDOWN - (now - u["last_bet"])
    return True, 0

# ========== ПРОВЕРКА ПОДПИСКИ ==========
async def check_subscription(uid: int) -> bool:
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL_ID, uid)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            user = get_user(uid)
            if user.get("subscribed", 0) == 0:
                upd_subscribed(uid, 1)
                if user.get("ref_id") and user.get("ref_id") > 0:
                    upd_bal(user["ref_id"], 1)
                    conn = sqlite3.connect('data.db')
                    cur = conn.cursor()
                    cur.execute("UPDATE users SET ref_earn = ref_earn + 1, ref_dep_cnt = ref_dep_cnt + 1 WHERE uid = ?", (user["ref_id"],))
                    conn.commit()
                    conn.close()
            return True
        return False
    except:
        return False

# ========== ОСНОВНЫЕ ОБРАБОТЧИКИ ==========
@dp.message(Command("start"), F.chat.type == "private")
async def start(msg: Message):
    if msg.from_user.username:
        upd_username(msg.from_user.id, msg.from_user.username)
    
    get_user(msg.from_user.id)
    
    args = msg.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != msg.from_user.id:
            u = get_user(msg.from_user.id)
            if u.get("ref_id") is None and u.get("subscribed") == 0:
                conn = sqlite3.connect('data.db')
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM users WHERE uid = ?", (ref_id,))
                if cur.fetchone():
                    cur.execute("UPDATE users SET ref_id = ?, ref_cnt = ref_cnt + 1 WHERE uid = ?", (ref_id, msg.from_user.id))
                    conn.commit()
                conn.close()
    
    if await check_subscription(msg.from_user.id):
        txt = p("""💰 <b>Деньги есть всегда!</b>

⚡️ <b>Бот с играми и дуэлями</b>
⚡️ <b>Быстрые ставки, моментальные выводы</b>
💵 <b>Доход с рефералов</b>
<i>От 💵100 в день — реально</i>""")
        await msg.answer(txt, reply_markup=main_kb(), parse_mode=ParseMode.HTML)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться", url="https://t.me/SecondNewsRU", icon_custom_emoji_id=PREMIUM_BUTTONS["chat"])],
            [InlineKeyboardButton(text="✅ Проверить", callback_data="check_sub", icon_custom_emoji_id=PREMIUM_BUTTONS["check"])]
        ])
        await msg.answer(
            "⚠️ <b>Для использования бота необходимо подписаться на наш канал!</b>\n\n👇 Нажмите на кнопку ниже, подпишитесь и нажмите «Проверить подписку»",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(c: CallbackQuery):
    if await check_subscription(c.from_user.id):
        await c.message.delete()
        await start(c.message)
        await c.answer("✅ Подписка подтверждена! Добро пожаловать!", show_alert=True)
    else:
        await c.answer("❌ Вы не подписаны на канал! Подпишитесь и нажмите снова.", show_alert=True)

# === HELP ===
@dp.message(Command("help"), F.chat.type == "private")
@dp.message(Command("help"), F.chat.type.in_(["group", "supergroup"]))
async def help_cmd(msg: Message):
    await msg.answer(
        p("🎮 <b>Доступные команды:</b>\n\n"
          "💰 <b>Баланс</b> — /balance\n"
          "🎲 <b>Кости</b> — /dice {сумма}\n"
          "⚽️ <b>Футбол</b> — /football {сумма}\n"
          "🎯 <b>Дартс</b> — /target {сумма}\n"
          "⚔️ <b>Дуэль</b> — /cub {ставка}\n\n"
          "📤 <b>Перевод</b> — /send {сумма} @username\n\n"
          "⭐️ <b>Пополнение</b> — в личных сообщениях с ботом\n"
          "💸 <b>Вывод</b> — в личных сообщениях с ботом\n\n"
          "<i>Подпишись на канал для игры!</i>"),
        parse_mode=ParseMode.HTML
    )

# === БАЛАНС ===
@dp.message(Command("balance"), F.chat.type == "private")
@dp.message(Command("balance"), F.chat.type.in_(["group", "supergroup"]))
@dp.message(F.text.lower().in_(["баланс", "б", "b", "бал", "мешок", "гроши"]), F.chat.type.in_(["group", "supergroup"]))
async def balance_cmd(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.reply("⚠️ Подпишитесь на канал!")
        return
    u = get_user(msg.from_user.id)
    await msg.reply(p(f"💰 Ваш баланс: 💵{u['balance']:.2f}"))

# === ИГРЫ В ЛИЧКЕ ===
@dp.message(F.text.in_(["🎮 Игры в боте", "Игры в боте"]), F.chat.type == "private")
async def games_menu(msg: Message):
    if not await check_subscription(msg.from_user.id):
        return
    u = get_user(msg.from_user.id)
    txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u['balance']:.2f}")
    await msg.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)

@dp.message(F.text.in_(["👤 Профиль", "Профиль"]), F.chat.type == "private")
async def profile_menu(msg: Message):
    if not await check_subscription(msg.from_user.id):
        return
    u = get_user(msg.from_user.id)
    days = (datetime.now() - u["reg"]).days
    txt = p(f"👤 <b>Ваш профиль</b>\n\n💰 Баланс: <b>💵{u['balance']:.2f}</b>\n⏰ Дней в боте: <b>{days}</b>")
    await msg.answer(txt, reply_markup=profile_kb(), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "back_main")
async def back_main(c: CallbackQuery):
    await c.message.delete()
    txt = p("""💰 <b>Деньги есть всегда!</b>

⚡️ <b>Бот с играми и дуэлями</b>
⚡️ <b>Быстрые ставки, моментальные выводы</b>
💵 <b>Доход с рефералов</b>
<i>От 💵100 в день — реально</i>""")
    await c.message.answer(txt, reply_markup=main_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

@dp.callback_query(F.data == "back_profile")
async def back_profile(c: CallbackQuery):
    await c.message.delete()
    u = get_user(c.from_user.id)
    days = (datetime.now() - u["reg"]).days
    txt = p(f"👤 <b>Ваш профиль</b>\n\n💰 Баланс: <b>💵{u['balance']:.2f}</b>\n⏰ Дней в боте: <b>{days}</b>")
    await c.message.answer(txt, reply_markup=profile_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

@dp.callback_query(F.data == "back_deposit")
async def back_deposit(c: CallbackQuery):
    await c.message.edit_text(p("💳 <b>Пополнение средств</b>"), reply_markup=deposit_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

# === РЕФЕРАЛКА ===
@dp.callback_query(F.data == "ref")
async def ref_prog(c: CallbackQuery):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    u = get_user(c.from_user.id)
    txt = p(f"""👥 <b>Реферальная программа</b>

👥 Рефералы: {u["ref_cnt"]} (пополнили: {u["ref_dep_cnt"]})
💵 Заработано: 💵{u["ref_earn"]:.2f}

<b>Условия:</b>
• 💵 1💵 за друга с депозитом от 5💵
• 💵 10% от проигрышей по пятницам

<b>Бонусы:</b>
• 100 друзей → +5💵
• 250 друзей → +15💵
• 500 друзей → +30💵
• 1000 друзей → +60💵

🏆 До бонуса: {max(0, 100 - u["ref_cnt"])} рефералов

🔗 Реферальная ссылка:
https://t.me/{BOT_USERNAME}?start={c.from_user.id}""")
    await c.message.edit_text(txt, reply_markup=back_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

# === ПРОМОКОДЫ ===
class PromoState(StatesGroup):
    wait = State()

@dp.callback_query(F.data == "promo")
async def promo_menu(c: CallbackQuery, state: FSMContext):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    txt = p("🎁 <b>Введи промокод:</b>\n\nПросто напиши код в чат — и бонус зачислится автоматически.")
    await c.message.edit_text(txt, reply_markup=back_kb(), parse_mode=ParseMode.HTML)
    await state.set_state(PromoState.wait)
    await c.answer()

@dp.message(PromoState.wait, F.chat.type == "private")
async def promo_use(msg: Message, state: FSMContext):
    code = msg.text.upper()
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM promos WHERE code = ?", (code,))
    p = cur.fetchone()
    if not p:
        await msg.answer(p("⭐️ Промокод не найден!"), reply_markup=back_kb())
        await state.clear()
        return
    cur.execute("SELECT 1 FROM promo_used WHERE code = ? AND uid = ?", (code, msg.from_user.id))
    if cur.fetchone():
        await msg.answer(p("⭐️ Вы уже активировали этот промокод!"), reply_markup=back_kb())
        await state.clear()
        return
    if p[3] >= p[2] and p[2] > 0:
        await msg.answer(p("⭐️ Промокод достиг лимита!"), reply_markup=back_kb())
        await state.clear()
        return
    upd_bal(msg.from_user.id, p[1])
    cur.execute("INSERT INTO promo_used VALUES (?, ?)", (code, msg.from_user.id))
    cur.execute("UPDATE promos SET activated = activated + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    await msg.answer(p(f"🎉 Промокод активирован! +💵{p[1]:.2f} на баланс!"))
    await state.clear()

# === ПЕРЕВОД ===
class TransferState(StatesGroup):
    waiting_amount = State()
    waiting_target = State()

@dp.callback_query(F.data == "transfer")
async def transfer_start(c: CallbackQuery, state: FSMContext):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    
    await c.message.edit_text(
        p(f"📤 <b>Перевод средств</b>\n\nВведите сумму перевода (мин. 💵{MIN_TRANSFER:.2f}):"),
        reply_markup=cancel_kb("cancel_transfer"),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(TransferState.waiting_amount)
    await c.answer()

@dp.message(TransferState.waiting_amount, F.chat.type == "private")
async def transfer_amount(msg: Message, state: FSMContext):
    try:
        amount = float(msg.text.replace(",", "."))
        if amount < MIN_TRANSFER:
            await msg.answer(p(f"❌ Минимальная сумма перевода 💵{MIN_TRANSFER:.2f}!"))
            return
        
        u = get_user(msg.from_user.id)
        if amount > u["balance"]:
            await msg.answer(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        await state.update_data(transfer_amount=amount)
        await msg.answer(
            p("📤 Введите username или ID получателя:\n\nПримеры:\n• @username\n• 123456789"),
            reply_markup=cancel_kb("cancel_transfer")
        )
        await state.set_state(TransferState.waiting_target)
    except:
        await msg.answer(p("❌ Введите число!"))

@dp.message(TransferState.waiting_target, F.chat.type == "private")
async def transfer_target(msg: Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("transfer_amount")
    
    target_id = None
    if msg.text.startswith("@"):
        username = msg.text[1:]
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT uid FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        if row:
            target_id = row[0]
    else:
        try:
            target_id = int(msg.text)
        except:
            pass
    
    if not target_id or target_id == msg.from_user.id:
        await msg.answer(p("❌ Получатель не найден или это вы сами!"))
        return
    
    target = get_user(target_id)
    if target["balance"] is None:
        await msg.answer(p("❌ Пользователь не найден!"))
        return
    
    upd_bal(msg.from_user.id, -amount)
    upd_bal(target_id, amount)
    
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO transfers (from_uid, to_uid, amount, created) VALUES (?, ?, ?, ?)",
               (msg.from_user.id, target_id, amount, datetime.now()))
    conn.commit()
    conn.close()
    
    await msg.answer(
        p(f"✅ Перевод выполнен!\n\n"
          f"📤 Отправитель: {msg.from_user.id}\n"
          f"📥 Получатель: {target_id}\n"
          f"💵 Сумма: 💵{amount:.2f}\n\n"
          f"💰 Ваш баланс: 💵{get_user(msg.from_user.id)['balance']:.2f}")
    )
    
    await bot.send_message(
        target_id,
        p(f"📥 Вам поступил перевод!\n\n"
          f"👤 От: {msg.from_user.id}\n"
          f"💵 Сумма: 💵{amount:.2f}\n\n"
          f"💰 Ваш баланс: 💵{get_user(target_id)['balance']:.2f}")
    )
    
    await state.clear()

@dp.callback_query(F.data == "cancel_transfer")
async def cancel_transfer(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await back_profile(c)

# === АНИМИРОВАННЫЕ ИГРЫ ===
class BetState(StatesGroup):
    wait = State()

class TowerState(StatesGroup):
    play = State()

@dp.callback_query(F.data.startswith("game_"))
async def game_start(c: CallbackQuery, state: FSMContext):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    
    game = c.data.split("_")[1]
    await c.message.answer(p(f"✏️ Введите сумму ставки (мин. 💵{MIN_BET:.2f})"), reply_markup=cancel_kb("cancel_bet"))
    await state.update_data(game=game)
    await state.set_state(BetState.wait)
    await c.answer()

@dp.callback_query(F.data == "cancel_bet")
async def cancel_bet(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await games_menu(c.message)
    await c.answer()

@dp.message(BetState.wait, F.chat.type == "private")
async def process_bet(msg: Message, state: FSMContext):
    u = get_user(msg.from_user.id)
    data = await state.get_data()
    game = data.get("game")
    
    try:
        bet = float(msg.text.replace(",", "."))
        if bet < MIN_BET:
            await msg.answer(p(f"❌ Минимальная ставка 💵{MIN_BET:.2f}!"))
            return
        if bet > u["balance"]:
            await msg.answer(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
    except:
        await msg.answer(p("❌ Введите число!"))
        return
    
    upd_bal(msg.from_user.id, -bet)
    
    if game == "dice":
        dice_msg = await msg.answer_dice(emoji="🎲")
        value = dice_msg.dice.value
        
        if value >= 4:
            mult = {4: 1.4, 5: 1.8, 6: 2.4}[value]
            win = bet * mult
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.answer(p(f"🎲 Выпало: {value}\n✅ Выигрыш: 💵{win:.2f} (x{mult})!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.answer(p(f"🎲 Выпало: {value}\n❌ Проигрыш: 💵{bet:.2f}!"))
    
    elif game == "football":
        football_msg = await msg.answer_dice(emoji="⚽️")
        value = football_msg.dice.value
        
        if value >= 4:
            win = bet * 1.3
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.answer(p(f"⚽️ ГОЛ! ✅ Выигрыш: 💵{win:.2f} (x1.3)!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.answer(p(f"⚽️ Мимо ворот! ❌ Проигрыш: 💵{bet:.2f}!"))
    
    elif game == "target":
        target_msg = await msg.answer_dice(emoji="🎯")
        value = target_msg.dice.value
        
        if value >= 5:
            win = bet * 5
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.answer(p(f"🎯 В ЦЕНТР! ✅ Выигрыш: 💵{win:.2f} (x5)!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.answer(p(f"🎯 Мимо! ❌ Проигрыш: 💵{bet:.2f}!"))
    
    elif game == "tower":
        await state.update_data(tower_bet=bet, tower_level=0, tower_mult=1.0)
        await state.set_state(TowerState.play)
        await play_tower(msg, state, 0, 1.0, bet)
        return
    
    await state.clear()
    u2 = get_user(msg.from_user.id)
    txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u2['balance']:.2f}")
    await msg.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)

# === БАШНЯ ===
async def play_tower(msg: Message, state: FSMContext, level: int, mult: float, bet: float):
    multipliers = [1.4, 1.7, 2.4, 3.2, 4.0, 6.0]
    
    if level >= len(multipliers):
        win = bet * multipliers[-1]
        upd_bal(msg.from_user.id, win)
        upd_wagered(msg.from_user.id, bet)
        await msg.answer(p(f"🏆 ПОЛНАЯ ПОБЕДА! 🏆\n🗼 Вы прошли все 6 уровней!\n💰 Выигрыш: 💵{win:.2f} (x{multipliers[-1]})!"))
        await state.clear()
        u = get_user(msg.from_user.id)
        txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u['balance']:.2f}")
        await msg.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)
        return
    
    bomb = random.randint(0, 1)
    await state.update_data(tower_bomb=bomb, tower_level=level, tower_bet=bet, tower_mult=mult)
    
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="⬅️ Левая 🟩", callback_data="tower_left"),
        InlineKeyboardButton(text="Правая 🟩 ➡️", callback_data="tower_right")
    )
    if level > 0:
        b.row(InlineKeyboardButton(text=p(f"💰 Забрать 💵{bet * mult:.2f}"), callback_data="tower_cashout"))
    b.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_tower", icon_custom_emoji_id=PREMIUM_BUTTONS["cross"]))
    
    await msg.answer(
        p(f"🗼 БАШНЯ - Уровень {level + 1}/6\n"
          f"💰 Ставка: 💵{bet:.2f}\n"
          f"📈 Множитель: x{multipliers[level]} (выигрыш: 💵{bet * multipliers[level]:.2f})\n"
          f"💥 В одной из клеток БОМБА!\n\n"
          f"Выбери клетку:"),
        reply_markup=b.as_markup()
    )

@dp.callback_query(F.data == "cancel_tower")
async def cancel_tower(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await games_menu(c.message)
    await c.answer()

@dp.callback_query(TowerState.play, F.data.in_(["tower_left", "tower_right", "tower_cashout"]))
async def tower_choice(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await c.answer(p("❌ Игра не найдена!"))
        return
    
    if c.data == "tower_cashout":
        bet = data.get("tower_bet", 0)
        mult = data.get("tower_mult", 1.0)
        level = data.get("tower_level", 0)
        if level == 0:
            await c.answer(p("⚠️ Нужно открыть хотя бы одну клетку!"), show_alert=True)
            return
        win = bet * mult
        upd_bal(c.from_user.id, win)
        upd_wagered(c.from_user.id, bet)
        await c.message.edit_text(p(f"💰 ВЫ ЗАБРАЛИ ВЫИГРЫШ! 💰\n🗼 Пройдено уровней: {level}/6\n✅ Выигрыш: 💵{win:.2f} (x{mult})!"))
        await state.clear()
        u = get_user(c.from_user.id)
        txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u['balance']:.2f}")
        await c.message.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)
        await c.answer()
        return
    
    bomb = data.get("tower_bomb")
    level = data.get("tower_level", 0)
    bet = data.get("tower_bet", 0)
    mult = data.get("tower_mult", 1.0)
    multipliers = [1.4, 1.7, 2.4, 3.2, 4.0, 6.0]
    chosen = 0 if c.data == "tower_left" else 1
    
    if chosen == bomb:
        upd_lost(c.from_user.id, bet)
        await c.message.edit_text(p(f"💥 БОМБА ВЗОРВАЛАСЬ! 💥\n🗼 Вы проиграли на уровне {level + 1}/6\n💰 Потеряно: 💵{bet:.2f}\n\n🎮 Попробуйте снова!"))
        await state.clear()
        u = get_user(c.from_user.id)
        txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u['balance']:.2f}")
        await c.message.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)
    else:
        level += 1
        new_mult = multipliers[level - 1]
        await c.message.edit_text(p(f"✅ БЕЗОПАСНО! 🟩\n🗼 Уровень {level}/6 пройден!\n💰 Текущий выигрыш: 💵{bet * new_mult:.2f} (x{new_mult})\n\n🎲 Продолжаем?"))
        
        if level >= len(multipliers):
            win = bet * multipliers[-1]
            upd_bal(c.from_user.id, win)
            upd_wagered(c.from_user.id, bet)
            await c.message.answer(p(f"🏆 ПОБЕДА! 🏆\n🗼 Вы прошли ВСЕ 6 уровней!\n💰 Выигрыш: 💵{win:.2f} (x{multipliers[-1]})!"))
            await state.clear()
            u = get_user(c.from_user.id)
            txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u['balance']:.2f}")
            await c.message.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)
        else:
            await state.update_data(tower_level=level, tower_mult=new_mult)
            new_bomb = random.randint(0, 1)
            await state.update_data(tower_bomb=new_bomb)
            b = InlineKeyboardBuilder()
            b.row(
                InlineKeyboardButton(text="⬅️ Левая 🟩", callback_data="tower_left"),
                InlineKeyboardButton(text="Правая 🟩 ➡️", callback_data="tower_right")
            )
            b.row(InlineKeyboardButton(text=p(f"💰 Забрать 💵{bet * new_mult:.2f}"), callback_data="tower_cashout"))
            b.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_tower", icon_custom_emoji_id=PREMIUM_BUTTONS["cross"]))
            await c.message.answer(
                p(f"🗼 БАШНЯ - Уровень {level + 1}/6\n"
                  f"💰 Ставка: 💵{bet:.2f}\n"
                  f"📈 Множитель: x{multipliers[level]} (выигрыш: 💵{bet * multipliers[level]:.2f})\n"
                  f"💥 В одной из клеток БОМБА!\n\n"
                  f"Выбери клетку:"),
                reply_markup=b.as_markup()
            )
    await c.answer()

# === ДЕПОЗИТЫ ===
class DepositState(StatesGroup):
    wait_crypto = State()

@dp.callback_query(F.data == "deposit")
async def deposit_menu(c: CallbackQuery):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    await c.message.edit_text(p("💳 <b>Пополнение средств</b>"), reply_markup=deposit_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

@dp.callback_query(F.data == "dep_crypto")
async def dep_crypto(c: CallbackQuery, state: FSMContext):
    await c.message.answer(p("✏️ Введите сумму для пополнения (мин. 💵0.15):"), reply_markup=cancel_kb("cancel_deposit"))
    await state.set_state(DepositState.wait_crypto)
    await c.answer()

@dp.callback_query(F.data == "cancel_deposit")
async def cancel_deposit(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await deposit_menu(c)
    await c.answer()

@dp.message(DepositState.wait_crypto, F.chat.type == "private")
async def process_crypto(msg: Message, state: FSMContext):
    try:
        amount = float(msg.text.replace(",", "."))
        if amount < 0.15:
            await msg.answer(p("❌ Минимальная сумма 💵0.15!"))
            return
        
        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
        data = {"asset": "USDT", "amount": str(amount)}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, timeout=10) as resp:
                result = await resp.json()
                if result.get("ok"):
                    invoice_url = result["result"]["bot_invoice_url"]
                    await msg.answer(
                        p(f"💳 Счет создан!\n\n"
                          f"💰 Сумма: 💵{amount:.2f} USDT\n"
                          f"🔗 <a href='{invoice_url}'>Оплатить</a>\n\n"
                          f"После оплаты нажмите кнопку ниже."),
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text=p("✅ Я оплатил"), callback_data=f"check_crypto_{amount}", icon_custom_emoji_id=PREMIUM_BUTTONS["check"])]
                        ]),
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await msg.answer(p("❌ Ошибка создания счета!"))
    except:
        await msg.answer(p("❌ Введите число!"))
    await state.clear()

@dp.callback_query(F.data.startswith("check_crypto_"))
async def check_crypto_payment(c: CallbackQuery):
    amount = float(c.data.split("_")[2])
    
    url = "https://pay.crypt.bot/api/getInvoices"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    params = {"asset": "USDT", "status": "paid"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params, timeout=10) as resp:
            result = await resp.json()
            if result.get("ok"):
                items = result.get("result", {}).get("items", [])
                for invoice in items:
                    if float(invoice.get("amount", 0)) == amount:
                        upd_bal(c.from_user.id, amount)
                        await c.message.edit_text(p(f"✅ Оплата подтверждена!\n\n💰 Баланс пополнен на 💵{amount:.2f}"))
                        await c.answer(p("✅ Баланс пополнен!"), show_alert=True)
                        return
    
    await c.answer(p("❌ Платеж не найден! Оплатите счет и нажмите снова."), show_alert=True)

# === STARS ОПЛАТА ===
@dp.callback_query(F.data == "dep_stars")
async def dep_stars(c: CallbackQuery):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    await c.message.edit_text(p("⭐️ <b>Пополнение через Telegram Stars</b>\n\nВыберите сумму:"), reply_markup=stars_amount_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

@dp.callback_query(F.data.startswith("stars_"))
async def stars_payment(c: CallbackQuery):
    stars = int(c.data.split("_")[1])
    amount_usd = stars * 0.011
    
    await c.message.answer_invoice(
        title=f"Покупка {stars} Stars",
        description=f"Вы покупаете {stars} Telegram Stars\nНа баланс будет начислено 💵{amount_usd:.2f}",
        payload=f"stars_{stars}_{c.from_user.id}",
        currency="XTR",
        prices=[LabeledPrice(label=f"{stars} Stars", amount=stars)],
        provider_token="",
        need_name=False,
        need_phone_number=False,
        need_email=False,
        start_parameter=f"stars_pay_{stars}"
    )
    await c.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def stars_payment_success(msg: Message):
    payload = msg.successful_payment.invoice_payload
    stars = int(payload.split("_")[1])
    amount_usd = stars * 0.011
    
    upd_bal(msg.from_user.id, amount_usd)
    
    await msg.answer(
        p(f"✅ Оплата прошла успешно!\n\n"
          f"⭐️ Куплено: {stars} Stars\n"
          f"💰 Начислено на баланс: 💵{amount_usd:.2f}\n\n"
          f"🎮 Приятной игры!")
    )

# === ВЫВОДЫ ===
class WithdrawState(StatesGroup):
    wait = State()

@dp.callback_query(F.data == "withdraw")
async def withdraw_menu(c: CallbackQuery, state: FSMContext):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    await c.message.answer(p(f"💰 Вывод средств\n\nМинимальная сумма: 💵{MIN_WITHDRAW:.2f}\nВведите сумму:"), reply_markup=cancel_kb("cancel_withdraw"))
    await state.set_state(WithdrawState.wait)
    await c.answer()

@dp.callback_query(F.data == "cancel_withdraw")
async def cancel_withdraw(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await profile_menu(c.message)
    await c.answer()

@dp.message(WithdrawState.wait, F.chat.type == "private")
async def process_withdraw(msg: Message, state: FSMContext):
    u = get_user(msg.from_user.id)
    try:
        amount = float(msg.text.replace(",", "."))
        if amount < MIN_WITHDRAW:
            await msg.answer(p(f"❌ Минимальная сумма 💵{MIN_WITHDRAW:.2f}!"))
            return
        if amount > u["balance"]:
            await msg.answer(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        upd_bal(msg.from_user.id, -amount)
        
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO withdraws (uid, amount, created) VALUES (?, ?, ?)", (msg.from_user.id, amount, datetime.now()))
        conn.commit()
        conn.close()
        
        for admin in ADMIN_IDS:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=p("✅ Одобрить"), callback_data=f"approve_{msg.from_user.id}_{amount}", icon_custom_emoji_id=PREMIUM_BUTTONS["check"]),
                 InlineKeyboardButton(text=p("❌ Отклонить"), callback_data=f"reject_{msg.from_user.id}_{amount}", icon_custom_emoji_id=PREMIUM_BUTTONS["cross"])]
            ])
            await bot.send_message(admin, p(f"💰 НОВАЯ ЗАЯВКА НА ВЫВОД!\n\n👤 {msg.from_user.id}\n💵 {amount:.2f}"), reply_markup=keyboard)
        
        await msg.answer(p(f"✅ Заявка на вывод 💵{amount:.2f} создана! Ожидайте подтверждения."))
    except:
        await msg.answer(p("❌ Введите число!"))
    await state.clear()

# === АДМИН ОБРАБОТЧИКИ (без премиум эмодзи) ===
@dp.message(Command("admin"))
async def admin_panel(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        await msg.answer("⛔ Доступ запрещен!")
        return
    
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT SUM(balance) FROM users")
    total_balance = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM withdraws WHERE status = 'pending'")
    pending_withdraws = cur.fetchone()[0]
    conn.close()
    
    await msg.answer(
        f"📊 Админ-панель\n\n"
        f"👥 Игроков: {total_users}\n"
        f"💰 Общий баланс: ${total_balance:.2f}\n"
        f"⏳ Заявок на вывод: {pending_withdraws}\n\n"
        "Команды:\n"
        "/withdraws - список заявок\n"
        "/approve id - одобрить вывод\n"
        "/reject id - отклонить вывод\n"
        "/add id сумма - пополнить баланс\n"
        "/remove id сумма - списать баланс\n"
        "/promo код сумма лимит - создать промокод\n"
        "/sendall текст - рассылка"
    )

@dp.message(Command("withdraws"))
async def list_withdraws(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT id, uid, amount, created FROM withdraws WHERE status = 'pending'")
    requests = cur.fetchall()
    conn.close()
    
    if not requests:
        await msg.answer("📭 Нет активных заявок")
        return
    
    for req in requests:
        await msg.answer(
            f"💰 Заявка #{req[0]}\n"
            f"👤 ID: {req[1]}\n"
            f"💵 Сумма: ${req[2]}\n"
            f"📅 {req[3]}\n\n"
            f"✅ /approve {req[0]}\n"
            f"❌ /reject {req[0]}"
        )

@dp.message(Command("approve"))
async def approve_withdraw(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    try:
        withdraw_id = int(msg.text.split()[1])
        
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT uid, amount FROM withdraws WHERE id = ? AND status = 'pending'", (withdraw_id,))
        req = cur.fetchone()
        
        if req:
            uid, amount = req
            cur.execute("UPDATE withdraws SET status = 'completed' WHERE id = ?", (withdraw_id,))
            conn.commit()
            await bot.send_message(uid, f"✅ Ваша заявка на вывод ${amount:.2f} ОДОБРЕНА!")
            await msg.answer(f"✅ Заявка #{withdraw_id} одобрена")
        else:
            await msg.answer("❌ Заявка не найдена")
        conn.close()
    except:
        await msg.answer("❌ /approve id")

@dp.message(Command("reject"))
async def reject_withdraw(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    try:
        withdraw_id = int(msg.text.split()[1])
        
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT uid, amount FROM withdraws WHERE id = ? AND status = 'pending'", (withdraw_id,))
        req = cur.fetchone()
        
        if req:
            uid, amount = req
            upd_bal(uid, amount)
            cur.execute("UPDATE withdraws SET status = 'rejected' WHERE id = ?", (withdraw_id,))
            conn.commit()
            await bot.send_message(uid, f"❌ Ваша заявка на вывод ${amount:.2f} ОТКЛОНЕНА. Деньги возвращены.")
            await msg.answer(f"❌ Заявка #{withdraw_id} отклонена")
        else:
            await msg.answer("❌ Заявка не найдена")
        conn.close()
    except:
        await msg.answer("❌ /reject id")

@dp.message(Command("add"))
async def admin_add_balance(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    try:
        parts = msg.text.split()
        user_id = int(parts[1])
        amount = float(parts[2])
        
        upd_bal(user_id, amount)
        await msg.answer(f"✅ Пользователю {user_id} начислено ${amount:.2f}")
        await bot.send_message(user_id, f"✅ Админ начислил вам ${amount:.2f}")
    except:
        await msg.answer("❌ /add id сумма")

@dp.message(Command("remove"))
async def admin_remove_balance(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    try:
        parts = msg.text.split()
        user_id = int(parts[1])
        amount = float(parts[2])
        
        upd_bal(user_id, -amount)
        await msg.answer(f"✅ У пользователя {user_id} списано ${amount:.2f}")
        await bot.send_message(user_id, f"⚠️ Админ списал ${amount:.2f} с баланса")
    except:
        await msg.answer("❌ /remove id сумма")

@dp.message(Command("promo"))
async def admin_create_promo(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    try:
        parts = msg.text.split()
        code = parts[1].upper()
        reward = float(parts[2])
        max_act = int(parts[3]) if len(parts) > 3 else 0
        
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO promos (code, reward, max_act, expires) VALUES (?, ?, ?, ?)",
                   (code, reward, max_act, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()
        
        await msg.answer(f"✅ Промокод {code} создан!\n💰 Награда: ${reward}\n🔢 Лимит: {max_act if max_act > 0 else '∞'}")
    except:
        await msg.answer("❌ /promo код сумма лимит")

@dp.message(Command("sendall"))
async def admin_mailing(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    text = msg.text.replace("/sendall ", "")
    if not text:
        await msg.answer("❌ /sendall текст")
        return
    
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT uid FROM users")
    users = cur.fetchall()
    conn.close()
    
    sent = 0
    for user in users:
        try:
            await bot.send_message(user[0], text)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass
    
    await msg.answer(f"✅ Рассылка завершена! Отправлено {sent} пользователям")

# === КОМАНДА /send ===
@dp.message(Command("send"), F.chat.type == "private")
async def send_money(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.answer("⚠️ Подпишитесь на канал!")
        return
    
    parts = msg.text.split()
    if len(parts) < 3:
        await msg.answer("❌ Использование: /send {сумма} {username или id}\n\nПример:\n/send 0.5 @username\n/send 1.5 123456789")
        return
    
    try:
        amount = float(parts[1].replace(",", "."))
        if amount < MIN_TRANSFER:
            await msg.answer(p(f"❌ Минимальная сумма перевода 💵{MIN_TRANSFER:.2f}!"))
            return
        
        u = get_user(msg.from_user.id)
        if amount > u["balance"]:
            await msg.answer(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        target = parts[2]
        target_id = None
        
        if target.startswith("@"):
            username = target[1:]
            conn = sqlite3.connect('data.db')
            cur = conn.cursor()
            cur.execute("SELECT uid FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            conn.close()
            if row:
                target_id = row[0]
        else:
            try:
                target_id = int(target)
            except:
                pass
        
        if not target_id or target_id == msg.from_user.id:
            await msg.answer(p("❌ Получатель не найден или это вы сами!"))
            return
        
        target_user = get_user(target_id)
        if target_user["balance"] is None:
            await msg.answer(p("❌ Пользователь не найден!"))
            return
        
        upd_bal(msg.from_user.id, -amount)
        upd_bal(target_id, amount)
        
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO transfers (from_uid, to_uid, amount, created) VALUES (?, ?, ?, ?)",
                   (msg.from_user.id, target_id, amount, datetime.now()))
        conn.commit()
        conn.close()
        
        await msg.answer(
            p(f"✅ Перевод выполнен!\n\n"
              f"📤 Отправитель: {msg.from_user.id}\n"
              f"📥 Получатель: {target_id}\n"
              f"💵 Сумма: 💵{amount:.2f}\n\n"
              f"💰 Ваш баланс: 💵{get_user(msg.from_user.id)['balance']:.2f}")
        )
        
        await bot.send_message(
            target_id,
            p(f"📥 Вам поступил перевод!\n\n"
              f"👤 От: {msg.from_user.id}\n"
              f"💵 Сумма: 💵{amount:.2f}\n\n"
              f"💰 Ваш баланс: 💵{get_user(target_id)['balance']:.2f}")
        )
    except:
        await msg.answer(p("❌ Ошибка! Использование: /send {сумма} {username или id}"))

# === ДУЭЛИ В ЧАТЕ ===
duels = {}

@dp.message(F.chat.type.in_(["group", "supergroup"]), Command("cub"))
async def create_duel(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.reply("⚠️ Подпишитесь на канал!")
        return
    
    try:
        bet = float(msg.text.split()[1].replace(",", "."))
        if bet < MIN_BET:
            await msg.reply(p(f"❌ Минимальная ставка 💵{MIN_BET:.2f}!"))
            return
        
        u = get_user(msg.from_user.id)
        if bet > u["balance"]:
            await msg.reply(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        upd_bal(msg.from_user.id, -bet)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Принять дуэль", callback_data=f"accept_duel_{bet}_{msg.from_user.id}", icon_custom_emoji_id=PREMIUM_BUTTONS["game"])]
        ])
        
        sent = await msg.reply(
            p(f"⚔️ Создана дуэль!\n\n"
              f"👤 Игрок №1: {msg.from_user.full_name}\n"
              f"👤 Игрок №2: ...\n"
              f"💰 Ставка: 💵{bet:.2f}\n\n"
              f"Нажмите кнопку ниже, чтобы принять дуэль!"),
            reply_markup=keyboard
        )
        
        duels[msg.chat.id] = {
            "player1": msg.from_user.id,
            "player1_name": msg.from_user.full_name,
            "amount": bet,
            "message_id": sent.message_id
        }
        
    except:
        await msg.reply(p("❌ Использование: /cub {ставка}\nПример: /cub 0.5"))

@dp.callback_query(F.data.startswith("accept_duel_"))
async def accept_duel(c: CallbackQuery):
    _, _, bet, player1_id = c.data.split("_")
    bet = float(bet)
    player1_id = int(player1_id)
    
    if c.from_user.id == player1_id:
        await c.answer(p("❌ Нельзя принять свою же дуэль!"), show_alert=True)
        return
    
    if c.message.chat.id not in duels:
        await c.answer(p("❌ Дуэль уже завершена или не существует!"), show_alert=True)
        return
    
    duel = duels[c.message.chat.id]
    if duel["player1"] != player1_id or duel["amount"] != bet:
        await c.answer(p("❌ Данные дуэли устарели!"), show_alert=True)
        return
    
    if not await check_subscription(c.from_user.id):
        await c.answer(p("❌ Подпишитесь на канал!"), show_alert=True)
        return
    
    u2 = get_user(c.from_user.id)
    if bet > u2["balance"]:
        await c.answer(p(f"❌ Недостаточно средств! Баланс: 💵{u2['balance']:.2f}"), show_alert=True)
        return
    
    upd_bal(c.from_user.id, -bet)
    
    duels[c.message.chat.id]["player2"] = c.from_user.id
    duels[c.message.chat.id]["player2_name"] = c.from_user.full_name
    
    await c.message.edit_text(
        p(f"⚔️ Дуэль началась!\n\n"
          f"👤 Игрок №1: {duel['player1_name']}\n"
          f"👤 Игрок №2: {c.from_user.full_name}\n"
          f"💰 Ставка: 💵{bet:.2f}\n\n"
          f"🎲 Кидаем кубики...")
    )
    
    await asyncio.sleep(2)
    
    dice1 = await bot.send_dice(c.message.chat.id, emoji="🎲")
    dice2 = await bot.send_dice(c.message.chat.id, emoji="🎲")
    
    value1 = dice1.dice.value
    value2 = dice2.dice.value
    
    result_text = p(f"🎲 Игрок №1 выбросил: {value1}\n🎲 Игрок №2 выбросил: {value2}\n\n")
    
    if value1 > value2:
        winner = duel["player1"]
        winner_name = duel["player1_name"]
        upd_bal(winner, bet * 2)
        upd_wagered(winner, bet)
        result_text += p(f"🏆 Победитель: {winner_name}\n💰 Выигрыш: 💵{bet * 2:.2f}")
    elif value2 > value1:
        winner = c.from_user.id
        winner_name = c.from_user.full_name
        upd_bal(winner, bet * 2)
        upd_wagered(winner, bet)
        result_text += p(f"🏆 Победитель: {winner_name}\n💰 Выигрыш: 💵{bet * 2:.2f}")
    else:
        upd_bal(duel["player1"], bet)
        upd_bal(c.from_user.id, bet)
        result_text += p(f"🤝 Ничья!\n💰 Ставки возвращены обоим игрокам.")
    
    await bot.send_message(c.message.chat.id, result_text)
    
    del duels[c.message.chat.id]
    await c.answer()

# === ИГРЫ В ЧАТЕ ===
@dp.message(F.chat.type.in_(["group", "supergroup"]), Command("dice"))
async def chat_dice(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.reply("⚠️ Подпишитесь на канал!")
        return
    
    try:
        bet = float(msg.text.split()[1].replace(",", "."))
        u = get_user(msg.from_user.id)
        if bet < MIN_BET:
            await msg.reply(p(f"❌ Минимальная ставка 💵{MIN_BET:.2f}!"))
            return
        if bet > u["balance"]:
            await msg.reply(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        upd_bal(msg.from_user.id, -bet)
        dice_msg = await msg.answer_dice(emoji="🎲")
        value = dice_msg.dice.value
        
        if value >= 4:
            mult = {4: 1.4, 5: 1.8, 6: 2.4}[value]
            win = bet * mult
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.reply(p(f"🎲 Выпало: {value}\n✅ Выигрыш: 💵{win:.2f} (x{mult})!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.reply(p(f"🎲 Выпало: {value}\n❌ Проигрыш: 💵{bet:.2f}!"))
    except:
        await msg.reply(p("❌ Использование: /dice {сумма}\nПример: /dice 0.5"))

@dp.message(F.chat.type.in_(["group", "supergroup"]), Command("football"))
async def chat_football(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.reply("⚠️ Подпишитесь на канал!")
        return
    
    try:
        bet = float(msg.text.split()[1].replace(",", "."))
        u = get_user(msg.from_user.id)
        if bet < MIN_BET:
            await msg.reply(p(f"❌ Минимальная ставка 💵{MIN_BET:.2f}!"))
            return
        if bet > u["balance"]:
            await msg.reply(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        upd_bal(msg.from_user.id, -bet)
        football_msg = await msg.answer_dice(emoji="⚽️")
        value = football_msg.dice.value
        
        if value >= 4:
            win = bet * 1.3
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.reply(p(f"⚽️ ГОЛ! ✅ Выигрыш: 💵{win:.2f} (x1.3)!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.reply(p(f"⚽️ Мимо ворот! ❌ Проигрыш: 💵{bet:.2f}!"))
    except:
        await msg.reply(p("❌ Использование: /football {сумма}\nПример: /football 0.5"))

@dp.message(F.chat.type.in_(["group", "supergroup"]), Command("target"))
async def chat_target(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.reply("⚠️ Подпишитесь на канал!")
        return
    
    try:
        bet = float(msg.text.split()[1].replace(",", "."))
        u = get_user(msg.from_user.id)
        if bet < MIN_BET:
            await msg.reply(p(f"❌ Минимальная ставка 💵{MIN_BET:.2f}!"))
            return
        if bet > u["balance"]:
            await msg.reply(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        upd_bal(msg.from_user.id, -bet)
        target_msg = await msg.answer_dice(emoji="🎯")
        value = target_msg.dice.value
        
        if value >= 5:
            win = bet * 5
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.reply(p(f"🎯 В ЦЕНТР! ✅ Выигрыш: 💵{win:.2f} (x5)!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.reply(p(f"🎯 Мимо! ❌ Проигрыш: 💵{bet:.2f}!"))
    except:
        await msg.reply(p("❌ Использование: /target {сумма}\nПример: /target 0.5"))

# === ЗАПУСК ===
async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="help", description="❓ Помощь"),
        BotCommand(command="balance", description="💰 Баланс"),
        BotCommand(command="dice", description="🎲 Кости"),
        BotCommand(command="football", description="⚽️ Футбол"),
        BotCommand(command="target", description="🎯 Дартс"),
        BotCommand(command="cub", description="⚔️ Дуэль"),
        BotCommand(command="send", description="📤 Перевод"),
        BotCommand(command="admin", description="👑 Админ"),
    ])
    logging.info("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())"
CRYPTOBOT_TOKEN = "594394:AAqYLgin8OMpwWvpBXCDiNGcpnGHJ5NDXPn"
ADMIN_IDS = [7966949924]
BOT_USERNAME = "SecondCasBOT"
CHAT_LINK = "https://t.me/SecondProjectChat"
REQUIRED_CHANNEL_ID = -1003948376817

MIN_BET = 0.10
MIN_WITHDRAW = 1.10
COOLDOWN = 3
MIN_TRANSFER = 0.10

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === ID ПРЕМИУМ ЭМОДЗИ ДЛЯ КНОПОК (НЕ ТРОГАЕМ) ===
PREMIUM_BUTTONS = {
    "game": "5258508428212445001",
    "profile": "5879770735999717115",
    "deposit": "5258043150110301407",
    "withdraw": "5258336354642697821",
    "gift": "5226731292334235524",
    "ref": "5879770735999717115",
    "send": "5258336354642697821",
    "back": "5258336354642697821",
    "chat": "5258501105293205250",
    "crypto": "5377820717024842074",
    "star": "5958376256788502078",
    "check": "5238078046174456159",
    "cross": "5238078046174456159",
}

# ========== ФУНКЦИЯ ДЛЯ ПРЕМИУМ ЭМОДЗИ В ТЕКСТАХ ==========
def p(text: str) -> str:
    """Заменяет обычные эмодзи на премиум в текстах"""
    replacements = {
        "💰": '<tg-emoji emoji-id="5377452788651429834">💰</tg-emoji>',
        "💵": '<tg-emoji emoji-id="5377452788651429834">💵</tg-emoji>',
        "⚡️": '<tg-emoji emoji-id="5377444769947490089">⚡️</tg-emoji>',
        "🎮": '<tg-emoji emoji-id="5258508428212445001">🎮</tg-emoji>',
        "👤": '<tg-emoji emoji-id="5879770735999717115">👤</tg-emoji>',
        "⏰": '<tg-emoji emoji-id="5778605968208170641">⏰</tg-emoji>',
        "💳": '<tg-emoji emoji-id="5258043150110301407">💳</tg-emoji>',
        "🎁": '<tg-emoji emoji-id="5226731292334235524">🎁</tg-emoji>',
        "👥": '<tg-emoji emoji-id="5879770735999717115">👥</tg-emoji>',
        "⭐️": '<tg-emoji emoji-id="5958376256788502078">⭐️</tg-emoji>',
        "💎": '<tg-emoji emoji-id="5377820717024842074">💎</tg-emoji>',
        "✅": '<tg-emoji emoji-id="5238078046174456159">✅</tg-emoji>',
        "❌": '<tg-emoji emoji-id="5238078046174456159">❌</tg-emoji>',
        "⚠️": '<tg-emoji emoji-id="5238078046174456159">⚠️</tg-emoji>',
        "🔙": '<tg-emoji emoji-id="5258336354642697821">🔙</tg-emoji>',
        "🏆": '<tg-emoji emoji-id="5235702276424737428">🏆</tg-emoji>',
        "🎉": '<tg-emoji emoji-id="5238078046174456159">🎉</tg-emoji>',
        "📤": '<tg-emoji emoji-id="5258336354642697821">📤</tg-emoji>',
        "💬": '<tg-emoji emoji-id="5258501105293205250">💬</tg-emoji>',
        "🗼": '<tg-emoji emoji-id="5377444769947490089">🗼</tg-emoji>',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# ========== КЛАВИАТУРЫ (НЕ ТРОГАЕМ) ==========
def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text=" Игры в боте", icon_custom_emoji_id=PREMIUM_BUTTONS["game"]),
            KeyboardButton(text=" Профиль", icon_custom_emoji_id=PREMIUM_BUTTONS["profile"])
        ]],
        resize_keyboard=True
    )

def games_kb():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="🎲", callback_data="game_dice"),
        InlineKeyboardButton(text="⚽️", callback_data="game_football"),
        InlineKeyboardButton(text="🎯", callback_data="game_target"),
        InlineKeyboardButton(text="🗼", callback_data="game_tower")
    )
    b.row(InlineKeyboardButton(text=" Чат", url=CHAT_LINK, icon_custom_emoji_id=PREMIUM_BUTTONS["chat"]))
    b.row(InlineKeyboardButton(text=" Назад", callback_data="back_main", icon_custom_emoji_id=PREMIUM_BUTTONS["back"]))
    return b.as_markup()

def profile_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Пополнить", callback_data="deposit", icon_custom_emoji_id=PREMIUM_BUTTONS["deposit"]),
         InlineKeyboardButton(text=" Вывести", callback_data="withdraw", icon_custom_emoji_id=PREMIUM_BUTTONS["withdraw"])],
        [InlineKeyboardButton(text=" Промокоды", callback_data="promo", icon_custom_emoji_id=PREMIUM_BUTTONS["gift"]),
         InlineKeyboardButton(text=" Рефералы", callback_data="ref", icon_custom_emoji_id=PREMIUM_BUTTONS["ref"])],
        [InlineKeyboardButton(text=" Перевод", callback_data="transfer", icon_custom_emoji_id=PREMIUM_BUTTONS["send"]),
         InlineKeyboardButton(text=" Назад", callback_data="back_main", icon_custom_emoji_id=PREMIUM_BUTTONS["back"])]
    ])

def deposit_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" CryptoBot", callback_data="dep_crypto", icon_custom_emoji_id=PREMIUM_BUTTONS["crypto"])],
        [InlineKeyboardButton(text=" Stars", callback_data="dep_stars", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" Назад", callback_data="back_profile", icon_custom_emoji_id=PREMIUM_BUTTONS["back"])]
    ])

def stars_amount_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" 50 Stars ($0.55)", callback_data="stars_50", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" 100 Stars ($1.10)", callback_data="stars_100", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" 250 Stars ($2.75)", callback_data="stars_250", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" 500 Stars ($5.50)", callback_data="stars_500", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" 1000 Stars ($11.00)", callback_data="stars_1000", icon_custom_emoji_id=PREMIUM_BUTTONS["star"])],
        [InlineKeyboardButton(text=" Назад", callback_data="back_deposit", icon_custom_emoji_id=PREMIUM_BUTTONS["back"])]
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Назад", callback_data="back_profile", icon_custom_emoji_id=PREMIUM_BUTTONS["back"])]
    ])

def cancel_kb(callback_data: str = "cancel"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Отмена", callback_data=callback_data, icon_custom_emoji_id=PREMIUM_BUTTONS["cross"])]
    ])

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        uid INTEGER PRIMARY KEY,
        balance REAL DEFAULT 0,
        reg TEXT,
        deposit REAL DEFAULT 0,
        wagered REAL DEFAULT 0,
        lost REAL DEFAULT 0,
        ref_id INTEGER,
        ref_earn REAL DEFAULT 0,
        ref_cnt INTEGER DEFAULT 0,
        ref_dep_cnt INTEGER DEFAULT 0,
        last_bet REAL DEFAULT 0,
        subscribed INTEGER DEFAULT 0,
        username TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS withdraws (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER,
        amount REAL,
        status TEXT DEFAULT 'pending',
        created TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS promos (
        code TEXT PRIMARY KEY,
        reward REAL,
        max_act INTEGER,
        activated INTEGER DEFAULT 0,
        expires TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS promo_used (
        code TEXT,
        uid INTEGER
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_uid INTEGER,
        to_uid INTEGER,
        amount REAL,
        created TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS duels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        player1 INTEGER,
        player2 INTEGER,
        amount REAL,
        status TEXT DEFAULT 'waiting',
        created TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def get_user(uid: int) -> Dict:
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE uid = ?", (uid,))
    u = cur.fetchone()
    conn.close()
    if not u:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users (uid, reg, last_bet, subscribed) VALUES (?, ?, 0, 0)", (uid, datetime.now()))
        conn.commit()
        conn.close()
        return {"uid": uid, "balance": 0, "reg": datetime.now(), "wagered": 0, "lost": 0,
                "ref_cnt": 0, "ref_earn": 0, "last_bet": 0, "subscribed": 0, "username": None}
    return {"uid": u[0], "balance": u[1], "reg": datetime.strptime(u[2], "%Y-%m-%d %H:%M:%S.%f"),
            "wagered": u[4], "lost": u[5], "ref_id": u[6], "ref_earn": u[7],
            "ref_cnt": u[8], "ref_dep_cnt": u[9], "last_bet": u[10], "subscribed": u[11], "username": u[12]}

def upd_bal(uid: int, amt: float):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE uid = ?", (amt, uid))
    conn.commit()
    conn.close()

def upd_username(uid: int, username: str):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET username = ? WHERE uid = ?", (username, uid))
    conn.commit()
    conn.close()

def upd_wagered(uid: int, amt: float):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET wagered = wagered + ? WHERE uid = ?", (amt, uid))
    conn.commit()
    conn.close()

def upd_lost(uid: int, amt: float):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET lost = lost + ? WHERE uid = ?", (amt, uid))
    conn.commit()
    conn.close()

def upd_last_bet(uid: int):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_bet = ? WHERE uid = ?", (datetime.now().timestamp(), uid))
    conn.commit()
    conn.close()

def upd_subscribed(uid: int, val: int = 1):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET subscribed = ? WHERE uid = ?", (val, uid))
    conn.commit()
    conn.close()

def can_bet(uid: int):
    u = get_user(uid)
    now = datetime.now().timestamp()
    if now - u["last_bet"] < COOLDOWN:
        return False, COOLDOWN - (now - u["last_bet"])
    return True, 0

# ========== ПРОВЕРКА ПОДПИСКИ ==========
async def check_subscription(uid: int) -> bool:
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL_ID, uid)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            user = get_user(uid)
            if user.get("subscribed", 0) == 0:
                upd_subscribed(uid, 1)
                if user.get("ref_id") and user.get("ref_id") > 0:
                    upd_bal(user["ref_id"], 1)
                    conn = sqlite3.connect('data.db')
                    cur = conn.cursor()
                    cur.execute("UPDATE users SET ref_earn = ref_earn + 1, ref_dep_cnt = ref_dep_cnt + 1 WHERE uid = ?", (user["ref_id"],))
                    conn.commit()
                    conn.close()
            return True
        return False
    except:
        return False

# ========== ОСНОВНЫЕ ОБРАБОТЧИКИ ==========
@dp.message(Command("start"), F.chat.type == "private")
async def start(msg: Message):
    if msg.from_user.username:
        upd_username(msg.from_user.id, msg.from_user.username)
    
    get_user(msg.from_user.id)
    
    args = msg.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != msg.from_user.id:
            u = get_user(msg.from_user.id)
            if u.get("ref_id") is None and u.get("subscribed") == 0:
                conn = sqlite3.connect('data.db')
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM users WHERE uid = ?", (ref_id,))
                if cur.fetchone():
                    cur.execute("UPDATE users SET ref_id = ?, ref_cnt = ref_cnt + 1 WHERE uid = ?", (ref_id, msg.from_user.id))
                    conn.commit()
                conn.close()
    
    if await check_subscription(msg.from_user.id):
        txt = p("""💰 <b>Деньги есть всегда!</b>

⚡️ <b>Бот с играми и дуэлями</b>
⚡️ <b>Быстрые ставки, моментальные выводы</b>
💵 <b>Доход с рефералов</b>
<i>От 💵100 в день — реально</i>""")
        await msg.answer(txt, reply_markup=main_kb(), parse_mode=ParseMode.HTML)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться", url="https://t.me/SecondNewsRU", icon_custom_emoji_id=PREMIUM_BUTTONS["chat"])],
            [InlineKeyboardButton(text="✅ Проверить", callback_data="check_sub", icon_custom_emoji_id=PREMIUM_BUTTONS["check"])]
        ])
        await msg.answer(
            "⚠️ <b>Для использования бота необходимо подписаться на наш канал!</b>\n\n👇 Нажмите на кнопку ниже, подпишитесь и нажмите «Проверить подписку»",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(c: CallbackQuery):
    if await check_subscription(c.from_user.id):
        await c.message.delete()
        await start(c.message)
        await c.answer("✅ Подписка подтверждена! Добро пожаловать!", show_alert=True)
    else:
        await c.answer("❌ Вы не подписаны на канал! Подпишитесь и нажмите снова.", show_alert=True)

# === HELP ===
@dp.message(Command("help"), F.chat.type == "private")
@dp.message(Command("help"), F.chat.type.in_(["group", "supergroup"]))
async def help_cmd(msg: Message):
    await msg.answer(
        p("🎮 <b>Доступные команды:</b>\n\n"
          "💰 <b>Баланс</b> — /balance\n"
          "🎲 <b>Кости</b> — /dice {сумма}\n"
          "⚽️ <b>Футбол</b> — /football {сумма}\n"
          "🎯 <b>Дартс</b> — /target {сумма}\n"
          "⚔️ <b>Дуэль</b> — /cub {ставка}\n\n"
          "📤 <b>Перевод</b> — /send {сумма} @username\n\n"
          "⭐️ <b>Пополнение</b> — в личных сообщениях с ботом\n"
          "💸 <b>Вывод</b> — в личных сообщениях с ботом\n\n"
          "<i>Подпишись на канал для игры!</i>"),
        parse_mode=ParseMode.HTML
    )

# === БАЛАНС ===
@dp.message(Command("balance"), F.chat.type == "private")
@dp.message(Command("balance"), F.chat.type.in_(["group", "supergroup"]))
@dp.message(F.text.lower().in_(["баланс", "б", "b", "бал", "мешок", "гроши"]), F.chat.type.in_(["group", "supergroup"]))
async def balance_cmd(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.reply("⚠️ Подпишитесь на канал!")
        return
    u = get_user(msg.from_user.id)
    await msg.reply(p(f"💰 Ваш баланс: 💵{u['balance']:.2f}"))

# === ИГРЫ В ЛИЧКЕ ===
@dp.message(F.text.in_(["🎮 Игры в боте", "Игры в боте"]), F.chat.type == "private")
async def games_menu(msg: Message):
    if not await check_subscription(msg.from_user.id):
        return
    u = get_user(msg.from_user.id)
    txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u['balance']:.2f}")
    await msg.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)

@dp.message(F.text.in_(["👤 Профиль", "Профиль"]), F.chat.type == "private")
async def profile_menu(msg: Message):
    if not await check_subscription(msg.from_user.id):
        return
    u = get_user(msg.from_user.id)
    days = (datetime.now() - u["reg"]).days
    txt = p(f"👤 <b>Ваш профиль</b>\n\n💰 Баланс: <b>💵{u['balance']:.2f}</b>\n⏰ Дней в боте: <b>{days}</b>")
    await msg.answer(txt, reply_markup=profile_kb(), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "back_main")
async def back_main(c: CallbackQuery):
    await c.message.delete()
    txt = p("""💰 <b>Деньги есть всегда!</b>

⚡️ <b>Бот с играми и дуэлями</b>
⚡️ <b>Быстрые ставки, моментальные выводы</b>
💵 <b>Доход с рефералов</b>
<i>От 💵100 в день — реально</i>""")
    await c.message.answer(txt, reply_markup=main_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

@dp.callback_query(F.data == "back_profile")
async def back_profile(c: CallbackQuery):
    await c.message.delete()
    u = get_user(c.from_user.id)
    days = (datetime.now() - u["reg"]).days
    txt = p(f"👤 <b>Ваш профиль</b>\n\n💰 Баланс: <b>💵{u['balance']:.2f}</b>\n⏰ Дней в боте: <b>{days}</b>")
    await c.message.answer(txt, reply_markup=profile_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

@dp.callback_query(F.data == "back_deposit")
async def back_deposit(c: CallbackQuery):
    await c.message.edit_text(p("💳 <b>Пополнение средств</b>"), reply_markup=deposit_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

# === РЕФЕРАЛКА ===
@dp.callback_query(F.data == "ref")
async def ref_prog(c: CallbackQuery):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    u = get_user(c.from_user.id)
    txt = p(f"""👥 <b>Реферальная программа</b>

👥 Рефералы: {u["ref_cnt"]} (пополнили: {u["ref_dep_cnt"]})
💵 Заработано: 💵{u["ref_earn"]:.2f}

<b>Условия:</b>
• 💵 1💵 за друга с депозитом от 5💵
• 💵 10% от проигрышей по пятницам

<b>Бонусы:</b>
• 100 друзей → +5💵
• 250 друзей → +15💵
• 500 друзей → +30💵
• 1000 друзей → +60💵

🏆 До бонуса: {max(0, 100 - u["ref_cnt"])} рефералов

🔗 Реферальная ссылка:
https://t.me/{BOT_USERNAME}?start={c.from_user.id}""")
    await c.message.edit_text(txt, reply_markup=back_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

# === ПРОМОКОДЫ ===
class PromoState(StatesGroup):
    wait = State()

@dp.callback_query(F.data == "promo")
async def promo_menu(c: CallbackQuery, state: FSMContext):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    txt = p("🎁 <b>Введи промокод:</b>\n\nПросто напиши код в чат — и бонус зачислится автоматически.")
    await c.message.edit_text(txt, reply_markup=back_kb(), parse_mode=ParseMode.HTML)
    await state.set_state(PromoState.wait)
    await c.answer()

@dp.message(PromoState.wait, F.chat.type == "private")
async def promo_use(msg: Message, state: FSMContext):
    code = msg.text.upper()
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM promos WHERE code = ?", (code,))
    p = cur.fetchone()
    if not p:
        await msg.answer(p("⭐️ Промокод не найден!"), reply_markup=back_kb())
        await state.clear()
        return
    cur.execute("SELECT 1 FROM promo_used WHERE code = ? AND uid = ?", (code, msg.from_user.id))
    if cur.fetchone():
        await msg.answer(p("⭐️ Вы уже активировали этот промокод!"), reply_markup=back_kb())
        await state.clear()
        return
    if p[3] >= p[2] and p[2] > 0:
        await msg.answer(p("⭐️ Промокод достиг лимита!"), reply_markup=back_kb())
        await state.clear()
        return
    upd_bal(msg.from_user.id, p[1])
    cur.execute("INSERT INTO promo_used VALUES (?, ?)", (code, msg.from_user.id))
    cur.execute("UPDATE promos SET activated = activated + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    await msg.answer(p(f"🎉 Промокод активирован! +💵{p[1]:.2f} на баланс!"))
    await state.clear()

# === ПЕРЕВОД ===
class TransferState(StatesGroup):
    waiting_amount = State()
    waiting_target = State()

@dp.callback_query(F.data == "transfer")
async def transfer_start(c: CallbackQuery, state: FSMContext):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    
    await c.message.edit_text(
        p(f"📤 <b>Перевод средств</b>\n\nВведите сумму перевода (мин. 💵{MIN_TRANSFER:.2f}):"),
        reply_markup=cancel_kb("cancel_transfer"),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(TransferState.waiting_amount)
    await c.answer()

@dp.message(TransferState.waiting_amount, F.chat.type == "private")
async def transfer_amount(msg: Message, state: FSMContext):
    try:
        amount = float(msg.text.replace(",", "."))
        if amount < MIN_TRANSFER:
            await msg.answer(p(f"❌ Минимальная сумма перевода 💵{MIN_TRANSFER:.2f}!"))
            return
        
        u = get_user(msg.from_user.id)
        if amount > u["balance"]:
            await msg.answer(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        await state.update_data(transfer_amount=amount)
        await msg.answer(
            p("📤 Введите username или ID получателя:\n\nПримеры:\n• @username\n• 123456789"),
            reply_markup=cancel_kb("cancel_transfer")
        )
        await state.set_state(TransferState.waiting_target)
    except:
        await msg.answer(p("❌ Введите число!"))

@dp.message(TransferState.waiting_target, F.chat.type == "private")
async def transfer_target(msg: Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("transfer_amount")
    
    target_id = None
    if msg.text.startswith("@"):
        username = msg.text[1:]
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT uid FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        if row:
            target_id = row[0]
    else:
        try:
            target_id = int(msg.text)
        except:
            pass
    
    if not target_id or target_id == msg.from_user.id:
        await msg.answer(p("❌ Получатель не найден или это вы сами!"))
        return
    
    target = get_user(target_id)
    if target["balance"] is None:
        await msg.answer(p("❌ Пользователь не найден!"))
        return
    
    upd_bal(msg.from_user.id, -amount)
    upd_bal(target_id, amount)
    
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO transfers (from_uid, to_uid, amount, created) VALUES (?, ?, ?, ?)",
               (msg.from_user.id, target_id, amount, datetime.now()))
    conn.commit()
    conn.close()
    
    await msg.answer(
        p(f"✅ Перевод выполнен!\n\n"
          f"📤 Отправитель: {msg.from_user.id}\n"
          f"📥 Получатель: {target_id}\n"
          f"💵 Сумма: 💵{amount:.2f}\n\n"
          f"💰 Ваш баланс: 💵{get_user(msg.from_user.id)['balance']:.2f}")
    )
    
    await bot.send_message(
        target_id,
        p(f"📥 Вам поступил перевод!\n\n"
          f"👤 От: {msg.from_user.id}\n"
          f"💵 Сумма: 💵{amount:.2f}\n\n"
          f"💰 Ваш баланс: 💵{get_user(target_id)['balance']:.2f}")
    )
    
    await state.clear()

@dp.callback_query(F.data == "cancel_transfer")
async def cancel_transfer(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await back_profile(c)

# === АНИМИРОВАННЫЕ ИГРЫ ===
class BetState(StatesGroup):
    wait = State()

class TowerState(StatesGroup):
    play = State()

@dp.callback_query(F.data.startswith("game_"))
async def game_start(c: CallbackQuery, state: FSMContext):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    
    game = c.data.split("_")[1]
    await c.message.answer(p(f"✏️ Введите сумму ставки (мин. 💵{MIN_BET:.2f})"), reply_markup=cancel_kb("cancel_bet"))
    await state.update_data(game=game)
    await state.set_state(BetState.wait)
    await c.answer()

@dp.callback_query(F.data == "cancel_bet")
async def cancel_bet(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await games_menu(c.message)
    await c.answer()

@dp.message(BetState.wait, F.chat.type == "private")
async def process_bet(msg: Message, state: FSMContext):
    u = get_user(msg.from_user.id)
    data = await state.get_data()
    game = data.get("game")
    
    try:
        bet = float(msg.text.replace(",", "."))
        if bet < MIN_BET:
            await msg.answer(p(f"❌ Минимальная ставка 💵{MIN_BET:.2f}!"))
            return
        if bet > u["balance"]:
            await msg.answer(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
    except:
        await msg.answer(p("❌ Введите число!"))
        return
    
    upd_bal(msg.from_user.id, -bet)
    
    if game == "dice":
        dice_msg = await msg.answer_dice(emoji="🎲")
        value = dice_msg.dice.value
        
        if value >= 4:
            mult = {4: 1.4, 5: 1.8, 6: 2.4}[value]
            win = bet * mult
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.answer(p(f"🎲 Выпало: {value}\n✅ Выигрыш: 💵{win:.2f} (x{mult})!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.answer(p(f"🎲 Выпало: {value}\n❌ Проигрыш: 💵{bet:.2f}!"))
    
    elif game == "football":
        football_msg = await msg.answer_dice(emoji="⚽️")
        value = football_msg.dice.value
        
        if value >= 4:
            win = bet * 1.3
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.answer(p(f"⚽️ ГОЛ! ✅ Выигрыш: 💵{win:.2f} (x1.3)!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.answer(p(f"⚽️ Мимо ворот! ❌ Проигрыш: 💵{bet:.2f}!"))
    
    elif game == "target":
        target_msg = await msg.answer_dice(emoji="🎯")
        value = target_msg.dice.value
        
        if value >= 5:
            win = bet * 5
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.answer(p(f"🎯 В ЦЕНТР! ✅ Выигрыш: 💵{win:.2f} (x5)!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.answer(p(f"🎯 Мимо! ❌ Проигрыш: 💵{bet:.2f}!"))
    
    elif game == "tower":
        await state.update_data(tower_bet=bet, tower_level=0, tower_mult=1.0)
        await state.set_state(TowerState.play)
        await play_tower(msg, state, 0, 1.0, bet)
        return
    
    await state.clear()
    u2 = get_user(msg.from_user.id)
    txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u2['balance']:.2f}")
    await msg.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)

# === БАШНЯ ===
async def play_tower(msg: Message, state: FSMContext, level: int, mult: float, bet: float):
    multipliers = [1.4, 1.7, 2.4, 3.2, 4.0, 6.0]
    
    if level >= len(multipliers):
        win = bet * multipliers[-1]
        upd_bal(msg.from_user.id, win)
        upd_wagered(msg.from_user.id, bet)
        await msg.answer(p(f"🏆 ПОЛНАЯ ПОБЕДА! 🏆\n🗼 Вы прошли все 6 уровней!\n💰 Выигрыш: 💵{win:.2f} (x{multipliers[-1]})!"))
        await state.clear()
        u = get_user(msg.from_user.id)
        txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u['balance']:.2f}")
        await msg.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)
        return
    
    bomb = random.randint(0, 1)
    await state.update_data(tower_bomb=bomb, tower_level=level, tower_bet=bet, tower_mult=mult)
    
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="⬅️ Левая 🟩", callback_data="tower_left"),
        InlineKeyboardButton(text="Правая 🟩 ➡️", callback_data="tower_right")
    )
    if level > 0:
        b.row(InlineKeyboardButton(text=p(f"💰 Забрать 💵{bet * mult:.2f}"), callback_data="tower_cashout"))
    b.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_tower", icon_custom_emoji_id=PREMIUM_BUTTONS["cross"]))
    
    await msg.answer(
        p(f"🗼 БАШНЯ - Уровень {level + 1}/6\n"
          f"💰 Ставка: 💵{bet:.2f}\n"
          f"📈 Множитель: x{multipliers[level]} (выигрыш: 💵{bet * multipliers[level]:.2f})\n"
          f"💥 В одной из клеток БОМБА!\n\n"
          f"Выбери клетку:"),
        reply_markup=b.as_markup()
    )

@dp.callback_query(F.data == "cancel_tower")
async def cancel_tower(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await games_menu(c.message)
    await c.answer()

@dp.callback_query(TowerState.play, F.data.in_(["tower_left", "tower_right", "tower_cashout"]))
async def tower_choice(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await c.answer(p("❌ Игра не найдена!"))
        return
    
    if c.data == "tower_cashout":
        bet = data.get("tower_bet", 0)
        mult = data.get("tower_mult", 1.0)
        level = data.get("tower_level", 0)
        if level == 0:
            await c.answer(p("⚠️ Нужно открыть хотя бы одну клетку!"), show_alert=True)
            return
        win = bet * mult
        upd_bal(c.from_user.id, win)
        upd_wagered(c.from_user.id, bet)
        await c.message.edit_text(p(f"💰 ВЫ ЗАБРАЛИ ВЫИГРЫШ! 💰\n🗼 Пройдено уровней: {level}/6\n✅ Выигрыш: 💵{win:.2f} (x{mult})!"))
        await state.clear()
        u = get_user(c.from_user.id)
        txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u['balance']:.2f}")
        await c.message.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)
        await c.answer()
        return
    
    bomb = data.get("tower_bomb")
    level = data.get("tower_level", 0)
    bet = data.get("tower_bet", 0)
    mult = data.get("tower_mult", 1.0)
    multipliers = [1.4, 1.7, 2.4, 3.2, 4.0, 6.0]
    chosen = 0 if c.data == "tower_left" else 1
    
    if chosen == bomb:
        upd_lost(c.from_user.id, bet)
        await c.message.edit_text(p(f"💥 БОМБА ВЗОРВАЛАСЬ! 💥\n🗼 Вы проиграли на уровне {level + 1}/6\n💰 Потеряно: 💵{bet:.2f}\n\n🎮 Попробуйте снова!"))
        await state.clear()
        u = get_user(c.from_user.id)
        txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u['balance']:.2f}")
        await c.message.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)
    else:
        level += 1
        new_mult = multipliers[level - 1]
        await c.message.edit_text(p(f"✅ БЕЗОПАСНО! 🟩\n🗼 Уровень {level}/6 пройден!\n💰 Текущий выигрыш: 💵{bet * new_mult:.2f} (x{new_mult})\n\n🎲 Продолжаем?"))
        
        if level >= len(multipliers):
            win = bet * multipliers[-1]
            upd_bal(c.from_user.id, win)
            upd_wagered(c.from_user.id, bet)
            await c.message.answer(p(f"🏆 ПОБЕДА! 🏆\n🗼 Вы прошли ВСЕ 6 уровней!\n💰 Выигрыш: 💵{win:.2f} (x{multipliers[-1]})!"))
            await state.clear()
            u = get_user(c.from_user.id)
            txt = p(f"🎮 <b>Выберите игру!</b>\n\n💰 Баланс: 💵{u['balance']:.2f}")
            await c.message.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)
        else:
            await state.update_data(tower_level=level, tower_mult=new_mult)
            new_bomb = random.randint(0, 1)
            await state.update_data(tower_bomb=new_bomb)
            b = InlineKeyboardBuilder()
            b.row(
                InlineKeyboardButton(text="⬅️ Левая 🟩", callback_data="tower_left"),
                InlineKeyboardButton(text="Правая 🟩 ➡️", callback_data="tower_right")
            )
            b.row(InlineKeyboardButton(text=p(f"💰 Забрать 💵{bet * new_mult:.2f}"), callback_data="tower_cashout"))
            b.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_tower", icon_custom_emoji_id=PREMIUM_BUTTONS["cross"]))
            await c.message.answer(
                p(f"🗼 БАШНЯ - Уровень {level + 1}/6\n"
                  f"💰 Ставка: 💵{bet:.2f}\n"
                  f"📈 Множитель: x{multipliers[level]} (выигрыш: 💵{bet * multipliers[level]:.2f})\n"
                  f"💥 В одной из клеток БОМБА!\n\n"
                  f"Выбери клетку:"),
                reply_markup=b.as_markup()
            )
    await c.answer()

# === ДЕПОЗИТЫ ===
class DepositState(StatesGroup):
    wait_crypto = State()

@dp.callback_query(F.data == "deposit")
async def deposit_menu(c: CallbackQuery):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    await c.message.edit_text(p("💳 <b>Пополнение средств</b>"), reply_markup=deposit_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

@dp.callback_query(F.data == "dep_crypto")
async def dep_crypto(c: CallbackQuery, state: FSMContext):
    await c.message.answer(p("✏️ Введите сумму для пополнения (мин. 💵0.15):"), reply_markup=cancel_kb("cancel_deposit"))
    await state.set_state(DepositState.wait_crypto)
    await c.answer()

@dp.callback_query(F.data == "cancel_deposit")
async def cancel_deposit(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await deposit_menu(c)
    await c.answer()

@dp.message(DepositState.wait_crypto, F.chat.type == "private")
async def process_crypto(msg: Message, state: FSMContext):
    try:
        amount = float(msg.text.replace(",", "."))
        if amount < 0.15:
            await msg.answer(p("❌ Минимальная сумма 💵0.15!"))
            return
        
        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
        data = {"asset": "USDT", "amount": str(amount)}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, timeout=10) as resp:
                result = await resp.json()
                if result.get("ok"):
                    invoice_url = result["result"]["bot_invoice_url"]
                    await msg.answer(
                        p(f"💳 Счет создан!\n\n"
                          f"💰 Сумма: 💵{amount:.2f} USDT\n"
                          f"🔗 <a href='{invoice_url}'>Оплатить</a>\n\n"
                          f"После оплаты нажмите кнопку ниже."),
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text=p("✅ Я оплатил"), callback_data=f"check_crypto_{amount}", icon_custom_emoji_id=PREMIUM_BUTTONS["check"])]
                        ]),
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await msg.answer(p("❌ Ошибка создания счета!"))
    except:
        await msg.answer(p("❌ Введите число!"))
    await state.clear()

@dp.callback_query(F.data.startswith("check_crypto_"))
async def check_crypto_payment(c: CallbackQuery):
    amount = float(c.data.split("_")[2])
    
    url = "https://pay.crypt.bot/api/getInvoices"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    params = {"asset": "USDT", "status": "paid"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params, timeout=10) as resp:
            result = await resp.json()
            if result.get("ok"):
                items = result.get("result", {}).get("items", [])
                for invoice in items:
                    if float(invoice.get("amount", 0)) == amount:
                        upd_bal(c.from_user.id, amount)
                        await c.message.edit_text(p(f"✅ Оплата подтверждена!\n\n💰 Баланс пополнен на 💵{amount:.2f}"))
                        await c.answer(p("✅ Баланс пополнен!"), show_alert=True)
                        return
    
    await c.answer(p("❌ Платеж не найден! Оплатите счет и нажмите снова."), show_alert=True)

# === STARS ОПЛАТА ===
@dp.callback_query(F.data == "dep_stars")
async def dep_stars(c: CallbackQuery):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    await c.message.edit_text(p("⭐️ <b>Пополнение через Telegram Stars</b>\n\nВыберите сумму:"), reply_markup=stars_amount_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

@dp.callback_query(F.data.startswith("stars_"))
async def stars_payment(c: CallbackQuery):
    stars = int(c.data.split("_")[1])
    amount_usd = stars * 0.011
    
    await c.message.answer_invoice(
        title=f"Покупка {stars} Stars",
        description=f"Вы покупаете {stars} Telegram Stars\nНа баланс будет начислено 💵{amount_usd:.2f}",
        payload=f"stars_{stars}_{c.from_user.id}",
        currency="XTR",
        prices=[LabeledPrice(label=f"{stars} Stars", amount=stars)],
        provider_token="",
        need_name=False,
        need_phone_number=False,
        need_email=False,
        start_parameter=f"stars_pay_{stars}"
    )
    await c.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def stars_payment_success(msg: Message):
    payload = msg.successful_payment.invoice_payload
    stars = int(payload.split("_")[1])
    amount_usd = stars * 0.011
    
    upd_bal(msg.from_user.id, amount_usd)
    
    await msg.answer(
        p(f"✅ Оплата прошла успешно!\n\n"
          f"⭐️ Куплено: {stars} Stars\n"
          f"💰 Начислено на баланс: 💵{amount_usd:.2f}\n\n"
          f"🎮 Приятной игры!")
    )

# === ВЫВОДЫ ===
class WithdrawState(StatesGroup):
    wait = State()

@dp.callback_query(F.data == "withdraw")
async def withdraw_menu(c: CallbackQuery, state: FSMContext):
    if not await check_subscription(c.from_user.id):
        await c.answer("❌ Подпишитесь на канал!", show_alert=True)
        return
    await c.message.answer(p(f"💰 Вывод средств\n\nМинимальная сумма: 💵{MIN_WITHDRAW:.2f}\nВведите сумму:"), reply_markup=cancel_kb("cancel_withdraw"))
    await state.set_state(WithdrawState.wait)
    await c.answer()

@dp.callback_query(F.data == "cancel_withdraw")
async def cancel_withdraw(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await profile_menu(c.message)
    await c.answer()

@dp.message(WithdrawState.wait, F.chat.type == "private")
async def process_withdraw(msg: Message, state: FSMContext):
    u = get_user(msg.from_user.id)
    try:
        amount = float(msg.text.replace(",", "."))
        if amount < MIN_WITHDRAW:
            await msg.answer(p(f"❌ Минимальная сумма 💵{MIN_WITHDRAW:.2f}!"))
            return
        if amount > u["balance"]:
            await msg.answer(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        upd_bal(msg.from_user.id, -amount)
        
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO withdraws (uid, amount, created) VALUES (?, ?, ?)", (msg.from_user.id, amount, datetime.now()))
        conn.commit()
        conn.close()
        
        for admin in ADMIN_IDS:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=p("✅ Одобрить"), callback_data=f"approve_{msg.from_user.id}_{amount}", icon_custom_emoji_id=PREMIUM_BUTTONS["check"]),
                 InlineKeyboardButton(text=p("❌ Отклонить"), callback_data=f"reject_{msg.from_user.id}_{amount}", icon_custom_emoji_id=PREMIUM_BUTTONS["cross"])]
            ])
            await bot.send_message(admin, p(f"💰 НОВАЯ ЗАЯВКА НА ВЫВОД!\n\n👤 {msg.from_user.id}\n💵 {amount:.2f}"), reply_markup=keyboard)
        
        await msg.answer(p(f"✅ Заявка на вывод 💵{amount:.2f} создана! Ожидайте подтверждения."))
    except:
        await msg.answer(p("❌ Введите число!"))
    await state.clear()

# === АДМИН ОБРАБОТЧИКИ (без премиум эмодзи) ===
@dp.message(Command("admin"))
async def admin_panel(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        await msg.answer("⛔ Доступ запрещен!")
        return
    
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT SUM(balance) FROM users")
    total_balance = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM withdraws WHERE status = 'pending'")
    pending_withdraws = cur.fetchone()[0]
    conn.close()
    
    await msg.answer(
        f"📊 Админ-панель\n\n"
        f"👥 Игроков: {total_users}\n"
        f"💰 Общий баланс: ${total_balance:.2f}\n"
        f"⏳ Заявок на вывод: {pending_withdraws}\n\n"
        "Команды:\n"
        "/withdraws - список заявок\n"
        "/approve id - одобрить вывод\n"
        "/reject id - отклонить вывод\n"
        "/add id сумма - пополнить баланс\n"
        "/remove id сумма - списать баланс\n"
        "/promo код сумма лимит - создать промокод\n"
        "/sendall текст - рассылка"
    )

@dp.message(Command("withdraws"))
async def list_withdraws(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT id, uid, amount, created FROM withdraws WHERE status = 'pending'")
    requests = cur.fetchall()
    conn.close()
    
    if not requests:
        await msg.answer("📭 Нет активных заявок")
        return
    
    for req in requests:
        await msg.answer(
            f"💰 Заявка #{req[0]}\n"
            f"👤 ID: {req[1]}\n"
            f"💵 Сумма: ${req[2]}\n"
            f"📅 {req[3]}\n\n"
            f"✅ /approve {req[0]}\n"
            f"❌ /reject {req[0]}"
        )

@dp.message(Command("approve"))
async def approve_withdraw(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    try:
        withdraw_id = int(msg.text.split()[1])
        
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT uid, amount FROM withdraws WHERE id = ? AND status = 'pending'", (withdraw_id,))
        req = cur.fetchone()
        
        if req:
            uid, amount = req
            cur.execute("UPDATE withdraws SET status = 'completed' WHERE id = ?", (withdraw_id,))
            conn.commit()
            await bot.send_message(uid, f"✅ Ваша заявка на вывод ${amount:.2f} ОДОБРЕНА!")
            await msg.answer(f"✅ Заявка #{withdraw_id} одобрена")
        else:
            await msg.answer("❌ Заявка не найдена")
        conn.close()
    except:
        await msg.answer("❌ /approve id")

@dp.message(Command("reject"))
async def reject_withdraw(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    try:
        withdraw_id = int(msg.text.split()[1])
        
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT uid, amount FROM withdraws WHERE id = ? AND status = 'pending'", (withdraw_id,))
        req = cur.fetchone()
        
        if req:
            uid, amount = req
            upd_bal(uid, amount)
            cur.execute("UPDATE withdraws SET status = 'rejected' WHERE id = ?", (withdraw_id,))
            conn.commit()
            await bot.send_message(uid, f"❌ Ваша заявка на вывод ${amount:.2f} ОТКЛОНЕНА. Деньги возвращены.")
            await msg.answer(f"❌ Заявка #{withdraw_id} отклонена")
        else:
            await msg.answer("❌ Заявка не найдена")
        conn.close()
    except:
        await msg.answer("❌ /reject id")

@dp.message(Command("add"))
async def admin_add_balance(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    try:
        parts = msg.text.split()
        user_id = int(parts[1])
        amount = float(parts[2])
        
        upd_bal(user_id, amount)
        await msg.answer(f"✅ Пользователю {user_id} начислено ${amount:.2f}")
        await bot.send_message(user_id, f"✅ Админ начислил вам ${amount:.2f}")
    except:
        await msg.answer("❌ /add id сумма")

@dp.message(Command("remove"))
async def admin_remove_balance(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    try:
        parts = msg.text.split()
        user_id = int(parts[1])
        amount = float(parts[2])
        
        upd_bal(user_id, -amount)
        await msg.answer(f"✅ У пользователя {user_id} списано ${amount:.2f}")
        await bot.send_message(user_id, f"⚠️ Админ списал ${amount:.2f} с баланса")
    except:
        await msg.answer("❌ /remove id сумма")

@dp.message(Command("promo"))
async def admin_create_promo(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    try:
        parts = msg.text.split()
        code = parts[1].upper()
        reward = float(parts[2])
        max_act = int(parts[3]) if len(parts) > 3 else 0
        
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO promos (code, reward, max_act, expires) VALUES (?, ?, ?, ?)",
                   (code, reward, max_act, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()
        
        await msg.answer(f"✅ Промокод {code} создан!\n💰 Награда: ${reward}\n🔢 Лимит: {max_act if max_act > 0 else '∞'}")
    except:
        await msg.answer("❌ /promo код сумма лимит")

@dp.message(Command("sendall"))
async def admin_mailing(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    
    text = msg.text.replace("/sendall ", "")
    if not text:
        await msg.answer("❌ /sendall текст")
        return
    
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT uid FROM users")
    users = cur.fetchall()
    conn.close()
    
    sent = 0
    for user in users:
        try:
            await bot.send_message(user[0], text)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass
    
    await msg.answer(f"✅ Рассылка завершена! Отправлено {sent} пользователям")

# === КОМАНДА /send ===
@dp.message(Command("send"), F.chat.type == "private")
async def send_money(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.answer("⚠️ Подпишитесь на канал!")
        return
    
    parts = msg.text.split()
    if len(parts) < 3:
        await msg.answer("❌ Использование: /send {сумма} {username или id}\n\nПример:\n/send 0.5 @username\n/send 1.5 123456789")
        return
    
    try:
        amount = float(parts[1].replace(",", "."))
        if amount < MIN_TRANSFER:
            await msg.answer(p(f"❌ Минимальная сумма перевода 💵{MIN_TRANSFER:.2f}!"))
            return
        
        u = get_user(msg.from_user.id)
        if amount > u["balance"]:
            await msg.answer(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        target = parts[2]
        target_id = None
        
        if target.startswith("@"):
            username = target[1:]
            conn = sqlite3.connect('data.db')
            cur = conn.cursor()
            cur.execute("SELECT uid FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            conn.close()
            if row:
                target_id = row[0]
        else:
            try:
                target_id = int(target)
            except:
                pass
        
        if not target_id or target_id == msg.from_user.id:
            await msg.answer(p("❌ Получатель не найден или это вы сами!"))
            return
        
        target_user = get_user(target_id)
        if target_user["balance"] is None:
            await msg.answer(p("❌ Пользователь не найден!"))
            return
        
        upd_bal(msg.from_user.id, -amount)
        upd_bal(target_id, amount)
        
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO transfers (from_uid, to_uid, amount, created) VALUES (?, ?, ?, ?)",
                   (msg.from_user.id, target_id, amount, datetime.now()))
        conn.commit()
        conn.close()
        
        await msg.answer(
            p(f"✅ Перевод выполнен!\n\n"
              f"📤 Отправитель: {msg.from_user.id}\n"
              f"📥 Получатель: {target_id}\n"
              f"💵 Сумма: 💵{amount:.2f}\n\n"
              f"💰 Ваш баланс: 💵{get_user(msg.from_user.id)['balance']:.2f}")
        )
        
        await bot.send_message(
            target_id,
            p(f"📥 Вам поступил перевод!\n\n"
              f"👤 От: {msg.from_user.id}\n"
              f"💵 Сумма: 💵{amount:.2f}\n\n"
              f"💰 Ваш баланс: 💵{get_user(target_id)['balance']:.2f}")
        )
    except:
        await msg.answer(p("❌ Ошибка! Использование: /send {сумма} {username или id}"))

# === ДУЭЛИ В ЧАТЕ ===
duels = {}

@dp.message(F.chat.type.in_(["group", "supergroup"]), Command("cub"))
async def create_duel(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.reply("⚠️ Подпишитесь на канал!")
        return
    
    try:
        bet = float(msg.text.split()[1].replace(",", "."))
        if bet < MIN_BET:
            await msg.reply(p(f"❌ Минимальная ставка 💵{MIN_BET:.2f}!"))
            return
        
        u = get_user(msg.from_user.id)
        if bet > u["balance"]:
            await msg.reply(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        upd_bal(msg.from_user.id, -bet)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Принять дуэль", callback_data=f"accept_duel_{bet}_{msg.from_user.id}", icon_custom_emoji_id=PREMIUM_BUTTONS["game"])]
        ])
        
        sent = await msg.reply(
            p(f"⚔️ Создана дуэль!\n\n"
              f"👤 Игрок №1: {msg.from_user.full_name}\n"
              f"👤 Игрок №2: ...\n"
              f"💰 Ставка: 💵{bet:.2f}\n\n"
              f"Нажмите кнопку ниже, чтобы принять дуэль!"),
            reply_markup=keyboard
        )
        
        duels[msg.chat.id] = {
            "player1": msg.from_user.id,
            "player1_name": msg.from_user.full_name,
            "amount": bet,
            "message_id": sent.message_id
        }
        
    except:
        await msg.reply(p("❌ Использование: /cub {ставка}\nПример: /cub 0.5"))

@dp.callback_query(F.data.startswith("accept_duel_"))
async def accept_duel(c: CallbackQuery):
    _, _, bet, player1_id = c.data.split("_")
    bet = float(bet)
    player1_id = int(player1_id)
    
    if c.from_user.id == player1_id:
        await c.answer(p("❌ Нельзя принять свою же дуэль!"), show_alert=True)
        return
    
    if c.message.chat.id not in duels:
        await c.answer(p("❌ Дуэль уже завершена или не существует!"), show_alert=True)
        return
    
    duel = duels[c.message.chat.id]
    if duel["player1"] != player1_id or duel["amount"] != bet:
        await c.answer(p("❌ Данные дуэли устарели!"), show_alert=True)
        return
    
    if not await check_subscription(c.from_user.id):
        await c.answer(p("❌ Подпишитесь на канал!"), show_alert=True)
        return
    
    u2 = get_user(c.from_user.id)
    if bet > u2["balance"]:
        await c.answer(p(f"❌ Недостаточно средств! Баланс: 💵{u2['balance']:.2f}"), show_alert=True)
        return
    
    upd_bal(c.from_user.id, -bet)
    
    duels[c.message.chat.id]["player2"] = c.from_user.id
    duels[c.message.chat.id]["player2_name"] = c.from_user.full_name
    
    await c.message.edit_text(
        p(f"⚔️ Дуэль началась!\n\n"
          f"👤 Игрок №1: {duel['player1_name']}\n"
          f"👤 Игрок №2: {c.from_user.full_name}\n"
          f"💰 Ставка: 💵{bet:.2f}\n\n"
          f"🎲 Кидаем кубики...")
    )
    
    await asyncio.sleep(2)
    
    dice1 = await bot.send_dice(c.message.chat.id, emoji="🎲")
    dice2 = await bot.send_dice(c.message.chat.id, emoji="🎲")
    
    value1 = dice1.dice.value
    value2 = dice2.dice.value
    
    result_text = p(f"🎲 Игрок №1 выбросил: {value1}\n🎲 Игрок №2 выбросил: {value2}\n\n")
    
    if value1 > value2:
        winner = duel["player1"]
        winner_name = duel["player1_name"]
        upd_bal(winner, bet * 2)
        upd_wagered(winner, bet)
        result_text += p(f"🏆 Победитель: {winner_name}\n💰 Выигрыш: 💵{bet * 2:.2f}")
    elif value2 > value1:
        winner = c.from_user.id
        winner_name = c.from_user.full_name
        upd_bal(winner, bet * 2)
        upd_wagered(winner, bet)
        result_text += p(f"🏆 Победитель: {winner_name}\n💰 Выигрыш: 💵{bet * 2:.2f}")
    else:
        upd_bal(duel["player1"], bet)
        upd_bal(c.from_user.id, bet)
        result_text += p(f"🤝 Ничья!\n💰 Ставки возвращены обоим игрокам.")
    
    await bot.send_message(c.message.chat.id, result_text)
    
    del duels[c.message.chat.id]
    await c.answer()

# === ИГРЫ В ЧАТЕ ===
@dp.message(F.chat.type.in_(["group", "supergroup"]), Command("dice"))
async def chat_dice(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.reply("⚠️ Подпишитесь на канал!")
        return
    
    try:
        bet = float(msg.text.split()[1].replace(",", "."))
        u = get_user(msg.from_user.id)
        if bet < MIN_BET:
            await msg.reply(p(f"❌ Минимальная ставка 💵{MIN_BET:.2f}!"))
            return
        if bet > u["balance"]:
            await msg.reply(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        upd_bal(msg.from_user.id, -bet)
        dice_msg = await msg.answer_dice(emoji="🎲")
        value = dice_msg.dice.value
        
        if value >= 4:
            mult = {4: 1.4, 5: 1.8, 6: 2.4}[value]
            win = bet * mult
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.reply(p(f"🎲 Выпало: {value}\n✅ Выигрыш: 💵{win:.2f} (x{mult})!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.reply(p(f"🎲 Выпало: {value}\n❌ Проигрыш: 💵{bet:.2f}!"))
    except:
        await msg.reply(p("❌ Использование: /dice {сумма}\nПример: /dice 0.5"))

@dp.message(F.chat.type.in_(["group", "supergroup"]), Command("football"))
async def chat_football(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.reply("⚠️ Подпишитесь на канал!")
        return
    
    try:
        bet = float(msg.text.split()[1].replace(",", "."))
        u = get_user(msg.from_user.id)
        if bet < MIN_BET:
            await msg.reply(p(f"❌ Минимальная ставка 💵{MIN_BET:.2f}!"))
            return
        if bet > u["balance"]:
            await msg.reply(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        upd_bal(msg.from_user.id, -bet)
        football_msg = await msg.answer_dice(emoji="⚽️")
        value = football_msg.dice.value
        
        if value >= 4:
            win = bet * 1.3
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.reply(p(f"⚽️ ГОЛ! ✅ Выигрыш: 💵{win:.2f} (x1.3)!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.reply(p(f"⚽️ Мимо ворот! ❌ Проигрыш: 💵{bet:.2f}!"))
    except:
        await msg.reply(p("❌ Использование: /football {сумма}\nПример: /football 0.5"))

@dp.message(F.chat.type.in_(["group", "supergroup"]), Command("target"))
async def chat_target(msg: Message):
    if not await check_subscription(msg.from_user.id):
        await msg.reply("⚠️ Подпишитесь на канал!")
        return
    
    try:
        bet = float(msg.text.split()[1].replace(",", "."))
        u = get_user(msg.from_user.id)
        if bet < MIN_BET:
            await msg.reply(p(f"❌ Минимальная ставка 💵{MIN_BET:.2f}!"))
            return
        if bet > u["balance"]:
            await msg.reply(p(f"❌ Недостаточно средств! Баланс: 💵{u['balance']:.2f}"))
            return
        
        upd_bal(msg.from_user.id, -bet)
        target_msg = await msg.answer_dice(emoji="🎯")
        value = target_msg.dice.value
        
        if value >= 5:
            win = bet * 5
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.reply(p(f"🎯 В ЦЕНТР! ✅ Выигрыш: 💵{win:.2f} (x5)!"))
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.reply(p(f"🎯 Мимо! ❌ Проигрыш: 💵{bet:.2f}!"))
    except:
        await msg.reply(p("❌ Использование: /target {сумма}\nПример: /target 0.5"))

# === ЗАПУСК ===
async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="help", description="❓ Помощь"),
        BotCommand(command="balance", description="💰 Баланс"),
        BotCommand(command="dice", description="🎲 Кости"),
        BotCommand(command="football", description="⚽️ Футбол"),
        BotCommand(command="target", description="🎯 Дартс"),
        BotCommand(command="cub", description="⚔️ Дуэль"),
        BotCommand(command="send", description="📤 Перевод"),
        BotCommand(command="admin", description="👑 Админ"),
    ])
    logging.info("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

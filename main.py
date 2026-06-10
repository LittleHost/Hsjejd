import asyncio
import logging
import random
import sqlite3
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Optional
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup,
    KeyboardButton, CallbackQuery, Message
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ========== КОНФИГ ==========
BOT_TOKEN = "7932790272:AAEu3HTVBc6gibrlSm4Wguq3ss5KurubpBs"
CRYPTOBOT_TOKEN = "594394:AAqYLgin8OMpwWvpBXCDiNGcpnGHJ5NDXPn"
ADMIN_IDS = [7966949924]
BOT_USERNAME = "SecondCasBOT"

MIN_BET = 0.10
MIN_WITHDRAW = 1.10
COOLDOWN = 3

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === ID ПРЕМИУМ ЭМОДЗИ ===
E = {
    "star": "5958376256788502078",
    "profile": "5879770735999717115",
    "time": "5778605968208170641",
    "crypto": "5377820717024842074",
    "money": "5377452788651429834",
    "game": "5258508428212445001",
    "deposit": "5258043150110301407",
    "withdraw": "5258336354642697821",
    "gift": "5226731292334235524",
    "ref": "5879770735999717115",
    "bolt": "5377444769947490089",
    "pop": "5238078046174456159",
    "diamond": "5235702276424737428",
    "cross": "5238078046174456159",
    "check": "5238078046174456159",
    "alert": "5238078046174456159",
    "pen": "5258508428212445001",
    "back": "5258336354642697821",
    "tower": "5377444769947490089",
    "link": "5377452788651429834",
    "crown": "5377789084590706807",
}

# Функция для премиум эмодзи в ТЕКСТАХ
def em(text: str) -> str:
    r = {
        "⭐️": f'<tg-emoji emoji-id="{E["star"]}">⭐️</tg-emoji>',
        "👤": f'<tg-emoji emoji-id="{E["profile"]}">👤</tg-emoji>',
        "⏰": f'<tg-emoji emoji-id="{E["time"]}">⏰</tg-emoji>',
        "💎": f'<tg-emoji emoji-id="{E["crypto"]}">💎</tg-emoji>',
        "💵": f'<tg-emoji emoji-id="{E["money"]}">💵</tg-emoji>',
        "🎮": f'<tg-emoji emoji-id="{E["game"]}">🎮</tg-emoji>',
        "💳": f'<tg-emoji emoji-id="{E["deposit"]}">💳</tg-emoji>',
        "💰": f'<tg-emoji emoji-id="{E["withdraw"]}">💰</tg-emoji>',
        "🎁": f'<tg-emoji emoji-id="{E["gift"]}">🎁</tg-emoji>',
        "👥": f'<tg-emoji emoji-id="{E["ref"]}">👥</tg-emoji>',
        "⚡️": f'<tg-emoji emoji-id="{E["bolt"]}">⚡️</tg-emoji>',
        "🎉": f'<tg-emoji emoji-id="{E["pop"]}">🎉</tg-emoji>',
        "🏆": f'<tg-emoji emoji-id="{E["diamond"]}">🏆</tg-emoji>',
        "❌": f'<tg-emoji emoji-id="{E["cross"]}">❌</tg-emoji>',
        "✅": f'<tg-emoji emoji-id="{E["check"]}">✅</tg-emoji>',
        "⚠️": f'<tg-emoji emoji-id="{E["alert"]}">⚠️</tg-emoji>',
        "✏️": f'<tg-emoji emoji-id="{E["pen"]}">✏️</tg-emoji>',
        "🔙": f'<tg-emoji emoji-id="{E["back"]}">🔙</tg-emoji>',
        "🗼": f'<tg-emoji emoji-id="{E["tower"]}">🗼</tg-emoji>',
        "🔗": f'<tg-emoji emoji-id="{E["link"]}">🔗</tg-emoji>',
        "👑": f'<tg-emoji emoji-id="{E["crown"]}">👑</tg-emoji>',
        "📈": f'<tg-emoji emoji-id="{E["link"]}">📈</tg-emoji>',
    }
    for old, new in r.items():
        text = text.replace(old, new)
    return text

# ========== КЛАВИАТУРЫ (С ПРЕМИУМ ЭМОДЗИ В КНОПКАХ) ==========
def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="Игры в боте", icon_custom_emoji_id=E["game"]),
            KeyboardButton(text="Профиль", icon_custom_emoji_id=E["profile"])
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
    b.row(InlineKeyboardButton(text="Назад", callback_data="back_main", icon_custom_emoji_id=E["back"]))
    return b.as_markup()

def profile_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пополнить", callback_data="deposit", icon_custom_emoji_id=E["deposit"]),
         InlineKeyboardButton(text="Вывести", callback_data="withdraw", icon_custom_emoji_id=E["withdraw"])],
        [InlineKeyboardButton(text="Промокоды", callback_data="promo", icon_custom_emoji_id=E["gift"]),
         InlineKeyboardButton(text="Реф Программа", callback_data="ref", icon_custom_emoji_id=E["ref"])],
        [InlineKeyboardButton(text="Назад", callback_data="back_main", icon_custom_emoji_id=E["back"])]
    ])

def deposit_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="CryptoBot", callback_data="dep_crypto", icon_custom_emoji_id=E["crypto"])],
        [InlineKeyboardButton(text="Stars", callback_data="dep_stars", icon_custom_emoji_id=E["star"])],
        [InlineKeyboardButton(text="Назад", callback_data="back_profile", icon_custom_emoji_id=E["back"])]
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_profile", icon_custom_emoji_id=E["back"])]
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
        last_bet REAL DEFAULT 0
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
        cur.execute("INSERT INTO users (uid, reg, last_bet) VALUES (?, ?, 0)", (uid, datetime.now()))
        conn.commit()
        conn.close()
        return {"uid": uid, "balance": 0, "reg": datetime.now(), "wagered": 0, "lost": 0,
                "ref_cnt": 0, "ref_earn": 0, "last_bet": 0}
    return {"uid": u[0], "balance": u[1], "reg": datetime.strptime(u[2], "%Y-%m-%d %H:%M:%S.%f"),
            "wagered": u[4], "lost": u[5], "ref_id": u[6], "ref_earn": u[7],
            "ref_cnt": u[8], "ref_dep_cnt": u[9], "last_bet": u[10]}

def upd_bal(uid: int, amt: float):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE uid = ?", (amt, uid))
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

def can_bet(uid: int):
    u = get_user(uid)
    now = datetime.now().timestamp()
    if now - u["last_bet"] < COOLDOWN:
        return False, COOLDOWN - (now - u["last_bet"])
    return True, 0

async def create_crypto_invoice(amount: float) -> Optional[str]:
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    data = {"asset": "USDT", "amount": str(amount)}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, timeout=10) as resp:
                result = await resp.json()
                if result.get("ok"):
                    return result["result"]["bot_invoice_url"]
    except:
        pass
    return None

# ========== ЛИЧКА ==========
@dp.message(Command("start"), F.chat.type == "private")
async def start(msg: Message):
    get_user(msg.from_user.id)
    args = msg.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref = int(args[1])
        if ref != msg.from_user.id:
            conn = sqlite3.connect('data.db')
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM users WHERE uid = ?", (ref,))
            if cur.fetchone():
                cur.execute("UPDATE users SET ref_id = ?, ref_cnt = ref_cnt + 1 WHERE uid = ?", (ref, msg.from_user.id))
                conn.commit()
            conn.close()
    txt = em("""<b>💰 Деньги есть всегда!</b>

⚡️ <b>Бот с играми и дуэлями</b>
⚡️ <b>Быстрые ставки, моментальные выводы</b>
💵 <b>Доход с рефералов</b>
<i>От 💵100 в день — реально</i>""")
    await msg.answer(txt, reply_markup=main_kb(), parse_mode=ParseMode.HTML)

@dp.message(F.text.in_(["Игры в боте", "Профиль"]), F.chat.type == "private")
async def menu_handler(msg: Message):
    if msg.text == "Игры в боте":
        u = get_user(msg.from_user.id)
        txt = em("🎮 <b>Выберите игру!</b>\n\n💵 Баланс: 💵{:.2f}".format(u["balance"]))
        await msg.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)
    else:
        u = get_user(msg.from_user.id)
        days = (datetime.now() - u["reg"]).days
        txt = em("👤 <b>Ваш профиль</b>\n\n💵 Баланс: <b>💵{:.2f}</b>\n⏰ Дней в боте: <b>{}</b>".format(u["balance"], days))
        await msg.answer(txt, reply_markup=profile_kb(), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "back_main")
async def back_main(c: CallbackQuery):
    await c.message.delete()
    txt = em("""<b>💰 Деньги есть всегда!</b>

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
    txt = em("👤 <b>Ваш профиль</b>\n\n💵 Баланс: <b>💵{:.2f}</b>\n⏰ Дней в боте: <b>{}</b>".format(u["balance"], days))
    await c.message.answer(txt, reply_markup=profile_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

# === РЕФЕРАЛКА (ВСЕ ЭМОДЗИ ПРЕМИУМ) ===
@dp.callback_query(F.data == "ref")
async def ref_prog(c: CallbackQuery):
    u = get_user(c.from_user.id)
    txt = em(f"""👥 <b>Реферальная программа</b>

👥 Рефералы: {u["ref_cnt"]} (пополнили: {u["ref_dep_cnt"]})
💵 За месяц: 💵0.00
💵 Всего: 💵{u["ref_earn"]:.2f}

<b>Условия:</b>
• 💵 1💵 за друга, который пополнил баланс от 5💵
• 💵 10% от проигрышей рефералов — каждую пятницу в 21:00

<b>Бонусы:</b>
• 100 друзей — +5💵
• 250 друзей — +15💵
• 500 друзей — +30💵
• 1000 друзей — +60💵

🏆 До бонуса: {max(0, 100 - u["ref_cnt"])} рефералов

🔗 <b>Реферальная ссылка:</b>
<code>https://t.me/{BOT_USERNAME}?start={c.from_user.id}</code>""")
    await c.message.edit_text(txt, reply_markup=back_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

# === ПРОМОКОДЫ ===
class PromoState(StatesGroup):
    wait = State()

@dp.callback_query(F.data == "promo")
async def promo_menu(c: CallbackQuery, state: FSMContext):
    txt = em("🎁 <b>Введи промокод:</b>\n\nПросто напиши код в чат — и бонус зачислится автоматически.")
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
        await msg.answer(em("⭐️ Промокод не найден!"))
        await state.clear()
        return
    cur.execute("SELECT 1 FROM promo_used WHERE code = ? AND uid = ?", (code, msg.from_user.id))
    if cur.fetchone():
        await msg.answer(em("⭐️ Вы уже активировали этот промокод!"))
        await state.clear()
        return
    if p[3] >= p[2] and p[2] > 0:
        await msg.answer(em("⭐️ Промокод достиг лимита!"))
        await state.clear()
        return
    upd_bal(msg.from_user.id, p[1])
    cur.execute("INSERT INTO promo_used VALUES (?, ?)", (code, msg.from_user.id))
    cur.execute("UPDATE promos SET activated = activated + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    await msg.answer(em("🎉 Промокод активирован! +💵{:.2f} на баланс!".format(p[1])))
    await state.clear()

# === ИГРЫ (ОБЫЧНЫЕ ЭМОДЗИ В ИГРАХ) ===
class BetState(StatesGroup):
    wait = State()

class TowerState(StatesGroup):
    play = State()

@dp.callback_query(F.data.startswith("game_"))
async def game_start(c: CallbackQuery, state: FSMContext):
    ok, rem = can_bet(c.from_user.id)
    if not ok:
        await c.answer(f"⚠️ Подожди {rem:.0f} сек между ставками!", show_alert=True)
        return
    game = c.data.split("_")[1]
    await state.update_data(game=game)
    await c.message.answer(f"✏️ Введи сумму ставки (мин. ${MIN_BET:.2f})")
    await state.set_state(BetState.wait)
    await c.answer()

@dp.message(BetState.wait, F.chat.type == "private")
async def process_bet(msg: Message, state: FSMContext):
    ok, rem = can_bet(msg.from_user.id)
    if not ok:
        await msg.answer(f"⚠️ Подожди {rem:.0f} сек между ставками!")
        return
    
    u = get_user(msg.from_user.id)
    data = await state.get_data()
    game = data.get("game")
    
    try:
        bet = float(msg.text.replace(",", "."))
        if bet < MIN_BET:
            await msg.answer(f"❌ Минимальная ставка ${MIN_BET:.2f}!")
            return
        if bet > u["balance"]:
            await msg.answer(f"❌ Недостаточно средств! Баланс: ${u['balance']:.2f}")
            return
    except:
        await msg.answer("❌ Введите число!")
        return
    
    upd_last_bet(msg.from_user.id)
    upd_bal(msg.from_user.id, -bet)
    
    if game == "dice":
        roll = random.randint(1, 6)
        if roll >= 4:
            mult = {4: 1.4, 5: 1.8, 6: 2.4}[roll]
            win = bet * mult
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.answer(f"🎲 Выпало: {roll}\n✅ Выигрыш: ${win:.2f} (x{mult})!")
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.answer(f"🎲 Выпало: {roll}\n❌ Проигрыш: ${bet:.2f}!")
    
    elif game == "football":
        if random.random() < 0.5:
            win = bet * 1.3
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.answer(f"⚽️ ГОЛ! ✅ Выигрыш: ${win:.2f} (x1.3)!")
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.answer(f"⚽️ Мимо ворот! ❌ Проигрыш: ${bet:.2f}!")
    
    elif game == "target":
        if random.random() < 0.2:
            win = bet * 5
            upd_bal(msg.from_user.id, win)
            upd_wagered(msg.from_user.id, bet)
            await msg.answer(f"🎯 В ЦЕНТР! ✅ Выигрыш: ${win:.2f} (x5)!")
        else:
            upd_lost(msg.from_user.id, bet)
            await msg.answer(f"🎯 Мимо! ❌ Проигрыш: ${bet:.2f}!")
    
    elif game == "tower":
        await state.update_data(tower_bet=bet, tower_level=0, tower_mult=1.0)
        await state.set_state(TowerState.play)
        await play_tower(msg, state, 0, 1.0, bet)
        return
    
    await state.clear()
    u2 = get_user(msg.from_user.id)
    txt = em("🎮 <b>Выберите игру!</b>\n\n💵 Баланс: 💵{:.2f}".format(u2["balance"]))
    await msg.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)

# === БАШНЯ ===
async def play_tower(msg: Message, state: FSMContext, level: int, mult: float, bet: float):
    multipliers = [1.4, 1.7, 2.4, 3.2, 4.0, 6.0]
    
    if level >= len(multipliers):
        win = bet * multipliers[-1]
        upd_bal(msg.from_user.id, win)
        upd_wagered(msg.from_user.id, bet)
        await msg.answer(f"🏆 ПОЛНАЯ ПОБЕДА! 🏆\n🗼 Вы прошли все 6 уровней!\n💰 Выигрыш: ${win:.2f} (x{multipliers[-1]})!")
        await state.clear()
        u = get_user(msg.from_user.id)
        txt = em("🎮 <b>Выберите игру!</b>\n\n💵 Баланс: 💵{:.2f}".format(u["balance"]))
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
        b.row(InlineKeyboardButton(text=f"💰 Забрать ${bet * mult:.2f}", callback_data="tower_cashout"))
    
    await msg.answer(
        f"🗼 БАШНЯ - Уровень {level + 1}/6\n"
        f"💰 Ставка: ${bet:.2f}\n"
        f"📈 Множитель: x{multipliers[level]} (выигрыш: ${bet * multipliers[level]:.2f})\n"
        f"💥 В одной из клеток БОМБА!\n\n"
        f"Выбери клетку:",
        reply_markup=b.as_markup()
    )

@dp.callback_query(TowerState.play, F.data.in_(["tower_left", "tower_right", "tower_cashout"]))
async def tower_choice(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await c.answer("Игра не найдена!")
        return
    
    if c.data == "tower_cashout":
        bet = data.get("tower_bet", 0)
        mult = data.get("tower_mult", 1.0)
        level = data.get("tower_level", 0)
        if level == 0:
            await c.answer("Нужно открыть хотя бы одну клетку!", show_alert=True)
            return
        win = bet * mult
        upd_bal(c.from_user.id, win)
        upd_wagered(c.from_user.id, bet)
        await c.message.edit_text(f"💰 ВЫ ЗАБРАЛИ ВЫИГРЫШ! 💰\n🗼 Пройдено уровней: {level}/6\n✅ Выигрыш: ${win:.2f} (x{mult})!")
        await state.clear()
        u = get_user(c.from_user.id)
        txt = em("🎮 <b>Выберите игру!</b>\n\n💵 Баланс: 💵{:.2f}".format(u["balance"]))
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
        await c.message.edit_text(f"💥 БОМБА ВЗОРВАЛАСЬ! 💥\n🗼 Вы проиграли на уровне {level + 1}/6\n💰 Потеряно: ${bet:.2f}\n\n🎮 Попробуйте снова!")
        await state.clear()
        u = get_user(c.from_user.id)
        txt = em("🎮 <b>Выберите игру!</b>\n\n💵 Баланс: 💵{:.2f}".format(u["balance"]))
        await c.message.answer(txt, reply_markup=games_kb(), parse_mode=ParseMode.HTML)
    else:
        level += 1
        new_mult = multipliers[level - 1]
        await c.message.edit_text(f"✅ БЕЗОПАСНО! 🟩\n🗼 Уровень {level}/6 пройден!\n💰 Текущий выигрыш: ${bet * new_mult:.2f} (x{new_mult})\n\n🎲 Продолжаем?")
        
        if level >= len(multipliers):
            win = bet * multipliers[-1]
            upd_bal(c.from_user.id, win)
            upd_wagered(c.from_user.id, bet)
            await c.message.answer(f"🏆 ПОБЕДА! 🏆\n🗼 Вы прошли ВСЕ 6 уровней!\n💰 Выигрыш: ${win:.2f} (x{multipliers[-1]})!")
            await state.clear()
            u = get_user(c.from_user.id)
            txt = em("🎮 <b>Выберите игру!</b>\n\n💵 Баланс: 💵{:.2f}".format(u["balance"]))
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
            b.row(InlineKeyboardButton(text=f"💰 Забрать ${bet * new_mult:.2f}", callback_data="tower_cashout"))
            await c.message.answer(
                f"🗼 БАШНЯ - Уровень {level + 1}/6\n"
                f"💰 Ставка: ${bet:.2f}\n"
                f"📈 Множитель: x{multipliers[level]} (выигрыш: ${bet * multipliers[level]:.2f})\n"
                f"💥 В одной из клеток БОМБА!\n\n"
                f"Выбери клетку:",
                reply_markup=b.as_markup()
            )
    await c.answer()

# === ДЕПОЗИТЫ ===
@dp.callback_query(F.data == "deposit")
async def deposit_menu(c: CallbackQuery):
    await c.message.edit_text(em("💳 <b>Пополнение средств</b>"), reply_markup=deposit_kb(), parse_mode=ParseMode.HTML)
    await c.answer()

@dp.callback_query(F.data == "dep_crypto")
async def dep_crypto(c: CallbackQuery, state: FSMContext):
    await c.message.answer("✏️ Введите сумму для пополнения (мин. $0.15):")
    await state.set_state(DepositState.wait_crypto)
    await c.answer()

@dp.callback_query(F.data == "dep_stars")
async def dep_stars(c: CallbackQuery, state: FSMContext):
    await c.message.answer("✏️ Введите количество звёзд (мин. 50, 1 звезда = $0.011):")
    await state.set_state(DepositState.wait_stars)
    await c.answer()

class DepositState(StatesGroup):
    wait_crypto = State()
    wait_stars = State()

@dp.message(DepositState.wait_crypto, F.chat.type == "private")
async def process_crypto(msg: Message, state: FSMContext):
    try:
        amount = float(msg.text.replace(",", "."))
        if amount < 0.15:
            await msg.answer("❌ Минимальная сумма $0.15!")
            return
        invoice = await create_crypto_invoice(amount)
        if invoice:
            await msg.answer(f"💳 Счет создан!\nСумма: ${amount:.2f}\nСсылка: {invoice}\n\nПосле оплаты нажмите /check_payment")
        else:
            await msg.answer("❌ Ошибка создания счета!")
    except:
        await msg.answer("❌ Введите число!")
    await state.clear()

@dp.message(DepositState.wait_stars, F.chat.type == "private")
async def process_stars(msg: Message, state: FSMContext):
    try:
        stars = int(msg.text)
        if stars < 50:
            await msg.answer("❌ Минимум 50 звёзд!")
            return
        amount_usd = stars * 0.011
        upd_bal(msg.from_user.id, amount_usd)
        await msg.answer(em(f"✅ Пополнено {stars} ⭐️ → 💵{amount_usd:.2f} на баланс!"))
    except:
        await msg.answer("❌ Введите целое число!")
    await state.clear()

# === ВЫВОДЫ ===
@dp.callback_query(F.data == "withdraw")
async def withdraw_menu(c: CallbackQuery, state: FSMContext):
    await c.message.answer(f"💰 Вывод средств\n\nМинимальная сумма: ${MIN_WITHDRAW:.2f}\nВведите сумму:")
    await state.set_state(WithdrawState.wait)
    await c.answer()

class WithdrawState(StatesGroup):
    wait = State()

@dp.message(WithdrawState.wait, F.chat.type == "private")
async def process_withdraw(msg: Message, state: FSMContext):
    u = get_user(msg.from_user.id)
    try:
        amount = float(msg.text.replace(",", "."))
        if amount < MIN_WITHDRAW:
            await msg.answer(f"❌ Минимальная сумма ${MIN_WITHDRAW:.2f}!")
            return
        if amount > u["balance"]:
            await msg.answer(f"❌ Недостаточно средств! Баланс: ${u['balance']:.2f}")
            return
        upd_bal(msg.from_user.id, -amount)
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO withdraws (uid, amount, created) VALUES (?, ?, ?)", (msg.from_user.id, amount, datetime.now()))
        conn.commit()
        conn.close()
        for admin in ADMIN_IDS:
            await bot.send_message(admin, f"💰 НОВАЯ ЗАЯВКА НА ВЫВОД!\n👤 {msg.from_user.id}\n💵 ${amount:.2f}")
        await msg.answer(f"✅ Заявка на вывод ${amount:.2f} создана! Ожидайте подтверждения.")
    except:
        await msg.answer("❌ Введите число!")
    await state.clear()

# === АДМИН ===
@dp.message(Command("admin"))
async def admin_panel(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    await msg.answer("📊 Админ-панель\n\nДоступные команды:\n/approve {id} - одобрить вывод\n/reject {id} - отклонить вывод")

# === ЗАПУСК ===
async def main():
    await bot.set_my_commands([BotCommand(command="start", description="Запустить бота")])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
import random
import sqlite3
import aiohttp
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup,
    KeyboardButton, CallbackQuery, Message, BotCommand
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ========== КОНФИГ ==========
BOT_TOKEN = "7932790272:AAEu3HTVBc6gibrlSm4Wguq3ss5KurubpBs"
CRYPTOBOT_TOKEN = "594394:AAqYLgin8OMpwWvpBXCDiNGcpnGHJ5NDXPn"  # Получите у @CryptoBot
ADMIN_IDS = [7966949924]
BOT_USERNAME = "SecondCasBOT"

MIN_BET = 0.10
MIN_WITHDRAW = 1.10
BET_COOLDOWN = 10

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === ПРЕМИУМ ЭМОДЗИ ===
P = {
    "звезда": '<tg-emoji emoji-id="5958376256788502078">⭐️</tg-emoji>',
    "профиль": '<tg-emoji emoji-id="5879770735999717115">👤</tg-emoji>',
    "время": '<tg-emoji emoji-id="5778605968208170641">⏰</tg-emoji>',
    "крипто_бот": '<tg-emoji emoji-id="5377820717024842074">💎</tg-emoji>',
    "доллар": '<tg-emoji emoji-id="5377452788651429834">💵</tg-emoji>',
    "играть": '<tg-emoji emoji-id="5258508428212445001">🎮</tg-emoji>',
    "привет": '<tg-emoji emoji-id="5258501105293205250">👋</tg-emoji>',
    "пополнить": '<tg-emoji emoji-id="5258043150110301407">💳</tg-emoji>',
    "вывести": '<tg-emoji emoji-id="5258336354642697821">💰</tg-emoji>',
    "подарок": '<tg-emoji emoji-id="5226731292334235524">🎁</tg-emoji>',
    "реф": '<tg-emoji emoji-id="5879770735999717115">👥</tg-emoji>',
    "молния": '<tg-emoji emoji-id="5377444769947490089">⚡️</tg-emoji>',
    "хлопушка": '<tg-emoji emoji-id="5238078046174456159">🎉</tg-emoji>',
}

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance REAL DEFAULT 0,
        reg_date TEXT,
        total_deposit REAL DEFAULT 0,
        total_withdraw REAL DEFAULT 0,
        total_wagered REAL DEFAULT 0,
        total_lost REAL DEFAULT 0,
        referrer_id INTEGER DEFAULT NULL,
        ref_earned REAL DEFAULT 0,
        ref_count INTEGER DEFAULT 0,
        ref_deposit_count INTEGER DEFAULT 0,
        last_bet_time REAL DEFAULT 0
    )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS invoices (
        invoice_id TEXT PRIMARY KEY,
        user_id INTEGER,
        amount REAL,
        status TEXT DEFAULT 'pending',
        created_at TEXT
    )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS withdraw_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        status TEXT DEFAULT 'pending',
        created_at TEXT
    )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS promocodes (
        code TEXT PRIMARY KEY,
        reward REAL,
        max_activations INTEGER,
        activated INTEGER DEFAULT 0,
        min_deposit REAL DEFAULT 0,
        min_wagered REAL DEFAULT 0,
        only_premium INTEGER DEFAULT 0,
        expires_at TEXT
    )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS promocode_activations (
        code TEXT,
        user_id INTEGER,
        activated_at TEXT
    )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS checks (
        check_id TEXT PRIMARY KEY,
        amount REAL,
        max_activations INTEGER,
        activated INTEGER DEFAULT 0,
        min_deposit REAL DEFAULT 0,
        min_wagered REAL DEFAULT 0,
        only_premium INTEGER DEFAULT 0,
        created_by INTEGER,
        created_at TEXT,
        expires_at TEXT
    )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS check_activations (
        check_id TEXT,
        user_id INTEGER,
        activated_at TEXT
    )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY,
        total_volume REAL DEFAULT 0,
        total_deposits REAL DEFAULT 0,
        total_deposits_stars REAL DEFAULT 0,
        total_withdraws REAL DEFAULT 0,
        total_players INTEGER DEFAULT 0
    )''')
    
    cur.execute("INSERT OR IGNORE INTO stats (id, total_players) VALUES (1, 0)")
    conn.commit()
    conn.close()

init_db()

# ========== ФУНКЦИИ ==========
def get_user(user_id: int) -> Dict:
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    
    if not user:
        reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect('bot_database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users (user_id, reg_date, last_bet_time) VALUES (?, ?, 0)", (user_id, reg_date))
        conn.commit()
        conn.close()
        
        conn = sqlite3.connect('bot_database.db')
        cur = conn.cursor()
        cur.execute("UPDATE stats SET total_players = total_players + 1 WHERE id = 1")
        conn.commit()
        conn.close()
        
        return {"user_id": user_id, "balance": 0, "reg_date": reg_date, "total_wagered": 0, "total_lost": 0,
                "ref_count": 0, "ref_deposit_count": 0, "ref_earned": 0, "last_bet_time": 0}
    
    return {
        "user_id": user[0], "balance": user[2], "reg_date": user[3],
        "total_wagered": user[6], "total_lost": user[7], "referrer_id": user[8],
        "ref_earned": user[9], "ref_count": user[10], "ref_deposit_count": user[11],
        "last_bet_time": user[12]
    }

def update_balance(user_id: int, amount: float):
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def add_to_wagered(user_id: int, amount: float):
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET total_wagered = total_wagered + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def add_to_lost(user_id: int, amount: float):
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET total_lost = total_lost + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def update_last_bet_time(user_id: int):
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_bet_time = ? WHERE user_id = ?", (datetime.now().timestamp(), user_id))
    conn.commit()
    conn.close()

def check_bet_cooldown(user_id: int):
    user = get_user(user_id)
    last_time = user.get("last_bet_time", 0)
    now = datetime.now().timestamp()
    elapsed = now - last_time
    if elapsed < BET_COOLDOWN:
        return False, BET_COOLDOWN - elapsed
    return True, 0

def generate_check_id() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# === CRYPTOBOT API ===
async def create_crypto_invoice(user_id: int, amount: float) -> Optional[str]:
    """Создает реальный счет через CryptoBot API"""
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    data = {
        "asset": "USDT",
        "amount": str(amount),
        "description": f"Пополнение баланса бота. User ID: {user_id}"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, timeout=15) as resp:
                result = await resp.json()
                if result.get("ok"):
                    invoice_id = result["result"]["invoice_id"]
                    bot_invoice_url = result["result"]["bot_invoice_url"]
                    
                    # Сохраняем инвойс в БД
                    conn = sqlite3.connect('bot_database.db')
                    cur = conn.cursor()
                    cur.execute("INSERT INTO invoices (invoice_id, user_id, amount, created_at) VALUES (?, ?, ?, ?)",
                               (str(invoice_id), user_id, amount, datetime.now()))
                    conn.commit()
                    conn.close()
                    
                    return bot_invoice_url
                else:
                    logging.error(f"CryptoBot error: {result}")
    except Exception as e:
        logging.error(f"Create invoice error: {e}")
    return None

async def check_crypto_payment(user_id: int, amount: float) -> bool:
    """Реальная проверка оплаты через CryptoBot API"""
    url = "https://pay.crypt.bot/api/getInvoices"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    params = {"asset": "USDT", "status": "paid"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=15) as resp:
                result = await resp.json()
                if result.get("ok"):
                    for invoice in result.get("result", []):
                        # Проверяем, что счет принадлежит этому пользователю и сумма совпадает
                        conn = sqlite3.connect('bot_database.db')
                        cur = conn.cursor()
                        cur.execute("SELECT * FROM invoices WHERE invoice_id = ? AND user_id = ? AND amount = ? AND status = 'pending'",
                                   (str(invoice["invoice_id"]), user_id, amount))
                        pending = cur.fetchone()
                        conn.close()
                        
                        if pending and invoice["status"] == "paid":
                            # Отмечаем инвойс как оплаченный
                            conn = sqlite3.connect('bot_database.db')
                            cur = conn.cursor()
                            cur.execute("UPDATE invoices SET status = 'paid' WHERE invoice_id = ?", (str(invoice["invoice_id"]),))
                            conn.commit()
                            conn.close()
                            return True
    except Exception as e:
        logging.error(f"Check payment error: {e}")
    return False

# === CRYPTOBOT WEBHOOK (для автоматических уведомлений) ===
async def crypto_webhook_payment(invoice_id: str, user_id: int, amount: float):
    """Обработка вебхука от CryptoBot"""
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoices WHERE invoice_id = ? AND status = 'pending'", (invoice_id,))
    invoice = cur.fetchone()
    
    if invoice:
        cur.execute("UPDATE invoices SET status = 'paid' WHERE invoice_id = ?", (invoice_id,))
        conn.commit()
        
        # Начисляем баланс
        update_balance(user_id, amount)
        
        # Реферальная комиссия
        user = get_user(user_id)
        if user.get("referrer_id") and amount >= 5:
            cur.execute("UPDATE users SET ref_earned = ref_earned + 1, ref_deposit_count = ref_deposit_count + 1 WHERE user_id = ?", 
                       (user['referrer_id'],))
            cur.execute("UPDATE users SET balance = balance + 1 WHERE user_id = ?", (user['referrer_id'],))
            conn.commit()
        
        # Уведомляем пользователя
        await bot.send_message(user_id, f"✅ Ваш платеж на сумму ${amount:.2f} получен! Баланс пополнен.")
    
    conn.close()

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"{P['играть']} Игры в боте"), KeyboardButton(text=f"{P['профиль']} Профиль")]],
        resize_keyboard=True
    )

def get_games_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎲", callback_data="game_dice"),
        InlineKeyboardButton(text="⚽️", callback_data="game_football"),
        InlineKeyboardButton(text="🎯", callback_data="game_target"),
        InlineKeyboardButton(text="🗼", callback_data="game_tower")
    )
    builder.row(InlineKeyboardButton(text=f"{P['привет']} Игровой чат", url="https://t.me/SecondProjectChat"))
    return builder.as_markup()

# ========== СОСТОЯНИЯ ==========
class BetState(StatesGroup):
    waiting_bet = State()

class DepositState(StatesGroup):
    waiting_crypto = State()
    waiting_stars = State()

class WithdrawState(StatesGroup):
    waiting_amount = State()

class PromoState(StatesGroup):
    waiting_code = State()

class AdminState(StatesGroup):
    waiting_mailing = State()
    waiting_mailing_buttons = State()
    waiting_promo_code = State()
    waiting_promo_reward = State()
    waiting_promo_max = State()
    waiting_promo_min_dep = State()
    waiting_promo_min_wag = State()
    waiting_promo_prem = State()
    waiting_check_amount = State()
    waiting_check_max = State()
    waiting_check_min_dep = State()
    waiting_check_min_wag = State()
    waiting_check_prem = State()
    waiting_ban_id = State()
    waiting_ban_amount = State()
    waiting_add_id = State()
    waiting_add_amount = State()
    waiting_stats_id = State()

# ========== Tower Game State ==========
class TowerState(StatesGroup):
    playing = State()

# ========== ОБРАБОТЧИКИ ==========
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = get_user(message.from_user.id)
    
    # Обработка реферальной ссылки
    args = message.text.split()
    if len(args) > 1:
        try:
            referrer_id = int(args[1])
            if referrer_id != message.from_user.id and not user.get("referrer_id"):
                conn = sqlite3.connect('bot_database.db')
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM users WHERE user_id = ?", (referrer_id,))
                if cur.fetchone():
                    cur.execute("UPDATE users SET referrer_id = ? WHERE user_id = ?", (referrer_id, message.from_user.id))
                    cur.execute("UPDATE users SET ref_count = ref_count + 1 WHERE user_id = ?", (referrer_id,))
                    conn.commit()
                conn.close()
        except:
            pass
    
    text = f"""Деньги есть всегда!

{P['молния']} Бот с играми и дуэлями
{P['молния']} Быстрые ставки, моментальные выводы
{P['доллар']} Доход с рефералов
От $100 в день — реально"""
    
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode=ParseMode.HTML)

@dp.message(F.text == f"{P['играть']} Игры в боте")
async def games_menu(message: Message):
    user = get_user(message.from_user.id)
    await message.answer(f"{P['играть']} Выберите игру, где хотите сделать ставку!\n\n{P['доллар']} Баланс: ${user['balance']:.2f}",
                         reply_markup=get_games_keyboard(), parse_mode=ParseMode.HTML)

@dp.message(F.text == f"{P['профиль']} Профиль")
async def profile_menu(message: Message):
    user = get_user(message.from_user.id)
    days = (datetime.now() - datetime.strptime(user['reg_date'], "%Y-%m-%d %H:%M:%S")).days
    
    text = f"""{P['профиль']} Ваш профиль

{P['доллар']} Баланс: ${user['balance']:.2f}
{P['время']} Дней в боте: {days}"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{P['пополнить']} Пополнить", callback_data="deposit"),
         InlineKeyboardButton(text=f"{P['вывести']} Вывести", callback_data="withdraw")],
        [InlineKeyboardButton(text=f"{P['подарок']} Промокоды", callback_data="promocodes"),
         InlineKeyboardButton(text=f"{P['реф']} Реф Программа", callback_data="ref")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# === ПРОМОКОДЫ ===
@dp.callback_query(lambda c: c.data == "promocodes")
async def promocodes_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(f"{P['подарок']} Введи промокод:\n\nПросто напиши код в чат — и бонус зачислится автоматически.")
    await state.set_state(PromoState.waiting_code)
    await callback.answer()

@dp.message(PromoState.waiting_code)
async def activate_promo(message: Message, state: FSMContext):
    code = message.text.upper()
    
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM promocodes WHERE code = ?", (code,))
    promo = cur.fetchone()
    
    if not promo:
        await message.answer(f"{P['звезда']} Промокод не найден!")
        await state.clear()
        return
    
    cur.execute("SELECT * FROM promocode_activations WHERE code = ? AND user_id = ?", (code, message.from_user.id))
    if cur.fetchone():
        await message.answer(f"{P['звезда']} Вы уже активировали этот промокод!")
        await state.clear()
        return
    
    if promo[3] >= promo[2] and promo[2] > 0:
        await message.answer(f"{P['звезда']} Промокод достиг лимита активаций!")
        await state.clear()
        return
    
    if promo[6] and datetime.now() > datetime.strptime(promo[6], "%Y-%m-%d"):
        await message.answer(f"{P['звезда']} Срок действия промокода истек!")
        await state.clear()
        return
    
    update_balance(message.from_user.id, promo[1])
    cur.execute("INSERT INTO promocode_activations VALUES (?, ?, ?)", (code, message.from_user.id, datetime.now()))
    cur.execute("UPDATE promocodes SET activated = activated + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    
    await message.answer(f"{P['хлопушка']} Промокод активирован! +${promo[1]:.2f} на баланс!")
    await state.clear()

# === РЕФЕРАЛКА ===
@dp.callback_query(lambda c: c.data == "ref")
async def ref_program(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE referrer_id = ? AND total_deposit >= 5", (callback.from_user.id,))
    ref_deposit_count = cur.fetchone()[0]
    
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("SELECT SUM(total_lost) FROM users WHERE referrer_id = ? AND reg_date > ?", (callback.from_user.id, month_ago))
    month_lost = cur.fetchone()[0] or 0
    month_bonus = month_lost * 0.1
    
    ref_count = user['ref_count']
    next_bonus = 0
    for level in [100, 250, 500, 1000]:
        if ref_count < level:
            next_bonus = level - ref_count
            break
    
    text = f"""{P['реф']} Реферальная программа

👥 Рефералы: {ref_count} (пополнили: {ref_deposit_count})
💰 За месяц: ${month_bonus:.2f}
💵 Всего: ${user['ref_earned']:.2f}

Условия:
• $1 за друга, который пополнил баланс от $5
• 10% от проигрышей рефералов — каждую пятницу в 21:00

Бонусы:
• 100 друзей — +$5
• 250 друзей — +$15
• 500 друзей — +$30
• 1000 друзей — +$60

🏆 До бонуса: {next_bonus} рефералов

🔗 Реферальная ссылка:
https://t.me/{BOT_USERNAME}?start={callback.from_user.id}"""
    
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML)
    await callback.answer()

# === ИГРЫ ===
@dp.callback_query(lambda c: c.data.startswith("game_"))
async def handle_game(callback: CallbackQuery, state: FSMContext):
    can_bet, remaining = check_bet_cooldown(callback.from_user.id)
    if not can_bet:
        await callback.answer(f"⚠️ Подожди {remaining:.0f} сек между ставками!", show_alert=True)
        return
    
    game = callback.data.split("_")[1]
    await state.update_data(game=game)
    await callback.message.answer(f"✏️ Введи сумму ставки (мин. ${MIN_BET:.2f})")
    await state.set_state(BetState.waiting_bet)
    await callback.answer()

@dp.message(BetState.waiting_bet)
async def process_bet(message: Message, state: FSMContext):
    can_bet, remaining = check_bet_cooldown(message.from_user.id)
    if not can_bet:
        await message.answer(f"⚠️ Подожди {remaining:.0f} сек между ставками!")
        return
    
    user = get_user(message.from_user.id)
    data = await state.get_data()
    game = data.get("game")
    
    try:
        bet = float(message.text.replace(",", "."))
        if bet < MIN_BET:
            await message.answer(f"❌ Минимальная ставка ${MIN_BET:.2f}!")
            return
        if bet > user["balance"]:
            await message.answer(f"❌ Недостаточно средств! Баланс: ${user['balance']:.2f}")
            return
    except:
        await message.answer("❌ Введите число!")
        return
    
    update_last_bet_time(message.from_user.id)
    update_balance(message.from_user.id, -bet)
    
    try:
        if game == "dice":
            roll = random.randint(1, 6)
            if roll >= 4:
                mult = {4: 1.4, 5: 1.8, 6: 2.4}[roll]
                win = bet * mult
                update_balance(message.from_user.id, win)
                add_to_wagered(message.from_user.id, bet)
                await message.answer(f"🎲 Выпало: {roll}\n✅ Выигрыш: ${win:.2f} (x{mult})!")
            else:
                add_to_lost(message.from_user.id, bet)
                await message.answer(f"🎲 Выпало: {roll}\n❌ Проигрыш: ${bet:.2f}!")
        
        elif game == "football":
            if random.random() < 0.5:
                win = bet * 1.3
                update_balance(message.from_user.id, win)
                add_to_wagered(message.from_user.id, bet)
                await message.answer(f"⚽️ ГОЛ! ✅ Выигрыш: ${win:.2f} (x1.3)!")
            else:
                add_to_lost(message.from_user.id, bet)
                await message.answer(f"⚽️ Мимо ворот! ❌ Проигрыш: ${bet:.2f}!")
        
        elif game == "target":
            if random.random() < 0.2:
                win = bet * 5
                update_balance(message.from_user.id, win)
                add_to_wagered(message.from_user.id, bet)
                await message.answer(f"🎯 В ЦЕНТР! ✅ Выигрыш: ${win:.2f} (x5)!")
            else:
                add_to_lost(message.from_user.id, bet)
                await message.answer(f"🎯 Мимо! ❌ Проигрыш: ${bet:.2f}!")
        
        elif game == "tower":
            await state.update_data(tower_bet=bet, tower_level=0, tower_mult=1.0)
            await state.set_state(TowerState.playing)
            await play_tower_level(message, state, 0, 1.0, bet)
            return
    
    except Exception as e:
        logging.error(f"Game error: {e}")
        update_balance(message.from_user.id, bet)
        await message.answer("❌ Ошибка! Ставка возвращена.")
    
    await state.clear()
    await games_menu(message)

# === БАШНЯ ===
async def play_tower_level(message: Message, state: FSMContext, level: int, current_mult: float, bet: float):
    multipliers = [1.4, 1.7, 2.4, 3.2, 4.0, 6.0]
    
    if level >= len(multipliers):
        win = bet * multipliers[-1]
        update_balance(message.from_user.id, win)
        add_to_wagered(message.from_user.id, bet)
        await message.answer(f"🏆 ПОЛНАЯ ПОБЕДА! 🏆\n🗼 Вы прошли все 6 уровней!\n💰 Выигрыш: ${win:.2f} (x{multipliers[-1]})!")
        await state.clear()
        await games_menu(message)
        return
    
    bomb_side = random.randint(0, 1)
    await state.update_data(tower_bomb_side=bomb_side, tower_level=level, tower_bet=bet, tower_mult=current_mult)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Левая 🟩", callback_data="tower_left"),
        InlineKeyboardButton(text="Правая 🟩 ➡️", callback_data="tower_right")
    )
    if level > 0:
        builder.row(InlineKeyboardButton(text=f"{P['вывести']} Забрать ${bet * current_mult:.2f}", callback_data="tower_cashout"))
    
    await message.answer(
        f"🗼 БАШНЯ - Уровень {level + 1}/6\n"
        f"💰 Ставка: ${bet:.2f}\n"
        f"📈 Множитель: x{multipliers[level]} (выигрыш: ${bet * multipliers[level]:.2f})\n"
        f"💀 В одной из клеток БОМБА!\n\n"
        f"Выбери клетку:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(TowerState.playing, lambda c: c.data in ["tower_left", "tower_right"])
async def tower_choice(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await callback.answer("Игра не найдена!")
        return
    
    bomb_side = data.get("tower_bomb_side")
    level = data.get("tower_level", 0)
    bet = data.get("tower_bet", 0)
    current_mult = data.get("tower_mult", 1.0)
    
    multipliers = [1.4, 1.7, 2.4, 3.2, 4.0, 6.0]
    chosen_side = 0 if callback.data == "tower_left" else 1
    
    if chosen_side == bomb_side:
        add_to_lost(callback.from_user.id, bet)
        await callback.message.edit_text(
            f"💥 БОМБА ВЗОРВАЛАСЬ! 💥\n"
            f"🗼 Вы проиграли на уровне {level + 1}/6\n"
            f"💰 Потеряно: ${bet:.2f}\n\n"
            f"🎮 Попробуйте снова!"
        )
        await state.clear()
        await games_menu(callback.message)
    else:
        level += 1
        new_mult = multipliers[level - 1]
        
        await callback.message.edit_text(
            f"✅ БЕЗОПАСНО! 🟩\n"
            f"🗼 Уровень {level}/6 пройден!\n"
            f"💰 Текущий выигрыш: ${bet * new_mult:.2f} (x{new_mult})\n\n"
            f"🎲 Продолжаем?"
        )
        
        if level >= len(multipliers):
            win = bet * multipliers[-1]
            update_balance(callback.from_user.id, win)
            add_to_wagered(callback.from_user.id, bet)
            await callback.message.answer(
                f"🏆 ПОБЕДА! 🏆\n"
                f"🗼 Вы прошли ВСЕ 6 уровней!\n"
                f"💰 Выигрыш: ${win:.2f} (x{multipliers[-1]})!"
            )
            await state.clear()
            await games_menu(callback.message)
        else:
            await state.update_data(tower_level=level, tower_mult=new_mult)
            new_bomb = random.randint(0, 1)
            await state.update_data(tower_bomb_side=new_bomb)
            
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="⬅️ Левая 🟩", callback_data="tower_left"),
                InlineKeyboardButton(text="Правая 🟩 ➡️", callback_data="tower_right")
            )
            builder.row(InlineKeyboardButton(text=f"{P['вывести']} Забрать ${bet * new_mult:.2f}", callback_data="tower_cashout"))
            
            await callback.message.answer(
                f"🗼 БАШНЯ - Уровень {level + 1}/6\n"
                f"💰 Ставка: ${bet:.2f}\n"
                f"📈 Множитель: x{multipliers[level]} (выигрыш: ${bet * multipliers[level]:.2f})\n"
                f"💀 В одной из клеток БОМБА!\n\n"
                f"Выбери клетку:",
                reply_markup=builder.as_markup()
            )
    
    await callback.answer()

@dp.callback_query(TowerState.playing, lambda c: c.data == "tower_cashout")
async def tower_cashout(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await callback.answer("Игра не найдена!")
        return
    
    bet = data.get("tower_bet", 0)
    current_mult = data.get("tower_mult", 1.0)
    level = data.get("tower_level", 0)
    
    if level == 0:
        await callback.answer("Нужно открыть хотя бы одну клетку!", show_alert=True)
        return
    
    win = bet * current_mult
    update_balance(callback.from_user.id, win)
    add_to_wagered(callback.from_user.id, bet)
    
    await callback.message.edit_text(
        f"💰 ВЫ ЗАБРАЛИ ВЫИГРЫШ! 💰\n"
        f"🗼 Пройдено уровней: {level}/6\n"
        f"✅ Выигрыш: ${win:.2f} (x{current_mult})!"
    )
    await state.clear()
    await games_menu(callback.message)
    await callback.answer()

# === ДЕПОЗИТЫ (РЕАЛЬНЫЕ) ===
@dp.callback_query(lambda c: c.data == "deposit")
async def deposit_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{P['крипто_бот']} CryptoBot", callback_data="deposit_crypto")],
        [InlineKeyboardButton(text=f"{P['звезда']} Stars", callback_data="deposit_stars")]
    ])
    await callback.message.edit_text(f"{P['пополнить']} Пополнение средств", reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "deposit_crypto")
async def deposit_crypto(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(f"✏️ Введите сумму для пополнения (мин. $0.15, макс. $1000):")
    await state.set_state(DepositState.waiting_crypto)
    await callback.answer()

@dp.message(DepositState.waiting_crypto)
async def process_crypto_deposit(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount < 0.15:
            await message.answer("❌ Минимальная сумма $0.15!")
            return
        if amount > 1000:
            await message.answer("❌ Максимальная сумма $1000 за один платеж!")
            return        
        # Создаем реальный счет в CryptoBot
        invoice_url = await create_crypto_invoice(message.from_user.id, amount)
        
        if invoice_url:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Перейти к оплате", url=invoice_url)],
                [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"verify_payment_{amount}")]
            ])
            await message.answer(
                f"💳 Счет для пополнения создан!\n"
                f"💰 Сумма: ${amount:.2f} USDT\n\n"
                f"1️⃣ Оплатите по ссылке выше\n"
                f"2️⃣ После оплаты нажмите 'Проверить оплату'\n\n"
                f"⏱ Счет действителен 1 час",
                reply_markup=keyboard
            )
        else:
            await message.answer("❌ Ошибка создания счета. Попробуйте позже или свяжитесь с администратором.")
    except Exception as e:
        logging.error(f"Deposit error: {e}")
        await message.answer("❌ Введите корректную сумму!")
    
    await state.clear()

@dp.callback_query(lambda c: c.data and c.data.startswith("verify_payment_"))
async def verify_payment(callback: CallbackQuery):
    amount = float(callback.data.split("_")[2])
    
    await callback.message.edit_text("🔄 Проверяем оплату... Пожалуйста, подождите.")
    
    # Реальная проверка через API
    is_paid = await check_crypto_payment(callback.from_user.id, amount)
    
    if is_paid:
        update_balance(callback.from_user.id, amount)
        
        # Обновляем статистику депозитов
        conn = sqlite3.connect('bot_database.db')
        cur = conn.cursor()
        cur.execute("UPDATE users SET total_deposit = total_deposit + ? WHERE user_id = ?", (amount, callback.from_user.id))
        
        # Реферальная комиссия
        user = get_user(callback.from_user.id)
        if user.get("referrer_id") and amount >= 5:
            cur.execute("UPDATE users SET ref_earned = ref_earned + 1, ref_deposit_count = ref_deposit_count + 1 WHERE user_id = ?", 
                       (user['referrer_id'],))
            cur.execute("UPDATE users SET balance = balance + 1 WHERE user_id = ?", (user['referrer_id'],))
        
        cur.execute("UPDATE stats SET total_deposits = total_deposits + ? WHERE id = 1", (amount,))
        conn.commit()
        conn.close()
        
        await callback.message.edit_text(
            f"✅ ОПЛАТА ПОДТВЕРЖДЕНА! ✅\n\n"
            f"💰 Баланс пополнен на ${amount:.2f}\n"
            f"🎮 Приятной игры!"
        )
    else:
        await callback.message.edit_text(
            f"⏳ Платеж не найден или еще не обработан.\n\n"
            f"💡 Если вы оплатили, подождите 1-2 минуты и попробуйте снова.\n"
            f"❓ Если проблема не решится, свяжитесь с администратором."
        )
    
    await callback.answer()

@dp.callback_query(lambda c: c.data == "deposit_stars")
async def deposit_stars(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✏️ Введите сумму для пополнения от 50 звёзд (курс 1 звезда = $0.011):")
    await state.set_state(DepositState.waiting_stars)
    await callback.answer()

@dp.message(DepositState.waiting_stars)
async def process_stars_deposit(message: Message, state: FSMContext):
    try:
        stars = int(message.text)
        if stars < 50:
            await message.answer("❌ Минимум 50 звезд!")
            return
        if stars > 100000:
            await message.answer("❌ Максимум 100,000 звезд за раз!")
            return
        
        amount_usd = stars * 0.011
        update_balance(message.from_user.id, amount_usd)
        
        conn = sqlite3.connect('bot_database.db')
        cur = conn.cursor()
        cur.execute("UPDATE users SET total_deposit = total_deposit + ? WHERE user_id = ?", (amount_usd, message.from_user.id))
        cur.execute("UPDATE stats SET total_deposits_stars = total_deposits_stars + ? WHERE id = 1", (amount_usd))
        conn.commit()
        conn.close()
        
        await message.answer(f"✅ Пополнено {stars} звезд → ${amount_usd:.2f} на баланс!")
    except ValueError:
        await message.answer("❌ Введите целое число!")
    
    await state.clear()

# === ВЫВОДЫ ===
@dp.callback_query(lambda c: c.data == "withdraw")
async def withdraw_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(f"{P['вывести']} Вывод средств\n\n💰 Минимальная сумма: ${MIN_WITHDRAW:.2f}\n💡 Максимальная: $1000\n\nВведите сумму:")
    await state.set_state(WithdrawState.waiting_amount)
    await callback.answer()

@dp.message(WithdrawState.waiting_amount)
async def process_withdraw(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    try:
        amount = float(message.text.replace(",", "."))
        if amount < MIN_WITHDRAW:
            await message.answer(f"❌ Минимальная сумма ${MIN_WITHDRAW:.2f}!")
            return
        if amount > 1000:
            await message.answer("❌ Максимальная сумма вывода $1000 за раз!")
            return
        if amount > user["balance"]:
            await message.answer(f"❌ Недостаточно средств! Баланс: ${user['balance']:.2f}")
            return
        
        # Резервируем средства
        update_balance(message.from_user.id, -amount)
        
        conn = sqlite3.connect('bot_database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO withdraw_requests (user_id, amount, created_at, status) VALUES (?, ?, ?, 'pending')",
                   (message.from_user.id, amount, datetime.now()))
        conn.commit()
        conn.close()
        
        # Уведомляем админов
        for admin_id in ADMIN_IDS:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_withdraw_{message.from_user.id}_{amount}"),
                 InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_withdraw_{message.from_user.id}_{amount}")]
            ])
            await bot.send_message(
                admin_id,
                f"💰 НОВАЯ ЗАЯВКА НА ВЫВОД!\n\n"
                f"👤 Пользователь: {message.from_user.id}\n"
                f"💵 Сумма: ${amount:.2f}\n"
                f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                reply_markup=keyboard
            )
        
        await message.answer(
            f"✅ Заявка на вывод ${amount:.2f} создана!\n\n"
            f"⏱ Обычно вывод обрабатывается в течение 24 часов.\n"
            f"📩 Вы получите уведомление при изменении статуса."
        )
    except Exception as e:
        logging.error(f"Withdraw error: {e}")
        await message.answer("❌ Ошибка! Попробуйте позже.")
    
    await state.clear()

# === АДМИН-ПАНЕЛЬ ===
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Доступ запрещен!")
        return
    
    # Получаем статистику
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("SELECT total_volume, total_deposits, total_deposits_stars, total_withdraws, total_players FROM stats WHERE id = 1")
    stats = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM withdraw_requests WHERE status = 'pending'")
    pending_withdraws = cur.fetchone()[0]
    conn.close()
    
    text = f"""📊 СТАТИСТИКА

💰 Оборот: ${stats[0]:.2f}
📈 Пополнений: ${stats[1]:.2f}
⭐️ Stars пополнений: ${stats[2]:.2f}
📤 Выводов: ${stats[3]:.2f}
👥 Игроков: {stats[4]}
⏳ Заявок на вывод: {pending_withdraws}"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="🎫 Создать промокод", callback_data="admin_create_promo")],
        [InlineKeyboardButton(text="🧾 Создать чек", callback_data="admin_create_check")],
        [InlineKeyboardButton(text="💰 Заявки на вывод", callback_data="admin_withdraws")],
        [InlineKeyboardButton(text="📝 Аннулировать баланс", callback_data="admin_ban")],
        [InlineKeyboardButton(text="➕ Пополнить баланс", callback_data="admin_add")],
        [InlineKeyboardButton(text="👤 Статистика игрока", callback_data="admin_stats")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data == "admin_withdraws")
async def admin_withdraws(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен!")
        return
    
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, amount, created_at FROM withdraw_requests WHERE status = 'pending'")
    requests = cur.fetchall()
    conn.close()
    
    if not requests:
        await callback.message.answer("📭 Нет активных заявок на вывод")
        await callback.answer()
        return
    
    for req in requests:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_withdraw_{req[1]}_{req[2]}_{req[0]}"),
             InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_withdraw_{req[0]}")]
        ])
        await callback.message.answer(
            f"💰 Заявка #{req[0]}\n"
            f"👤 ID: {req[1]}\n"
            f"💵 Сумма: ${req[2]}\n"
            f"📅 Дата: {req[3]}",
            reply_markup=keyboard
        )
    
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("approve_withdraw_"))
async def approve_withdraw(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен!")
        return
    
    parts = callback.data.split("_")
    user_id = int(parts[2])
    amount = float(parts[3])
    request_id = int(parts[4])
    
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("UPDATE withdraw_requests SET status = 'completed' WHERE id = ?", (request_id,))
    cur.execute("UPDATE stats SET total_withdraws = total_withdraws + ? WHERE id = 1", (amount,))
    conn.commit()
    conn.close()
    
    await bot.send_message(user_id, f"✅ Ваша заявка на вывод ${amount:.2f} ОДОБРЕНА! Средства будут отправлены в ближайшее время.")
    await callback.message.edit_text(f"✅ Заявка #{request_id} одобрена! Пользователь уведомлен.")
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("reject_withdraw_"))
async def reject_withdraw(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен!")
        return
    
    request_id = int(callback.data.split("_")[2])
    
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id, amount FROM withdraw_requests WHERE id = ?", (request_id,))
    req = cur.fetchone()
    
    if req:
        user_id, amount = req
        update_balance(user_id, amount)  # Возвращаем средства
        cur.execute("UPDATE withdraw_requests SET status = 'rejected' WHERE id = ?", (request_id,))
        conn.commit()
        await bot.send_message(user_id, f"❌ Ваша заявка на вывод ${amount:.2f} ОТКЛОНЕНА. Средства возвращены на баланс.")
    
    conn.close()
    
    await callback.message.edit_text(f"❌ Заявка #{request_id} отклонена. Средства возвращены.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_ban")
async def admin_ban(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен!")
        return
    
    await callback.message.answer("✏️ Введите ID пользователя для аннулирования баланса:")
    await state.set_state(AdminState.waiting_ban_id)
    await callback.answer()

@dp.message(AdminState.waiting_ban_id)
async def admin_ban_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await state.update_data(ban_user_id=user_id)
        await message.answer(f"✏️ Введите сумму для списания (минус) или укажите 'full' для полного обнуления:")
        await state.set_state(AdminState.waiting_ban_amount)
    except:
        await message.answer("❌ Введите корректный ID!")

@dp.message(AdminState.waiting_ban_amount)
async def admin_ban_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("ban_user_id")
    user = get_user(user_id)
    
    if message.text.lower() == "full":
        update_balance(user_id, -user["balance"])
        await message.answer(f"✅ Баланс пользователя {user_id} обнулен! Было: ${user['balance']:.2f}")
    else:
        try:
            amount = float(message.text.replace(",", "."))
            if amount > 0:
                amount = -amount
            update_balance(user_id, amount)
            await message.answer(f"✅ Списано ${abs(amount):.2f} с баланса пользователя {user_id}")
        except:
            await message.answer("❌ Введите число или 'full'!")
    
    await state.clear()

@dp.callback_query(lambda c: c.data == "admin_add")
async def admin_add(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен!")
        return
    
    await callback.message.answer("✏️ Введите ID пользователя для пополнения баланса:")
    await state.set_state(AdminState.waiting_add_id)
    await callback.answer()

@dp.message(AdminState.waiting_add_id)
async def admin_add_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await state.update_data(add_user_id=user_id)
        await message.answer("✏️ Введите сумму для пополнения:")
        await state.set_state(AdminState.waiting_add_amount)
    except:
        await message.answer("❌ Введите корректный ID!")

@dp.message(AdminState.waiting_add_amount)
async def admin_add_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("add_user_id")
    
    try:
        amount = float(message.text.replace(",", "."))
        update_balance(user_id, amount)
        await message.answer(f"✅ Пользователю {user_id} начислено ${amount:.2f}")
    except:
        await message.answer("❌ Введите число!")
    
    await state.clear()

@dp.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен!")
        return
    
    await callback.message.answer("✏️ Введите ID пользователя для просмотра статистики:")
    await state.set_state(AdminState.waiting_stats_id)
    await callback.answer()

@dp.message(AdminState.waiting_stats_id)
async def admin_stats_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user = get_user(user_id)
        
        text = f"""📊 СТАТИСТИКА ИГРОКА #{user_id}

💰 Баланс: ${user['balance']:.2f}
📈 Всего депозитов: ${user.get('total_deposit', 0):.2f}
🎲 Оборот ставок: ${user['total_wagered']:.2f}
💸 Проигрыши: ${user['total_lost']:.2f}
📅 Дата регистрации: {user['reg_date']}

👥 Реферальная система:
• Привел друзей: {user['ref_count']}
• Пополнили от $5: {user['ref_deposit_count']}
• Заработано: ${user['ref_earned']:.2f}"""
        
        await message.answer(text, parse_mode=ParseMode.HTML)
    except:
        await message.answer("❌ Введите корректный ID!")
    
    await state.clear()

# === РАССЫЛКА ===
@dp.callback_query(lambda c: c.data == "admin_mailing")
async def admin_mailing(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен!")
        return
    
    await callback.message.answer("📢 Отправьте текст рассылки (можно с HTML-разметкой):")
    await state.set_state(AdminState.waiting_mailing)
    await callback.answer()

@dp.message(AdminState.waiting_mailing)
async def process_mailing_text(message: Message, state: FSMContext):
    await state.update_data(mailing_text=message.text, mailing_has_buttons=False)
    await message.answer("✏️ Добавить кнопки? (да/нет)\n\nЕсли да, то после этого я попрошу ввести кнопки в формате:\nтекст - url")
    await state.set_state(AdminState.waiting_mailing_buttons)

@dp.message(AdminState.waiting_mailing_buttons)
async def process_mailing_buttons(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("mailing_text")
    
    if message.text.lower() == "да":
        await message.answer("✏️ Введите кнопки. Каждая с новой строки в формате:\nТекст кнопки - https://ссылка\n\nПример:\nКанал - https://t.me/channel\nЧат - https://t.me/chat")
        await state.set_state(AdminState.waiting_mailing_buttons)
        await state.update_data(mailing_has_buttons=True)
        return
    elif message.text.lower() == "нет":
        # Отправляем рассылку без кнопок
        await send_mailing(message, state, text, None)
    else:
        # Пользователь ввел кнопки
        buttons = []
        for line in message.text.split("\n"):
            if " - " in line:
                btn_text, url = line.split(" - ", 1)
                buttons.append([InlineKeyboardButton(text=btn_text.strip(), url=url.strip())])
        
        if buttons:
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await send_mailing(message, state, text, keyboard)
        else:
            await message.answer("❌ Неверный формат! Используйте: Текст - ссылка")
            return

async def send_mailing(message: Message, state: FSMContext, text: str, keyboard: Optional[InlineKeyboardMarkup]):
    await message.answer("🔄 Начинаю рассылку...")
    
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    conn.close()
    
    sent = 0
    failed = 0
    
    for user in users:
        try:
            await bot.send_message(user[0], text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1
    
    await message.answer(f"✅ Рассылка завершена!\n📨 Отправлено: {sent}\n❌ Не доставлено: {failed}")
    await state.clear()

# === ПРОМОКОДЫ (АДМИН) ===
@dp.callback_query(lambda c: c.data == "admin_create_promo")
async def admin_create_promo(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен!")
        return
    
    await callback.message.answer("✏️ Введите код промокода (латиница, цифры, без пробелов):")
    await state.set_state(AdminState.waiting_promo_code)
    await callback.answer()

@dp.message(AdminState.waiting_promo_code)
async def promo_code_step1(message: Message, state: FSMContext):
    await state.update_data(promo_code=message.text.upper())
    await message.answer("💰 Введите сумму награды (в долларах):")
    await state.set_state(AdminState.waiting_promo_reward)

@dp.message(AdminState.waiting_promo_reward)
async def promo_code_step2(message: Message, state: FSMContext):
    try:
        reward = float(message.text)
        if reward <= 0:
            await message.answer("❌ Сумма должна быть больше 0!")
            return
        await state.update_data(promo_reward=reward)
        await message.answer("🔢 Введите максимальное количество активаций (0 - безлимит):")
        await state.set_state(AdminState.waiting_promo_max)
    except:
        await message.answer("❌ Введите число!")

@dp.message(AdminState.waiting_promo_max)
async def promo_code_step3(message: Message, state: FSMContext):
    try:
        max_act = int(message.text)
        await state.update_data(promo_max_act=max_act)
        await message.answer("💰 Минимальный депозит для активации (в $, 0 - без ограничений):")
        await state.set_state(AdminState.waiting_promo_min_dep)
    except:
        await message.answer("❌ Введите целое число!")

@dp.message(AdminState.waiting_promo_min_dep)
async def promo_code_step4(message: Message, state: FSMContext):
    try:
        min_dep = float(message.text)
        await state.update_data(promo_min_deposit=min_dep)
        await message.answer("🎲 Минимальный оборот для активации (в $, 0 - без ограничений):")
        await state.set_state(AdminState.waiting_promo_min_wag)
    except:
        await message.answer("❌ Введите число!")

@dp.message(AdminState.waiting_promo_min_wag)
async def promo_code_step5(message: Message, state: FSMContext):
    try:
        min_wag = float(message.text)
        await state.update_data(promo_min_wagered=min_wag)
        await message.answer("👑 Только для премиум пользователей? (да/нет):")
        await state.set_state(AdminState.waiting_promo_prem)
    except:
        await message.answer("❌ Введите число!")

@dp.message(AdminState.waiting_promo_prem)
async def promo_code_step6(message: Message, state: FSMContext):
    only_premium = 1 if message.text.lower() == "да" else 0
    data = await state.get_data()
    
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO promocodes (code, reward, max_activations, min_deposit, min_wagered, only_premium, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
               (data['promo_code'], data['promo_reward'], data['promo_max_act'], data['promo_min_deposit'], 
                data['promo_min_wagered'], only_premium, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()
    
    await message.answer(f"✅ Промокод {data['promo_code']} создан!\n"
                        f"💰 Награда: ${data['promo_reward']}\n"
                        f"🔢 Макс. активаций: {data['promo_max_act'] if data['promo_max_act'] > 0 else '∞'}\n"
                        f"💎 Мин. депозит: ${data['promo_min_deposit']}\n"
                        f"🎲 Мин. оборот: ${data['promo_min_wagered']}\n"
                        f"👑 Только премиум: {'да' if only_premium else 'нет'}")
    await state.clear()

# === СОЗДАНИЕ ЧЕКА ===
@dp.callback_query(lambda c: c.data == "admin_create_check")
async def admin_create_check(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен!")
        return
    
    await callback.message.answer("💰 Введите сумму чека (в долларах):")
    await state.set_state(AdminState.waiting_check_amount)
    await callback.answer()

@dp.message(AdminState.waiting_check_amount)
async def check_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(check_amount=amount)
        await message.answer("🔢 Введите максимальное количество активаций (0 - безлимит):")
        await state.set_state(AdminState.waiting_check_max)
    except:
        await message.answer("❌ Введите число!")

@dp.message(AdminState.waiting_check_max)
async def check_max(message: Message, state: FSMContext):
    try:
        max_act = int(message.text)
        await state.update_data(check_max_act=max_act)
        await message.answer("💰 Минимальный депозит для активации (в $, 0 - без ограничений):")
        await state.set_state(AdminState.waiting_check_min_dep)
    except:
        await message.answer("❌ Введите целое число!")

@dp.message(AdminState.waiting_check_min_dep)
async def check_min_dep(message: Message, state: FSMContext):
    try:
        min_dep = float(message.text)
        await state.update_data(check_min_deposit=min_dep)
        await message.answer("🎲 Минимальный оборот для активации (в $, 0 - без ограничений):")
        await state.set_state(AdminState.waiting_check_min_wag)
    except:
        await message.answer("❌ Введите число!")

@dp.message(AdminState.waiting_check_min_wag)
async def check_min_wag(message: Message, state: FSMContext):
    try:
        min_wag = float(message.text)
        await state.update_data(check_min_wagered=min_wag)
        await message.answer("👑 Только для премиум пользователей? (да/нет):")
        await state.set_state(AdminState.waiting_check_prem)
    except:
        await message.answer("❌ Введите число!")

@dp.message(AdminState.waiting_check_prem)
async def check_prem(message: Message, state: FSMContext):
    only_premium = 1 if message.text.lower() == "да" else 0
    data = await state.get_data()
    
    check_id = generate_check_id()
    
    conn = sqlite3.connect('bot_database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO checks (check_id, amount, max_activations, min_deposit, min_wagered, only_premium, created_by, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (check_id, data['check_amount'], data['check_max_act'], data['check_min_deposit'], 
                data['check_min_wagered'], only_premium, message.from_user.id, datetime.now(),
                (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()
    
    check_link = f"https://t.me/{BOT_USERNAME}?start=check_{check_id}"
    
    await message.answer(f"✅ Чек создан!\n"
                        f"💰 Сумма: ${data['check_amount']}\n"
                        f"🔗 Ссылка: {check_link}\n"
                        f"🔢 Макс. активаций: {data['check_max_act'] if data['check_max_act'] > 0 else '∞'}\n"
                        f"💎 Мин. депозит: ${data['check_min_deposit']}\n"
                        f"🎲 Мин. оборот: ${data['check_min_wagered']}\n"
                        f"👑 Только премиум: {'да' if only_premium else 'нет'}")
    await state.clear()

# === ОБРАБОТЧИК ЧЕКОВ ===
@dp.message(Command("start"))
async def handle_check_start(message: Message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("check_"):
        check_id = args[1].replace("check_", "")
        
        conn = sqlite3.connect('bot_database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM checks WHERE check_id = ?", (check_id,))
        check = cur.fetchone()
        
        if not check:
            await message.answer("❌ Чек не найден!")
            return
        
        check_id, amount, max_act, activated, min_dep, min_wag, only_premium, created_by, created_at, expires_at = check
        
        if expires_at and datetime.now() > datetime.strptime(expires_at, "%Y-%m-%d"):
            await message.answer("❌ Срок действия чека истек!")
            return
        
        if max_act > 0 and activated >= max_act:
            await message.answer("❌ Чек уже использован максимальное количество раз!")
            return
        
        user = get_user(message.from_user.id)
        
        if only_premium and not user.get("is_premium", False):
            await message.answer("❌ Этот чек только для премиум пользователей!")
            return
        
        if min_dep > 0 and user.get("total_deposit", 0) < min_dep:
            await message.answer(f"❌ Для активации чека нужен депозит от ${min_dep}!")
            return
        
        if min_wag > 0 and user.get("total_wagered", 0) < min_wag:
            await message.answer(f"❌ Для активации чека нужен оборот от ${min_wag}!")
            return
        
        # Активируем чек
        update_balance(message.from_user.id, amount)
        cur.execute("UPDATE checks SET activated = activated + 1 WHERE check_id = ?", (check_id,))
        cur.execute("INSERT INTO check_activations VALUES (?, ?, ?)", (check_id, message.from_user.id, datetime.now()))
        conn.commit()
        conn.close()
        
        await message.answer(f"🎉 Чек активирован! +${amount:.2f} на баланс!")

# ========== ЗАПУСК ==========
async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="admin", description="👑 Админ-панель")
    ])
    
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
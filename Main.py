import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, LabeledPrice, PreCheckoutQuery
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "СЮДА_ТОКЕН_ИЗ_BOTFATHER")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://km726.github.io/tarot/")
PRICE_STARS = 50  # Цена полного расклада в Stars

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔮 Открыть Таро",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    await message.answer(
        "🔮 <b>Добро пожаловать в Таро!</b>\n\n"
        "Получи ответ на свой вопрос с помощью карт.\n"
        "Первая карта — бесплатно.\n"
        f"Полный расклад из 3 карт — {PRICE_STARS} ⭐",
        reply_markup=kb,
        parse_mode="HTML"
    )


@dp.message(F.web_app_data)
async def web_app_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        await message.answer("Ошибка данных. Попробуй ещё раз.")
        return

    if data.get("action") == "buy_full_spread":
        await bot.send_invoice(
            chat_id=message.chat.id,
            title="Полный расклад Таро",
            description="3 карты: прошлое, настоящее, будущее",
            payload=json.dumps({
                "question": data.get("question", ""),
                "firstCard": data.get("firstCard"),
                "firstReversed": data.get("firstReversed")
            }),
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Расклад", amount=PRICE_STARS)],
            start_parameter="full_spread"
        )


@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def payment_success(message: types.Message):
    payload = json.loads(message.successful_payment.invoice_payload)

    paid_url = f"{WEBAPP_URL}?paid=true"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✨ Открыть полный расклад",
            web_app=WebAppInfo(url=paid_url)
        )]
    ])

    await message.answer(
        f"⭐ <b>Оплата прошла!</b>\n\n"
        f"Вопрос: <i>{payload.get('question', '')}</i>\n\n"
        "Нажми кнопку ниже — откроется полный расклад.",
        reply_markup=kb,
        parse_mode="HTML"
    )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
import os
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]
VIP_STARS = int(os.getenv("VIP_STARS", "50"))
PORT = int(os.getenv("PORT", "10000"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Simple in-memory VIP list for testing (resets if server restarts)
vip_users: set[int] = set()


@dp.message(Command("start"))
async def start_cmd(message: Message) -> None:
    await message.answer(
        "Hello! Welcome to the bot.\n\n"
        "Commands:\n"
        "/sample - See a sample market snapshot\n"
        "/vip - Pay with Telegram Stars to unlock VIP\n"
        "/status - Check your VIP status"
    )


@dp.message(Command("sample"))
async def sample_cmd(message: Message) -> None:
    await message.answer(
        "Sample Snapshot (Demo Data):\n"
        "Index: NIFTY 50\n"
        "Sample Spot: 24,500\n"
        "Sample PCR: 1.05\n"
        "Note: Replace this with a live data feed later."
    )


@dp.message(Command("vip"))
async def vip_cmd(message: Message) -> None:
    invoice_link = await bot.create_invoice_link(
        title="VIP Access (30 Days)",
        description="Unlock VIP features using Telegram Stars.",
        payload=f"vip_{message.from_user.id}",
        currency="XTR",
        prices=[LabeledPrice(label="VIP Pass", amount=VIP_STARS)],
    )
    await message.answer(
        f"Tap the link below to pay {VIP_STARS} Telegram Stars:\n{invoice_link}"
    )


@dp.message(Command("status"))
async def status_cmd(message: Message) -> None:
    if message.from_user.id in vip_users:
        await message.answer("Status: VIP Active")
    else:
        await message.answer("Status: Free User (use /vip to upgrade)")


@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def payment_success(message: Message) -> None:
    vip_users.add(message.from_user.id)
    await message.answer("Payment received! Your VIP access is now active.")


async def health_handler(request: web.Request) -> web.Response:
    return web.Response(text="OK")


async def start_web_server() -> None:
    app = web.Application()
    app.router.add_get("/", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()


async def main() -> None:
    await start_web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

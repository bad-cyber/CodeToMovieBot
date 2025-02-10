import logging
from bot import bot
from config.config import CHANNEL_ID

async def check_sub(userid: int) -> bool:
    try:
        check_member = await bot.get_chat_member(CHANNEL_ID, userid)
        return check_member.status in ["member", "creator", "administrator"]
    except Exception as e:
        logging.error(f"Error checking subscription: {e}")
        return False  # Deny access on error

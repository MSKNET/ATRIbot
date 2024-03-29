import random
from .data import Data
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.log import logger
from nonebot import get_driver

data = Data()

GROUP_ID = getattr(data, "GROUP_ID", [])
RATE = getattr(data, "RATE", 0)


def need_send(event: GroupMessageEvent) -> bool:
    if event.to_me:
        return False

    group_id = event.group_id
    user_id = event.user_id

    if group_id not in GROUP_ID:
        return False

    if event.raw_message.startswith("/"):
        return False

    if user_id == 1000000:
        return False

    if event.message[0].type in ["sign", "share", "json", "forward"]:
        return False

    if ("http://" in event.raw_message.lower()
            or "https://" in event.raw_message.lower()):
        return False

    rand = random.random()
    logger.info(f"rand: {rand}")
    if rand > RATE:
        return False

    return True

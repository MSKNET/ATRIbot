from nonebot import get_driver
from nonebot.adapters.onebot.v11 import GROUP
from nonebot.plugin import on_keyword
from nonebot.rule import to_me
import random


tietie = on_keyword("贴贴", rule=to_me(), priority=6, permission=GROUP)


@tietie.handle()
async def handle_func():
    if random.randint(1, 100) <= 50:
        await tietie.finish("贴贴", at_sender=True)
    else:
        await tietie.finish("(逃走)")

from nonebot import on_message, get_driver
from nonebot.adapters.onebot.v11 import GROUP, MessageSegment
from nonebot.plugin import on_command
from .rule import need_send
from .data import Data
from urllib.parse import quote
import aiohttp
import random

data = Data()

DRIVE_URL = getattr(data, "DRIVE_URL", "")
DRIVE_PARAMS = getattr(data, "DRIVE_PARAMS", {})


async def get_drive():
    if DRIVE_URL == "":
        return "未配置URL"

    async with aiohttp.ClientSession() as session:
        async with session.post(DRIVE_URL, params=DRIVE_PARAMS) as resp:
            if resp.status != 200:
                print(await resp.text())
                return f"获取图片失败 ({resp.status})"

            json_data = await resp.json()

            if 'files' not in json_data:
                return "没有找到文件"

            files = [
                file for file in json_data['files']
                if file['mimeType'] in ['image/jpeg', 'image/png']
            ]

            if len(files) == 0:
                return "没有找到文件"

            pic = random.choice(json_data['files'])
            pic_url = DRIVE_URL + quote(pic['name'])

            return MessageSegment.image(pic_url) + "\n" + pic['name']


getrandompic = on_command('getrandompic', permission=GROUP, priority=3)


@getrandompic.handle()
async def getrandompic_handle():
    await getrandompic.finish(await get_drive())


sendrandompic = on_message(
    rule=need_send,
    permission=GROUP,
    priority=7,
    block=True,
)


@sendrandompic.handle()
async def sendrandompic_handle():
    await sendrandompic.finish(get_drive())

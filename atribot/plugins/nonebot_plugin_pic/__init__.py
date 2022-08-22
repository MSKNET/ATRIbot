from nonebot import get_driver
from nonebot.adapters.onebot.v11 import GROUP, MessageSegment
from nonebot.plugin import on_command
from .config import Config
from urllib.parse import quote
import requests
import random

global_config = get_driver().config
config = Config.parse_obj(global_config)
DRIVE_URL = getattr(config, "DRIVE_URL", "")
DRIVE_PARAMS = getattr(config, "DRIVE_PARAMS", {})

getrandompic = on_command('getrandompic', permission=GROUP, priority=3)


@getrandompic.handle()
async def handle_func():
    if DRIVE_URL == "":
        await getrandompic.finish("未配置URL")

    resp = requests.post(DRIVE_URL, params=DRIVE_PARAMS)
    if resp.status_code == 200:
        json_data = resp.json()
        if 'files' in json_data:
            for failed_count in range(10):
                pic = random.choice(json_data['files'])
                if pic['mimeType'] == 'image/jpeg' or pic['mimeType'] == 'image/png':
                    pic_url = DRIVE_URL + quote(pic['name'])
                    await getrandompic.finish(MessageSegment.image(pic_url)+"\n"+pic['name'])

            if failed_count == 9:
                await getrandompic.finish("没有找到文件")
        else:
            await getrandompic.finish("没有找到文件")

    else:
        await getrandompic.finish(f"获取图片失败 ({resp.status_code})")

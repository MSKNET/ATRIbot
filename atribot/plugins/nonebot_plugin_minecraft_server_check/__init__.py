from nonebot import get_driver
from nonebot.adapters.onebot.v11 import GROUP
from nonebot.plugin import on_command
from .config import Config
import requests

global_config = get_driver().config
config = Config.parse_obj(global_config)
MC_SERVERS = getattr(config, "MC_SERVERS", {})
MC_API_SERVER = getattr(config, "MC_API_SERVER", "")

mcscheck = on_command('mcscheck', permission=GROUP, priority=4)


@mcscheck.handle()
async def handle_func():
    if len(MC_SERVERS) == 0:
        await mcscheck.finish("未配置服务器")

    for mcserver_addr, mcserver_desc in MC_SERVERS.items():
        resp = requests.get(MC_API_SERVER + mcserver_addr)
        if resp.status_code == 200:
            json_data = resp.json()
            if json_data["online"] == False:
                await mcscheck.send(f"{mcserver_addr} ({mcserver_desc}) 当前不在线。")
            else:
                if json_data['players']['online'] == 0:
                    await mcscheck.send(f"{mcserver_addr} ({mcserver_desc}) 当前没有玩家在线。")
                else:
                    await mcscheck.send(f"{mcserver_addr} ({mcserver_desc}) 在线玩家： {json_data['players']['uuid']}。")
        else:
            await mcscheck.send(f"{mcserver_addr} ({mcserver_desc}) 获取信息失败（{resp.status_code}）。")

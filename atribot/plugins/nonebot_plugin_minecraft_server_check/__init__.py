from nonebot import get_driver
from nonebot.adapters.onebot.v11 import GROUP
from nonebot.plugin import on_command
from .config import Config
import requests
import threading

global_config = get_driver().config
config = Config.parse_obj(global_config)
MC_SERVERS = getattr(config, "MC_SERVERS", {})
MC_API_SERVER = getattr(config, "MC_API_SERVER", "")
MC_BEDROCK_SERVERS = getattr(config, "MC_BEDROCK_SERVERS", "")
MC_API_SERVER_BEDROCK = getattr(config, "MC_API_SERVER_BEDROCK", "")

mcscheck = on_command('mcscheck', permission=GROUP, priority=4)


def check_server(addr, desc):
    resp = requests.get(addr)
    if resp.status_code == 200:
        json_data = resp.json()
        addr = addr.split('/')[-1]
        if not json_data["online"]:
            return f"{addr} ({desc}) 当前不在线。"
        else:
            if json_data['players']['online'] == 0:
                return f"{addr} ({desc}) 当前没有玩家在线。"
            else:
                return f"{addr} ({desc}) 在线玩家： {json_data['players']['uuid']}。"
    else:
        return f"{addr} ({desc}) 获取信息失败（{resp.status_code}）。"


@mcscheck.handle()
async def handle_func():
    if len(MC_SERVERS) == 0:
        await mcscheck.finish("未配置服务器")

    result = []
    thread_list = []
    for addr, desc in MC_SERVERS.items():
        t = threading.Thread(target=lambda: result.append(check_server(MC_API_SERVER + addr, desc)))
        t.start()
        thread_list.append(t)

    for addr, desc in MC_BEDROCK_SERVERS.items():
        t = threading.Thread(target=lambda: result.append(check_server(MC_API_SERVER_BEDROCK + addr, desc)))
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

    await mcscheck.finish("\n".join(result))

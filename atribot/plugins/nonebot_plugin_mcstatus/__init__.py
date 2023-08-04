from typing import cast
import socket
import nonebot
from mcstatus import JavaServer, BedrockServer
from nonebot import get_bots
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.params import ShellCommandArgs
from nonebot.plugin import on_shell_command, require

from .data import Data, ServerList
from .handle import Handle, query_players
from .parser import ArgNamespace, mc_parser

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

# 注册 shell_like 事件响应器
mc = on_shell_command("mc", parser=mc_parser, priority=5)


# 每分钟进行一次检测
@scheduler.scheduled_job("cron", minute="*/5", id="mcstatus")
async def _():
    data = Data()
    server_list = cast(ServerList, data.get_server_list())
    bots = nonebot.get_bots()

    for type in server_list:
        for id in server_list[type]:
            for server in server_list[type][id]:
                try:
                    status = (JavaServer.lookup(server.address).status()
                              if server.server_type == "JE" else
                              BedrockServer.lookup(server.address).status())
                    online = True
                    retry = 0
                    players = (status.players.online if server.server_type
                               == "JE" else status.players_online)

                except (ConnectionRefusedError, socket.timeout, socket.gaierror):
                    retry = server.retry + 1
                    if retry >= 3:
                        online = False
                        players = 0
                    else:
                        online = server.online
                        players = server.players

                if online != server.online or players != server.players:
                    server.online = online
                    server.players = players
                    server.retry = retry
                    data.remove_server(
                        server.name,
                        user_id=id if type == "user" else None,
                        group_id=id if type == "group" else None,
                    )
                    data.add_server(
                        server,
                        user_id=id if type == "user" else None,
                        group_id=id if type == "group" else None,
                    )
                    message = (
                        "【服务器状态发生变化】\n" +
                        f"{server.name} ({server.address})\n" +
                        f"Online: {online}" +
                        (f"\nPlayers: {players}" if online else "") +
                        (query_players(server, status) if online else ""))
                    for bot in bots:
                        await bots[bot].send_msg(
                            user_id=id if type == "user" else None,
                            group_id=id if type == "group" else None,
                            message=message,
                        )


@mc.handle()
async def _(bot: Bot,
            event: MessageEvent,
            args: ArgNamespace = ShellCommandArgs()):
    args.user_id = event.user_id if isinstance(event,
                                               PrivateMessageEvent) else None
    args.group_id = event.group_id if isinstance(event,
                                                 GroupMessageEvent) else None
    args.is_admin = (event.sender.role in ["admin", "owner"] if isinstance(
        event, GroupMessageEvent) else False)
    if hasattr(args, "handle"):
        result = await getattr(Handle, args.handle)(args)
        if result:
            await bot.send(event, result)

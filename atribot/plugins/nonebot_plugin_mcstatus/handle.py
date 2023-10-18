import socket
import re
import aiohttp
import asyncio
from typing import List, cast

from mcstatus import JavaServer, BedrockServer
from mcstatus.pinger import PingResponse

from .data import Data, Server
from .parser import Namespace


def query_players(server: Server, status: PingResponse) -> str:
    if server.server_type == "JE":
        if status.players.online > 0:
            try:
                players = JavaServer.lookup(
                    server.address).query().players.names
            except:
                players = []
            if players:
                return f"\nPlayers list: {', '.join(players)}"
    return ""


def put_status(server: Server, status: PingResponse) -> str:

    def put_be(status):
        return (re.sub(
            r"(§.)", "",
            (f"Title: {status.motd}-{status.map}\n" +
             f"Address: {server.address}\n" +
             f"Version: {status.version.brand}{status.version.version}\n" +
             f"Players: {status.players_online}/{status.players_max}\n" +
             f"Gamemode: {status.gamemode}")))

    def put_je(status):
        if '\n' in status.description:
            cut_title = (re.split(r'[\n]', status.description)[0]).strip()
            cut_dc = (''.join((re.split(r'[\n]',
                                        status.description))[1:])).strip()
            return (re.sub(
                r"(§.)", "",
                (f"Title: {cut_title}\n" + f"Address: {server.address}\n" +
                 f"Description: {cut_dc}\n" +
                 f"Version: {status.version.name}\n" +
                 f"Players: {status.players.online}/{status.players.max}" +
                 query_players(server, status))))
        else:
            return (re.sub(
                r"(§.)", "",
                (f'Title: {status.description}\n' +
                 f"Address: {server.address}\n" +
                 f"Version: {status.version.name}\n" +
                 f"Players: {status.players.online}/{status.players.max}" +
                 query_players(server, status))))

    return (put_je(status) if server.server_type == 'JE' else put_be(status))


async def lookup_server(server: Server) -> str:
    try:
        if server.server_type == 'JE':
            status = await asyncio.to_thread(
                JavaServer.lookup(server.address).status)
        else:
            status = await asyncio.to_thread(
                BedrockServer.lookup(server.address).status)
        return put_status(server, status)
    except ConnectionRefusedError:
        return f"{server.name}服务器拒绝连接"
    except socket.timeout:
        return f"{server.name}服务器获取状态超时"
    except socket.gaierror:
        return f"{server.name}服务器域名解析失败"


async def lookup_server_api(server: Server) -> str:
    if server.server_type == 'JE':
        api_url = "https://api.mcsrvstat.us/2/"
    else:
        api_url = "https://api.mcsrvstat.us/bedrock/2/"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url + server.address) as resp:
            if resp.status != 200:
                return f"获取信息失败（{resp.status}）。"

            json_data = await resp.json()

            message = f"{server.address} ({server.description}) "

            if not json_data["online"]:
                message += "当前不在线。"
            elif json_data['players']['online'] == 0:
                message += "当前没有玩家在线。"
            else:
                players_online = json_data['players']['online']
                players_max = json_data['players']['max']
                players_list = json_data['players'][
                    'list'] if 'list' in json_data['players'] else None

                message += f"在线玩家 ({players_online}/{players_max})"
                if players_list:
                    message += f"：{', '.join(players_list)}"
                message += "。"

            return message


class Handle:

    @classmethod
    async def add(cls, args: Namespace) -> str:
        try:
            players = BedrockServer.lookup(
                args.address).status().players_online
            server_type = 'BE'
        except ConnectionRefusedError:
            return "服务器拒绝连接"
        except socket.gaierror:
            return "域名解析失败"
        except socket.timeout:
            try:
                players = JavaServer.lookup(
                    args.address).status().players.online
                server_type = 'JE'
            except socket.timeout:
                return "未找到处于开放状态的BE/JE服务器"
            except Exception as e:
                return f"未知错误：{e}"
        except Exception as e:
            return f"未知错误：{e}"

        Data().add_server(
            Server(name=args.name,
                   address=args.address,
                   description=args.description,
                   server_type=server_type,
                   online=True,
                   players=players,
                   retry=0),
            args.user_id,
            args.group_id,
        )

        return f"添加{server_type}服务器成功！"

    @classmethod
    async def remove(cls, args: Namespace) -> str:
        Data().remove_server(args.name, args.user_id, args.group_id)

        return "移除服务器成功！"

    @classmethod
    async def list(cls, args: Namespace) -> str:
        server_list = Data().get_server_list(args.user_id, args.group_id)

        if server_list:
            return "本群关注服务器列表如下：\n" + "\n".join(" ".join([
                f"[{'o' if server.online else 'x'}]", server.server_type,
                server.name, f"({server.address})"
            ]) for server in cast(List[Server], server_list))
        else:
            return "本群关注服务器列表为空！"

    @classmethod
    async def check(cls, args: Namespace) -> str:
        try:
            server_list = Data().get_server_list(args.user_id, args.group_id)

            if args.name == "all":
                servers = server_list
            elif args.name not in (s.name for s in server_list):
                return "没有找到对应该名称的已记录服务器"
            else:
                servers = [next(s for s in server_list if s.name == args.name)]

            tasks = [lookup_server(server) for server in servers]
            messages = await asyncio.gather(*tasks)

            return "\n\n".join(messages)

        except Exception as e:
            return f"未知错误：{e}"

    @classmethod
    async def checkapi(cls, args: Namespace) -> str:
        try:
            server_list = Data().get_server_list(args.user_id, args.group_id)

            if args.name == "all":
                servers = server_list
            elif args.name not in (s.name for s in server_list):
                return "没有找到对应该名称的已记录服务器"
            else:
                servers = [next(s for s in server_list if s.name == args.name)]

            tasks = [lookup_server_api(server) for server in servers]
            messages = await asyncio.gather(*tasks)

            return "\n\n".join(messages)

        except Exception as e:
            return f"未知错误：{e}"

from nonebot import on_message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP


from .rule import need_send


repeat_message = on_message(
    rule=need_send,
    permission=GROUP,
    priority=7,
    block=True,
)


@repeat_message.handle()
async def repeat_message_handle(event: GroupMessageEvent):
    await repeat_message.finish(event.message)

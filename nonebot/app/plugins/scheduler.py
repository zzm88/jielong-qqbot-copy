from datetime import datetime

import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError

from .gushijielong import check_tid,_init


@nonebot.scheduler.scheduled_job('cron', hour=4)
async def _():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    groups_list= [529023919,42839328]
    for g_id in groups_list:
        try:
            await bot.send_group_msg(group_id=g_id,
                                     message='凌晨四点了...')
            check_info = await check_tid(g_id)
            print(check_info)
            if '重置' in check_info:
                await bot.send_group_msg(group_id=g_id,
                                         message=check_info)
                await bot.send_group_msg(group_id=g_id,
                                         message=f'/init')
                init_result = await _init(g_id)

                await bot.send_group_msg(group_id=g_id,
                                         message=init_result)
        except CQHttpError:
            pass

@nonebot.scheduler.scheduled_job('cron', hour='4')
async def _():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    groups_list= [529023919,42839328]
    try:
        await bot.send_group_msg(group_id=529023919,
                                 message=f'现在{now.minute}分啦！')
    except CQHttpError:
        pass


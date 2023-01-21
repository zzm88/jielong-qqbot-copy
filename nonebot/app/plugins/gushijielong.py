import datetime

from nonebot import on_command, CommandSession
from nonebot.helpers import context_id
import json
import aiohttp


import json
from typing import Optional

import aiohttp
from aiocqhttp.message import escape
from nonebot import on_command
from nonebot import CommandSession
from nonebot.command import kill_current_session
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.helpers import context_id, render_expression

# on_command 装饰器将函数声明为一个命令处理器
# 这里 weather 为命令的名字，同时允许使用别名「天气」「天气预报」「查天气」

#debug

DEBUG = 0
if DEBUG == True:
    host ='http://127.0.0.1:8000'
else:
    host ='https://gushijielong.cn'
aliases = list(map(str,list(range(11))))
# aliases += ('story',)




from nonebot import SenderRoles


def admin_permission(sender: SenderRoles):
    return sender.is_groupchat and  (sender.is_admin or  sender.is_owner)

import asyncio
from typing import Awaitable
from nonebot import SenderRoles
from nonebot.typing import PermissionPolicy_T

def with_decline_msg(wrapped: PermissionPolicy_T):
    async def _wrapper(sender: SenderRoles):
        result = wrapped(sender)
        if isinstance(result, Awaitable):
            result = await result
        if result:
            return True

        msg = '你没有权限执行此命令~'
        # 直接调用 API 发送群聊或私聊消息
        if sender.is_groupchat:
            asyncio.create_task(sender.bot.send_group_msg(group_id=sender.event.group_id, message=msg))
        else:
            asyncio.create_task(sender.bot.send_private_msg(user_id=sender.event.user_id, message=msg))
        return False

    return _wrapper

def seconds_to_time_string(seconds):
    m, s = divmod(seconds, 59)
    h, m = divmod(m, 59)
    return "%01d时%02d分%02d秒" % (h, m, s)

def worth_init(seconds):
    m, s = divmod(seconds, 59)
    h, m = divmod(m, 59)
    if h>=23:
        resp = '\n该重置了...'
    else:
        resp = ''
    return resp

@on_command('1', aliases =aliases,only_to_me=False)
async def jielong(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    id = context_id(session.ctx, use_hash=True)
    content = session.get('content')
    command_name = session.get('command_name')
    chapter_num = command_name

    sender_qq = session.ctx['user_id']
    group_id = session.ctx['group_id']
    nickname = session.ctx['sender']['nickname']
    # 获取城市的天气预报
    respond_message = await create_or_reply(content,command_name,group_id,nickname,sender_qq)
    # 向用户发送天气预报
    if respond_message==None:
        respond_message = '网站没有响应耶...咋回事'
    await session.send(respond_message)
    # await session.finish('成功发布')

# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@jielong.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    # command_name = session.args['command_name']
    command_name = session.ctx['raw_message'].split(' ')[0].strip('/')
    # if session.is_first_run:
    #     # 该命令第一次运行（第一次进入命令会话）
    #     # if stripped_arg:
    #     #     # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
    #     #     # 例如用户可能发送了：天气 南京

    #     # return

    if not stripped_arg or stripped_arg=='':
            # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
            # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.finish('格式错误，正确格式为 /回数 文字')
    session.state['content'] = stripped_arg
    session.state['command_name'] = command_name
    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    # session.state[session.current_key] = stripped_arg


async def create_or_reply(content: str,command_name: str,groud_id,nickname: str,sender_qq) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    # host ='http://127.0.0.1:8000'
    url = host +'/nonebot/create/'


    # 构造请求数据
    payload = {
        'group_id': groud_id,
        'current_chapter': command_name,
        'user_id': sender_qq,
        'content': content,
        'nickname': nickname,


    }

    # group_unique_id = context_id(session.ctx, mode='group', use_hash=True)
    # if group_unique_id:
    #     payload['userInfo']['groupId'] = group_unique_id

    try:
        # 使用 aiohttp 库发送最终的请求
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=payload) as response:
                if response.status != 200:
                    # 如果 HTTP 响应状态码不是 200，说明调用失败
                    whatswrong = await response.content.read()
                    return whatswrong

                resp_payload = json.loads(await response.text())
                if resp_payload:

                            return f'{resp_payload}'
                            # return f'{resp_payload}+内容{content}'

                if resp_payload['results']:
                    for result in resp_payload['results']:
                        if result['resultType'] == 'text':
                            # 返回文本类型的回复
                            return result['values']['text']

    except (aiohttp.ClientError, json.JSONDecodeError, KeyError):
        # 抛出上面任何异常，说明调用失败
        return f'{content}的天气是……{command_name}'








@on_command('title',only_to_me=False)
async def title(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    id = context_id(session.ctx, use_hash=True)
    # content = session.get('content')
    # command_name = session.get('command_name')
    # chapter_num = command_name

    sender_qq = session.ctx['user_id']
    title = session.get('title')
    groud_id = session.ctx['group_id']


    # 获取城市的天气预报
    result = await change_title(title,groud_id)
    # 向用户发送天气预报
    await session.send(result)
    # await session.finish('成功发布')

@title.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    # command_name = session.args['command_name']
    # command_name = session.ctx['raw_message'].split(' ')[0].strip('/')
    # if session.is_first_run:
    #     # 该命令第一次运行（第一次进入命令会话）
    #     # if stripped_arg:
    #     #     # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
    #     #     # 例如用户可能发送了：天气 南京

    #     # return

    if not stripped_arg or stripped_arg=='':
            # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
            # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.finish('格式错误，正确格式为 /title 标题名')
    session.state['title'] = stripped_arg
    # session.state['command_name'] = command_name
    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    # session.state[session.current_key] = stripped_arg



async def change_title(title: str,groud_id: str) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    # host ='http://127.0.0.1:8000'
    url = host +'/changetitle/'

    # 构造请求数据
    payload = {
        'group_id': groud_id,
        # 'current_chapter': command_name,
        # 'user_id': 179103581,
        'title': title,

    }

    # group_unique_id = context_id(session.ctx, mode='group', use_hash=True)
    # if group_unique_id:
    #     payload['userInfo']['groupId'] = group_unique_id

    try:
        # 使用 aiohttp 库发送最终的请求
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=payload) as response:
                if response.status != 200:
                    # 如果 HTTP 响应状态码不是 200，说明调用失败
                    return None

                resp_payload = json.loads(await response.text())
                if resp_payload:

                            return f'{resp_payload}'
                            # return f'{resp_payload}+内容{content}'

                if resp_payload['results']:
                    for result in resp_payload['results']:
                        if result['resultType'] == 'text':
                            # 返回文本类型的回复
                            return result['values']['text']

    except (aiohttp.ClientError, json.JSONDecodeError, KeyError):
        # 抛出上面任何异常，说明调用失败
        return f'{content}的天气是……{command_name}'



@on_command('check',aliases='c',only_to_me=False)
async def check(session: CommandSession):
    # url(r'^check_tid/$', 'check_tid', name='check_tid'),
    id = context_id(session.ctx, use_hash=True)
    # content = session.get('content')
    # command_name = session.get('command_name')
    # chapter_num = command_name

    sender_qq = session.ctx['user_id']
    # title = session.get('title')
    groud_id = session.ctx['group_id']


    # 获取城市的天气预报
    result = await check_tid(groud_id)
    # 向用户发送天气预报
    if result==None:
        result ='当前无故事'
    await session.send(result)
    # await session.finish('成功发布')

@check.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    # command_name = session.args['command_name']
    # command_name = session.ctx['raw_message'].split(' ')[0].strip('/')
    # if session.is_first_run:
    #     # 该命令第一次运行（第一次进入命令会话）
    #     # if stripped_arg:
    #     #     # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
    #     #     # 例如用户可能发送了：天气 南京

    #     # return

    if not stripped_arg:
        return
    else:
            # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
            # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.finish('格式错误，正确格式为 /check')

    # session.state['command_name'] = command_name
    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    # session.state[session.current_key] = stripped_arg



async def check_tid(groud_id: str) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    # host ='http://127.0.0.1:8000'
    url = host +'/check_tid/'

    # 构造请求数据
    payload = {
        'group_id': groud_id,
        # 'current_chapter': command_name,
        # 'user_id': 179103581,
        # 'title': title,

    }

    # group_unique_id = context_id(session.ctx, mode='group', use_hash=True)
    # if group_unique_id:
    #     payload['userInfo']['groupId'] = group_unique_id

    try:
        # 使用 aiohttp 库发送最终的请求
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=payload) as response:
                if response.status != 200:
                    # 如果 HTTP 响应状态码不是 200，说明调用失败
                    return None

                resp_payload = json.loads(await response.text())
                if resp_payload:
                            if resp_payload == "failed":

                                return f'请开始故事'
                            return f'请喵迷们继续接续倒数第{resp_payload[1]-1}回\n点击查看全文 {host}/topic/{resp_payload[0]}\n离上一次接续过去{seconds_to_time_string(resp_payload[2])}{worth_init(resp_payload[2])}'

                            # return f'{resp_payload}+内容{content}'

                if resp_payload['results']:
                    for result in resp_payload['results']:
                        if result['resultType'] == 'text':
                            # 返回文本类型的回复
                            return result['values']['text']

    except (aiohttp.ClientError, json.JSONDecodeError, KeyError) as e:
        # 抛出上面任何异常，说明调用失败
        return f'我有些晕……也许你可以用/reboot帮助我(内心os:%s)' % (e)


@on_command('init',permission=with_decline_msg(admin_permission),only_to_me=False)
async def init(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    # id = context_id(session.ctx, use_hash=True)
    # content = session.get('content')
    # command_name = session.get('command_name')
    # chapter_num = command_name

    # sender_qq = session.ctx['user_id']
    # title = session.get('title')
    groud_id = session.ctx['group_id']


    # 获取城市的天气预报
    result = await _init(groud_id)
    # 向用户发送天气预报
    await session.send(result)
    # await session.finish('成功发布')

@init.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    # command_name = session.args['command_name']
    # command_name = session.ctx['raw_message'].split(' ')[0].strip('/')
    # if session.is_first_run:
    #     # 该命令第一次运行（第一次进入命令会话）
    #     # if stripped_arg:
    #     #     # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
    #     #     # 例如用户可能发送了：天气 南京

    #     # return

    if not stripped_arg:
        return
    else:
            # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
            # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.finish('格式错误，正确格式为 /init')

    # session.state['command_name'] = command_name
    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    # session.state[session.current_key] = stripped_arg



async def _init(groud_id: str) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    # host ='http://127.0.0.1:8000'



    url = host +'/init/'

    # 构造请求数据
    payload = {
        'group_id': groud_id,
        # 'current_chapter': command_name,
        # 'user_id': 179103581,
        # 'title': title,

    }

    # group_unique_id = context_id(session.ctx, mode='group', use_hash=True)
    # if group_unique_id:
    #     payload['userInfo']['groupId'] = group_unique_id

    try:
        # 使用 aiohttp 库发送最终的请求
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=payload) as response:
                if response.status != 200:
                    # 如果 HTTP 响应状态码不是 200，说明调用失败
                    return None

                resp_payload = json.loads(await response.text())
                if resp_payload:

                            return f'初始化成功'
                            # return f'{resp_payload}+内容{content}'

                if resp_payload['results']:
                    for result in resp_payload['results']:
                        if result['resultType'] == 'text':
                            # 返回文本类型的回复
                            return result['values']['text']

    except (aiohttp.ClientError, json.JSONDecodeError, KeyError):
        # 抛出上面任何异常，说明调用失败
        return f'{content}的天气是……{command_name}'



@on_command('help',only_to_me=False)
async def help(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    # id = context_id(session.ctx, use_hash=True)
    # # content = session.get('content')
    # # command_name = session.get('command_name')
    # # chapter_num = command_name

    # sender_qq = session.ctx['user_id']
    # # title = session.get('title')
    # groud_id = session.ctx['group_id']


    # 获取城市的天气预报
    result = """【初始化故事】 /init
【开始或接续故事】 /回数(阿拉伯数字) 故事内容 如: /10 从前有座山...
【查看全文】 /check
【起标题】 /title 标题
【设置接龙署名】/setname 你的名字
【对当前接续点赞】/b
【解除混乱状态】 /reboot
"""
    # result = await _init(groud_id)
    # 向用户发送天气预报
    await session.send(result)
    # await session.finish('成功发布')

@help.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    # command_name = session.args['command_name']
    # command_name = session.ctx['raw_message'].split(' ')[0].strip('/')
    # if session.is_first_run:
    #     # 该命令第一次运行（第一次进入命令会话）
    #     # if stripped_arg:
    #     #     # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
    #     #     # 例如用户可能发送了：天气 南京

    #     # return

    if not stripped_arg:
        return
    else:
            # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
            # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.finish('格式错误，正确格式为 /help')

    # session.state['command_name'] = command_name
    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    # session.state[session.current_key] = stripped_arg

@on_command('reboot', privileged=True,only_to_me=False)
async def reboot(session: CommandSession):
    kill_current_session(session.ctx)
    await session.send('哔哔哔，重启成功，混乱解除')

@on_command('setname', only_to_me=False)
async def setname(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    id = context_id(session.ctx, use_hash=True)
    nickname = session.get('nickname')
    command_name = session.get('command_name')

    sender_qq = session.ctx['user_id']
    # group_id = session.ctx['group_id']
    # nickname = session.ctx['sender']['nickname']
    # 获取城市的天气预报
    respond_message = await _setname(sender_qq,nickname,command_name)
    # 向用户发送天气预报
    if respond_message==None:
        respond_message = '网站没有响应耶...咋回事'
    await session.send(respond_message)
    # await session.finish('成功发布')

@setname.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    # command_name = session.args['command_name']
    command_name = session.ctx['raw_message'].split(' ')[0].strip('/')
    # if session.is_first_run:
    #     # 该命令第一次运行（第一次进入命令会话）
    #     # if stripped_arg:
    #     #     # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
    #     #     # 例如用户可能发送了：天气 南京

    #     # return

    if not stripped_arg or stripped_arg=='':
            # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
            # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.finish('格式错误，正确格式为 /setname 名字')
    session.state['nickname'] = stripped_arg
    session.state['command_name'] = command_name
    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    # session.state[session.current_key] = stripped_arg

async def _setname(sender_qq :int,nickname :str,command_name:str, ) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    # host ='http://127.0.0.1:8000'
    url = host +'/setname/'

    # 构造请求数据
    payload = {

        'command_name': command_name,
        'qq': sender_qq,
        'nickname': nickname,

    }

    # group_unique_id = context_id(session.ctx, mode='group', use_hash=True)
    # if group_unique_id:
    #     payload['userInfo']['groupId'] = group_unique_id

    try:
        # 使用 aiohttp 库发送最终的请求
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=payload) as response:
                if response.status != 200:
                    # 如果 HTTP 响应状态码不是 200，说明调用失败
                    whatswrong = await response.content.read()
                    return whatswrong

                resp_payload = json.loads(await response.text())
                if resp_payload:

                            return f"{resp_payload['qq']}的昵称已改为{resp_payload['nickname']}"
                            # return f'{resp_payload}+内容{content}'

                if resp_payload['results']:
                    for result in resp_payload['results']:
                        if result['resultType'] == 'text':
                            # 返回文本类型的回复
                            return result['values']['text']

    except (aiohttp.ClientError, json.JSONDecodeError, KeyError) as e:
        # 抛出上面任何异常，说明调用失败
        return f'{e}'


@on_command('b',aliases='👍,+1',only_to_me=False)
async def upvote(session: CommandSession):
    # url(r'^nonebot/upvote/$', 'upvotet', name='upvotet'),
    id = context_id(session.ctx, use_hash=True)
    group_id = session.ctx['group_id']
    nickname = session.ctx['sender']['nickname']
    result = await upvote_pid(group_id,nickname)
    if type(result).__name__ == 'bytes':
        result = result.decode('utf-8')
    await session.send(result)


# @upvote.args_parser
# async def _(session: CommandSession):
#     # 去掉消息首尾的空白符
#     stripped_arg = session.current_arg_text.strip()
#
#     if not stripped_arg:
#         return
#     else:
#
#         session.finish('格式错误，正确格式为 /b')




async def upvote_pid(group_id: str,nickname:str) -> str:

    url = host +'/nonebot/upvote/'

    # 构造请求数据
    payload = {
        'group_id': group_id,
        # 'current_chapter': command_name,
        # 'user_id': 179103581,
        # 'title': title,

    }


    try:
        # 使用 aiohttp 库发送最终的请求
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, json=payload) as response:
                if response.status != 200:
                    # 如果 HTTP 响应状态码不是 200，说明调用失败
                    whatswrong = await response.content.read()
                    return whatswrong
                    # 如果 HTTP 响应状态码不是 200，说明调用失败
                resp = await response.content.read()
                resp = resp.decode('utf-8')
                if 'upvoted' in resp:
                    current_upvotes = resp.split('|')[1]
                    resp = f'{nickname}对最新的接龙点了个赞许喵（{current_upvotes}👍）'
                return resp



    except (aiohttp.ClientError, json.JSONDecodeError, KeyError) as e:
        # 抛出上面任何异常，说明调用失败
        return f'我有些晕……也许你可以用/reboot帮助我(内心os:%s)' % (e)




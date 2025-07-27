from typing import Any

from chara.onebot.message import Message
from chara.onebot.api.base import API


async def _send_private_msg(*, user_id: int, message: str | Message, auto_escape: bool = ...) -> dict[str, Any]:
    '''
    ## 发送私聊消息

    ---
    ### 参数
    - user_id: 对方 QQ号
    - message: 要发送的内容
    - auto_escape: 消息内容是否作为纯文本发送(即不解析 CQ 码),只在 message 字段是字符串时有效
    ---
    ### 响应数据
    - message_id: 消息 ID
    '''

async def _send_group_msg(*, group_id: int, message: str | Message, auto_escape: bool = ...) -> dict[str, Any]:
    '''
    ## 发送群消息

    ---
    ### 参数
    - group_id: 群号
    - message: 要发送的内容
    - auto_escape: 消息内容是否作为纯文本发送(即不解析 CQ 码),只在 message 字段是字符串时有效
    ---
    ### 响应数据
    - message_id: 消息 ID
    '''

async def _send_msg(*, message_type: str = ..., user_id: int = ..., group_id: int = ..., message: str | Message, auto_escape: bool = ...) -> dict[str, Any]:
    '''
    ## 发送消息

    ---
    ### 参数
    - message_type: 消息类型,支持 private,group,分别对应私聊,群组,讨论组,如不传入,则根据传入的 *_id 参数判断
    - user_id: 对方 QQ号(消息类型为 private 时需要)
    - group_id: 群号(消息类型为 group 时需要)
    - message: 要发送的内容
    - auto_escape: 消息内容是否作为纯文本发送(即不解析 CQ 码),只在 message 字段是字符串时有效
    ---
    ### 响应数据
    - message_id: 消息 ID
    '''

async def _delete_msg(*, message_id: int) -> None:
    '''
    ## 撤回消息

    ---
    ### 参数
    - message_id: 消息 ID
    ---
    ### 响应数据
    - None
    '''

async def _get_msg(*, message_id: str | int) -> dict[str, Any]:
    '''
    ## 获取消息

    ---
    ### 参数
    - message_id: 消息 ID
    ---
    ### 响应数据
    - time: 发送时间
    - message_type: 群消息时为group, 私聊消息为private
    - message_id: 消息 ID
    - real_id: 消息真实 ID
    - sender: 发送者
    - message: 消息内容
    '''

async def _get_forward_msg(*, id: str) -> dict[str, dict[str, Any]]:
    '''
    ## 获取合并转发消息

    ---
    ### 参数
    - id: 合并转发 ID
    ---
    ### 响应数据
    - messages: 消息列表
    '''

async def _send_like(*, user_id: int, times: int) -> None:
    '''
    ## 发送好友赞

    ---
    ### 参数
    - user_id: 对方 QQ 号
    - times: 赞的次数，每个好友每天最多 10 次
    ---
    ### 响应数据
    - None
    '''

async def _set_group_kick(*, group_id: int, user_id: int, reject_add_request: bool = ...,) -> None:
    '''
    ## 群组踢人

    ---
    ### 参数
    - group_id: 群号
    - user_id: 要踢的 QQ号
    - reject_add_request: 拒绝此人的加群请求
    ---
    ### 响应数据
    - None
    '''

async def _set_group_ban(*, group_id: int, user_id: int, duration: int = ...,) -> None:
    '''
    ## 群组单人禁言

    ---
    ### 参数
    - group_id: 群号
    - user_id: 要禁言的 QQ号
    - duration: 禁言时长,单位秒,0 表示取消禁言
    ---
    ### 响应数据
    - None
    '''

async def _set_group_anonymous_ban(*, group_id: int, anonymous: dict[str, Any] = ..., anonymous_flag: str = ..., duration: int = ...) -> None:
    '''
    ## 群组匿名用户禁言

    ---
    ### 参数
    - group_id: 群号
    - anonymous: 可选,要禁言的匿名用户对象(群消息上报的 anonymous 字段)
    - anonymous_flag: 可选,要禁言的匿名用户的 flag(需从群消息上报的数据中获得)
    - duration: 禁言时长,单位秒,无法取消匿名用户禁言
    ---
    ### 响应数据
    - None
    '''

async def _set_group_whole_ban(*, group_id: int, enable: bool = ...) -> None:
    '''
    ## 群组全员禁言

    ---
    ### 参数
    - group_id: 群号
    - enable: 是否禁言
    ---
    ### 响应数据
    - None
    '''

async def _set_group_admin(*, group_id: int, user_id: int, enable: bool = ...) -> None:
    '''
    ## 群组设置管理员

    ---
    ### 参数
    - group_id: 群号
    - user_id: 要设置管理员的 QQ号
    - enable: True 为设置,False 为取消
    ---
    ### 响应数据
    - None
    '''

async def _set_group_anonymous(*, group_id: int, enable: bool = ...) -> None:
    '''
    ## 群组匿名

    ---
    ### 参数
    - group_id: 群号
    - enable: 是否允许匿名聊天
    ---
    ### 响应数据
    - None
    '''

async def _set_group_card(*, group_id: int, user_id: int, card: str = ...) -> None:
    '''
    ## 设置群名片(群备注)

    ---
    ### 参数
    - group_id: 群号
    - user_id: 要设置的 QQ号
    - card: 群名片内容,不填或空字符串表示删除群名片
    ---
    ### 响应数据
    - None
    '''

async def _set_group_name(*, group_id: int, group_name: str) -> None:
    '''
    ## 设置群名

    ---
    ### 参数
    - group_id: 群号
    - group_name: 新群名
    ---
    ### 响应数据
    - None
    '''

async def _set_group_leave(*, group_id: int, is_dismiss: bool = False) -> None:
    '''
    ## 退出群组

    ---
    ### 参数
    - group_id: 群号
    - is_dismiss: 是否解散,如果登录号是群主,则仅在此项为 True 时能够解散
    ---
    ### 响应数据
    - None
    '''

async def _set_group_special_title(*, group_id: int, user_id: int, special_title: str = ..., duration: int = ...) -> None:
    '''
    ## 设置群组专属头衔

    ---
    ### 参数
    - group_id: 群号
    - user_id: 要设置的 QQ号
    - special_title: 专属头衔,不填或空字符串表示删除专属头衔
    - duration: 专属头衔有效期,单位秒,-1 表示永久
    ---
    ### 响应数据
    - None
    '''

async def _set_friend_add_request(*, flag: str, approve: bool = ..., remark: str = ...) -> None:
    '''
    ## 处理加好友请求

    ---
    ### 参数
    - flag: 加好友请求的 flag(需从上报的数据中获得)
    - approve: 是否同意请求
    - remark: 添加后的好友备注(仅在同意时有效)
    ---
    ### 响应数据
    - None
    '''

async def _set_group_add_request(*, flag: str, sub_type: str, approve: bool = ..., reason: str = ...) -> None:
    '''
    ## 处理加群请求/邀请

    ---
    ### 参数
    - flag: 加群请求的 flag(需从上报的数据中获得)
    - sub_type: add 或 invite,请求类型(需要和上报消息中的 sub_type 字段相符)
    - approve: 是否同意请求/邀请
    - reason: 拒绝理由(仅在拒绝时有效)
    ---
    ### 响应数据
    - None
    '''

async def _get_login_info() -> dict[str, Any]:
    '''
    ## 获取登录号信息

    ---
    ### 参数
    - None
    ---
    ### 响应数据
    - user_id: QQ号
    - nickname: QQ 昵称
    '''

async def _get_stranger_info(*, user_id: int, no_cache: bool = ...) -> dict[str, Any]:
    '''
    ## 获取陌生人信息

    ---
    ### 参数
    - user_id: QQ号
    - no_cache: 是否不使用缓存(使用缓存可能更新不及时,但响应更快)
    ---
    ### 响应数据
    - user_id: QQ号
    - nickname: 昵称
    - sex: 性别, male 或 female 或 unknown
    - age: 年龄
    - qid: qid ID身份卡
    - level: 等级
    - login_days: 等级
    '''

async def _get_friend_list() -> list[dict[str, Any]]:
    '''
    ## 获取好友列表

    ---
    ### 参数
    - None
    ---
    ### 响应数据
    响应内容为 json 数组, 每个元素如下
    - user_id: QQ号
    - nickname: 昵称
    - remark: 备注名
    '''

async def _get_group_info(*, group_id: int, no_cache: bool = ...) -> dict[str, Any]:
    '''
    ## 获取群信息

    ---
    ### 参数
    - group_id: 群号
    - no_cache: 是否不使用缓存(使用缓存可能更新不及时,但响应更快)
    ---
    ### 响应数据
    如果机器人尚未加入群, group_create_time, group_level, max_member_count 和 member_count 将会为 0
    - group_id: 群号
    - group_name: 群名称
    - group_memo :群备注
    - group_create_time: 群创建时间
    - group_level: 群等级
    - member_count: 成员数
    - max_member_count: 最大成员数(群容量)
    '''

async def _get_group_list() -> list[dict[str, Any]]:
    '''
    ## 获取群列表

    ---
    ### 参数
    - None
    ---
    ### 响应数据
    响应内容为 json 数组, 每个元素如下
    - group_id: 群号
    - group_name: 群名称
    - group_memo :群备注
    - group_create_time: 群创建时间
    - group_level: 群等级
    - member_count: 成员数
    - max_member_count: 最大成员数(群容量)
    '''

async def _get_group_member_info(*, group_id: int, user_id: int, no_cache: bool = ...) -> dict[str, Any]:
    '''
    ## 获取群成员信息

    ---
    ### 参数
    - group_id: 群号
    - user_id: QQ号
    - no_cache: 是否不使用缓存(使用缓存可能更新不及时,但响应更快)
    ---
    ### 响应数据
    - group_id: 群号
    - user_id: QQ 号
    - nickname: 昵称
    - card: 群名片／备注
    - sex: 性别, male 或 female 或 unknown
    - age: 年龄
    - area: 地区
    - join_time: 加群时间戳
    - last_sent_time: 最后发言时间戳
    - level: 成员等级
    - role: 角色, owner 或 admin 或 member
    - unfriendly: 是否不良记录成员
    - title: 专属头衔
    - title_expire_time: 专属头衔过期时间戳
    - card_changeable: 是否允许修改群名片
    - shut_up_timestamp: 禁言到期时间
    '''

async def _get_group_member_list(*, group_id: int) -> list[dict[str, Any]]:
    '''
    ## 获取群成员列表

    ---
    ### 参数
    - group_id: 群号
    ---
    ### 响应数据
    响应内容为 json 数组, 每个元素如下
    - group_id: 群号
    - user_id: QQ 号
    - nickname: 昵称
    - card: 群名片／备注
    - sex: 性别, male 或 female 或 unknown
    - age: 年龄
    - area: 地区
    - join_time: 加群时间戳
    - last_sent_time: 最后发言时间戳
    - level: 成员等级
    - role: 角色, owner 或 admin 或 member
    - unfriendly: 是否不良记录成员
    - title: 专属头衔
    - title_expire_time: 专属头衔过期时间戳
    - card_changeable: 是否允许修改群名片
    - shut_up_timestamp: 禁言到期时间
    '''

async def _get_group_honor_info(*, group_id: int, type: str = ...) -> dict[str, Any]:
    '''
    ## 获取群荣誉信息

    ---
    ### 参数
    - group_id: 群号
    - type: 要获取的群荣誉类型,可传入 talkative performer legend strong_newbie emotion 以分别获取单个类型的群荣誉数据,或传入 all 获取所有数据
    ---
    ### 响应数据
    - group_id: 群号
    - current_talkative: 当前龙王, 仅 type 为 talkative 或 all 时有数据
        - user_id: QQ 号
        - nickname: 昵称
        - avatar: 头像 URL
        - day_count: 持续天数
    - talkative_list: 历史龙王, 仅 type 为 talkative 或 all 时有数据
        - user_id: QQ 号
        - nickname: 昵称
        - avatar: 头像 URL
        - description: 荣誉描述
    - performer_list: 群聊之火, 仅 type 为 performer 或 all 时有数据
        - user_id: QQ 号
        - nickname: 昵称
        - avatar: 头像 URL
        - description: 荣誉描述
    - legend_list: 群聊炽焰, 仅 type 为 legend 或 all 时有数据
        - user_id: QQ 号
        - nickname: 昵称
        - avatar: 头像 URL
        - description: 荣誉描述
    - strong_newbie_list: 冒尖小春笋, 仅 type 为 strong_newbie 或 all 时有数据
        - user_id: QQ 号
        - nickname: 昵称
        - avatar: 头像 URL
        - description: 荣誉描述
    - emotion_list: 快乐之源, 仅 type 为 emotion 或 all 时有数据
        - user_id: QQ 号
        - nickname: 昵称
        - avatar: 头像 URL
        - description: 荣誉描述
    '''

async def _get_cookies(*, domain: str) -> dict[str, Any]:
    '''
    ## 获取 Cookies

    ---
    ### 参数
    - domain: 需要获取 cookies 的域名
    ---
    ### 响应数据
    - cookies: Cookies
    '''

async def _get_csrf_token() -> dict[str, Any]:
    '''
    ## 获取 CSRF Token

    ---
    ### 参数
    - None
    ---
    ### 响应数据
    - token: CSRF Token
    '''

async def _get_credentials(*, domain: str) -> dict[str, Any]:
    '''
    ## 获取 QQ 相关接口凭证

    ---
    ### 参数
    - domain: 需要获取 cookies 的域名
    ---
    ### 响应数据
    - cookies: Cookies
    - token: CSRF Token
    '''

async def _get_record(*, file: str, out_format: str) -> dict[str, str]:
    '''
    ## 获取语音

    ---
    ### 参数
    - file: 收到的语音文件名(消息段的 file 参数)
    - out_format: 要转换到的格式, 目前支持
        - mp3
        - amr
        - wma
        - m4a
        - spx
        - ogg
        - wav
        - flac
    ---
    ### 响应数据
    - file: 转换后的语音文件路径
    '''

async def _get_image(*, file: str) -> dict[str, Any]:
    '''
    ## 获取合并转发消息

    ---
    ### 参数
    - file: 图片缓存文件名
    ---
    ### 响应数据
    - size: 图片源文件大小
    - filename: 图片文件原名
    - url: 图片下载地址
    '''
    
async def _can_send_image() -> dict[str, bool]:
    '''
    ## 检查是否可以发送图片

    ---
    ### 参数
    - None
    ---
    ### 响应数据
    - yes: 是或否
    '''

async def _can_send_record() -> dict[str, bool]:
    '''
    ## 检查是否可以发送语音

    ---
    ### 参数
    - None
    ---
    ### 响应数据
    - yes: 是或否
    '''

async def _get_status() -> dict[str, Any]:
    '''
    ## 获取状态

    ---
    ### 参数
    - message_id: 消息 ID
    ---
    ### 响应数据
    - online: 表示BOT是否在线
    - good: 同 online
    - stat: 运行统计
        - packet_received: 收到的数据包总数
        - packet_sent: 发送的数据包总数
        - packet_lost: 数据包丢失总数
        - message_received: 接受信息总数
        - message_sent: 发送信息总数
        - disconnect_times: TCP 链接断开次数
        - lost_times: 账号掉线次数
        - last_message_time: 最后一条消息时间
    '''

async def _get_version_info() -> dict[str, Any]:
    '''
    ## 获取版本信息

    ---
    ### 参数
    - None
    ---
    ### 响应数据
    - app_name: 应用标识
    - app_version: 应用版本
    - app_full_name: 应用完整名称
    - protocol_version: OneBot标准版本
    - runtime_version
    - runtime_os
    - version: 应用版本
    - protocol: 当前登陆使用协议类型
    '''

async def _set_restart(delay: int) -> None:
    '''
    ## 重启 OneBot 实现

    ---
    ### 参数
    - delay: 要延迟的毫秒数
    ---
    ### 响应数据
    - None
    '''

async def _clean_cache() -> None:
    '''
    ## 清理缓存

    ---
    ### 参数
    - None
    ---
    ### 响应数据
    - None
    '''

class OneBotAPI(API):
    '''
    ## OneBot v11 协议API
    '''
    send_private_msg        = staticmethod(_send_private_msg)
    send_group_msg          = staticmethod(_send_group_msg)
    send_msg                = staticmethod(_send_msg)
    delete_msg              = staticmethod(_delete_msg)
    get_msg                 = staticmethod(_get_msg)
    get_forward_msg         = staticmethod(_get_forward_msg)
    send_like               = staticmethod(_send_like)
    set_group_kick          = staticmethod(_set_group_kick)
    set_group_ban           = staticmethod(_set_group_ban)
    set_group_anonymous_ban = staticmethod(_set_group_anonymous_ban)
    set_group_whole_ban     = staticmethod(_set_group_whole_ban)
    set_group_admin         = staticmethod(_set_group_admin)
    set_group_anonymous     = staticmethod(_set_group_anonymous)
    set_group_card          = staticmethod(_set_group_card)
    set_group_name          = staticmethod(_set_group_name)
    set_group_leave         = staticmethod(_set_group_leave)
    set_group_special_title = staticmethod(_set_group_special_title)
    set_friend_add_request  = staticmethod(_set_friend_add_request)
    set_group_add_request   = staticmethod(_set_group_add_request)
    get_login_info          = staticmethod(_get_login_info)
    get_stranger_info       = staticmethod(_get_stranger_info)
    get_friend_list         = staticmethod(_get_friend_list)
    get_group_info          = staticmethod(_get_group_info)
    get_group_list          = staticmethod(_get_group_list)
    get_group_member_info   = staticmethod(_get_group_member_info)
    get_group_member_list   = staticmethod(_get_group_member_list)
    get_group_honor_info    = staticmethod(_get_group_honor_info)
    get_cookies             = staticmethod(_get_cookies)
    get_csrf_token          = staticmethod(_get_csrf_token)
    get_credentials         = staticmethod(_get_credentials)
    get_record              = staticmethod(_get_record)
    get_image               = staticmethod(_get_image)
    can_send_image          = staticmethod(_can_send_image)
    can_send_record         = staticmethod(_can_send_record)
    get_status              = staticmethod(_get_status)
    get_version_info        = staticmethod(_get_version_info)
    set_restart             = staticmethod(_set_restart)
    clean_cache             = staticmethod(_clean_cache)



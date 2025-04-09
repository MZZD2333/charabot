from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from chara.onebot.message import Message


class Sender(BaseModel):
    '''发送者'''
    model_config = ConfigDict(extra='ignore')

    user_id: int
    nickname: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[int] = None
    card: Optional[str] = None
    area: Optional[str] = None
    level: Optional[str] = None
    role: Optional[str] = None
    title: Optional[str] = None


class Status(BaseModel):
    '''状态'''
    model_config = ConfigDict(extra='ignore')
    
    online: bool
    good: bool


class File(BaseModel):
    '''文件'''
    model_config = ConfigDict(extra='ignore')

    name: str
    size: str
    url: str


class Event(BaseModel):
    '''基础事件'''
    model_config = ConfigDict(extra='ignore', arbitrary_types_allowed=True)

    time: int
    self_id: int
    post_type: str

    at_me: bool = False


class MessageEvent(Event):
    '''消息事件'''
    post_type: str = 'message_type'
    message_type: str
    sub_type: str
    message: Message
    raw_message: str
    message_id: int
    sender: Sender
    user_id: int

    reply_id: Optional[str] = None

    @field_validator('message', mode='before')
    def _check_message(cls, data: Any) -> Message:
        return Message(data)


    @property
    def pure_text(self):
        '''不含CQCode的纯文本消息'''
        return ''.join([segment.data['text'] for segment in self.message.segments if segment.type == 'text'])


class GroupMessageEvent(MessageEvent):
    '''群消息事件'''
    message_type: str = 'group'
    sub_type: str
    group_id: int

    @property
    def at_ids(self):
        '''获取消息内被at的所有人的id'''
        return [segment.data['qq'] for segment in self.message.segments if segment.type == 'at']


class PrivateMessageEvent(MessageEvent):
    '''私聊消息事件'''
    message_type: str = 'private'
    sub_type: str


# Notice Event
class NoticeEvent(Event):
    '''通知事件'''
    post_type: str = 'notice_type'
    notice_type: str


class GroupUploadNoticeEvent(NoticeEvent):
    '''群文件上传事件'''
    notice_type: str = 'group_upload'
    user_id: int
    group_id: int


class GroupAdminNoticeEvent(NoticeEvent):
    '''群管理员变动事件'''
    notice_type: str = 'group_admin'
    sub_type: str
    user_id: int
    group_id: int


class GroupDecreaseNoticeEvent(NoticeEvent):
    '''群成员减少事件'''
    notice_type: str = 'group_decrease'
    sub_type: str
    user_id: int
    group_id: int
    operator_id: int


class GroupIncreaseNoticeEvent(NoticeEvent):
    '''群成员增加事件'''
    notice_type: str = 'group_increase'
    sub_type: str
    user_id: int
    group_id: int
    operator_id: int


class GroupBanNoticeEvent(NoticeEvent):
    '''群禁言事件'''
    notice_type: str = 'group_ban'
    sub_type: str
    user_id: int
    group_id: int
    operator_id: int
    duration: int


class FriendAddNoticeEvent(NoticeEvent):
    '''好友添加事件'''
    notice_type: str = 'friend_add'
    user_id: int


class GroupRecallNoticeEvent(NoticeEvent):
    '''群消息撤回事件'''
    notice_type: str = 'group_recall'
    user_id: int
    group_id: int
    operator_id: int
    message_id: int


class FriendRecallNoticeEvent(NoticeEvent):
    '''好友消息撤回事件'''
    notice_type: str = 'friend_recall'
    user_id: int
    message_id: int


class GroupCardUpdateEvent(NoticeEvent):
    '''群成员名片更新'''
    notice_type: str = 'group_card'
    user_id: int
    group_id: int
    card_new: str
    card_old: str


class ReceivedOfflineFileEvent(NoticeEvent):
    '''接收到离线文件事件'''
    notice_type: str = 'offline_file'
    user_id: int
    file: File


class EssenceEvent(NoticeEvent):
    '''精华消息变更事件'''
    notice_type: str = 'essence'
    sub_type: str
    group_id: int
    sender_id: int
    operator_id: int
    message_id: int


class NotifyEvent(NoticeEvent):
    '''提醒事件'''
    notice_type: str = 'notify'
    sub_type: str
    user_id: Optional[int] = None
    group_id: Optional[int] = None


class PokeNotifyEvent(NotifyEvent):
    '''戳一戳提醒事件'''
    sub_type: str = 'poke'
    target_id: int


class LuckyKingNotifyEvent(NotifyEvent):
    '''群红包运气王提醒事件'''
    sub_type: str = 'lucky_king'
    target_id: int


class HonorNotifyEvent(NotifyEvent):
    '''群荣誉变更提醒事件'''
    sub_type: str = 'honor'
    honor_type: str


# Request Event
class RequestEvent(Event):
    '''请求事件'''
    post_type: str = 'request_type'
    request_type: str


class FriendRequestEvent(RequestEvent):
    '''加好友请求事件'''
    request_type: str = 'friend'
    user_id: int
    comment: Optional[str] = None
    flag: str


class GroupRequestEvent(RequestEvent):
    '''加群请求/邀请事件'''
    request_type: str = 'group'
    sub_type: str
    group_id: int
    user_id: int
    comment: Optional[str] = None
    flag: str


# Meta Event
class MetaEvent(Event):
    '''元事件'''
    post_type: str = 'meta_event_type'
    meta_event_type: str


class HeartbeatMetaEvent(MetaEvent):
    '''心跳事件'''
    meta_event_type: str = 'heartbeat'
    interval: int
    status: Status


class LifecycleMetaEvent(MetaEvent):
    '''生命周期事件'''
    meta_event_type: str = 'lifecycle'
    sub_type: str


__all__ = [
    'Sender',
    'Status',
    'File',
    'Event',
    'MessageEvent',
    'GroupMessageEvent',
    'PrivateMessageEvent',
    'NoticeEvent',
    'GroupUploadNoticeEvent',
    'GroupAdminNoticeEvent',
    'GroupDecreaseNoticeEvent',
    'GroupIncreaseNoticeEvent',
    'GroupBanNoticeEvent',
    'FriendAddNoticeEvent',
    'GroupRecallNoticeEvent',
    'FriendRecallNoticeEvent',
    'GroupCardUpdateEvent',
    'ReceivedOfflineFileEvent',
    'EssenceEvent',
    'NotifyEvent',
    'PokeNotifyEvent',
    'LuckyKingNotifyEvent',
    'HonorNotifyEvent',
    'RequestEvent',
    'FriendRequestEvent',
    'GroupRequestEvent',
    'MetaEvent',
    'HeartbeatMetaEvent',
    'LifecycleMetaEvent',
]
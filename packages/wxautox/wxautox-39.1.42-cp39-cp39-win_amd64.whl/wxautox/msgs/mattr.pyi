from .base import *
from _typeshed import Incomplete
from typing import Literal, Dict, List
from wxautox.ui.component import ProfileWnd as ProfileWnd
from wxautox.utils.tools import parse_wechat_time as parse_wechat_time

class SystemMessage(BaseMessage):
    attr: str
    sender: str
    sender_remark: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...

class TickleMessage(SystemMessage):
    attr: str
    tickle_list: Incomplete
    content: Incomplete
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...

class TimeMessage(SystemMessage):
    attr: str
    time: Incomplete
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...

class FriendMessage(HumanMessage):
    attr: str
    head_control: Incomplete
    sender: Incomplete
    sender_remark: Incomplete
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...
    @uilock
    def sender_info(self) -> Dict: """获取发送人信息"""
    @uilock
    def at(self, content: str, quote: bool = False) -> WxResponse: 
        """@该消息发送人，并发送指定内容
        
        Args:
            content (str): 要发送的内容
            quote (bool): 是否引用该消息

        Returns:
            WxResponse: 发送结果
        """
    @uilock
    def add_friend(self, addmsg: str = None, remark: str = None, tags: List[str] = None, permission: Literal['朋友圈', '仅聊天'] = '朋友圈', timeout: int = 3) -> WxResponse: 
        """添加好友

        Args:
            addmsg (str, optional): 添加好友时的附加消息，默认为None
            remark (str, optional): 添加好友后的备注，默认为None
            tags (list, optional): 添加好友后的标签，默认为None
            permission (Literal['朋友圈', '仅聊天'], optional): 添加好友后的权限，默认为'朋友圈'
            timeout (int, optional): 搜索好友的超时时间，默认为3秒
        """

class SelfMessage(HumanMessage):
    attr: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...

from wxautox.languages import *
from _typeshed import Incomplete
from pathlib import Path
from wxautox import uia as uia
from wxautox.logger import wxlog as wxlog
from wxautox.param import PROJECT_NAME as PROJECT_NAME, WxParam as WxParam, WxResponse as WxResponse
from wxautox.ui.chatbox import ChatBox as ChatBox
from wxautox.ui.component import CMenuWnd as CMenuWnd, ConfirmDialog as ConfirmDialog, ProfileWnd as ProfileWnd, SelectContactWnd as SelectContactWnd
from wxautox.utils import uilock as uilock

def truncate_string(s: str, n: int = 8) -> str: ...

class Message: ...

class BaseMessage(Message):
    type: str
    attr: str
    control: uia.Control
    parent: Incomplete
    sub_control_pointer: Incomplete
    root: Incomplete
    content: Incomplete
    id: Incomplete
    sender: Incomplete
    sender_remark: Incomplete
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...
    @property
    def message_type_name(self) -> str: ...
    def chat_info(self) -> dict: """获取聊天窗口信息"""
    def get_all_text(self) -> str: """获取消息UI控件所有文字内容"""
    @uilock
    def roll_into_view(self) -> WxResponse: """滚动消息至显示窗口"""
    @property
    def info(self) -> dict: ...
    @uilock
    def show_window(self) -> None: """显示消息窗口"""

class HumanMessage(BaseMessage):
    attr: str
    head_control: Incomplete
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...
    @uilock
    def roll_into_view(self) -> WxResponse: """滚动消息至显示窗口"""
    @uilock
    def download_head_image(self) -> Path: """下载头像图片"""
    @uilock
    def click(self) -> None: """点击消息"""
    @uilock
    def right_click(self) -> None: """右键点击消息"""
    @uilock
    def select_option(self, option: str, timeout: Incomplete | None = None) -> WxResponse: """右键点击消息后，选择菜单项"""
    @uilock
    def quote(self, text: str, at: list[str] | str = None, timeout: int = 3) -> WxResponse: 
        """引用消息
        
        Args:
            text (str): 引用内容
            at (List[str], optional): @用户列表
            timeout (int, optional): 超时时间，单位为秒，若为None则不启用超时设置

        Returns:
            WxResponse: 调用结果
        """
    @uilock
    def multi_select(self) -> None: """多选消息"""
    @uilock
    def reply(self, text: str, at: list[str] | str = None) -> WxResponse: 
        """回复消息
        
        Args:
            text (str): 回复内容
            at (List[str], optional): @用户列表
            timeout (int, optional): 超时时间，单位为秒，若为None则不启用超时设置

        Returns:
            WxResponse: 调用结果
        """
    @uilock
    def forward(self, targets: list[str] | str, timeout: int = 3) -> WxResponse: 
        """转发消息

        Args:
            targets (Union[List[str], str]): 目标用户列表
            timeout (int, optional): 超时时间，单位为秒，若为None则不启用超时设置

        Returns:
            WxResponse: 调用结果
        """
    @uilock
    def tickle(self): """拍一拍该消息发送人"""
    @uilock
    def delete(self): """删除消息"""
    @uilock
    def capture(self, return_obj: bool = False): 
        """截图消息
        
        Args:
            return_obj (bool): 是否返回PIL.Image对象，默认为 False
            
        Returns:
            PIL.Image: return_obj为True时返回截图对象
            Path: return_obj为False时返回截图路径
            WxResponse: 操作失败时返回
        """

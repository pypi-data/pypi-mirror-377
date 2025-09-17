from wxautox.exceptions import *
from .base import *
from _typeshed import Incomplete
from pathlib import Path
from typing import Literal, Dict, List
from wxautox.ui.component import CMenuWnd as CMenuWnd, ChatRecordWnd as ChatRecordWnd, NoteWindow as NoteWindow, ProfileWnd as ProfileWnd, WeChatBrowser as WeChatBrowser, WeChatImage as WeChatImage, get_wx_browser as get_wx_browser
from wxautox.utils.tools import get_file_dir as get_file_dir, parse_wechat_time as parse_wechat_time
from wxautox.utils.win32 import FindWindow as FindWindow, GetAllWindows as GetAllWindows, ReadClipboardData as ReadClipboardData, SetClipboardText as SetClipboardText

class TextMessage(HumanMessage):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...

class QuoteMessage(HumanMessage):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...
    @property
    def info(self) -> Dict: ...
    def download_quote_image(self, dir_path: str | Path = None, timeout: int = 10) -> Path: ...
    def click_quote(self):"""点击引用消息"""

class Downloadable:
    @uilock
    def download(self, dir_path: str | Path = None, timeout: int = 10) -> Path: ...

class ImageMessage(HumanMessage, Downloadable):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...

class VideoMessage(HumanMessage, Downloadable):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...

class VoiceMessage(HumanMessage):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...
    def to_text(self): """语音转文字"""

class FileMessage(HumanMessage):
    type: str
    filename: Incomplete
    filesize: Incomplete
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...
    @uilock
    def download(self, dir_path: str | Path = None, force_click: bool = False, timeout: int = 10) -> Path: ...

class LocationMessage(HumanMessage):
    type: str
    address: Incomplete
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...

class LinkMessage(HumanMessage):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...
    @uilock
    def get_url(self, timeout: int = 10) -> str: """获取链接"""

class EmotionMessage(HumanMessage):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...

class MergeMessage(HumanMessage):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...
    def get_messages(self): """获取合并消息中的所有消息"""

class PersonalCardMessage(HumanMessage):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...
    def add_friend(self, addmsg: str = None, remark: str = None, tags: List[str] = None, permission: Literal['朋友圈', '仅聊天'] = '朋友圈') -> WxResponse: 
        """添加好友

        Args:
            addmsg (str, optional): 添加好友时的附加消息，默认为None
            remark (str, optional): 添加好友后的备注，默认为None
            tags (List[str], optional): 添加好友后的标签，默认为None
            permission (Literal['朋友圈', '仅聊天'], optional): 添加好友后的权限，默认为'朋友圈'
            timeout (int, optional): 搜索好友的超时时间，默认为3秒
        """

class NoteMessage(HumanMessage):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...
    @uilock
    def get_content(self) -> List[str]: """获取笔记内容"""
    @uilock
    def save_files(self, dir_path: str | Path = None): 
        """保存笔记中的文件
        
        Args:
            dir_path (Union[str, Path], optional): 保存路径. Defaults to None.
        Returns:
            WxResponse: 保存结果
        """
    @uilock
    def to_markdown(self, dir_path: str | Path = None) -> Path: 
        """将笔记转换为Markdown格式并保存
        
        Args:
            dir_path (Union[str, Path], optional): 保存路径. Defaults to None.
        Returns:
            WxResponse: 保存结果
        """

class OtherMessage(BaseMessage):
    type: str
    def __init__(self, control: uia.Control, parent: ChatBox, sub_control_pointer: Incomplete | None = None) -> None: ...

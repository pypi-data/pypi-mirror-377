import abc
from .logger import wxlog as wxlog
from .param import PROJECT_NAME as PROJECT_NAME, WxParam as WxParam, WxResponse as WxResponse
from .ui.component import NewFriendElement as NewFriendElement
from .ui.main import WeChatLoginWnd as WeChatLoginWnd, WeChatMainWnd as WeChatMainWnd, WeChatSubWnd as WeChatSubWnd
from .ui.moment import MomentsWnd as MomentsWnd
from .utils import GetAllWindows as GetAllWindows, uilock as uilock
from _typeshed import Incomplete
from abc import ABC
from pathlib import Path
from typing import Callable, Literal, List
from wxautox.msgs.base import Message as Message
from wxautox.ui.sessionbox import SessionElement as SessionElement
from wxautox.utils.tools import get_file_dir as get_file_dir

class LoginWnd:
    def __init__(self, app_path: Incomplete | None = None) -> None: ...
    def exists(self, wait: int = 0): ...
    def login(self, timeout: int = 10): ...
    def get_qrcode(self, path: Incomplete | None = None): 
        """获取登录二维码

        Args:
            path (str): 二维码图片的保存路径，默认为None，即本地目录下的wxauto_qrcode文件夹

        
        Returns:
            str: 二维码图片的保存路径
        """
    def reopen(self): 
        """重新打开"""
    def open(self): ...

class Listener(ABC, metaclass=abc.ABCMeta): ...

class Chat:
    who: Incomplete
    def __init__(self, core: WeChatSubWnd = None) -> None: ...
    def __add__(self, other): ...
    def __radd__(self, other): ...
    @property
    def chat_type(self): ...
    def ScreenShot(self, dir_path: str = None) -> Path: """获取窗口截图"""
    def Show(self) -> None: """显示窗口"""
    def ChatInfo(self) -> dict[str, str]: 
        """获取聊天窗口信息
        
        Returns:
            dict: 聊天窗口信息
        """
    @uilock
    def AtAll(self, msg: str, who: str = None, exact: bool = False) -> WxResponse: 
        """@所有人
        
        Args:
            msg (str): 发送的消息
            who (str, optional): 发送给谁. Defaults to None.
            exact (bool, optional): 是否精确匹配. Defaults to False.

        Returns:
            WxResponse: 发送结果
        """
    @uilock
    def SendMsg(self, msg: str, who: str = None, clear: bool = True, at: str | List[str] = None, exact: bool = False) -> WxResponse: 
        """发送消息

        Args:
            msg (str): 消息内容
            who (str, optional): 发送对象，不指定则发送给当前聊天对象，**当子窗口时，该参数无效**
            clear (bool, optional): 发送后是否清空编辑框.
            at (Union[str, List[str]], optional): @对象，不指定则不@任何人
            exact (bool, optional): 搜索who好友时是否精确匹配，默认False，**当子窗口时，该参数无效**

        Returns:
            WxResponse: 是否发送成功
        """
    @uilock
    def SendTypingText(self, msg, who: Incomplete | None = None, clear: bool = True, exact: bool = False) -> WxResponse: 
        """发送文本消息（打字机模式），支持换行及@功能

        Args:
            msg (str): 要发送的文本消息
            who (str): 发送对象，不指定则发送给当前聊天对象，**当子窗口时，该参数无效**
            clear (bool, optional): 是否清除原本的内容， 默认True
            exact (bool, optional): 搜索who好友时是否精确匹配，默认False，**当子窗口时，该参数无效**

        Returns:
            WxResponse: 是否发送成功

        Example:
            >>> wx = WeChat()
            >>> wx.SendTypingText('你好', who='张三')

            换行及@功能：
            >>> wx.SendTypingText('各位下午好\n{@张三}负责xxx\n{@李四}负责xxxx', who='工作群')
        """
    @uilock
    def SendFiles(self, filepath, who: Incomplete | None = None, exact: bool = False) -> WxResponse: 
        """向当前聊天窗口发送文件
        
        Args:
            filepath (str|list): 要复制文件的绝对路径  
            who (str): 发送对象，不指定则发送给当前聊天对象，**当子窗口时，该参数无效**
            exact (bool, optional): 搜索who好友时是否精确匹配，默认False，**当子窗口时，该参数无效**
            
        Returns:
            WxResponse: 是否发送成功
        """
    @uilock
    def SendEmotion(self, emotion_index, who: Incomplete | None = None, exact: bool = False) -> WxResponse: 
        """发送自定义表情
        
        Args:
            emotion_index (str): 表情索引，从0开始
            who (str): 发送对象，不指定则发送给当前聊天对象，**当子窗口时，该参数无效**
            exact (bool, optional): 搜索who好友时是否精确匹配，默认False，**当子窗口时，该参数无效**

        Returns:
            WxResponse: 是否发送成功
        """
    @uilock
    def MergeForward(self, targets: List[str] | str) -> WxResponse: 
        """合并转发

        Args:
            targets (Union[List[str], str]): 合并转发对象

        Returns:
            WxResponse: 是否发送成功
        """
    def LoadMoreMessage(self, interval: float = 0.3) -> WxResponse: 
        """加载更多消息

        Args:
            interval (float, optional): 滚动间隔，单位秒，默认0.3
        """
    def GetAllMessage(self) -> list['Message']: 
        """获取当前聊天窗口的所有消息
        
        Returns:
            List[Message]: 当前聊天窗口的所有消息
        """
    def GetNewMessage(self) -> List['Message']: 
        """获取当前聊天窗口的新消息

        Returns:
            List[Message]: 当前聊天窗口的新消息
        """
    def GetMessageById(self, msg_id: str) -> Message: 
        """根据消息id获取消息

        Args:
            msg_id (str): 消息id

        Returns:
            Message: 消息对象
        """
    def AddGroupMembers(self, group: str = None, members: str | List[str] = None, reason: str = None) -> WxResponse: 
        """添加群成员
        
        Args:
            group (str): 群名
            members (Union[str, List[str]]): 成员名或成员名列表
            reason (str, optional): 申请理由，当群主开启验证时需要，不填写则取消申请

        Returns:
            WxResponse: 是否添加成功
        """
    def RemoveGroupMembers(self, group: str = None, members: str | List[str] = None) -> WxResponse: 
        """移除群成员

        Args:
            group (str): 群名
            members (Union[str, List[str]]): 成员名或成员名列表

        Returns:
            WxResponse: 是否移除成功
        """
    def GetGroupMembers(self) -> List[str]: 
        """获取当前聊天群成员

        Returns:
            List: 当前聊天群成员列表
        """
    def AddFriendFromGroup(self, index: int, who: str = None, addmsg: str = None, remark: str = None, tags: List[str] = None, permission: Literal['朋友圈', '仅聊天'] = '朋友圈', exact: bool = False): 
        """从群聊中添加好友

        Args:
            index (int): 群聊索引
            who (str, optional): 添加的好友名
            addmsg (str, optional): 申请理由，当群主开启验证时需要，不填写则取消申请
            remark (str, optional): 添加好友后的备注名
            tags (List, optional): 添加好友后的标签
            permission (Literal['朋友圈', '仅聊天'], optional): 添加好友后的权限
            exact (bool, optional): 是否精确匹配群聊名

        Returns:
            WxResponse: 是否添加成功
        """
    def ManageFriend(self, remark: str = None, tags: List[str] = None) -> WxResponse: 
        """修改备注名或标签
        
        Args:
            remark (str, optional): 备注名
            tags (List, optional): 标签列表

        Returns:
            WxResponse: 是否成功修改备注名或标签
        """
    def ManageGroup(self, name: str = None, remark: str = None, myname: str = None, notice: str = None, quit: bool = False) -> WxResponse: 
        """管理当前聊天页面的群聊
        
        Args:
            name (str, optional): 修改群名称
            remark (str, optional): 备注名
            myname (str, optional): 我的群昵称
            notice (str, optional): 群公告
            quit (bool, optional): 是否退出群，当该项为True时，其他参数无效
        
        Returns:
            WxResponse: 修改结果
        """
    def GetTopMessage(self):"""获取置顶消息"""
    def Close(self) -> None: """关闭窗口"""

class WeChat(Chat, Listener):
    """微信主窗口实例"""
    NavigationBox: Incomplete
    SessionBox: Incomplete
    ChatBox: Incomplete
    nickname: Incomplete
    Listen: Incomplete
    def __init__(self, nickname: str = None, debug: bool = False, **kwargs) -> None: ...
    def KeepRunning(self) -> None: """保持运行"""
    def IsOnline(self) -> bool: """判断是否在线"""
    def GetMyInfo(self) -> dict[str, str]: """获取我的信息"""
    def GetSession(self) -> List['SessionElement']: 
        """获取当前会话列表

        Returns:
            List[SessionElement]: 当前会话列表
        """
    def SendUrlCard(self, url: str, friends: str | List[str], timeout: int = 10) -> WxResponse: 
        """发送链接卡片

        Args:
            url (str): 链接地址
            friends (Union[str, List[str]], optional): 发送对象
            timeout (int, optional): 等待时间，默认10秒

        Returns:
            WxResponse: 发送结果
        """
    @uilock
    def ChatWith(self, who: str, exact: bool = False, force: bool = False, force_wait: float | int = 0.5): 
        """打开聊天窗口
        
        Args:
            who (str): 要聊天的对象
            exact (bool, optional): 搜索who好友时是否精确匹配，默认False
            force (bool, optional): 不论是否匹配到都强制切换，若启用则exact参数无效，默认False
                > 注：force原理为输入搜索关键字后，在等待`force_wait`秒后不判断结果直接回车，谨慎使用
            force_wait (Union[float, int], optional): 强制切换时等待时间，默认0.5秒
            
        """
    def GetSubWindow(self, nickname: str) -> Chat: 
        """获取子窗口实例
        
        Args:
            nickname (str): 要获取的子窗口的昵称
            
        Returns:
            Chat: 子窗口实例
        """
    def GetAllSubWindow(self) -> List['Chat']: 
        """获取所有子窗口实例
        
        Returns:
            List[Chat]: 所有子窗口实例
        """
    @uilock
    def AddListenChat(self, nickname: str, callback: Callable[[Message, Chat], None]) -> WxResponse: 
        """添加监听聊天，将聊天窗口独立出去形成Chat对象子窗口，用于监听
        
        Args:
            nickname (str): 要监听的聊天对象
            callback (Callable[['Message', Chat], None]): 回调函数，参数为(Message对象, Chat对象)，返回值为None
        """
    def StopListening(self, remove: bool = True) -> None: 
        """停止监听
        
        Args:
            remove (bool, optional): 是否移除监听对象. Defaults to True.
        """
    def StartListening(self) -> None: """开启监听"""
    @uilock
    def RemoveListenChat(self, nickname: str, close_window: bool = True) -> WxResponse: 
        """移除监听聊天

        Args:
            nickname (str): 要移除的监听聊天对象
            close_window (bool, optional): 是否关闭聊天窗口. Defaults to True.

        Returns:
            WxResponse: 执行结果
        """
    def Moments(self, timeout: int = 3) -> MomentsWnd: """进入朋友圈"""
    def GetNextNewMessage(self, filter_mute: bool = False) -> dict[str, List['Message']]: 
        """获取下一个新消息
        
        Args:
            filter_mute (bool, optional): 是否过滤掉免打扰消息. Defaults to False.

        Returns:
            Dict[str, List['Message']]: 消息列表
        """
    def GetNewFriends(self, acceptable: bool = True) -> List['NewFriendElement']: 
        """获取新的好友申请列表

        Args:
            acceptable (bool, optional): 是否过滤掉已接受的好友申请
        
        Returns:
            List['NewFriendElement']: 新的好友申请列表，元素为NewFriendElement对象，可直接调用Accept方法

        Example:
            >>> wx = WeChat()
            >>> newfriends = wx.GetNewFriends(acceptable=True)
            >>> tags = ['标签1', '标签2']
            >>> for friend in newfriends:
            ...     remark = f'备注{friend.name}'
            ...     friend.Accept(remark=remark, tags=tags)  # 接受好友请求，并设置备注和标签
        """
    def AddNewFriend(self, keywords: str, addmsg: str = None, remark: str = None, tags: List[str] = None, permission: Literal['朋友圈', '仅聊天'] = '朋友圈', timeout: int = 5) -> WxResponse: 
        """添加新的好友

        Args:
            keywords (str): 搜索关键词，可以是昵称、微信号、手机号等
            addmsg (str, optional): 添加好友时的附加消息，默认为None
            remark (str, optional): 添加好友后的备注，默认为None
            tags (List, optional): 添加好友后的标签，默认为None
            permission (Literal['朋友圈', '仅聊天'], optional): 添加好友后的权限，默认为'朋友圈'
            timeout (int, optional): 搜索好友的超时时间，默认为5秒

        Returns:
            WxResponse: 添加好友的结果
        """
    def GetAllRecentGroups(self, speed: int = 1, interval: float = 0.05) -> WxResponse | List[str]: 
        """获取所有最近群聊
        
        Args:
            speed (int, optional): 获取速度，默认为1
            interval (float, optional): 获取间隔，默认为0.05秒

        Returns:
            WxResponse | List[str]: 失败时返回WxResponse，成功时返回所有最近群聊列表
        """
    def GetContactGroups(
            self,
            speed: int = 1,
            interval: float = 0.1
    ) -> List[str]:
        """获取通讯录中的所有群聊
        
        Args:
            speed (int, optional): 获取速度，默认为1
            interval (float, optional): 滚动间隔，默认为0.1秒

        Returns:
            List[str]: 所有群聊列表
        """
    def GetFriendDetails(self, n: Incomplete | None = None, tag: Incomplete | None = None, timeout: int = 1048575) -> List[dict]: 
        """获取好友详情

        Args:
            n (int, optional): 获取前n个好友详情信息, 默认为None，获取所有好友详情信息
            tag (str, optional): 从指定标签开始获取好友详情信息，如'A'，默认为None即从第一个好友开始获取
            timeout (int, optional): 获取超时时间（秒），超过该时间则直接返回结果

        Returns:
            List[dict]: 所有好友详情信息
            
        注：1. 该方法运行时间较长，约0.5~1秒一个好友的速度，好友多的话可将n设置为一个较小的值，先测试一下
            2. 如果遇到企业微信的好友且为已离职状态，可能导致微信卡死，需重启（此为微信客户端BUG）
            3. 该方法未经过大量测试，可能存在未知问题，如有问题请微信群内反馈
        """
    def SwitchToChat(self) -> None: """切换到聊天页面"""
    def SwitchToContact(self) -> None: """切换到联系人页面"""

def get_wx_clients() -> List[WeChat]: 
    """获取当前所有微信客户端
    
    Returns:
        List[WeChat]: 当前所有微信客户端
    """

from functools import wraps
from typing import Any, Callable, Coroutine, Dict, Optional, Union
from workwechatapi.models.agent import AMSBase, AMRBase
from workwechatapi.models.wcb_message import WMRBase
from workwechatapi.actions.crypt import WechatEDCryption
from workwechatapi.actions.core import WechatExecutor
import requests
import json
import time
import asyncio
import inspect


class Agent:
    agent_name: str
    """企业应用的名称"""
    agent_id: int
    """企业应用的ID"""
    agent_secret: str
    """企业应用的凭证密钥"""
    api_token: str
    """API Token，用于验证API请求的合法性"""
    api_EncodingAESkey: str
    """API的EncodingAESkey，用于消息加密和解密"""
    msg_handler: Dict[str, Optional[Callable]]
    """消息处理器字典，键为消息类型，值为处理函数"""
    msg_handlerline: list
    """消息处理器列表，包含正在运行的消息类型"""
    corp_id: str = ""
    """企业ID，通常与Corp对象关联"""
    access_token: str = ""
    """企业应用的Access Token"""
    access_token_until: int = 0
    """Access Token的有效期，单位为秒，从1970年1月1日开始计算的时间戳"""

    def to_dict(self) -> dict:
        """
        将Agent对象转换为字典格式，方便序列化和存储。
        :return: 包含Agent信息的字典
        """
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "agent_secret": self.agent_secret,
            "api_token": self.api_token,
            "api_EncodingAESkey": self.api_EncodingAESkey,
        }

    def save(self):
        """
        保存Agent对象到指定位置或返回字典格式。
        :param location: 保存位置，如果为None则返回字典
        """
        return self.to_dict()

    @staticmethod
    def save_example():
        """
        保存Agent对象的示例数据
        """
        return {
            "agent_name": "agent_name:str",
            "agent_id": "agent_id:int",
            "agent_secret": "agent_secret:str",
            "api_token": "api_token:str",
            "api_EncodingAESkey": "api_EncodingAESkey:str",
        }

    @staticmethod
    def load(data: dict) -> "Agent":
        """
        从字典数据加载Agent对象。
        :param data: 包含Agent信息的字典
        :return: Agent对象
        """
        return Agent(
            agent_name=data["agent_name"],
            agent_id=data["agent_id"],
            agent_secret=data["agent_secret"],
            api_token=data["api_token"],
            api_EncodingAESkey=data["api_EncodingAESkey"],
        )

    def __init__(
        self,
        agent_name: str,
        agent_id: int,
        agent_secret: str,
        api_token: str,
        api_EncodingAESkey: str,
    ):

        self.agent_name = agent_name
        self.agent_id = agent_id
        self.agent_secret = agent_secret
        self.api_token = api_token
        self.api_EncodingAESkey = api_EncodingAESkey
        if not self.update_token():
            raise RuntimeError(
                f"Failed to initialize Agent {self.agent_name}: Unable to update access token"
            )

        self.DEcryption = WechatEDCryption(
            self.api_token, self.api_EncodingAESkey, self.corp_id
        )
        self.msg_handler: Dict[str, Optional[Callable]] = {}
        self.msg_handlerline = []

    def upload_temp_media(self, media_file: Union[str, bytes], media_type: str) -> dict:
        """
        上传临时媒体文件到企业微信服务器。
        :param media_file: 媒体文件路径或字节内容
        :param media_type: 媒体类型，支持'image', 'voice', 'video', 'file'
        :raises AssertionError: 如果access_token未设置或media_type不支持
        :raises FileNotFoundError: 如果提供的media_file路径不存在
        :raises ValueError: 如果media_type不在支持的类型列表中
        :return: 媒体文件的media_id, 创建时间戳等信息
        """
        import os

        assert (
            self.access_token
        ), "AgentMessage: access_token must be set before uploading media"
        assert media_type in [
            "image",
            "voice",
            "video",
            "file",
        ], "AgentMessage: Unsupported media type"

        headers = {"Content-Type": "multipart/form-data"}
        file_object = None
        media_file_name = ""

        if isinstance(media_file, str):
            if not media_file:
                raise ValueError("AgentMessage: media_file cannot be an empty string")
            if not os.path.exists(media_file):
                raise FileNotFoundError(
                    f"AgentMessage: Media file '{media_file}' does not exist"
                )
            if not os.path.isfile(media_file):
                raise ValueError(
                    f"AgentMessage: Media file '{media_file}' is not a valid file"
                )
            media_file_path = os.path.abspath(media_file)
            if media_type == "image" and not media_file_path.lower().endswith(
                (".png", ".jpg", ".jpeg", ".gif")
            ):
                raise ValueError(
                    "AgentMessage: Media file must be an image with a valid extension"
                )
            if media_type == "voice" and not media_file_path.lower().endswith(
                (".mp3", ".wav", ".amr")
            ):
                raise ValueError(
                    "AgentMessage: Media file must be a voice file with a valid extension"
                )
            if media_type == "video" and not media_file_path.lower().endswith(
                (".mp4", ".avi", ".mov")
            ):
                raise ValueError(
                    "AgentMessage: Media file must be a video file with a valid extension"
                )
            if media_type == "file" and not media_file_path.lower().endswith(
                (".txt", ".pdf", ".docx", ".xlsx")
            ):
                raise ValueError(
                    "AgentMessage: Media file must be a file with a valid extension"
                )
            file_object = open(media_file_path, "rb")
            media_file_name = os.path.basename(media_file_path)
        elif isinstance(media_file, bytes):
            import hashlib

            md5 = hashlib.md5(media_file).hexdigest()
            media_file_name = f"media_{md5[:8]}.{media_type}"
            file_object = media_file

        files = {"media": (media_file_name, file_object, "application/octet-stream")}

        try:
            response = requests.post(
                f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.access_token}&type={media_type}",
                headers=headers,
                files=files,  # type: ignore
            )
            response_data = response.json()
            if response_data.get("errcode") != 0:
                raise ValueError(
                    f"AgentMessage: Failed to upload media file: {response_data.get('errmsg', 'Unknown error')}"
                )
        finally:
            if (
                isinstance(media_file, str)
                and file_object
                and hasattr(file_object, "close")
            ):
                file_object.close()  # type: ignore

        if "media_id" not in response_data:
            raise ValueError(
                "AgentMessage: Media upload response does not contain media_id"
            )
        return {
            "media_id": response_data["media_id"],
            "created_at": response_data["created_at"],
        }

    def add_msg_handler(
        self, msg_type: str, handler: Callable[[WMRBase], Coroutine[Any, Any, None]]
    ) -> None:
        """
        添加消息处理器，用于处理特定类型的消息。
        :param msg_type: 消息类型，["text","image","voice","video","location"]
        :param handler: 处理函数，接受一个参数（消息对象）, 示例: def example(message:WMRBase) -> None:
        """
        assert msg_type in [
            "text",
            "image",
            "voice",
            "video",
            "location",
        ], "msg_type must be anyone in text, image, voice, video, or location"
        sig = inspect.signature(handler)
        params = list(sig.parameters.values())
        if len(params) != 1:
            raise ValueError(
                "Handler must accept exactly one argument that is a WMRBase instance"
            )
        param_type = params[0].annotation
        if param_type is inspect.Parameter.empty or not issubclass(param_type, WMRBase):
            raise TypeError("Handler argument must be WMRBase or its subclass")
        if self.msg_handler.get(msg_type):
            import warnings

            warnings.warn(
                f"Agent {self.agent_id} already has a handler for {msg_type} messages, replacing it",
                RuntimeWarning,
            )
        self.msg_handler[msg_type] = handler

    def del_msg_handler(self, msg_type: str) -> None:
        assert msg_type in [
            "text",
            "image",
            "voice",
            "video",
            "location",
        ], "msg_type must be anyone in text, image, voice, video, or location"
        self.msg_handler[msg_type] = None

    def run_msg_handler(self, message: WMRBase) -> None:
        msg_type = message.msg_type
        handler = self.msg_handler[msg_type]
        if not handler:
            raise ValueError(
                f"Agent {self.agent_id} has none handler to deal with {msg_type} message "
            )
        if message.msg_id not in self.msg_handlerline:
            self.msg_handlerline.append(message.msg_id)
            if inspect.iscoroutinefunction(handler):
                # 异步处理器，在线程池中运行协程
                WechatExecutor.submit(lambda: asyncio.run(handler(message)))
            else:
                # 同步处理器，直接在线程池中运行
                WechatExecutor.submit(handler, message)

    @staticmethod
    def auto_validate_token(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.validate_access_token():
                raise RuntimeError(
                    f"Agent {self.agent_id} access token validation failed"
                )
            return func(self, *args, **kwargs)

        return wrapper

    def update_token(self):
        """
        更新Access Token和有效期
        :param token: 新的Access Token
        :param until: Access Token的有效期，单位为秒
        """
        response = requests.get(
            f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corp_id}&corpsecret={self.agent_secret}"
        )
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            self.access_token_until = int(time.time()) + 7200
            return True
        else:
            return False

    def validate_access_token(self) -> bool:
        """验证企业微信的Access Token是否有效，在下述函数执行前自动调用"""
        if self.access_token_until < int(time.time()):
            return self.update_token()
        return True

    @auto_validate_token
    def send(self, sender: AMSBase) -> AMRBase:
        """
        发送消息的抽象方法，子类应实现具体的发送逻辑。
        :param sender: 发送者信息
        :return: 消息发送响应
        """
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.post(
            f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}",
            headers=headers,
            data=json.dumps(sender.to_dict(), ensure_ascii=False),
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"AgentMessage: Failed to send message: {response.status_code} {response.text}"
            )

        response_data = response.json()
        return AMRBase(**response_data)

    @auto_validate_token
    def recall(self, msgid: str) -> AMRBase:
        """
        撤回消息
        :param msgid: 消息ID
        :return: 撤回响应信息
        """

        data = {"msgid": msgid}
        headers = {"Content-Type": "application/json; charset=utf-8"}

        response = requests.post(
            f"https://qyapi.weixin.qq.com/cgi-bin/message/recall?access_token={self.access_token}",
            headers=headers,
            data=json.dumps(data, ensure_ascii=False),
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Failed to recall message: {response.status_code} {response.text}"
            )

        response_data = response.json()
        return AMRBase(**response_data)

    def decrypt(
        self, body: bytes, msg_signature: str, timestamp: str, nonce: str
    ) -> str:
        ret, sEchoStr = self.DEcryption.decrypt_msg(
            body, str(msg_signature), str(timestamp), str(nonce)
        )
        if ret != self.DEcryption.Status.OK:
            raise RuntimeError(f"Decrypt message failed: {sEchoStr}")

        return sEchoStr

    def get_message(self, body: bytes, msg_signature: str, timestamp: str, nonce: str):
        try:
            msg_str = self.decrypt(body, msg_signature, timestamp, nonce)
            msg = WMRBase.load(msg_str)
            self.run_msg_handler(msg)
        except Exception as e:
            raise e

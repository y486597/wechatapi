"""
Wechat Callback Messages\\
This module defines the base class for Wechat callback messages and specific message types like text, image, voice, video, and location.\\
It includes methods for loading messages from XML, converting them to dictionaries, and converting them to XML format.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
import xml.etree.ElementTree as ET
from abc import abstractmethod


@dataclass
class WMRBase:
    """
    Wechat回调消息基类
    WechatMessageReceivedBase
    """

    to_user_name: str
    """接收方帐号（企业ID）"""
    from_user_name: str
    """发送方帐号（用户ID）"""
    create_time: int
    """消息创建时间（整型）"""
    msg_type: str
    """消息类型"""
    msg_id: int = field(default=0)
    """消息id，64位整型"""
    agent_id: int = field(default=0)
    """应用的AgentID，整型"""

    # 消息类型映射，用于自动匹配对应的继承类
    _message_classes = {}

    def __init_subclass__(cls, **kwargs):
        """注册子类到消息类型映射中"""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "msg_type"):
            default_type = cls.msg_type.default  # type: ignore
            WMRBase._message_classes[default_type] = cls

    @staticmethod
    def load(xml_data: str) -> "WMRBase":
        """
        从XML字符串自动解析对应类型的消息
        :param xml_data: XML字符串
        :return: 对应类型的消息实例
        """
        try:
            root = ET.fromstring(xml_data)
            xml_dict = {}
            for child in root:
                xml_dict[child.tag] = child.text

            msg_type = xml_dict.get("MsgType", "")

            if msg_type in WMRBase._message_classes:
                message_class = WMRBase._message_classes[msg_type]
                return message_class.load(xml_data)
            else:
                raise ValueError(f"Unsupported message type: {msg_type}")

        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        将消息转换为字典格式
        :return: 字典格式的消息
        """
        pass

    @abstractmethod
    def to_xml(self) -> str:
        """
        将消息转换为XML格式
        :return: XML格式的消息
        """
        pass


@dataclass
class WMRText(WMRBase):
    """
    Wechat回调文本事件消息
    """

    msg_type: str = field(default="text")
    """消息类型，文本为text"""
    content: str = field(default="")
    """文本消息内容"""

    @staticmethod
    def load(xml_data: str) -> "WMRText":
        """
        从XML字符串解析文本事件消息
        :param xml_data: XML字符串
        :return: WMRText实例
        """
        try:
            root = ET.fromstring(xml_data)
            xml_dict = {}
            for child in root:
                xml_dict[child.tag] = child.text
            return WMRText(
                to_user_name=xml_dict.get("ToUserName", ""),
                from_user_name=xml_dict.get("FromUserName", ""),
                create_time=int(xml_dict.get("CreateTime", 0)),
                msg_type=xml_dict.get("MsgType", "text"),
                content=xml_dict.get("Content", ""),
                msg_id=int(xml_dict.get("MsgId", 0)),
                agent_id=int(xml_dict.get("AgentID", 0)),
            )
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        将文本事件消息转换为字典格式
        :return: 字典格式的文本事件消息
        """
        return {
            "ToUserName": self.to_user_name,
            "FromUserName": self.from_user_name,
            "CreateTime": self.create_time,
            "MsgType": self.msg_type,
            "Content": self.content,
            "MsgId": self.msg_id,
            "AgentID": self.agent_id,
        }

    def to_xml(self) -> str:
        """
        将文本事件消息转换为XML格式
        :return: XML格式的文本事件消息
        """
        root = ET.Element("xml")

        def add_cdata_element(parent: ET.Element, tag: str, value: str) -> None:
            elem = ET.SubElement(parent, tag)
            elem.text = value

        add_cdata_element(root, "ToUserName", self.to_user_name)
        add_cdata_element(root, "FromUserName", self.from_user_name)

        create_time_elem = ET.SubElement(root, "CreateTime")
        create_time_elem.text = str(self.create_time)

        add_cdata_element(root, "MsgType", self.msg_type)
        add_cdata_element(root, "Content", self.content)

        msg_id_elem = ET.SubElement(root, "MsgId")
        msg_id_elem.text = str(self.msg_id)

        agent_id_elem = ET.SubElement(root, "AgentID")
        agent_id_elem.text = str(self.agent_id)

        return ET.tostring(root, encoding="unicode")


@dataclass
class WMRImage(WMRBase):
    """
    Wechat回调图片事件消息
    """

    msg_type: str = field(default="image")
    """消息类型，图片为image"""
    pic_url: str = field(default="")
    """图片链接"""
    media_id: str = field(default="")
    """图片媒体文件id，可以调用多媒体文件下载接口拉取数据"""

    @staticmethod
    def load(xml_data: str) -> "WMRImage":
        """
        从XML字符串解析图片事件消息
        :param xml_data: XML字符串
        :return: WMRImage实例
        """
        try:
            root = ET.fromstring(xml_data)
            xml_dict = {}
            for child in root:
                xml_dict[child.tag] = child.text
            return WMRImage(
                to_user_name=xml_dict.get("ToUserName", ""),
                from_user_name=xml_dict.get("FromUserName", ""),
                create_time=int(xml_dict.get("CreateTime", 0)),
                msg_type=xml_dict.get("MsgType", "image"),
                pic_url=xml_dict.get("PicUrl", ""),
                media_id=xml_dict.get("MediaId", ""),
                msg_id=int(xml_dict.get("MsgId", 0)),
                agent_id=int(xml_dict.get("AgentID", 0)),
            )
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        将图片事件消息转换为字典格式
        :return: 字典格式的图片事件消息
        """
        return {
            "ToUserName": self.to_user_name,
            "FromUserName": self.from_user_name,
            "CreateTime": self.create_time,
            "MsgType": self.msg_type,
            "PicUrl": self.pic_url,
            "MediaId": self.media_id,
            "MsgId": self.msg_id,
            "AgentID": self.agent_id,
        }

    def to_xml(self) -> str:
        """
        将图片事件消息转换为XML格式
        :return: XML格式的图片事件消息
        """
        root = ET.Element("xml")

        def add_cdata_element(parent: ET.Element, tag: str, value: str) -> None:
            elem = ET.SubElement(parent, tag)
            elem.text = value

        add_cdata_element(root, "ToUserName", self.to_user_name)
        add_cdata_element(root, "FromUserName", self.from_user_name)

        create_time_elem = ET.SubElement(root, "CreateTime")
        create_time_elem.text = str(self.create_time)

        add_cdata_element(root, "MsgType", self.msg_type)
        add_cdata_element(root, "PicUrl", self.pic_url)
        add_cdata_element(root, "MediaId", self.media_id)

        msg_id_elem = ET.SubElement(root, "MsgId")
        msg_id_elem.text = str(self.msg_id)

        agent_id_elem = ET.SubElement(root, "AgentID")
        agent_id_elem.text = str(self.agent_id)

        return ET.tostring(root, encoding="unicode")


@dataclass
class WMRVoice(WMRBase):
    """
    Wechat回调语音事件消息
    """

    msg_type: str = field(default="voice")
    """消息类型，语音为voice"""
    media_id: str = field(default="")
    """语音媒体文件id，可以调用多媒体文件下载接口拉取数据"""
    format: str = field(default="")
    """语音格式，如amr，speex等"""

    @staticmethod
    def load(xml_data: str) -> "WMRVoice":
        """
        从XML字符串解析语音事件消息
        :param xml_data: XML字符串
        :return: WMRVoice实例
        """
        try:
            root = ET.fromstring(xml_data)
            xml_dict = {}
            for child in root:
                xml_dict[child.tag] = child.text
            return WMRVoice(
                to_user_name=xml_dict.get("ToUserName", ""),
                from_user_name=xml_dict.get("FromUserName", ""),
                create_time=int(xml_dict.get("CreateTime", 0)),
                msg_type=xml_dict.get("MsgType", "voice"),
                media_id=xml_dict.get("MediaId", ""),
                format=xml_dict.get("Format", ""),
                msg_id=int(xml_dict.get("MsgId", 0)),
                agent_id=int(xml_dict.get("AgentID", 0)),
            )
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        将语音事件消息转换为字典格式
        :return: 字典格式的语音事件消息
        """
        return {
            "ToUserName": self.to_user_name,
            "FromUserName": self.from_user_name,
            "CreateTime": self.create_time,
            "MsgType": self.msg_type,
            "MediaId": self.media_id,
            "Format": self.format,
            "MsgId": self.msg_id,
            "AgentID": self.agent_id,
        }

    def to_xml(self) -> str:
        """将语音事件消息转换为XML格式
        :return: XML格式的语音事件消息
        """
        root = ET.Element("xml")

        def add_cdata_element(parent: ET.Element, tag: str, value: str) -> None:
            elem = ET.SubElement(parent, tag)
            elem.text = value

        add_cdata_element(root, "ToUserName", self.to_user_name)
        add_cdata_element(root, "FromUserName", self.from_user_name)

        create_time_elem = ET.SubElement(root, "CreateTime")
        create_time_elem.text = str(self.create_time)

        add_cdata_element(root, "MsgType", self.msg_type)
        add_cdata_element(root, "MediaId", self.media_id)
        add_cdata_element(root, "Format", self.format)

        msg_id_elem = ET.SubElement(root, "MsgId")
        msg_id_elem.text = str(self.msg_id)

        agent_id_elem = ET.SubElement(root, "AgentID")
        agent_id_elem.text = str(self.agent_id)

        return ET.tostring(root, encoding="unicode")


@dataclass
class WMRVideo(WMRBase):
    """
    Wechat回调视频事件消息
    """

    msg_type: str = field(default="video")
    """消息类型，视频为video"""
    media_id: str = field(default="")
    """视频媒体文件id，可以调用多媒体文件下载接口拉取数据"""
    thumb_media_id: str = field(default="")
    """视频消息缩略图的媒体id，可以调用多媒体文件下载接口拉取数据"""

    @staticmethod
    def load(xml_data: str) -> "WMRVideo":
        """
        从XML字符串解析视频事件消息
        :param xml_data: XML字符串
        :return: WMRVideo实例
        """
        try:
            root = ET.fromstring(xml_data)
            xml_dict = {}
            for child in root:
                xml_dict[child.tag] = child.text
            return WMRVideo(
                to_user_name=xml_dict.get("ToUserName", ""),
                from_user_name=xml_dict.get("FromUserName", ""),
                create_time=int(xml_dict.get("CreateTime", 0)),
                msg_type=xml_dict.get("MsgType", "video"),
                media_id=xml_dict.get("MediaId", ""),
                thumb_media_id=xml_dict.get("ThumbMediaId", ""),
                msg_id=int(xml_dict.get("MsgId", 0)),
                agent_id=int(xml_dict.get("AgentID", 0)),
            )
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        将视频事件消息转换为字典格式
        :return: 字典格式的视频事件消息
        """
        return {
            "ToUserName": self.to_user_name,
            "FromUserName": self.from_user_name,
            "CreateTime": self.create_time,
            "MsgType": self.msg_type,
            "MediaId": self.media_id,
            "ThumbMediaId": self.thumb_media_id,
            "MsgId": self.msg_id,
            "AgentID": self.agent_id,
        }

    def to_xml(self) -> str:
        """
        将视频事件消息转换为XML格式
        :return: XML格式的视频事件消息
        """
        root = ET.Element("xml")

        def add_cdata_element(parent: ET.Element, tag: str, value: str) -> None:
            elem = ET.SubElement(parent, tag)
            elem.text = value

        add_cdata_element(root, "ToUserName", self.to_user_name)
        add_cdata_element(root, "FromUserName", self.from_user_name)

        create_time_elem = ET.SubElement(root, "CreateTime")
        create_time_elem.text = str(self.create_time)

        add_cdata_element(root, "MsgType", self.msg_type)
        add_cdata_element(root, "MediaId", self.media_id)
        add_cdata_element(root, "ThumbMediaId", self.thumb_media_id)

        msg_id_elem = ET.SubElement(root, "MsgId")
        msg_id_elem.text = str(self.msg_id)

        agent_id_elem = ET.SubElement(root, "AgentID")
        agent_id_elem.text = str(self.agent_id)

        return ET.tostring(root, encoding="unicode")


@dataclass
class WMRLocation(WMRBase):
    """
    Wechat回调位置事件消息
    """

    msg_type: str = field(default="location")
    """消息类型，位置为location"""
    location_x: float = field(default=0.0)
    """地理位置纬度"""
    location_y: float = field(default=0.0)
    """地理位置经度"""
    scale: int = field(default=0)
    """地图缩放大小"""
    label: str = field(default="")
    """地理位置信息"""
    app_type: str = field(default="wxwork")

    @staticmethod
    def load(xml_data: str) -> "WMRLocation":
        """
        从XML字符串解析位置事件消息
        :param xml_data: XML字符串
        :return: WMRLocation实例
        """
        try:
            root = ET.fromstring(xml_data)
            xml_dict = {}
            for child in root:
                xml_dict[child.tag] = child.text
            return WMRLocation(
                to_user_name=xml_dict.get("ToUserName", ""),
                from_user_name=xml_dict.get("FromUserName", ""),
                create_time=int(xml_dict.get("CreateTime", 0)),
                msg_type=xml_dict.get("MsgType", "location"),
                location_x=float(xml_dict.get("Location_X", 0.0)),
                location_y=float(xml_dict.get("Location_Y", 0.0)),
                scale=int(xml_dict.get("Scale", 0)),
                label=xml_dict.get("Label", ""),
                msg_id=int(xml_dict.get("MsgId", 0)),
                agent_id=int(xml_dict.get("AgentID", 0)),
                app_type=xml_dict.get("AppType", "wxwork"),
            )
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        将位置事件消息转换为字典格式
        :return: 字典格式的位置事件消息
        """
        return {
            "ToUserName": self.to_user_name,
            "FromUserName": self.from_user_name,
            "CreateTime": self.create_time,
            "MsgType": self.msg_type,
            "Location_X": self.location_x,
            "Location_Y": self.location_y,
            "Scale": self.scale,
            "Label": self.label,
            "MsgId": self.msg_id,
            "AgentID": self.agent_id,
            "AppType": self.app_type,
        }

    def to_xml(self) -> str:
        """
        将位置事件消息转换为XML格式
        :return: XML格式的位置事件消息
        """
        root = ET.Element("xml")

        def add_cdata_element(parent: ET.Element, tag: str, value: str) -> None:
            elem = ET.SubElement(parent, tag)
            elem.text = value

        add_cdata_element(root, "ToUserName", self.to_user_name)
        add_cdata_element(root, "FromUserName", self.from_user_name)

        create_time_elem = ET.SubElement(root, "CreateTime")
        create_time_elem.text = str(self.create_time)

        add_cdata_element(root, "MsgType", self.msg_type)
        location_x_elem = ET.SubElement(root, "Location_X")
        location_x_elem.text = str(self.location_x)
        location_y_elem = ET.SubElement(root, "Location_Y")
        location_y_elem.text = str(self.location_y)
        scale_elem = ET.SubElement(root, "Scale")
        scale_elem.text = str(self.scale)
        add_cdata_element(root, "Label", self.label)

        msg_id_elem = ET.SubElement(root, "MsgId")
        msg_id_elem.text = str(self.msg_id)

        agent_id_elem = ET.SubElement(root, "AgentID")
        agent_id_elem.text = str(self.agent_id)

        app_type_elem = ET.SubElement(root, "AppType")
        app_type_elem.text = self.app_type

        return ET.tostring(root, encoding="unicode")

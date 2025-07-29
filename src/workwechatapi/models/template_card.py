from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
import json


@dataclass
class Source:
    """卡片来源样式信息"""

    icon_url: Optional[str] = field(default=None)
    desc: Optional[str] = field(default=None)
    desc_color: int = field(default=0)
    """ 0-灰色, 1-黑色, 2-红色, 3-绿色 """


@dataclass
class ActionMenu:
    """卡片右上角更多操作按钮"""

    desc: str
    action_list: List[Dict[str, Union[str, Any]]]
    """[{"text": "", "key": ""}]"""


@dataclass
class MainTitle:
    """模版卡片的主要内容，包括一级标题和标题辅助信息"""

    title: Optional[str] = field(default=None)
    desc: Optional[str] = field(default=None)


@dataclass
class EmphasisContent:
    """关键数据样式"""

    title: Optional[str] = field(default=None)
    desc: Optional[str] = field(default=None)


@dataclass
class QuoteArea:
    """引用文献样式"""

    type: int = field(default=0)
    """0-无跳转, 1-跳转URL, 2-跳转小程序"""
    url: Optional[str] = field(default=None)
    appid: Optional[str] = field(default=None)
    pagepath: Optional[str] = field(default=None)
    title: Optional[str] = field(default=None)
    quote_text: Optional[str] = field(default=None)


@dataclass
class HorizontalContent:
    """二级标题+文本列表"""

    keyname: str
    value: str
    type: int = field(default=0)
    """0-普通文本, 1-跳转URL, 3-成员详情"""
    url: Optional[str] = field(default=None)
    userid: Optional[str] = field(default=None)


@dataclass
class JumpAction:
    """跳转指引样式的列表"""

    title: str
    type: int = field(default=0)
    """0-无跳转, 1-跳转URL, 2-跳转小程序, 3-智能回复"""
    question: Optional[str] = field(default=None)
    url: Optional[str] = field(default=None)
    appid: Optional[str] = field(default=None)
    pagepath: Optional[str] = field(default=None)


@dataclass
class CardAction:
    """整体卡片的点击跳转事件"""

    type: int
    """1-跳转URL, 2-打开小程序"""
    url: Optional[str] = field(default=None)
    appid: Optional[str] = field(default=None)
    pagepath: Optional[str] = field(default=None)


@dataclass
class VerticalContent:
    """卡片二级垂直内容"""

    title: str
    desc: Optional[str] = field(default=None)


@dataclass
class CardImage:
    """图片样式"""

    url: str
    aspect_ratio: Optional[float] = 1.3
    """宽高比范围(1.3-2.25)"""


@dataclass
class ImageTextArea:
    """左图右文样式"""

    image_url: str
    type: int = field(default=0)
    """ 0-无跳转, 1-跳转URL, 2-跳转小程序 """
    url: Optional[str] = field(default=None)
    appid: Optional[str] = field(default=None)
    pagepath: Optional[str] = field(default=None)
    title: Optional[str] = field(default=None)
    desc: Optional[str] = field(default=None)


@dataclass
class SubmitButton:
    """提交按钮样式"""

    text: str
    key: str


@dataclass
class SelectionItem:
    """下拉式的选择器列表"""

    question_key: str
    title: Optional[str] = field(default=None)
    disable: Optional[bool] = field(default=None)
    selected_id: Optional[str] = field(default=None)
    option_list: Optional[List[Dict[str, Union[str, bool]]]] = field(default=None)
    """ [{"id": "...", "text": "...", "is_checked": ...}]"""


@dataclass
class Button:
    """按钮列表"""

    text: str
    key: str
    style: Optional[int] = field(default=None)
    """1:蓝底白字\\
    2:灰底蓝字\\
    3:灰底红字\\
    4:灰底黑字"""


@dataclass
class Checkbox:
    """选择题样式"""

    question_key: str
    disable: Optional[bool] = field(default=None)
    mode: Optional[int] = 0
    """# 0-单选, 1-多选"""
    option_list: Optional[List[Dict[str, Union[str, bool]]]] = field(default=None)
    """ [{"id": "...", "text": "...", "is_checked": ...}]"""


@dataclass
class TemplateCard:
    """模版卡片基类"""

    card_type: str
    source: Optional[Source] = field(default=None)
    action_menu: Optional[ActionMenu] = field(default=None)
    task_id: Optional[str] = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        """将卡片转换为字典格式"""
        return {key: value for key, value in self.__dict__.items() if value is not None}

    def json(self) -> str:
        """将卡片转换为JSON格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class TextNoticeCard(TemplateCard):
    """文本通知卡片"""

    main_title: Optional[MainTitle] = field(default=None)
    emphasis_content: Optional[EmphasisContent] = field(default=None)
    quote_area: Optional[QuoteArea] = field(default=None)
    sub_title_text: Optional[str] = field(default=None)
    horizontal_content_list: Optional[List[HorizontalContent]] = field(default=None)
    jump_list: Optional[List[JumpAction]] = field(default=None)
    card_action: CardAction = field(default_factory=lambda: CardAction(type=1))

    def __init__(self):
        super().__init__("text_notice")


@dataclass
class NewsNoticeCard(TemplateCard):
    """图文展示卡片"""

    main_title: MainTitle = field(default_factory=MainTitle)
    card_image: Optional[CardImage] = field(default=None)
    image_text_area: Optional[ImageTextArea] = field(default=None)
    vertical_content_list: Optional[List[VerticalContent]] = field(default=None)
    horizontal_content_list: Optional[List[HorizontalContent]] = field(default=None)
    jump_list: Optional[List[JumpAction]] = field(default=None)
    card_action: CardAction = field(default_factory=lambda: CardAction(type=1))

    def __init__(self):
        super().__init__("news_notice")


@dataclass
class ButtonInteractionCard(TemplateCard):
    """按钮交互卡片"""

    main_title: MainTitle = field(default_factory=lambda: MainTitle(title=""))
    button_list: List[Button] = field(default_factory=list)
    quote_area: Optional[QuoteArea] = field(default=None)
    sub_title_text: Optional[str] = field(default=None)
    horizontal_content_list: Optional[List[HorizontalContent]] = field(default=None)
    button_selection: Optional[SelectionItem] = field(default=None)
    card_action: Optional[CardAction] = field(default=None)

    def __init__(self):
        super().__init__("button_interaction")


@dataclass
class VoteInteractionCard(TemplateCard):
    """投票选择卡片"""

    main_title: MainTitle = field(default_factory=MainTitle)
    checkbox: Checkbox = field(default_factory=lambda: Checkbox(question_key=""))
    submit_button: SubmitButton = field(
        default_factory=lambda: SubmitButton(text="", key="")
    )

    def __init__(self):
        super().__init__("vote_interaction")


#
@dataclass
class MultipleInteractionCard(TemplateCard):
    """多项选择卡片"""

    
    main_title: MainTitle = field(default_factory=MainTitle)
    select_list: List[SelectionItem] = field(default_factory=list)
    submit_button: SubmitButton = field(
        default_factory=lambda: SubmitButton(text="", key="")
    )
    def __init__(self):
            super().__init__("multiple_interaction")


@dataclass
class UpdateTo:
    """更新模版卡片消息"""

    agentid: str
    """应用的agentid"""
    response_code: str
    """更新卡片所需要消费的code，可通过发消息接口和回调接口返回值获取，一个code只能调用一次该接口，且只能在72小时内调用"""
    partyids: Optional[List[str]] = field(default=None)
    """企业的部门ID列表（最多支持100个）"""
    userids: Optional[List[str]] = field(default=None)
    """企业的成员ID列表（最多支持1000个）"""
    tagids: Optional[List[str]] = field(default=None)
    """企业的标签ID列表（最多支持100个）"""
    atall: Optional[bool] = field(default=None)
    """更新整个任务接收人员"""

    def __post_init__(self):
        if not isinstance(self.response_code, str):
            raise ValueError("UpdateTo: response_code must be a string")
        if self.partyids and not isinstance(self.partyids, list):
            raise ValueError("UpdateTo: partyids must be a list of strings")
        if self.userids and not isinstance(self.userids, list):
            raise ValueError("UpdateTo: userids must be a list of strings")
        if self.tagids and not isinstance(self.tagids, list):
            raise ValueError("UpdateTo: tagids must be a list of strings")

    def to_dict(self) -> Dict[str, Any]:
        """将 UpdateTo 转换为字典格式"""
        data = self.__dict__.copy()
        return {key: value for key, value in data.items() if value is not None}


@dataclass
class UpdateToUninteraction(UpdateTo):
    """仅原卡片为 按钮交互型、投票选择型、多项选择型的卡片可以更新按钮，可以将按钮更新为不可点击状态，并且自定义文案"""

    replace_button: str = ""

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.replace_button, str):
            raise ValueError("UpdateToUninteraction: replace_button must be a string")
        if not self.replace_button:
            raise ValueError("UpdateToUninteraction: replace_button cannot be empty")
        self.button = {"replace_button": self.replace_button}

    def to_dict(self) -> Dict[str, Any]:
        """将 UpdateToUninteraction 转换为字典格式"""
        data = super().to_dict()
        data["button"] = self.button
        return data


@dataclass
class UpdateToCard(UpdateTo):
    template_card: TemplateCard = field(
        default_factory=lambda: TemplateCard("text_notice")
    )
    enable_id_trans: Optional[int] = 0
    """表示是否开启id转译，0表示否，1表示是，默认0"""

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.enable_id_trans, int):
            raise ValueError("UpdateToCard: enable must be an integer")
        if not isinstance(self.template_card, TemplateCard):
            raise ValueError(
                "UpdateToCard: template_card must be an instance of TemplateCard"
            )

    def to_dict(self) -> Dict[str, Any]:
        """将 UpdateToCard 转换为字典格式"""
        data = super().to_dict()
        data["enable_id_trans"] = self.enable_id_trans
        data["template_card"] = self.template_card.to_dict()
        return data

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AMSBase:
    """
    Wechat应用消息发送基类\\
    touser、toparty、totag不能同时为空
    """

    touser: Optional[str] = None
    """指定接收消息的成员，成员ID列表（多个接收者用‘|’分隔，最多支持1000个）。\\
    特殊情况：指定为"@all"，则向该企业应用的全部成员发送消息。"""
    toparty: Optional[str] = None
    """指定接收消息的部门，部门ID列表，多个接收者用‘|’分隔，最多支持100个。\\
    当touser为"@all"时忽略本参数"""
    totag: Optional[str] = None
    """指定接收消息的标签，标签ID列表，多个接收者用‘|’分隔，最多支持100个。\\
    当touser为"@all"时忽略本参数"""
    agentid: int = 0
    """应用ID，必填"""
    safe: int = 0
    """是否开启保密消息，0=否，1=是"""
    enable_id_trans: int = 0
    """是否开启ID转译，0=否，1=是"""
    enable_duplicate_check: int = 0
    """ 是否开启重复消息检查，0=否，1=是"""
    duplicate_check_interval: int = 1800
    """重复消息检查时间间隔，单位：秒"""

    def __post_init__(self):
        if not self.touser and not self.toparty and not self.totag:
            raise ValueError(
                "AMSBase: touser, toparty, totag cannot all be None"
            )

        if self.touser == "@all":
            self.toparty = None
            self.totag = None

        if self.agentid <= 0:
            raise ValueError("AMSBase: agentid must be a positive integer")

        if self.safe not in (0, 1):
            raise ValueError("AMSBase: safe must be 0 or 1")

        if self.enable_id_trans not in (0, 1):
            raise ValueError("AMSBase: enable_id_trans must be 0 or 1")

        if self.enable_duplicate_check not in (0, 1):
            raise ValueError(
                "AMSBase: enable_duplicate_check must be 0 or 1"
            )

        if self.enable_duplicate_check and (
            self.duplicate_check_interval <= 0 or self.duplicate_check_interval > 86400
        ):
            raise ValueError(
                "AMSBase: duplicate_check_interval must be between 1 and 86400 seconds"
            )

    def to_dict(self) -> dict:
        """
        将发送者信息转换为字典格式
        :return: 发送者信息字典
        """
        content = {
            "touser": self.touser,
            "toparty": self.toparty,
            "totag": self.totag,
            "agentid": self.agentid,
            "safe": self.safe,
            "enable_id_trans": self.enable_id_trans,
            "enable_duplicate_check": self.enable_duplicate_check,
            "duplicate_check_interval": self.duplicate_check_interval,
        }
        content["msgtype"] = self.msgtype  # type: ignore
        content[content["msgtype"]] = self.__dict__.get(content["msgtype"])

        return {k: v for k, v in content.items() if v is not None and v != ""}

@dataclass
class AMRBase:
    """
    Wechat应用消息发送返回值基类
    """

    errcode: int
    """返回码"""
    errmsg: str
    """对返回码的文本描述内容"""
    invaliduser: Optional[str]
    """不合法的userid，不区分大小写，统一转为小写"""
    invalidparty: Optional[str]
    """不合法的partyid"""
    invalidtag: Optional[str]
    """不合法的标签id"""
    unlicenseduser: Optional[str]
    """没有基础接口许可(包含已过期)的userid"""
    msgid: str
    """消息id，用于撤回应用消息"""
    response_code: Optional[int]
    """仅消息类型为"按钮交互型"，"投票选择型"和"多项选择型"的模板卡片消息返回，应用可使用response_code调用更新模版卡片消息接口，72小时内有效，且只能使用一次"""


@dataclass
class AMSText(AMSBase):
    """
    文本消息类型
    """

    msgtype = "text"
    content: str = field(default_factory=str)
    """消息内容，最长不超过2048个字节，超过将截断（支持id转译）"""

    def __post_init__(self):
        super().__post_init__()
        if not self.content:
            raise ValueError("AMSText: text must not be empty")
        if len(self.content.encode("utf-8")) > 2048:
            raise ValueError("AMSText: text must not exceed 2048 bytes")
        self.text = dict({"content": self.content})


@dataclass
class AMSImage(AMSBase):
    """
    图片消息类型
    """

    msgtype = "image"
    media_id: str = field(default_factory=str)
    """图片的media_id，上传图片素材接口返回的media_id"""

    def __post_init__(self):
        super().__post_init__()
        if not self.media_id:
            raise ValueError("AMSImage: image must not be empty")
        self.image = dict({"media_id": self.media_id})


@dataclass
class AMSVoice(AMSBase):
    """
    图片消息类型
    """

    msgtype = "voice"
    media_id: str = field(default_factory=str)
    """图片的media_id，上传图片素材接口返回的media_id"""

    def __post_init__(self):
        super().__post_init__()
        if not self.media_id:
            raise ValueError("AMSVoice: voice must not be empty")
        self.voice = dict({"media_id": self.media_id})


@dataclass
class AMSVideo(AMSBase):
    """
    视频消息类型
    """

    msgtype = "video"
    media_id: str = field(default_factory=str)
    """media_id:视频媒体文件id，可以调用上传临时素材接口获取
    title:视频消息的标题，不超过128个字节，超过会自动截断, 非必须\\
    description:视频消息的描述，不超过512个字节，超过会自动截断, 非必须\\"""

    def __post_init__(self):
        super().__post_init__()
        if not self.media_id:
            raise ValueError("AMSVideo: video must not be empty")
        self.video = dict({"media_id": self.media_id})


@dataclass
class AMSFile(AMSBase):
    """
    文件消息类型
    """

    msgtype = "file"
    media_id: str = field(default_factory=str)
    """文件的media_id，上传文件素材接口返回的media_id"""

    def __post_init__(self):
        super().__post_init__()
        if not self.media_id:
            raise ValueError("AMSFile: file must not be empty")
        self.file = dict({"media_id": self.media_id})


@dataclass
class AMSTextCard(AMSBase):
    """
    文本卡片消息
    """

    msgtype = "textcard"
    textcard: dict = field(default_factory=dict)
    """title:标题，不超过128个字符，超过会自动截断（支持id转译）\\
    description:描述，不超过512个字符，超过会自动截断（支持id转译）\\
    文字颜色：灰色(gray)、高亮(highlight)、默认黑色(normal)，将其作为div标签的class属性即可\\
    url:点击后跳转的链接。最长2048字节，请确保包含了协议头(http/https)\\
    btntxt:按钮文字。 默认为“详情”，不超过4个文字，超过自动截断，非必须"""

    def __post_init__(self):
        super().__post_init__()
        self.textcard = dict(self.textcard)
        if not self.textcard.get("media_id"):
            raise ValueError("AMSTextCard: textcard must not be empty")
        if not self.textcard.get("url"):
            raise ValueError("AMSTextCard: url must not be empty")
        if len(self.textcard["url"].encode("utf-8")) > 2048:
            raise ValueError("AMSTextCard: url must not exceed 2048 bytes")
        if not self.textcard.get("url").startswith("http://") and not self.textcard[  # type: ignore
            "url"
        ].startswith(
            "https://"
        ):
            raise ValueError("AMSTextCard: url must start with http:// or https://")


@dataclass
class News:
    """
    图文消息
    """

    title: str
    """标题，不超过128个字节，超过会自动截断（支持id转译）"""
    description: str
    """描述，不超过512个字节，超过会自动截断（支持id转译）"""
    url: str | None = None
    """点击后跳转的链接。最长2048字节，请确保包含了协议头(http/https)，小程序或者url必须填写一个"""
    picurl: str | None = None
    """图文消息的图片链接，最长2048字节，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。"""
    appid: str | None = None
    """小程序appid，必须是与当前应用关联的小程序，appid和pagepath
    必须同时填写，填写后会忽略url字段"""
    pagepath: str | None = None
    """点击消息卡片后的小程序页面，最长128字节，仅限本小程序内的页面。appid和pagepath
    必须同时填写，填写后会忽略url字段"""

    def __post_init__(self):
        if not self.title:
            raise ValueError("AMSNews: self title must not be empty")
        if not self.url and not (self.appid and self.pagepath):
            raise ValueError(
                "AMSNews: self must have either url or both appid and pagepath"
            )
        if self.url and len(self.url.encode("utf-8")) > 2048:
            raise ValueError("AMSNews: self url must not exceed 2048 bytes")
        if self.picurl and len(self.picurl.encode("utf-8")) > 2048:
            raise ValueError("AMSNews: self picurl must not exceed 2048 bytes")
        if self.appid and not self.pagepath:
            raise ValueError(
                "AMSNews: if appid is provided, pagepath must also be provided"
            )
        if self.pagepath and not self.appid:
            raise ValueError(
                "AMSNews: if pagepath is provided, appid must also be provided"
            )
        if self.appid and self.pagepath:
            self.url = None

    def to_dict(self) -> dict:
        """
        将图文消息转换为字典格式
        :return: 图文消息字典
        """
        content = {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "picurl": self.picurl,
            "appid": self.appid,
            "pagepath": self.pagepath,
        }
        return {k: v for k, v in content.items() if v is not None and v != ""}


@dataclass
class AMSNews(AMSBase):
    """
    图文消息
    """

    msgtype = "news"
    articles: list[News] = field(default_factory=list)
    """title:标题，不超过128个字节，超过会自动截断（支持id转译）\\
    description:描述，不超过512个字节，超过会自动截断（支持id转译）\\
    url:点击后跳转的链接。 最长2048字节，请确保包含了协议头(http/https)，小程序或者url必须填写一个\\
    picurl:图文消息的图片链接，最长2048字节，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。\\
    appid:小程序appid，必须是与当前应用关联的小程序，appid和pagepath必须同时填写，填写后会忽略url字段\\
    pagepath:点击消息卡片后的小程序页面，最长128字节，仅限本小程序内的页面。appid和pagepath必须同时填写，填写后会忽略url字段\\"""

    def __post_init__(self):
        super().__post_init__()
        if not self.articles or not isinstance(self.articles, list):
            raise ValueError("AMSNews: articles must be a non-empty list")
        if len(self.articles) > 8:
            raise ValueError("AMSNews: articles cannot exceed 8 items")
        self.news: dict = {"articles": []}
        for article in self.articles:
            if not isinstance(article, News):
                raise ValueError(
                    "AMSNews: each article must be an instance of News"
                )
            article.__post_init__()
            self.news["articles"].append(article.to_dict())


@dataclass
class Mpnews:
    """
    mpnews类型的图文消息，跟普通的图文消息一致，唯一的差异是图文内容存储在企业微信。
    多次发送mpnews，会被认为是不同的图文，阅读、点赞的统计会被分开计算。
    """

    title: str
    """标题，不超过128个字节，超过会自动截断（支持id转译）"""
    thumb_media_id: str
    """图文消息缩略图的media_id, 可以通过素材管理接口获得。此处thumb_media_id即上传接口返回的media_id"""
    content: str
    """图文消息的内容，支持html标签，不超过666 K个字节（支持id转译）"""
    author: str | None = None
    """图文消息的作者，不超过64个字节"""
    content_source_url: str | None = None
    """图文消息点击“阅读原文”之后的页面链接"""
    digest: str | None = None
    """图文消息的描述，不超过512个字节，超过会自动截断（支持id转译）"""

    def __post_init__(self):
        if not self.title:
            raise ValueError("AMSMpnews: article title must not be empty")
        if not self.thumb_media_id:
            raise ValueError("AMSMpnews: article thumb_media_id must not be empty")
        if not self.content_source_url:
            raise ValueError(
                "AMSMpnews: article content_source_url must not be empty"
            )
        if not self.content:
            raise ValueError("AMSMpnews: article content must not be empty")
        if len(self.content.encode("utf-8")) > 666 * 1024:
            raise ValueError(
                "AMSMpnews: article content must not exceed 666 K bytes"
            )
        if self.digest and len(self.digest.encode("utf-8")) > 512:
            raise ValueError("AMSMpnews: article digest must not exceed 512 bytes")
        if self.author and len(self.author.encode("utf-8")) > 64:
            raise ValueError("AMSMpnews: article author must not exceed 64 bytes")

    def to_dict(self) -> dict:
        """
        将mpnews文章转换为字典格式
        :return: mpnews文章字典
        """
        content = {
            "title": self.title,
            "thumb_media_id": self.thumb_media_id,
            "content": self.content,
            "author": self.author,
            "content_source_url": self.content_source_url,
            "digest": self.digest,
        }
        return {k: v for k, v in content.items() if v is not None and v != ""}


@dataclass
class AMSMpnews(AMSBase):
    """
    mpnews类型的图文消息，跟普通的图文消息一致，唯一的差异是图文内容存储在企业微信。
    多次发送mpnews，会被认为是不同的图文，阅读、点赞的统计会被分开计算。
    """

    msgtype = "mpnews"
    articles: list[Mpnews] = field(default_factory=list)
    """title:标题，不超过128个字节，超过会自动截断（支持id转译）\\
    thumb_media_id:图文消息缩略图的media_id, 可以通过素材管理接口获得。此处thumb_media_id即上传接口返回的media_id\\
    author:图文消息的作者，不超过64个字节\\
    content_source_url:图文消息点击“阅读原文”之后的页面链接\\
    content:图文消息的内容，支持html标签，不超过666 K个字节（支持id转译）\\
    digest:图文消息的描述，不超过512个字节，超过会自动截断（支持id转译）"""

    def __post_init__(self):
        super().__post_init__()
        if not self.articles or not isinstance(self.articles, list):
            raise ValueError("AMSMpnews: articles must be a non-empty list")
        if len(self.articles) > 8:
            raise ValueError("AMSMpnews: articles cannot exceed 8 items")
        self.mpnews: dict = {"articles": []}
        for article in self.articles:
            if not isinstance(article, Mpnews):
                raise ValueError(
                    "AMSMpnews: each article must be an instance of Mpnews"
                )
            article.__post_init__()
            self.mpnews["articles"].append(article.to_dict())


@dataclass
class AMSMarkdown(AMSBase):
    """
    目前仅支持markdown语法的子集
    微工作台（原企业号）不支持展示markdown消息
    """

    msgtype = "markdown"
    content: str = field(default_factory=str)
    """content:markdown内容，最长不超过2048个字节，必须是utf8编码"""

    def __post_init__(self):
        super().__post_init__()
        if not self.content:
            raise ValueError("AMSMarkdown: markdown content must not be empty")
        if len(self.content.encode("utf-8")) > 2048:
            raise ValueError(
                "AMSMarkdown: markdown content must not exceed 2048 bytes"
            )
        self.markdown = dict({"content": self.content})


@dataclass
class MiniprogramItem:
    key: str
    """键，长度10个汉字以内"""
    value: str | None = None
    """值，长度30个汉字以内（支持id转译）"""

    def __post_init__(self):
        if not self.key:
            raise ValueError("MiniprogramItem: key must not be empty")
        if len(self.key.encode("utf-8")) > 10:
            raise ValueError("MiniprogramItem: key must not exceed 10 bytes")
        if self.value and len(self.value.encode("utf-8")) > 30:
            raise ValueError("MiniprogramItem: value must not exceed 30 bytes")

    def to_dict(self) -> dict:
        """
        将小程序内容项转换为字典格式
        :return: 小程序内容项字典
        """
        return {"key": self.key, "value": self.value or ""}


@dataclass
class MiniprogramNotice:
    """
    小程序通知消息
    """

    appid: str
    """小程序appid，必须是与当前应用关联的小程序"""
    title: str
    """消息标题，长度限制4-12个汉字（支持id转译）"""
    page: str | None = None
    """点击消息卡片后的小程序页面，最长1024个字节，仅限本小程序内的页面。该字段不填则消息点击后不跳转。"""
    description: str | None = None
    """消息描述，长度限制4-12个汉字（支持id转译）"""
    emphasis_first_item: bool = False
    """是否放大第一个content_item"""
    content_item: list[MiniprogramItem] | None = None
    """消息内容键值对，最多允许10个item"""

    def __post_init__(self):
        if not self.appid:
            raise ValueError("AMSMiniprogramNotice: appid must not be empty")
        if not self.title:
            raise ValueError("AMSMiniprogramNotice: title must not be empty")
        if len(self.title.encode("utf-8")) > 12 or len(self.title.encode("utf-8")) < 4:
            raise ValueError(
                "AMSMiniprogramNotice: title must not exceed 12 bytes and must be at least 4 bytes"
            )
        if self.description and (
            len(self.description.encode("utf-8")) > 12
            or len(self.description.encode("utf-8")) < 4
        ):
            raise ValueError(
                "AMSMiniprogramNotice: description must not exceed 12 bytes and must be at least 4 bytes"
            )
        if self.content_item:
            if not isinstance(self.content_item, list):
                raise ValueError(
                    "AMSMiniprogramNotice: content_item must be a list"
                )
            if len(self.content_item) > 10:
                raise ValueError(
                    "AMSMiniprogramNotice: content_item cannot exceed 10 items"
                )
            self.content_item = []
            for item in self.content_item:
                if not isinstance(item, MiniprogramItem):
                    raise ValueError(
                        "AMSMiniprogramNotice: each content_item must be an instance of MiniprogramItem"
                    )
                item.__post_init__()

    def to_dict(self) -> dict:
        """
        将小程序通知消息转换为字典格式
        :return: 小程序通知消息字典
        """
        content = {
            "appid": self.appid,
            "title": self.title,
            "page": self.page,
            "description": self.description,
            "emphasis_first_item": self.emphasis_first_item,
        }
        if self.content_item:
            content["content_item"] = [item.to_dict() for item in self.content_item]
        return {k: v for k, v in content.items() if v is not None and v != ""}


@dataclass
class AMSMiniprogramNotice(AMSBase):
    """
    小程序通知消息
    """

    msgtype = "miniprogram_notice"
    miniprogram: MiniprogramNotice = field(default_factory=lambda: MiniprogramNotice(appid="", title=""))
    """appid:小程序appid，必须是与当前应用关联的小程序\\
    page:点击消息卡片后的小程序页面，最长1024个字节，仅限本小程序内的页面。该字段不填则消息点击后不跳转。\\
    title:消息标题，长度限制4-12个汉字（支持id转译）\\
    description:消息描述，长度限制4-12个汉字（支持id转译）\\
    emphasis_first_item:是否放大第一个content_item\\
    content_item:消息内容键值对，最多允许10个item\\
    key:长度10个汉字以内\\
    value:长度30个汉字以内（支持id转译）\\
    key和value两个字段同时为空时，该键值对将被忽略"""

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.miniprogram, MiniprogramNotice):
            raise ValueError(
                "AMSMiniprogramNotice: miniprogram must be an instance of MiniprogramNotice"
            )
        self.miniprogram.__post_init__()
        self.miniprogram_notice = self.miniprogram.to_dict()

from dataclasses import dataclass
import json
from typing import List, Optional
import requests
from workwechatapi.models.template_card import UpdateToCard


@dataclass
class UpdateCardResponse:
    """更新卡片响应信息"""

    errcode: int
    """返回码"""
    errmsg: str
    """对返回码的文本描述内容"""
    invaliduser: Optional[List[str]] = None
    """不合法的userid，不区分大小写，统一转为小写"""


class UpdateCard:
    """
    更新卡片
    """

    access_token: str

    def __init__(self, access_token: str):
        """
        初始化更新卡片类
        :param access_token: 企业微信的access_token
        """
        self.access_token = access_token
        self.url = f"https://qyapi.weixin.qq.com/cgi-bin/message/update_template_card?access_token={access_token}"

    def update(self, update_to: "UpdateToCard") -> "UpdateCardResponse":
        """
        更新卡片
        :param update_to: UpdateToCard对象，包含更新所需的参数
        :return: 响应结果
        """
        assert isinstance(
            update_to, UpdateToCard
        ), "update_to must be an instance of UpdateToCard"

        headers = {"Content-Type": "application/json"}
        response = requests.post(
            self.url,
            headers=headers,
            data=json.dumps(update_to.to_dict(), ensure_ascii=False),
        )

        if response.status_code != 200:
            raise Exception(f"Failed to update card: {response.text}")

        return UpdateCardResponse(**response.json())

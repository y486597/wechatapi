# WorkWechatApi 企业微信 API Python 库

## 项目简介

WorkWechatApi 是一个用于企业微信（WeCom/WeChat Work）API交互的 Python 库，支持消息发送、事件回调解析、模板卡片等多种企业微信功能，适用于企业微信应用开发、消息推送、回调处理等场景。

- 支持企业微信消息发送（文本、图片、语音、视频、文件、卡片等）
- 支持企业微信回调消息解析（文本、图片、语音、视频、地理位置等）
- 支持企业微信模板卡片（通知、图文、按钮交互、投票、多项选择等）

## 快速开始

```python
from workwechatapi import Corp
corp = Corp("")
from workwechatapi.actions.agent import Agent
agent = Agent(agent_name= '',agent_id= 1000001,agent_secret= '',api_token= '',api_EncodingAESkey= '')
corp.add_agent(agent)
```

## 主要模块与调用方法

### 应用消息发送模型
- `AgentMessageSender`, 简称 `AMS`
- `AMSBase`：消息发送基础类，支持 touser/toparty/totag/agentid 等参数
- `AMSText`、`AMSImage`、`AMSVoice`、`AMSVideo`、`AMSFile`、`AMSTextCard`、`AMSNews`、`AMSMpnews`、`AMSMarkdown`、`AMSMiniprogramNotice` 等：对应企业微信各类消息类型
- 所有模型均支持 `to_dict()` 方法，便于序列化为 API 请求体

### 模板卡片模型
- `TemplateCard`：卡片基础类
- `TextNoticeCard`、`NewsNoticeCard`、`ButtonInteractionCard`、`VoteInteractionCard`、`MultipleInteractionCard`：企业微信支持的各类模板卡片
- 支持卡片内容、跳转、按钮、图片、投票等丰富交互

### 回调消息模型
- `WMRBase`：回调消息基础类，支持 XML 加载与字典序列化
- 支持文本、图片、语音、视频、地理位置等消息类型
- 消息类均支持 `load(xml_data)` 加载 XML，`to_dict()`、`to_xml()` 序列化

## 数据模型一览

- 消息发送模型：
  - 文本（AMSText）
  - 图片（AMSImage）
  - 语音（AMSVoice）
  - 视频（AMSVideo）
  - 文件（AMSFile）
  - 文本卡片（AMSTextCard）
  - 图文（AMSNews）
  - mpnews（AMSMpnews）
  - markdown（AMSMarkdown）
  - 小程序通知（AMSMiniprogramNotice）
- 模板卡片模型：
  - 通知卡片（TextNoticeCard）
  - 图文卡片（NewsNoticeCard）
  - 按钮交互卡片（ButtonInteractionCard）
  - 投票卡片（VoteInteractionCard）
  - 多项选择卡片（MultipleInteractionCard）
- 回调消息模型：
  - 文本（WMRText）
  - 图片（WMRImage）
  - 语音（WMRVoice）
  - 视频（WMRVideo）
  - 地理位置（WMRLocation）

## 典型用例

### 发送企业微信文本消息
```python
from workwechatapi import AMSText
msg = AMSText(touser="@all", agentid=1000002, content="Hello WeChat!")
print(msg.to_dict())
```

### 解析企业微信回调事件
```python
from workwechatapi import CreateDepartmentEvent
xml_data = "<xml>...</xml>"
event = CreateDepartmentEvent()
event.load(xml_data)
print(event.to_dict())
```

### 构建企业微信模板卡片
```python
from workwechatapi import TextNoticeCard
card = TextNoticeCard()
card.main_title = ...
card.card_action = ...
print(card.to_dict())
```

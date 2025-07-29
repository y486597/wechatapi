import json
from workwechatapi.actions.agent import Agent


class Corp:
    corp_id: str
    """企业ID"""
    agents: dict[str, Agent] = {}
    """企业应用列表，键为应用ID，值为应用对象"""

    def __init__(self, corp_id: str):
        self.corp_id = corp_id

    def add_agent(self, agent: Agent):
        """
        添加企业应用到企业
        :param agent: Agent对象
        """
        agent.corp_id = self.corp_id
        self.agents[agent.agent_name] = agent

    def get_agent(self, agent_name: str) -> Agent:
        """
        获取指定名称的企业应用
        :param agent_name: 企业应用名称
        :return: Agent对象
        """
        if agent_name not in self.agents:
            raise ValueError(
                f"Agent with name {agent_name} does not exist in this Corp."
            )
        return self.agents.get(agent_name)  # type: ignore

    def remove_agent(self, agent_name: str):
        """
        从企业中移除指定ID的企业应用
        :param agent_name: 企业应用名称
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
        else:
            raise ValueError(
                f"Agent with name {agent_name} does not exist in this Corp."
            )

    def to_dict(self) -> dict:
        """
        将Corp对象转换为字典
        :return: 字典表示的Corp对象
        """
        return {
            "corp_id": self.corp_id,
            "agents": {
                agent_name: agent.to_dict() for agent_name, agent in self.agents.items()
            },
        }

    def save(self, location: str | None = None):
        """
        保存Corp对象到数据库或其他存储
        这里可以实现具体的保存逻辑
        """
        save_data = {
            "corp_id": self.corp_id,
            "agents": [agent.to_dict() for agent in self.agents.values()],
        }
        if location:
            with open(location, "w") as f:
                json.dump(save_data, f)
        else:
            return save_data

    @staticmethod
    def save_example(location: str | None = None):
        """
        保存Corp对象的示例数据到指定位置
        :param location: 保存位置，如果为None则返回字典
        """
        example_data = {
            "corp_id": "example_corp_id",
            "agents": [
                Agent.save_example(),
            ],
        }
        if location:
            with open(location, "w") as f:
                json.dump(example_data, f)
        else:
            return example_data

    @staticmethod
    def load(data: dict | str):
        """
        从字典或存储地址加载Corp对象
        :param data: 字典或存储地址
        """
        if isinstance(data, str):
            with open(data, "r") as f:
                data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary or a valid file path.")
        if "corp_id" not in data:
            raise ValueError("Data must contain 'corp_id'.")
        corp = Corp(corp_id=data["corp_id"])
        for en, agent in enumerate(data.get("agents", [])):
            if isinstance(agent, dict):
                try:
                    corp.add_agent(Agent.load(agent))
                except Exception as e:
                    raise ValueError(f"Failed to load agent {en}: {e}")
            else:
                raise ValueError(
                    f"Each agent must be a dictionary like {Agent.save_example()}."
                )
        return corp
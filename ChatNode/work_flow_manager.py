from typing import Dict, Any
import os
from bot import TelegramBot
from .node_manager import NodeManager


class WorkflowManager(object):
    instance = None

    @classmethod
    def initialize(
            cls,
            bot: TelegramBot,
            base_directory: str,
            workflow_names: Dict[str, str],
    ) -> Any:
        workflow_chat_nodes: Dict[str, NodeManager] = {}
        for name, path in workflow_names.items():
            path: str = os.path.join(base_directory, path)
            chat_nodes: NodeManager = NodeManager(name, path, bot, cls)
            workflow_chat_nodes[name] = chat_nodes

        cls.instance = cls(
            bot,
            workflow_chat_nodes
        )

        return cls.instance

    def __init__(
            self,
            bot: TelegramBot,
            workflow_chat_nodes: Dict[str, NodeManager]):
        self.bot: TelegramBot = bot
        self.workflows = workflow_chat_nodes
        self.active_workflows = {}

    def get_active_workflow(
            self,
            chat_id) -> NodeManager:
        return self.active_workflows.get(chat_id)

    def wf(self,
           wf_name,
           chat_id,
           username=None,
           root_wf=None):

        node_manager: NodeManager = self.workflows.get(wf_name)
        self.active_workflows[chat_id] = node_manager
        node_manager.username = username
        node_manager.chat_id = chat_id
        if root_wf is not None:
            node_manager.pwf = root_wf
        return node_manager

from typing import Dict, Any
import glob
import sys
import os
import imp
from bot import TelegramBot
from .node import Node


class NodeManager(object):
    def __init__(
            self,
            name: str,
            path: str,
            bot: TelegramBot,
            wf_mgr: object = None,
            chat_id: int = None,
            username: str = None,
            pwf=None):
        """
        :param name:
            name of manager
        :param path:
            path to all nodes
        :param bot:
            Telegram Bot
        :param wf_mgr:
        :param chat_id:
        :param username:
        :param pwf:
        """
        self.name = name
        self.wf_mgr = wf_mgr
        self.nodes: Dict[str, Node] = self.load(path)
        self.path = path
        self.pwf: NodeManager = pwf
        self.bot: TelegramBot = bot
        self.chat_id: int = chat_id
        self.username: str = username
        self.previous_chat_node: Node or None = None
        self.current_chat_node: Node = self.start_node()
        self.state: Dict[Any, Any] = {}

    def load(self, path) -> Dict[str, Node]:
        chat_nodes: Dict[str, Node] = {}
        for module in glob.glob(path + '/*.py'):
            sys.path.append(module)
            fname, fext = os.path.splitext(os.path.basename(module))
            dynamod = imp.load_source(fname, module)
            init_function = getattr(dynamod, fname)
            o = init_function()
            chat_nodes[o.name] = o

        return chat_nodes

    def start_node(self):
        return self.nodes.get("start")

    def find(self, node_name):
        return self.nodes.get(node_name)

    def reset(self):
        self.current_chat_node = self.start_node()

    def input_to_node(self, update):
        action = self.current_chat_node.input_to_node(self, update)
        if action.flow:
            return self.output_to_user(update)

    def output_to_user(self, update):
        action = self.current_chat_node.output_to_user(self, update)

        if action.end:
            return 0

        next_chat_node: Node = self.find(action.next_node)

        self.previous_chat_node = self.current_chat_node
        self.current_chat_node = next_chat_node
        return self.input_to_node(update)


class NodeAction(object):
    def __init__(self, next_node="", end: bool = False, flow=False):
        self.next_node = next_node
        self.end = end
        self.flow = flow


class Node(object):
    def __init__(self, name):
        self.name = name

    def input_to_node(self, node_manager, update) -> NodeAction:
        ...

    def output_to_user(self, node_manager, update) -> NodeAction:
        ...

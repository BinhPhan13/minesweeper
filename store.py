from eqn import EQN

class _Node:
    def __init__(self, eqn:EQN):
        self.__eqn = eqn
        self.__prev:'_Node' = None
        self.__next:'_Node' = None

    @property
    def prev(self):
        return self.__prev

    @prev.setter
    def prev(self, node:'_Node'):
        assert node is None or isinstance(node, (_Node, None))
        self.__prev = node

    @property
    def next(self):
        return self.__next

    @next.setter
    def next(self, node:'_Node'):
        assert node is None or isinstance(node, (_Node, None))
        self.__next = node

    @property
    def eqn(self):
        return self.__eqn

class Store:
    def __init__(self):
        self.__nodes:list[_Node|None] = []
        # doubly linked todo list
        self.__head:_Node = None
        self.__tail:_Node = None

    def get_overlap(self, eqn:EQN):
        return [i for i, node in enumerate(self.__nodes)
            if node and eqn.munge(node.eqn, False)
        ]

    def add(self, eqn:EQN):
        for node in self.__nodes:
            if node and node.eqn == eqn: return

        new_node = _Node(eqn)
        self.__nodes.append(new_node)
        self.__add_todo(new_node)

    def __add_todo(self, node:_Node):
        node.prev = self.__tail
        if node.prev:
            node.prev.next = node
        else: self.__head = node
        self.__tail = node

    def remove(self, index:int):
        assert index > -1
        self.__remove_todo(self.__nodes[index])
        self.__nodes[index] = None

    def __remove_todo(self, node:_Node):
        if node.prev:
            node.prev.next = node.next
        elif node is self.__head:
            self.__head = node.next

        if node.next:
            node.next.prev = node.prev
        elif node is self.__tail:
            self.__tail = node.prev

        node.prev = None
        node.next = None

    def clean(self):
        self.__nodes = [node for node in self.__nodes if node]

    def get_eqn(self, index:int):
        assert index > -1
        return self.__nodes[index].eqn

    def fetch(self):
        ret = self.__head
        if not ret: return None
        self.__remove_todo(ret)
        return ret.eqn

    def clear(self):
        self.__nodes.clear()
        self.__head = None
        self.__tail = None
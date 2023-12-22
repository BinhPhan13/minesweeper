from eqn import EQN
import random

class _Node:
    def __init__(self, eqn:EQN):
        self._eqn = eqn
        self._prev:'_Node' = None
        self._next:'_Node' = None

    @property
    def prev(self):
        return self._prev

    @prev.setter
    def prev(self, node:'_Node'):
        assert node is None or isinstance(node, _Node)
        self._prev = node

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, node:'_Node'):
        assert node is None or isinstance(node, _Node)
        self._next = node

    @property
    def eqn(self):
        return self._eqn

class Store:
    def __init__(self):
        self._nodes:list[_Node|None] = []
        # doubly linked todo list
        self._head:_Node = None
        self._tail:_Node = None

    def get_overlap(self, eqn:EQN):
        return [i for i, node in enumerate(self._nodes)
            if node and eqn.munge(node.eqn, False)
        ]

    def add(self, eqn:EQN):
        for node in self._nodes:
            if node and node.eqn == eqn: return

        new_node = _Node(eqn)
        self._nodes.append(new_node)
        self._add_todo(new_node)

    def _add_todo(self, node:_Node):
        node.prev = self._tail
        if node.prev:
            node.prev.next = node
        else: self._head = node
        self._tail = node

    def remove(self, index:int):
        assert index > -1
        self._remove_todo(self._nodes[index])
        self._nodes[index] = None

    def _remove_todo(self, node:_Node):
        if node.prev:
            node.prev.next = node.next
        elif node is self._head:
            self._head = node.next

        if node.next:
            node.next.prev = node.prev
        elif node is self._tail:
            self._tail = node.prev

        node.prev = None
        node.next = None

    def clean(self):
        self._nodes = [node for node in self._nodes if node]

    def get_eqn(self, index:int):
        assert index > -1
        return self._nodes[index].eqn

    def get_all(self):
        return [node.eqn for node in self._nodes]

    def pick(self):
        if not self._nodes: return None
        return random.choice(self._nodes).eqn

    def fetch(self):
        ret = self._head
        if not ret: return None
        self._remove_todo(ret)
        return ret.eqn

    def clear(self):
        self._nodes.clear()
        self._head = None
        self._tail = None
import sys, shutil
from typing import Generic, TypeVar

T = TypeVar('T')

class DoublyLinkedList(Generic[T]):
    class Node(Generic[T]):
        def __init__(self, parent, val : T, prev, next):
            super().__init__()
            self.val : T = val
            self.prev : DoublyLinkedList.Node[T]  = prev
            self.next : DoublyLinkedList.Node[T]  = next

    def __init__(self):
        super().__init__()
        self.begin : DoublyLinkedList.Node[T] = None
        self.end : DoublyLinkedList.Node[T] = None

    def __repr__(self) -> str:
        res = '['
        current = self.begin
        if current != None:
            res += current.val.__repr__()
            current = current.next
            while current != None:
                res += ', ' + current.val.__repr__()
                current = current.next
        return res + ']'

    def is_empty(self):
        return self.begin == None

    def add_begin(self, val : T) -> Node[T]:
        new = self.Node(self, val, None, self.begin)
        if self.begin != None:
            self.begin.prev = new
        self.begin = new
        if self.end == None:
            self.end = new
        return new

    def add_end(self, val : T) -> Node[T]:
        new = self.Node(self, val, self.end, None)
        if self.end != None:
            self.end.next = new
        self.end = new
        if self.begin == None:
            self.begin = new
        return new

    def remove(self, node : Node[T]):
        if node.next != None:
            node.next.prev = node.prev
        else:
            self.end = node.prev

        if node.prev != None:
            node.prev.next = node.next
        else:
            self.begin = node.next

    def pop_begin(self) -> Node[T]:
        begin = self.begin
        if begin != None:
            self.remove(begin)
        return begin

    def pop_end(self) -> Node[T]:
        end = self.end
        if end != None:
            self.remove(end)
        return end

    def add_list_before(self, list, node : Node[T]):
        if list.is_empty():
            return None
        prev = node.prev
        node.prev = list.end
        list.end.next = node
        if prev == None:
            self.begin = list.begin
        else:
            prev.next = list.begin
            list.begin.prev = prev
        list.begin = None
        list.end = None

    def add_list_after(self, list, node : Node[T]):
        if list.is_empty():
            return None
        next = node.next
        node.next = list.begin
        list.begin.prev = node
        if next == None:
            self.end = list.end
        else:
            next.prev = list.end
            list.end.next = next
        list.begin = None
        list.end = None

    def extract_list(self, f : Node[T], t : Node[T]):
        l = f.prev
        r = t.next
        if l == None:
            self.begin = r
        else:
            l.next = r
        if r == None:
            self.end = l
        else:
            r.prev = l

        res = DoublyLinkedList()
        res.begin = f
        res.end = t
        f.prev = None
        t.next = None
        return res

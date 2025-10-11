import heapq
import os
from collections import Counter
from typing import Dict, Tuple


class Node:
    def __init__(self, freq: int, symbol: bytes = None, left: 'Node' = None, right: 'Node' = None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right

    def __lt__(self, other: 'Node'):
        return self.freq < other.freq


def build_huffman_tree(data: bytes) -> Node:
    freq = Counter(data)
    heap = [Node(f, s) for s, f in freq.items()]
    heapq.heapify(heap)
    if len(heap) == 1:
        only = heap[0]
        return Node(only.freq, None, left=only)
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, Node(a.freq + b.freq, None, left=a, right=b))
    return heap[0]


def build_codes(root: Node) -> Dict[int, str]:
    codes: Dict[int, str] = {}

    def _walk(node: Node, prefix: str):
        if node is None:
            return
        if node.symbol is not None:
            # node.symbol comes from iterating bytes, so it's an int
            codes[int(node.symbol)] = prefix or '0'
            return
        _walk(node.left, prefix + '0')
        _walk(node.right, prefix + '1')

    _walk(root, '')
    return codes

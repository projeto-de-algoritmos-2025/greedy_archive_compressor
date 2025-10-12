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
            codes[int(node.symbol)] = prefix or '0'
            return
        _walk(node.left, prefix + '0')
        _walk(node.right, prefix + '1')

    _walk(root, '')
    return codes


def compress_bytes(data: bytes) -> Tuple[bytes, Dict[int, str]]:
    if not data:
        return b'', {}
    root = build_huffman_tree(data)
    codes = build_codes(root)
    # codes is already int -> code
    bitstr = ''.join(codes[b] for b in data)
    extra = (8 - len(bitstr) % 8) % 8
    bitstr += '0' * extra
    out = bytearray()
    out.append(extra)
    for i in range(0, len(bitstr), 8):
        out.append(int(bitstr[i:i+8], 2))
    # naive header: number of symbols (1 byte if <=255 else 0) then pairs (sym, code_len, code bits as bytes)
    # For simplicity, we will prepend a simple header: symbol count (2 bytes), then for each: symbol (1 byte), code length (1 byte), code in ASCII ('0'/'1') terminated by '\n'
    header = bytearray()
    header += len(codes).to_bytes(2, 'big')
    for sym_int, code in codes.items():
        header += bytes([sym_int])
        header += bytes([len(code)])
        header += code.encode('ascii')

    return bytes(header) + bytes(out), codes


def decompress_bytes(blob: bytes) -> bytes:
    if not blob:
        return b''
    # read header
    if len(blob) < 2:
        raise ValueError('Invalid blob')
    sym_count = int.from_bytes(blob[0:2], 'big')
    idx = 2
    codes = {}
    for _ in range(sym_count):
        sym = blob[idx]
        idx += 1
        l = blob[idx]
        idx += 1
        code = blob[idx:idx+l].decode('ascii')
        idx += l
        codes[code] = sym
    if idx >= len(blob):
        return b''
    extra = blob[idx]
    idx += 1
    bitstr = ''
    for b in blob[idx:]:
        bitstr += f'{b:08b}'
    if extra:
        bitstr = bitstr[:-extra]
    # iterate bits
    out = bytearray()
    cur = ''
    for bit in bitstr:
        cur += bit
        if cur in codes:
            out.append(codes[cur])
            cur = ''
    return bytes(out)


def compress_file(in_path: str, out_path: str) -> None:
    with open(in_path, 'rb') as f:
        data = f.read()
    blob, _ = compress_bytes(data)
    with open(out_path, 'wb') as f:
        f.write(blob)


def decompress_file(in_path: str, out_path: str) -> None:
    with open(in_path, 'rb') as f:
        blob = f.read()
    data = decompress_bytes(blob)
    with open(out_path, 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('Usage: python huffman.py <in> <out>')
    else:
        compress_file(sys.argv[1], sys.argv[2])
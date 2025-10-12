import os
from src import huffman


def test_roundtrip(tmp_path):
    txt = b'This is an example for Huffman encoding. Huffman! Huffman!'
    in_file = tmp_path / 'in.bin'
    comp = tmp_path / 'out.huff'
    dec = tmp_path / 'out.dec'
    in_file.write_bytes(txt)
    huffman.compress_file(str(in_file), str(comp))
    huffman.decompress_file(str(comp), str(dec))
    assert dec.read_bytes() == txt

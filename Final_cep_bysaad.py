import heapq
import json
import os

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq

def build_frequency_table(text):
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    return freq

def build_huffman_tree(freq_table):
    if not freq_table:
        return None
    heap = [Node(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    return heap[0]

def generate_codes(node, code="", codes=None):
    if codes is None:
        codes = {}
    if node is None:
        return codes
    if node.char is not None:
        if code == "":
            code = "0"
        codes[node.char] = code
        return codes
    generate_codes(node.left, code + "0", codes)
    generate_codes(node.right, code + "1", codes)
    return codes

def encode_text(text, codes):
    return "".join(codes[ch] for ch in text)

def pad_encoded(encoded):
    extra = (8 - len(encoded) % 8) % 8
    padded_info = f"{extra:08b}"
    encoded += "0" * extra
    return padded_info + encoded, extra

def write_binary_file(encoded_str, output_file):
    b = bytearray()
    for i in range(0, len(encoded_str), 8):
        b.append(int(encoded_str[i:i+8], 2))
    with open(output_file, "wb") as f:
        f.write(b)

def remove_padding(encoded_data):
    padded_info = encoded_data[:8]
    extra_padding = int(padded_info, 2)
    encoded_data = encoded_data[8:]
    if extra_padding > 0:
        encoded_data = encoded_data[:-extra_padding]
    return encoded_data

def decode_text(encoded_data, codes):
    reverse_codes = {v: k for k, v in codes.items()}
    current = ""
    decoded = []
    for bit in encoded_data:
        current += bit
        if current in reverse_codes:
            decoded.append(reverse_codes[current])
            current = ""
    return "".join(decoded)

def read_binary_as_bits(input_file):
    with open(input_file, "rb") as f:
        byte_data = f.read()
    return "".join(f"{byte:08b}" for byte in byte_data)

def compress(input_file):
    print("\n--- COMPRESSION ---")
    if not os.path.exists(input_file):
        print("File not found.")
        return
    with open(input_file, "r") as f:
        text = f.read()
    if not text:
        print("File empty.")
        return
    freq = build_frequency_table(text)
    root = build_huffman_tree(freq)
    codes = generate_codes(root)
    encoded = encode_text(text, codes)
    padded_encoded, _ = pad_encoded(encoded)
    out_name = input("Output .bin file name (default output.bin): ").strip() or "output.bin"
    write_binary_file(padded_encoded, out_name)
    with open(out_name + "_codes.json", "w") as f:
        json.dump(codes, f, indent=2)
    print("Done.")

def decompress(encoded_file, codes_file):
    print("\n--- DECOMPRESSION ---")
    if not (os.path.exists(encoded_file) and os.path.exists(codes_file)):
        print("Missing file.")
        return
    bits = read_binary_as_bits(encoded_file)
    bits = remove_padding(bits)
    with open(codes_file, "r") as f:
        codes = json.load(f)
    text = decode_text(bits, codes)
    out_name = input("Output .txt file name (default decompressed.txt): ").strip() or "decompressed.txt"
    with open(out_name, "w") as f:
        f.write(text)
    print("Done.")

# ---------------- Streamlit (simple) ----------------
try:
    import streamlit as st

    def _bits_to_bytes(bitstring):
        return bytes(int(bitstring[i:i+8], 2) for i in range(0, len(bitstring), 8))
    def _bytes_to_bits(data):
        return "".join(f"{b:08b}" for b in data)

    def _compress_text(text):
        if not text:
            raise ValueError("Empty text.")
        freq = build_frequency_table(text)
        root = build_huffman_tree(freq)
        codes = generate_codes(root)
        encoded = encode_text(text, codes)
        padded, _ = pad_encoded(encoded)
        return _bits_to_bytes(padded), codes

    def _decompress_bytes(bin_bytes, codes):
        bits = _bytes_to_bits(bin_bytes)
        bits = remove_padding(bits)
        return decode_text(bits, codes)

    def _streamlit_app():
        st.title("Huffman Compressor")
        mode = st.radio("Mode", ["Compress", "Decompress"])

        if mode == "Compress":
            up = st.file_uploader("Upload text file", type=["txt"])
            if up and st.button("Compress"):
                try:
                    text = up.read().decode("utf-8", errors="ignore")
                    bin_bytes, codes = _compress_text(text)
                    st.success("Compressed.")
                    st.download_button("Download .bin", bin_bytes, file_name="output.bin")
                    st.download_button("Download codes.json",
                                       json.dumps(codes, indent=2),
                                       file_name="output.bin_codes.json")
                except Exception as e:
                    st.error(e)

        else:
            bin_up = st.file_uploader("Upload .bin", type=["bin"])
            codes_up = st.file_uploader("Upload codes.json", type=["json"])
            if bin_up and codes_up and st.button("Decompress"):
                try:
                    codes = json.loads(codes_up.read().decode("utf-8", errors="ignore"))
                    text = _decompress_bytes(bin_up.read(), codes)
                    st.success("Decompressed.")
                    st.text_area("Text preview", text[:5000], height=200)
                    st.download_button("Download decompressed.txt", text, file_name="decompressed.txt")
                except Exception as e:
                    st.error(e)

    if __name__ == "__main__":
        _streamlit_app()
except Exception:
    pass

# Uncomment to use simple CLI instead of Streamlit
# if __name__ == "__main__":
#     print("1 = Compress, 2 = Decompress")
#     c = input("Choice: ").strip()
#     if c == "1":
#         fname = input("File to compress (default sample.txt): ").strip() or "sample.txt"
#         compress(fname)
#     elif c == "2":
#         ef = input("Encoded .bin file: ").strip()
#         cf = input("Codes .json file: ").strip()
#         decompress(ef, cf)
#     else:
#         print("Invalid.")

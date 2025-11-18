# import streamlit as st
# import heapq
# from collections import Counter
# import json
# import zipfile
# import io

# # ----------------------------
# # Huffman Classes & Functions
# # ----------------------------

# class Node:
#     """A node in the Huffman tree.

#     Attributes:
#         char (str or None): The character for leaf nodes, None for internal nodes.
#         freq (int): Frequency of the character or sum of child frequencies for internal nodes.
#         left (Node): Left child node.
#         right (Node): Right child node.
#     """
#     def __init__(self, char, freq):
#         self.char = char  # Character (None for internal nodes)
#         self.freq = freq  # Frequency
#         self.left = None
#         self.right = None

#     def __lt__(self, other):
#         """Comparison operator for priority queue (heapq), based on frequency."""
#         return self.freq < other.freq

# def build_huffman_tree(freq_table):
#     """Builds a Huffman tree from a frequency table.

#     Args:
#         freq_table (dict): Dictionary mapping characters to their frequencies.

#     Returns:
#         Node: The root node of the Huffman tree.
#     """
#     heap = [Node(char, freq) for char, freq in freq_table.items()]
#     heapq.heapify(heap)

#     while len(heap) > 1:
#         left = heapq.heappop(heap)
#         right = heapq.heappop(heap)
        
#         merged = Node(None, left.freq + right.freq)
#         merged.left = left
#         merged.right = right
        
#         heapq.heappush(heap, merged)
        
#     return heap[0] if heap else None

# def generate_codes(node, current_code="", codes=None):
#     """Generates Huffman codes for each character by traversing the tree.

#     Args:
#         node (Node): The current node in the Huffman tree.
#         current_code (str): The binary code accumulated so far.
#         codes (dict): Dictionary to store character-to-code mapping.

#     Returns:
#         dict: Mapping of characters to their Huffman binary codes.
#     """
#     if codes is None:
#         codes = {}
    
#     if node is None:
#         return codes
        
#     if node.char is not None:
#         codes[node.char] = current_code
        
#     generate_codes(node.left, current_code + "0", codes)
#     generate_codes(node.right, current_code + "1", codes)
#     return codes

# def encode_text(text, codes):
#     """Encodes a string of text using Huffman codes.

#     Args:
#         text (str): Input text to encode.
#         codes (dict): Character-to-code mapping.

#     Returns:
#         str: The encoded binary string.
#     """
#     return "".join(codes[char] for char in text)

# def pad_encoded_data(encoded_data):
#     """Pads the encoded data so that its length is a multiple of 8 bits.
    
#     The first 8 bits store the amount of padding added.

#     Args:
#         encoded_data (str): Huffman encoded binary string.

#     Returns:
#         str: Padded encoded string with padding info.
#     """
#     extra_padding = (8 - len(encoded_data) % 8) % 8
#     padded_info = "{0:08b}".format(extra_padding)
#     encoded_data += "0" * extra_padding
#     return padded_info + encoded_data

# def huffman_decoding(encoded_data, codes):
#     """Decodes a Huffman encoded string back into the original text.

#     Args:
#         encoded_data (str): Padded Huffman encoded binary string.
#         codes (dict): Character-to-code mapping used for encoding.

#     Returns:
#         str: The original decoded text.
#     """
#     padded_info = encoded_data[:8]
#     extra_padding = int(padded_info, 2)
#     encoded_data = encoded_data[8:]
    
#     if extra_padding > 0:
#         encoded_data = encoded_data[:-extra_padding]

#     reverse_codes = {v: k for k, v in codes.items()}

#     current_code = ""
#     decoded_text = ""
#     for bit in encoded_data:
#         current_code += bit
#         if current_code in reverse_codes:
#             decoded_text += reverse_codes[current_code]
#             current_code = ""
            
#     return decoded_text

# # ----------------------------
# # Streamlit App UI and Logic
# # ----------------------------

# st.set_page_config(layout="centered", page_title="Huffman Compressor")
# st.title("📦 Huffman File Compressor / Decompressor")

# if 'mode' not in st.session_state:
#     st.session_state.mode = 'none'

# col1, col2 = st.columns([1, 1])

# with col1:
#     if st.button("🟢 Compress File", use_container_width=True):
#         st.session_state.mode = 'compress'
# with col2:
#     if st.button("🔵 Decompress File", use_container_width=True):
#         st.session_state.mode = 'decompress'

# st.markdown("---")

# # ----------------------------
# # Compression Flow Logic
# # ----------------------------
# if st.session_state.mode == 'compress':
#     st.subheader("Compress a Text File")
    
#     uploaded_file = st.file_uploader("Upload a text file (.txt)", type=["txt"], key="compress_uploader")
    
#     if uploaded_file:
#         try:
#             text = uploaded_file.read().decode("utf-8")
#             st.text_area("Original Text Preview", text[:1000] + ("..." if len(text) > 1000 else ""), height=100)

#             freq_table = Counter(text)
#             root = build_huffman_tree(freq_table)
            
#             if not root:
#                 st.warning("The file is empty or contains no processable data.")
#             elif len(freq_table) == 1:
#                 codes = {list(freq_table.keys())[0]: "0"}
#                 encoded_data = encode_text(text, codes)
#             else:
#                 codes = generate_codes(root)
#                 encoded_data = encode_text(text, codes)

#             padded_encoded_data = pad_encoded_data(encoded_data)

#             original_bits = len(text) * 8
#             compressed_bits = len(padded_encoded_data)
#             compression_ratio = (1 - compressed_bits / original_bits) * 100
            
#             st.info(f"Original Size: **{original_bits} bits** | Compressed Size: **{compressed_bits} bits**")
#             st.success(f"Compression Ratio: **{compression_ratio:.2f}%**")
            
#             zip_buffer = io.BytesIO()
#             with zipfile.ZipFile(zip_buffer, "w") as zf:
#                 zf.writestr("compressed.bin", padded_encoded_data)
#                 zf.writestr("codes.json", json.dumps(codes))
#             zip_buffer.seek(0)

#             st.download_button(
#                 "⬇️ Download Compressed File (ZIP)",
#                 zip_buffer,
#                 file_name=f"{uploaded_file.name.replace('.txt', '')}_huffman.zip",
#                 use_container_width=True
#             )

#         except Exception as e:
#             st.error(f"An error occurred during compression: {e}")

# # ----------------------------
# # Decompression Flow Logic
# # ----------------------------
# elif st.session_state.mode == 'decompress':
#     st.subheader("Decompress a ZIP File")
    
#     uploaded_file = st.file_uploader("Upload a compressed ZIP file (must contain compressed.bin and codes.json)", type=["zip"], key="decompress_uploader")
    
#     if uploaded_file:
#         try:
#             st.spinner("Decompressing...")
#             zip_bytes = io.BytesIO(uploaded_file.read())
            
#             compressed_data = None
#             codes = None

#             with zipfile.ZipFile(zip_bytes, "r") as zf:
#                 required_files = {"compressed.bin", "codes.json"}
#                 if not required_files.issubset(set(zf.namelist())):
#                     st.error("Error: The ZIP file must contain 'compressed.bin' and 'codes.json'.")

#                 compressed_data = zf.read("compressed.bin").decode("utf-8")
#                 codes = json.loads(zf.read("codes.json").decode("utf-8"))

#             decoded_text = huffman_decoding(compressed_data, codes)
            
#             st.text_area("Decompressed Text", decoded_text, height=200)

#             st.download_button(
#                 "⬇️ Download Decompressed Text",
#                 decoded_text,
#                 file_name="decompressed_output.txt",
#                 use_container_width=True
#             )
#             st.success("✅ Decompression successful! File is ready for download.")

#         except Exception as e:
#             st.error(f"An error occurred during decompression. Is this a valid Huffman ZIP file? Details: {e}")

# else:
#     st.info("Select **Compress File** to shrink a text file, or **Decompress File** to restore a compressed ZIP.")














# import heapq
# import json
# import os
# import io
# import zipfile

# class Node:
#     def __init__(self, char, freq):
#         self.char = char
#         self.freq = freq
#         self.left = None
#         self.right = None
#     def __lt__(self, other):
#         return self.freq < other.freq

# class HuffmanCoding:
#     def build_frequency_table(self, text):
#         freq = {}
#         for char in text:
#             freq[char] = freq.get(char, 0) + 1
#         return freq

#     def build_huffman_tree(self, freq_table):
#         if not freq_table:
#             return None
#         heap = [Node(char, freq) for char, freq in freq_table.items()]
#         heapq.heapify(heap)
#         while len(heap) > 1:
#             left = heapq.heappop(heap)
#             right = heapq.heappop(heap)
#             merged = Node(None, left.freq + right.freq)
#             merged.left = left
#             merged.right = right
#             heapq.heappush(heap, merged)
#         return heap[0]

#     def generate_codes(self, node, code="", codes=None):
#         if codes is None:
#             codes = {}
#         if node is None:
#             return codes
#         if node.char is not None:
#             if code == "":
#                 code = "0"
#             codes[node.char] = code
#             return codes
#         self.generate_codes(node.left, code + "0", codes)
#         self.generate_codes(node.right, code + "1", codes)
#         return codes

#     def encode_text(self, text, codes):
#         return "".join(codes[ch] for ch in text)

#     def pad_encoded(self, encoded):
#         extra = (8 - len(encoded) % 8) % 8
#         padded_info = f"{extra:08b}"
#         encoded += "0" * extra
#         return padded_info + encoded, extra

#     def remove_padding(self, encoded_data):
#         padded_info = encoded_data[:8]
#         extra_padding = int(padded_info, 2)
#         encoded_data = encoded_data[8:]
#         if extra_padding > 0:
#             encoded_data = encoded_data[:-extra_padding]
#         return encoded_data

#     def decode_text(self, encoded_data, codes):
#         reverse_codes = {v: k for k, v in codes.items()}
#         current = ""
#         decoded = []
#         for bit in encoded_data:
#             current += bit
#             if current in reverse_codes:
#                 decoded.append(reverse_codes[current])
#                 current = ""
#         return "".join(decoded)

# class FileManager:
#     def __init__(self, huffman: HuffmanCoding):
#         self.huffman = huffman

#     def read_text(self, path):
#         with open(path, "r") as f:
#             return f.read()

#     def write_text(self, path, text):
#         with open(path, "w") as f:
#             f.write(text)

#     def write_binary_file(self, encoded_str, output_file):
#         b = bytearray()
#         for i in range(0, len(encoded_str), 8):
#             b.append(int(encoded_str[i:i+8], 2))
#         with open(output_file, "wb") as f:
#             f.write(b)

#     def read_binary_as_bits(self, input_file):
#         with open(input_file, "rb") as f:
#             byte_data = f.read()
#         return "".join(f"{byte:08b}" for byte in byte_data)

#     def write_json(self, path, obj):
#         with open(path, "w") as f:
#             json.dump(obj, f, indent=2)

#     def read_json(self, path):
#         with open(path, "r") as f:
#             return json.load(f)

#     def compress(self, input_file):
#         print("\n--- COMPRESSION ---")
#         if not os.path.exists(input_file):
#             print("File not found.")
#             return
#         text = self.read_text(input_file)
#         if not text:
#             print("File empty.")
#             return
#         freq = self.huffman.build_frequency_table(text)
#         root = self.huffman.build_huffman_tree(freq)
#         codes = self.huffman.generate_codes(root)
#         encoded = self.huffman.encode_text(text, codes)
#         padded_encoded, _ = self.huffman.pad_encoded(encoded)
#         out_name = input("Output .bin file name (default output.bin): ").strip() or "output.bin"
#         self.write_binary_file(padded_encoded, out_name)
#         self.write_json(out_name + "_codes.json", codes)
#         print("Done.")

#     def decompress(self, encoded_file, codes_file):
#         print("\n--- DECOMPRESSION ---")
#         if not (os.path.exists(encoded_file) and os.path.exists(codes_file)):
#             print("Missing file.")
#             return
#         bits = self.read_binary_as_bits(encoded_file)
#         bits = self.huffman.remove_padding(bits)
#         codes = self.read_json(codes_file)
#         text = self.huffman.decode_text(bits, codes)
#         out_name = input("Output .txt file name (default decompressed.txt): ").strip() or "decompressed.txt"
#         self.write_text(out_name, text)
#         print("Done.")

# hc = HuffmanCoding()
# fm = FileManager(hc)

# try:
#     import streamlit as st

#     def _bits_to_bytes(bitstring):
#         return bytes(int(bitstring[i:i+8], 2) for i in range(0, len(bitstring), 8))
#     def _bytes_to_bits(data):
#         return "".join(f"{b:08b}" for b in data)

#     def _compress_text(text):
#         freq = hc.build_frequency_table(text)
#         root = hc.build_huffman_tree(freq)
#         codes = hc.generate_codes(root)
#         encoded = hc.encode_text(text, codes)
#         padded, _ = hc.pad_encoded(encoded)
#         return _bits_to_bytes(padded), codes

#     def _decompress_bytes(bin_bytes, codes):
#         bits = _bytes_to_bits(bin_bytes)
#         bits = hc.remove_padding(bits)
#         return hc.decode_text(bits, codes)

#     def _streamlit_app():
#         st.title("Huffman Compressor")
#         mode = st.radio("Mode", ["Compress", "Decompress"])

#         if mode == "Compress":
#             up = st.file_uploader("Upload text file", type=["txt"])
#             if up and st.button("Compress"):
#                 try:
#                     raw = up.read()
#                     text = raw.decode("utf-8", errors="ignore")
#                     bin_bytes, codes = _compress_text(text)
#                     orig_size = len(raw)
#                     comp_size = len(bin_bytes)
#                     ratio = (comp_size / orig_size) if orig_size else 0.0
#                     reduction = (1 - ratio) * 100 if orig_size else 0.0
#                     base = up.name.rsplit(".", 1)[0] if "." in up.name else up.name
#                     zip_buf = io.BytesIO()
#                     with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
#                         zf.writestr(f"{base}.bin", bin_bytes)
#                         zf.writestr(f"{base}_codes.json", json.dumps(codes, indent=2))
#                     zip_buf.seek(0)
#                     st.success("Compressed.")
#                     st.write(f"Original: {orig_size} bytes, Compressed: {comp_size} bytes")
#                     st.write(f"Compression ratio: {ratio:.3f}x, Reduction: {reduction:.2f}%")
#                     st.download_button("Download compressed.zip",
#                                        data=zip_buf.getvalue(),
#                                        file_name=f"{base}_compressed.zip",
#                                        mime="application/zip")
#                 except Exception as e:
#                     st.error(e)
#         else:
#             # CHANGED: accept one ZIP with .bin and codes.json, and offer .txt download
#             zip_up = st.file_uploader("Upload compressed.zip", type=["zip"])
#             if zip_up and st.button("Decompress"):
#                 try:
#                     zdata = zip_up.read()
#                     with zipfile.ZipFile(io.BytesIO(zdata), "r") as zf:
#                         names = zf.namelist()
#                         bin_name = next((n for n in names if n.lower().endswith(".bin")), None)
#                         json_name = next((n for n in names if n.lower().endswith(".json")), None)
#                         if not bin_name or not json_name:
#                             raise ValueError("ZIP must contain a .bin and a codes .json file.")
#                         bin_bytes = zf.read(bin_name)
#                         codes = json.loads(zf.read(json_name).decode("utf-8", errors="ignore"))

#                     text = _decompress_bytes(bin_bytes, codes)

#                     comp_size = len(bin_bytes)
#                     decomp_size = len(text.encode("utf-8"))
#                     ratio = (comp_size / decomp_size) if decomp_size else 0.0
#                     reduction = (1 - ratio) * 100 if decomp_size else 0.0
#                     base = zip_up.name.rsplit(".", 1)[0]

#                     st.success("Decompressed.")
#                     st.write(f"Compressed: {comp_size} bytes, Decompressed: {decomp_size} bytes")
#                     st.write(f"Compression ratio (compressed/decompressed): {ratio:.3f}x, Reduction: {reduction:.2f}%")
#                     st.text_area("Text preview", text[:5000], height=200)

#                     st.download_button("Download decompressed.txt",
#                                        data=text,
#                                        file_name=f"{base}_decompressed.txt",
#                                        mime="text/plain")
#                 except Exception as e:
#                     st.error(e)

#     if __name__ == "__main__":
#         _streamlit_app()
# except Exception:
#     pass




import heapq
import json
import os
import io
import zipfile

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
    import io
    import zipfile

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
                    # Read once, keep original size in bytes
                    raw = up.read()
                    text = raw.decode("utf-8", errors="ignore")
                    bin_bytes, codes = _compress_text(text)

                    # Stats
                    orig_size = len(raw)
                    comp_size = len(bin_bytes)
                    ratio = (comp_size / orig_size) if orig_size else 0.0
                    reduction = (1 - ratio) * 100 if orig_size else 0.0

                    # Build ZIP: .bin + codes.json
                    base = up.name.rsplit(".", 1)[0] if "." in up.name else up.name
                    zip_buf = io.BytesIO()
                    with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                        zf.writestr(f"{base}.bin", bin_bytes)
                        zf.writestr(f"{base}_codes.json", json.dumps(codes, indent=2))
                    zip_buf.seek(0)

                    st.success("Compressed.")
                    st.write(f"Original: {orig_size} bytes, Compressed: {comp_size} bytes")
                    st.write(f"Compression ratio: {ratio:.3f}x, Reduction: {reduction:.2f}%")

                    st.download_button(
                        "Download compressed.zip",
                        data=zip_buf.getvalue(),
                        file_name=f"{base}_compressed.zip",
                        mime="application/zip",
                    )
                except Exception as e:
                    st.error(e)

        else:
            bin_up = st.file_uploader("Upload .bin", type=["bin"])
            codes_up = st.file_uploader("Upload codes.json", type=["json"])
            if bin_up and codes_up and st.button("Decompress"):
                try:
                    bin_bytes = bin_up.read()
                    codes = json.loads(codes_up.read().decode("utf-8", errors="ignore"))
                    text = _decompress_bytes(bin_bytes, codes)

                    # Stats (relative to decompressed size)
                    comp_size = len(bin_bytes)
                    decomp_size = len(text.encode("utf-8"))
                    ratio = (comp_size / decomp_size) if decomp_size else 0.0
                    reduction = (1 - ratio) * 100 if decomp_size else 0.0

                    # Build ZIP: decompressed.txt
                    base = bin_up.name.rsplit(".", 1)[0] if "." in bin_up.name else bin_up.name
                    zip_buf = io.BytesIO()
                    with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                        zf.writestr(f"{base}_decompressed.txt", text)
                    zip_buf.seek(0)

                    st.success("Decompressed.")
                    st.write(f"Compressed: {comp_size} bytes, Decompressed: {decomp_size} bytes")
                    st.write(f"Compression ratio (comp/decomp): {ratio:.3f}x, Reduction: {reduction:.2f}%")
                    st.text_area("Text preview", text[:5000], height=200)

                    st.download_button(
                        "Download decompressed.zip",
                        data=zip_buf.getvalue(),
                        file_name=f"{base}_decompressed.zip",
                        mime="application/zip",
                    )
                except Exception as e:
                    st.error(e)

    if __name__ == "__main__":
        _streamlit_app()
except Exception:
    pass


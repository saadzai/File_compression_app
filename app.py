import streamlit as st
import heapq
from collections import Counter
import json
import zipfile
import io

# ----------------------------
# Huffman Classes & Functions
# ----------------------------

class Node:
    """A node in the Huffman tree.

    Attributes:
        char (str or None): The character for leaf nodes, None for internal nodes.
        freq (int): Frequency of the character or sum of child frequencies for internal nodes.
        left (Node): Left child node.
        right (Node): Right child node.
    """
    def __init__(self, char, freq):
        self.char = char  # Character (None for internal nodes)
        self.freq = freq  # Frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        """Comparison operator for priority queue (heapq), based on frequency."""
        return self.freq < other.freq

def build_huffman_tree(freq_table):
    """Builds a Huffman tree from a frequency table.

    Args:
        freq_table (dict): Dictionary mapping characters to their frequencies.

    Returns:
        Node: The root node of the Huffman tree.
    """
    heap = [Node(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        
        heapq.heappush(heap, merged)
        
    return heap[0] if heap else None

def generate_codes(node, current_code="", codes=None):
    """Generates Huffman codes for each character by traversing the tree.

    Args:
        node (Node): The current node in the Huffman tree.
        current_code (str): The binary code accumulated so far.
        codes (dict): Dictionary to store character-to-code mapping.

    Returns:
        dict: Mapping of characters to their Huffman binary codes.
    """
    if codes is None:
        codes = {}
    
    if node is None:
        return codes
        
    if node.char is not None:
        codes[node.char] = current_code
        
    generate_codes(node.left, current_code + "0", codes)
    generate_codes(node.right, current_code + "1", codes)
    return codes

def encode_text(text, codes):
    """Encodes a string of text using Huffman codes.

    Args:
        text (str): Input text to encode.
        codes (dict): Character-to-code mapping.

    Returns:
        str: The encoded binary string.
    """
    return "".join(codes[char] for char in text)

def pad_encoded_data(encoded_data):
    """Pads the encoded data so that its length is a multiple of 8 bits.
    
    The first 8 bits store the amount of padding added.

    Args:
        encoded_data (str): Huffman encoded binary string.

    Returns:
        str: Padded encoded string with padding info.
    """
    extra_padding = (8 - len(encoded_data) % 8) % 8
    padded_info = "{0:08b}".format(extra_padding)
    encoded_data += "0" * extra_padding
    return padded_info + encoded_data

def huffman_decoding(encoded_data, codes):
    """Decodes a Huffman encoded string back into the original text.

    Args:
        encoded_data (str): Padded Huffman encoded binary string.
        codes (dict): Character-to-code mapping used for encoding.

    Returns:
        str: The original decoded text.
    """
    padded_info = encoded_data[:8]
    extra_padding = int(padded_info, 2)
    encoded_data = encoded_data[8:]
    
    if extra_padding > 0:
        encoded_data = encoded_data[:-extra_padding]

    reverse_codes = {v: k for k, v in codes.items()}

    current_code = ""
    decoded_text = ""
    for bit in encoded_data:
        current_code += bit
        if current_code in reverse_codes:
            decoded_text += reverse_codes[current_code]
            current_code = ""
            
    return decoded_text

# ----------------------------
# Streamlit App UI and Logic
# ----------------------------

st.set_page_config(layout="centered", page_title="Huffman Compressor")
st.title("📦 Huffman File Compressor / Decompressor")

if 'mode' not in st.session_state:
    st.session_state.mode = 'none'

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🟢 Compress File", use_container_width=True):
        st.session_state.mode = 'compress'
with col2:
    if st.button("🔵 Decompress File", use_container_width=True):
        st.session_state.mode = 'decompress'

st.markdown("---")

# ----------------------------
# Compression Flow Logic
# ----------------------------
if st.session_state.mode == 'compress':
    st.subheader("Compress a Text File")
    
    uploaded_file = st.file_uploader("Upload a text file (.txt)", type=["txt"], key="compress_uploader")
    
    if uploaded_file:
        try:
            text = uploaded_file.read().decode("utf-8")
            st.text_area("Original Text Preview", text[:1000] + ("..." if len(text) > 1000 else ""), height=100)

            freq_table = Counter(text)
            root = build_huffman_tree(freq_table)
            
            if not root:
                st.warning("The file is empty or contains no processable data.")
            elif len(freq_table) == 1:
                codes = {list(freq_table.keys())[0]: "0"}
                encoded_data = encode_text(text, codes)
            else:
                codes = generate_codes(root)
                encoded_data = encode_text(text, codes)

            padded_encoded_data = pad_encoded_data(encoded_data)

            original_bits = len(text) * 8
            compressed_bits = len(padded_encoded_data)
            compression_ratio = (1 - compressed_bits / original_bits) * 100
            
            st.info(f"Original Size: **{original_bits} bits** | Compressed Size: **{compressed_bits} bits**")
            st.success(f"Compression Ratio: **{compression_ratio:.2f}%**")
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                zf.writestr("compressed.bin", padded_encoded_data)
                zf.writestr("codes.json", json.dumps(codes))
            zip_buffer.seek(0)

            st.download_button(
                "⬇️ Download Compressed File (ZIP)",
                zip_buffer,
                file_name=f"{uploaded_file.name.replace('.txt', '')}_huffman.zip",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"An error occurred during compression: {e}")

# ----------------------------
# Decompression Flow Logic
# ----------------------------
elif st.session_state.mode == 'decompress':
    st.subheader("Decompress a ZIP File")
    
    uploaded_file = st.file_uploader("Upload a compressed ZIP file (must contain compressed.bin and codes.json)", type=["zip"], key="decompress_uploader")
    
    if uploaded_file:
        try:
            st.spinner("Decompressing...")
            zip_bytes = io.BytesIO(uploaded_file.read())
            
            compressed_data = None
            codes = None

            with zipfile.ZipFile(zip_bytes, "r") as zf:
                required_files = {"compressed.bin", "codes.json"}
                if not required_files.issubset(set(zf.namelist())):
                    st.error("Error: The ZIP file must contain 'compressed.bin' and 'codes.json'.")

                compressed_data = zf.read("compressed.bin").decode("utf-8")
                codes = json.loads(zf.read("codes.json").decode("utf-8"))

            decoded_text = huffman_decoding(compressed_data, codes)
            
            st.text_area("Decompressed Text", decoded_text, height=200)

            st.download_button(
                "⬇️ Download Decompressed Text",
                decoded_text,
                file_name="decompressed_output.txt",
                use_container_width=True
            )
            st.success("✅ Decompression successful! File is ready for download.")

        except Exception as e:
            st.error(f"An error occurred during decompression. Is this a valid Huffman ZIP file? Details: {e}")

else:
    st.info("Select **Compress File** to shrink a text file, or **Decompress File** to restore a compressed ZIP.")






# import heapq
# import json
# import os

# # -------------------------------
# # HUFFMAN TREE NODE
# # -------------------------------
# class Node:
#     def __init__(self, char, freq):
#         self.char = char
#         self.freq = freq
#         self.left = None
#         self.right = None

#     def __lt__(self, other):
#         return self.freq < other.freq


# # -------------------------------
# # BUILD FREQUENCY TABLE
# # -------------------------------
# def build_frequency_table(self, text):
#     freq = {}
#     for char in text:
#         if char not in freq:
#             freq[char] = 0
#         freq[char] += 1
#     return freq


# # -------------------------------
# # BUILD HUFFMAN TREE
# # -------------------------------
# def build_huffman_tree(freq_table):
#     heap = [Node(char, freq) for char, freq in freq_table.items()]
#     heapq.heapify(heap)

#     while len(heap) > 1:
#         left = heapq.heappop(heap)
#         right = heapq.heappop(heap)

#         merged = Node(None, left.freq + right.freq)
#         merged.left = left
#         merged.right = right

#         heapq.heappush(heap, merged)

#     return heap[0]


# # -------------------------------
# # GENERATE CODES
# # -------------------------------
# def generate_codes(node, code="", codes=None):
#     if codes is None:
#         codes = {}

#     if node is None:
#         return codes

#     # Leaf node found
#     if node.char is not None:
#         codes[node.char] = code

#     generate_codes(node.left, code + "0", codes)
#     generate_codes(node.right, code + "1", codes)

#     return codes


# # -------------------------------
# # ENCODE TEXT
# # -------------------------------
# def encode_text(text, codes):
#     temp="".join(codes[ch] for ch in text)
#     return temp


# # -------------------------------
# # PADDING (8 bit)
# # -------------------------------
# def pad_encoded(encoded):
#     extra = (8 - len(encoded) % 8) % 8
#     padded_info = f"{extra:08b}"
#     encoded += "0" * extra
#     return padded_info + encoded, extra


# # -------------------------------
# # SAVE BINARY STRING TO BYTES FILE
# # -------------------------------
# def write_binary_file(encoded_str, output_file):
#     # Convert 0/1 string → bytes
#     b = bytearray()
#     for i in range(0, len(encoded_str), 8):
#         byte = encoded_str[i:i + 8]
#         b.append(int(byte, 2))

#     with open(output_file, "wb") as f:
#         f.write(b)


# # -------------------------------
# # DECODEING
# # -------------------------------
# def remove_padding(encoded_data):
#     # First byte → padding info
#     padded_info = encoded_data[:8]
#     extra_padding = int(padded_info, 2)
#     encoded_data = encoded_data[8:]

#     if extra_padding > 0:
#         encoded_data = encoded_data[:-extra_padding]

#     return encoded_data


# def decode_text(encoded_data, codes):
#     reverse_codes = {v: k for k, v in codes.items()}
#     #ulta bana dega key -value ko value key
#     current = ""
#     decoded = ""

#     for bit in encoded_data:
#         current += bit
#         if current in reverse_codes:
#             decoded += reverse_codes[current]
#             current = ""

#     return decoded


# # -------------------------------
# # BINARY FILE → BIT STRING
# # -------------------------------
# def read_binary_as_bits(input_file):
#     with open(input_file, "rb") as f:
#         byte_data = f.read()

#     bits = ""
#     for byte in byte_data:
#         bits += "{0:08b}".format(byte)

#     return bits


# # =============================================================
# # MAIN FUNCTIONS
# # =============================================================

# def compress(input_file):
#     print("\n--- COMPRESSION STARTED ---")

#     if not os.path.exists(input_file):
#         print("❌ File not found.")
#         return

#     with open(input_file, "r") as f:
#         text = f.read()

#     # Build freq
#     freq = build_frequency_table(text)

#     # Make tree
#     root = build_huffman_tree(freq)

#     # Codes
#     codes = generate_codes(root)

#     # Encode
#     encoded = encode_text(text, codes)

#     # Padding
#     padded_encoded, _ = pad_encoded(encoded)

#     # Save encoded data
#     output_file = input("Output compressed file name (e.g., output.bin): ")
#     write_binary_file(padded_encoded, output_file)

#     # Save codes to JSON
#     code_file = output_file + "_codes.json"
#     with open(code_file, "w") as f:
#         json.dump(codes, f, indent=4)

#     print("✔ Compression successful!")
#     print(f"Compressed file saved as: {output_file}")
#     print(f"Codes saved as: {code_file}")


# def decompress(encoded_file, codes_file):
#     print("\n--- DECOMPRESSION STARTED ---")

#     # Load binary data
#     bits = read_binary_as_bits(encoded_file)

#     # Remove padding
#     bits = remove_padding(bits)

#     # Load codes
#     with open(codes_file, "r") as f:
#         codes = json.load(f)

#     # Decode
#     decoded = decode_text(bits, codes)

#     # Save output
#     output_file = input("Output decompressed text file name: ")

#     with open(output_file, "w") as f:
#         f.write(decoded)

#     print("✔ Decompression successful!")
#     print(f"Decompressed text saved as: {output_file}")


# # =============================================================
# # MAIN MENU
# # =============================================================
# if __name__ == "__main__":

#     print("-------------------------")
#     print(" HUFFMAN CODING PROGRAM")
#     print("-------------------------")
#     print("1. Compress a file")
#     print("2. Decompress a file")
#     print("-------------------------")

#     choice = input("Choose option (1/2): ").strip()

#     if choice == "1":
#         file_name = input("Enter file name to compress (press Enter for default sample.txt): ").strip()
#         if file_name == "":
#             file_name = "sample.txt"
#         compress(file_name)

#     elif choice == "2":
#         encoded_file = input("Enter encoded (.bin) file: ").strip()
#         codes_file = input("Enter JSON codes file: ").strip()
#         decompress(encoded_file, codes_file)

#     else:
#         print("Invalid choice.")


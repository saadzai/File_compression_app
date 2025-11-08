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

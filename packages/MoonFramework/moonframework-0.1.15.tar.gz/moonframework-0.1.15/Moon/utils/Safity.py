from urllib.parse import quote, unquote
import sys

def encode_from_quote(code: str) -> str:
    return quote(code)

def encode_from_hex(code: str):
    return code.encode().hex()

def encode(code: str) -> str:
    c = encode_from_quote(code)
    c = encode_from_hex(c)
    return c



import sys

if len(sys.argv) > 1:
    file_path = sys.argv[1]
    with open(file_path, 'r') as f:
        CODE = f.read()
else:
    CODE = "print('Hello, world!')"

encoded_code = encode(CODE)
file = open("out.py", 'w')

out_code = f"""
from urllib.parse import unquote
CODE = \
"""

text_lenght = 50
encoded_parts = [encoded_code[i:i+text_lenght] for i in range(0, len(encoded_code), text_lenght)]

for i, p in enumerate(encoded_parts):
    if i == 0:
        out_code += f' "{p}"\\\n'
    elif i == len(encoded_parts) - 1:
        out_code += f'\t\t"{p}"'
    else:
        out_code += f'\t\t"{p}"\\\n'
out_code += '\n'
out_code += "exec(unquote(bytes.fromhex(CODE.replace('\\n', '')).decode()))"

file.write(out_code)
file.close()
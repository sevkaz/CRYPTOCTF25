import re
from Crypto.Util.number import *

# output.txt içeriğini oku
with open("/mnt/data/output.txt", "r") as f:
    content = f.read()

# R'yi, n'yi ve c'yi çıkartalım
# R = [....]
r_match = re.search(r"R\s*=\s*\[([^\]]+)\]", content, re.DOTALL)
R_list = list(map(int, r_match.group(1).split(","))) if r_match else []

# n = ...
n_match = re.search(r"n\s*=\s*(\d+)", content)
n = int(n_match.group(1)) if n_match else None

# c = ...
c_match = re.search(r"c\s*=\s*(\d+)", content)
c = int(c_match.group(1)) if c_match else None

len(R_list), type(n), type(c)

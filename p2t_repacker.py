import os, lzss, sys
from struct import *
#dir = "0000"
def get_num_files(dir):
    cnt = 0
    for f in os.scandir(dir):
        if f.is_file():
            cnt += 1
    return cnt

if (len(sys.argv) != 2):
    print("Usage:\npy p2t_repacker.py <input dir>")
    sys.exit(0)

dir = sys.argv[1]

# wish i could think of a more elegant solution than this
with open(dir + "_repacked.p2t", "w+b") as out:
    offsets = [0]
    compressed_sizes = []
    num_files = get_num_files(dir)

    # writing header
    out.write(pack("<5i12x", num_files * 64 + 32, 1024, 32, num_files, num_files * 64 + 32))

    # writing file info
    files = os.listdir(dir)
    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    for file in (files):
        print(file)
        with open(os.path.join(dir, file), "rb") as tm2:
            tm2.seek(16)
            out.write(tm2.read(48))
            out.write(pack("4c3i", b"\xFF", b"\xFF", b"\xFF", b"\xFF", 0, 1, 0))
    cur_offset = 0

    # writing file offsets and sizes
    for file in (files):
        with open(os.path.join(dir, file), "rb") as tm2:
            tm2.seek(0, 2)
            uncompressed_len = tm2.tell()
            out.write(pack("<i", uncompressed_len - 64))

            tm2.seek(64)
            compressed_data = lzss.compress(tm2.read())
            out.write(compressed_data)
            compressed_sizes.append(len(compressed_data))

            padding_len = 32 - ((len(compressed_data) + 4) % 32)
            
            cur_offset += padding_len + len(compressed_data) + 4
            offsets.append(cur_offset)

            for i in range(padding_len):
                out.write(pack("c", b"\xFF"))

    out.seek(84)
    for i in range(num_files):
        out.write(pack("<iii", offsets[i], 1, compressed_sizes[i]))
        out.seek(52, 1)
    print(offsets)
    print(compressed_sizes)
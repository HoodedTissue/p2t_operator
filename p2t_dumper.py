import sys, os, lzss
from dataclasses import dataclass
'''
# ported from https://github.com/nickworonekin/puyotools/blob/master/src/PuyoTools.Core/Compression/Formats/Lz01Compression.cs
def decompress(fname, compressed_size, out):
    file = open(fname + ".lz", "rb")

    sourcePointer = 0x0
    destinationPointer = 0x0
    bufferPointer = 0xFEE

    buffer = bytearray(0x1000)

    while (sourcePointer < compressed_size):
        flag = file.read(1)
        sourcePointer += 1
        #print(flag)
        for i in range(8):
            if ((int.from_bytes(flag, "little") & 0x1) > 0): # data is not compressed
                value = file.read(1)
                sourcePointer += 1

                out.write(value)
                destinationPointer += 1

                buffer[bufferPointer] = int.from_bytes(value, "little")
                bufferPointer = (bufferPointer + 1) & 0xFFF
            else: # data is compressed
                b1 = int.from_bytes(file.read(1), "little")
                b2 = int.from_bytes(file.read(1), "little")
                sourcePointer += 2

                matchOffset = (((b2 >> 4) & 0xF) << 8) | b1
                matchLength = (b2 & 0xF) + 3

                for j in range(matchLength):

                    out.write(buffer[(matchOffset + j) & 0xFFF].to_bytes(1, "little"))
                    destinationPointer += 1

                    buffer[bufferPointer] = buffer[(matchOffset + j) & 0xFFF]
                    bufferPointer = (bufferPointer + 1) & 0xFFF

            if (sourcePointer >= compressed_size):
                break
            flag = (int.from_bytes(flag, "little") >> 1).to_bytes(1, "little")
'''

@dataclass
class FileEntry:
    tim_header: bytes
    offset: int
    size: int

file_entries = []

if (len(sys.argv) != 2):
    print("Usage:\npy p2t_dumper.py <input file>")
    sys.exit(0)

out_folder = sys.argv[1].split(".")[0]

with open(sys.argv[1], "rb") as f:

    # reading in header info
    file_info_end = int.from_bytes(f.read(4), "little")
    block_size = int.from_bytes(f.read(4), "little")
    header_end = int.from_bytes(f.read(4), "little")
    num_files = int.from_bytes(f.read(4), "little")
    data_start = int.from_bytes(f.read(4), "little")
    f.seek(header_end, 0)

    print(f"File info end: {file_info_end}")
    print(f"block size: {block_size}")
    print(f"header end: {header_end}")
    print(f"data start: {data_start}\n")

    # reading in file entries
    print("~~~~~~~~~~~ file entries ~~~~~~~~~~~")
    for i in range(num_files):
        
        tim_header = f.read(48)
        assert f.read(4) == b"\xFF\xFF\xFF\xFF"
        data_offset = int.from_bytes(f.read(4), "little") + data_start
        assert f.read(4) == b"\x01\x00\x00\x00"
        data_length = int.from_bytes(f.read(4), "little")

        file_entries.append(FileEntry(tim_header, data_offset, data_length))

        print("data offset: %8s\tdata length: %8s" % (data_offset, data_length))

    # write files
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    for i in range(len(file_entries)):
        
        f.seek(file_entries[i].offset)

        uncompressed_size = f.read(4) # not really needed
        
        #with open(out_folder + "/" + str(i) + ".lzss0", "wb") as out:
        #    out.write(f.read(file_entries[i].size))

        data = f.read(file_entries[i].size)
        with open(out_folder + "/" + str(i) + ".tm2", "wb") as tm2:
            tm2.write(b"TIM2\x04\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00") # hopefully its the same for every file
            tm2.write(file_entries[i].tim_header)
            tm2.write(lzss.decompress(data))
            #decompress((out_folder + "/" + str(i)), file_entries[i].size, tm2)
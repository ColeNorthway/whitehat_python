key = 0x42


target_bin = input("Enter the binary path to encode: ")

try:
    with open(target_bin, 'rb') as f:
        data = bytearray(f.read())

        encrypted = bytearray([b ^ key for b in data])

        with open(target_bin, "wb") as fb:
            fb.write(encrypted)

            print(f"Shellcode encrypted w/ XOR key {hex(key)}.")
except FileNotFoundError:
    print("Path not found")

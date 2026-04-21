# CRC
def shift_crc_i(crc_in, data_bit, polynomial, width_mask):
    msb = (crc_in >> 31) & 1
    feedback = msb ^ data_bit
    shifted = (crc_in << 1) & width_mask # limits to crc_width bits
    if feedback:
        shifted ^= polynomial
    return shifted

# CRC/MPEG-2
def gen_crc(crc_width, data_width, polynomial=0x04C11DB7, crc_in=None, data_in=None, write_to_file=True):
    print(f"Generating...CRC Width: {crc_width}, Data Width: {data_width}, Polynomial: {polynomial}")
    if crc_in and data_in: print(f"Calculating CRC...CRC In:{hex(crc_in)}, Data In:{hex(data_in)}")

    # Input checks
    if (len(bin(crc_in))-2 != crc_width):
        raise ValueError("crc_width did not match crc_in width.")
    if (len(bin(data_in))-2 != data_width):
        raise ValueError("data_width did not match data_in width.")

    width_mask = (1 << crc_width) - 1 # generate width mask used to model bit wrapping behavior

    # 1. Map old CRC bits
    crc_arr = []
    for i in range(crc_width):
        val = (1 << i)
        for _ in range(data_width): # Shift data width times
            val = shift_crc_i(val, 0, polynomial, width_mask)
        crc_arr.append(val)

    # for i in crc_arr: print(bin(i))

    # 2. Map Data bits
    data_arr = []
    for j in range(data_width):
    # for j in range(data_width):
        val = shift_crc_i(0, 1, polynomial, width_mask) # Shift the '1' once
        for _ in range(j):
            val = shift_crc_i(val, 0, polynomial, width_mask)
        data_arr.append(val)

    # 3. Generate verilog and calculate
    code_file_name = 'crc.v'
    if write_to_file: code_file = open(code_file_name, 'w')
    crc_out = 0
    for k in range(crc_width):
        terms = []
        k_crc = 0
        for i in range(crc_width):
            if (crc_arr[i] >> k) & 1:
                terms.append(f"current_crc[{i}]") # A
                if crc_in: k_crc ^= (crc_in >> i) & 1

        for j in range(data_width):
            if (data_arr[j] >> k) & 1:
                terms.append(f"data_in[{j}]") # B
                if data_in: k_crc ^= (data_in >> j) & 1

        if k_crc: crc_out |= (1 << k)
        
        verilog = f"assign next_crc[{k}] = " + " ^ ".join(terms) + ";" # C
        print(verilog)
        if write_to_file: code_file.write(verilog + "\n")

    if write_to_file: 
        code_file.close()
        print(f"Write to file done: {code_file_name}")
    if crc_in and data_in: print("CRC Out:", hex(crc_out))

if __name__ == "__main__":
    crc_in      = 0xFFFFFFFF
    data        = 0xd13b99799619b663d13b99799619b663d13b99799619b663d13b99799619b663
    polynomial  = 0x04C11DB7            # CRC32
    crc_width   = 32
    data_width  = 256
    gen_crc(crc_width, data_width, polynomial, crc_in, data)
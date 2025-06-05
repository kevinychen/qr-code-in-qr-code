import random

def format_coordinates(L):
    return [
        [(8, c) for c in (0, 1, 2, 3, 4, 5, 7, L - 8, L - 7, L - 6, L - 5, L - 4, L - 3, L - 2, L - 1)],
        [(r, 8) for r in (L - 1, L - 2, L - 3, L - 4, L - 5, L - 6, L - 7, 8, 7, 5, 4, 3, 2, 1, 0)],
    ]

def mask(mask_index, i, j):
    return {
        0: i * j % 2 + i * j % 3 == 0,
        1: (i // 2 + j // 3) % 2 == 0,
        2: (i * j % 3 + i + j) % 2 == 0,
        3: (i * j % 3 + i * j) % 2 == 0,
        4: i % 2 == 0,
        5: (i + j) % 2 == 0,
        6: (i + j) % 3 == 0,
        7: j % 3 == 0,
    }[mask_index]

BLACK = '■'
WHITE = '▢'

version = 20

L = 4 * version + 17
start_alignment_coordinates = [
    -1, 6, 18, 22, 26, 30, 34, 22, 24, 26,
    28, 30, 32, 34, 26, 26, 26, 30, 30, 30,
    34, 28, 26, 30, 28, 32, 30, 34, 26, 30,
    26, 30, 34, 30, 34, 30, 24, 28, 32, 26,
    30
]
# https://www.thonky.com/qr-code-tutorial/error-correction-table
block_sizes = {
    19: [113] * 3 + [114] * 4,
    20: [107] * 3 + [108] * 5,
    26: [114] * 10 + [115] * 2,
    27: [122] * 8 + [123] * 4,
}[version]
num_steps = version // 7
start_alignment_coordinate = start_alignment_coordinates[version]
step = (L - 7 - start_alignment_coordinate) // num_steps
alignment_coordinates = [6]
for i in range(num_steps + 1):
    alignment_coordinates.append(start_alignment_coordinate + i * step)

# position of small QR code
D = alignment_coordinates[2] - 22

# alphanumeric uses 11 modules per 2 characters
CAPACITY = sum(block_sizes) * 8 // 11 - 1

outer_qr_code = [[' ' for _ in range(L)] for _ in range(L)]

def draw_finder(x, y):
    for dy in range(7):
        for dx in range(7):
            if dx in [0, 6] or dy in [0, 6] or (2 <= dx <= 4 and 2 <= dy <= 4):
                outer_qr_code[y + dy][x + dx] = BLACK
            else:
                outer_qr_code[y + dy][x + dx] = WHITE

def draw_separator(x, y):
    for i in range(8):
        if x == 0 and y == 0:  # left
            outer_qr_code[y + 7][x + i] = WHITE
            outer_qr_code[y + i][x + 7] = WHITE
        elif x == L - 7:  # right
            outer_qr_code[y + 7][x + i - 1] = WHITE
            outer_qr_code[y + i][x - 1] = WHITE
        elif y == L - 7:  # bottom
            outer_qr_code[y + i - 1][x + 7] = WHITE
            outer_qr_code[y - 1][x + i] = WHITE

outer_qr_code[L - 8][8] = BLACK

def draw_format_info():
    format_bits = [BLACK] * 15  # doesn't matter

    # Top-left: vertical
    for i in range(6):
        outer_qr_code[i][8] = format_bits[i]
    outer_qr_code[7][8] = format_bits[6]
    outer_qr_code[8][8] = format_bits[7]
    outer_qr_code[8][7] = format_bits[8]
    for i in range(6):
        outer_qr_code[8][5 - i] = format_bits[9 + i]

    # Top-right
    for i in range(8):
        outer_qr_code[8][L - 1 - i] = format_bits[i]

    # Bottom-left
    for i in range(7):
        outer_qr_code[L - 1 - i][8] = format_bits[i + 8]

draw_finder(0, 0)
draw_separator(0, 0)

draw_finder(L - 7, 0)
draw_separator(L - 7, 0)

draw_finder(0, L - 7)
draw_separator(0, L - 7)

draw_format_info()

# Alignment patterns
for i in alignment_coordinates:
    for j in alignment_coordinates:
        if outer_qr_code[i][j] == ' ':
            for ii in range(i - 2, i + 3):
                for jj in range(j - 2, j + 3):
                    outer_qr_code[ii][jj] = BLACK if max(abs(ii - i), abs(jj - j)) in (0, 2) else WHITE

# Timing patterns
for i in range(8, L - 8):
    outer_qr_code[6][i] = BLACK if i % 2 == 0 else WHITE
    outer_qr_code[i][6] = BLACK if i % 2 == 0 else WHITE

version_info = [0] * 18  # doesn't matter
for i in range(6):
    for j in range(3):
        outer_qr_code[i][L - 11 + j] = BLACK if version_info[3 * i + j] else WHITE
        outer_qr_code[L - 11 + j][i] = BLACK if version_info[3 * i + j] else WHITE

def read_qr_data_modules(grid):
    size = len(grid)
    result = []
    up = True  # reading direction

    x = size - 1
    while x > 0:
        if x == 6:  # skip vertical timing pattern
            x -= 1

        col = [x, x - 1]

        # Read column pair in either upward or downward direction
        y_range = range(size - 1, -1, -1) if up else range(size)

        for y in y_range:
            for cx in col:
                if grid[y][cx] == ' ':  # only collect if it's a data cell
                    result.append((y, cx))

        x -= 2
        up = not up

    return result

data_cells = read_qr_data_modules(outer_qr_code)

# Now add inner QR code and other contents
# Inner QR code says "I AM A SMALL QR CODE"
assert (D + 22) in alignment_coordinates
inner_qr_code = """
▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢
▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢
▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢
▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢
▢▢▢▢■■■■■■■▢▢■▢▢■■■▢▢▢■■■■■■■▢▢▢▢
▢▢▢▢■▢▢▢▢▢■▢▢▢■■■▢■■■▢■▢▢▢▢▢■▢▢▢▢
▢▢▢▢■▢■■■▢■▢■■■▢■▢▢■■▢■▢■■■▢■▢▢▢▢
▢▢▢▢■▢■■■▢■▢▢■■■▢■■■▢▢■▢■■■▢■▢▢▢▢
▢▢▢▢■▢■■■▢■▢▢▢■▢▢▢■▢▢▢■▢■■■▢■▢▢▢▢
▢▢▢▢■▢▢▢▢▢■▢▢■▢▢▢■■■▢▢■▢▢▢▢▢■▢▢▢▢
▢▢▢▢■■■■■■■▢■▢■▢■▢■▢■▢■■■■■■■▢▢▢▢
▢▢▢▢▢▢▢▢▢▢▢▢■■■▢■■▢■▢▢▢▢▢▢▢▢▢▢▢▢▢
▢▢▢▢■■■▢■■■■■▢■■▢▢▢▢■■■▢▢▢■▢▢▢▢▢▢
▢▢▢▢■▢▢▢■▢▢■▢▢■■▢■▢▢▢■▢▢▢■▢■▢▢▢▢▢
▢▢▢▢▢▢▢▢■■■▢■■▢▢▢▢▢▢■▢■■■■■■■▢▢▢▢
▢▢▢▢■▢■■■▢▢■▢▢▢■▢■■▢▢▢▢▢■▢▢■▢▢▢▢▢
▢▢▢▢▢■▢■■▢■▢▢▢▢▢■■■▢▢■■▢■▢■▢■▢▢▢▢
▢▢▢▢▢■■▢▢▢▢■■■▢■■■▢■■■▢▢▢▢■■■▢▢▢▢
▢▢▢▢■▢■■■▢■■▢▢■■■▢■▢▢■▢■▢■■▢■▢▢▢▢
▢▢▢▢▢■■▢▢▢▢▢■■■▢■■■■▢■▢■▢■▢▢▢▢▢▢▢
▢▢▢▢■▢■▢■▢■■■▢▢■▢▢■▢■■■■■▢▢▢▢▢▢▢▢
▢▢▢▢▢▢▢▢▢▢▢▢■■■■▢▢▢▢■▢▢▢■■▢■▢▢▢▢▢
▢▢▢▢■■■■■■■▢■▢▢▢▢■▢▢■▢■▢■▢■■■▢▢▢▢
▢▢▢▢■▢▢▢▢▢■▢■▢▢■▢▢▢▢■▢▢▢■▢▢▢▢▢▢▢▢
▢▢▢▢■▢■■■▢■▢■▢■▢■▢▢▢■■■■■▢■■■▢▢▢▢
▢▢▢▢■▢■■■▢■▢▢■■■■■▢■▢▢▢▢▢■▢▢▢▢▢▢▢
▢▢▢▢■▢■■■▢■▢■▢▢■■▢■▢■▢■■■■■▢■▢▢▢▢
▢▢▢▢■▢▢▢▢▢■▢■▢▢▢■■■■■▢■■▢■▢■▢▢▢▢▢
▢▢▢▢■■■■■■■▢■▢■■▢▢■▢■▢■▢■▢▢■■▢▢▢▢
▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢
▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢
▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢
▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢▢
""".split()
for i in range(len(inner_qr_code)):
    for j in range(len(inner_qr_code)):
        outer_qr_code[D + i][D + j] = BLACK if mask(7, D + i, D + j) ^ (inner_qr_code[i][j] == BLACK) else WHITE

# Fill in the remaining cells with things that will result in the bad pattern ("10111010000") when masked with masks
# 0-6. This bad pattern looks similar to a finder pattern, so is heavily penalized by the QR generation algorithm.
codewords = [data_cells[i:i+8] for i in range(0, 8 * sum(block_sizes), 8)]
START = min(c for codeword in codewords for r, c in codeword) + 4
END = L - 2

index = 0
K = 2
for c in range(START, END - 18):
    for r in range(L):
        if all(outer_qr_code[r][c + i] == ' ' for i in range(18)):
            for i, bit in enumerate('101110100001011101'):
                outer_qr_code[r][c + i] = BLACK if mask(index // K % 7, r, c + i) ^ (bit == '1') else WHITE
            index += 1
for c in range(START, END):
    for r in range(L - 18):
        if all(outer_qr_code[r + i][c] == ' ' for i in range(18)):
            for i, bit in enumerate('101110100001011101'):
                outer_qr_code[r + i][c] = BLACK if mask(index // K % 7, r + i, c) ^ (bit == '1') else WHITE
            index += 1
for c in range(START, END - 11):
    for r in range(L):
        if all(outer_qr_code[r][c + i] == ' ' for i in range(11)):
            for i, bit in enumerate('10111010000'):
                outer_qr_code[r][c + i] = BLACK if mask(index // K % 7, r, c + i) ^ (bit == '1') else WHITE
            index += 1
for c in range(START, END):
    for r in range(L - 11):
        if all(outer_qr_code[r + i][c] == ' ' for i in range(11)):
            for i, bit in enumerate('10111010000'):
                outer_qr_code[r + i][c] = BLACK if mask(index // K % 7, r + i, c) ^ (bit == '1') else WHITE
            index += 1

random.seed(0)
for r in range(L):
    for c in range(L):
        if outer_qr_code[r][c] == ' ':
            outer_qr_code[r][c] = random.choice(BLACK + WHITE)

# Now decode the QR code to get the contents
codeword_lists = [[] for _ in block_sizes]
index = 0
for codeword in codewords:
    while len(codeword_lists[index]) == block_sizes[index]:
        index += 1
        index %= len(block_sizes)
    codeword_lists[index].append(codeword)
    index += 1
    index %= len(block_sizes)

interleaved_codewords = [codeword for codeword_list in codeword_lists for codeword in codeword_list]

all_positions = []
for codeword in interleaved_codewords:
    for r, c in codeword:
        all_positions.append((r, c))
all_bits = [outer_qr_code[r][c] for r, c in all_positions]

start = all_bits[:4]
grouped_bits = [all_bits[i+4:i+15] for i in range(11, CAPACITY * 11, 11)]

alphanumeric_table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'
values = ''
for grouped_bit in grouped_bits:
    num = int(''.join('1' if bit == BLACK else '0' for bit in grouped_bit), 2)
    if num >= 2025:
        num ^= (1 << 10)
    values += alphanumeric_table[num // 45]
    values += alphanumeric_table[num % 45]

prefix = 'I AM A BIG QR CODE. HERE IS SOME DATA: '
suffix = '.'
values = prefix + values[len(prefix):-len(suffix)] + suffix
print(values)

import pygame
import json


ascii_table = {}

with open("charTable.json", "r") as file:
    ascii_table = json.load(file)
    file.close()

pygame.init()

file_path = input("QR code path: ")
img = pygame.image.load(file_path)

matrix = []
mask_matrix = []

def XOR(bit_1, bit_2):
    if (bit_1 == "1" and bit_2 == "0") or (bit_1 == "0" and bit_2 == "1"):
        return "1"
    else:
        return "0"

mask_patterns = {
    "111": [[1,0,0,1,0,0],
            [1,0,0,1,0,0],
            [1,0,0,1,0,0],
            [1,0,0,1,0,0],
            [1,0,0,1,0,0],
            [1,0,0,1,0,0]],

    "100": [[1,1,1,1,1,1],
            [0,0,0,0,0,0],
            [1,1,1,1,1,1],
            [0,0,0,0,0,0],
            [1,1,1,1,1,1],
            [0,0,0,0,0,0]],
    
    "110": [[1,0,0,1,0,0],
            [0,0,1,0,0,1],
            [0,1,0,0,1,0],
            [1,0,0,1,0,0],
            [0,0,1,0,0,1],
            [0,1,0,0,1,0]],
    
    "010": [[1,0,1,0,1,0],
            [0,0,0,1,1,1],
            [1,0,0,0,1,1],
            [0,1,0,1,0,1],
            [1,1,1,0,0,0],
            [0,1,1,1,0,0]],
    
    "101": [[1,0,1,0,1,0],
            [0,1,0,1,0,1],
            [1,0,1,0,1,0],
            [0,1,0,1,0,1],
            [1,0,1,0,1,0],
            [0,1,0,1,0,1]],
    
    "011": [[1,1,1,1,1,1],
            [1,1,1,0,0,0],
            [1,1,0,1,1,0],
            [1,0,1,0,1,0],
            [1,0,1,1,0,1],
            [1,0,0,0,1,1]],
    
    "001": [[1,1,1,0,0,0],
            [1,1,1,0,0,0],
            [0,0,0,1,1,1],
            [0,0,0,1,1,1],
            [1,1,1,0,0,0],
            [1,1,1,0,0,0],
            [0,0,0,1,1,1],
            [0,0,0,1,1,1]],
    
    "000": [[1,1,1,1,1,1],
            [1,0,0,0,0,0],
            [1,0,0,1,0,0],
            [1,0,1,0,1,0],
            [1,0,0,1,0,0],
            [1,0,0,0,0,0]],
}

encodings = {
    "1000": "numeric",
    "0100": "alphanumeric",
    "0010": "byte",
    "1110": "ECI"
}

bounds = [0, 0, 0, 0] # top, left, right, bottom

alignment_pattern_positions = []


for y in range(img.get_height()):
    for x in range(img.get_width()):
        if img.get_at((x, y)) != (255, 255, 255) and (bounds[0] == 0 and bounds[1] == 0):
            bounds[0] = y
            bounds[1] = x
        
        if bounds[1] != 0:
            if img.get_at((bounds[1], img.get_height()-(y-1))) != (255, 255, 255) and bounds[3] == 0:
                bounds[3] = img.get_height()-(y-1)
                bounds[2] = bounds[3]

# Determine module size in terms of pixels
search_x = 0
search_y = 0
for i in range(bounds[2]-bounds[1]+1):
    if img.get_at((bounds[1]+i, bounds[0])) == (255, 255, 255):
        search_x = (bounds[1]+i)-1
        break

search_y = search_x
width = 0
height = 0
for i in range(100):
    # Find the width, then you can also find the height
    if img.get_at((search_x+i+1, search_y)) != (255, 255, 255):
        height = width
        break
    else:
        width += 1

num_modules = int(((bounds[3]-bounds[0])+1)/width)
if num_modules < 21:
    num_modules = 21


for y in range(num_modules):
    matrix.append([])
    for x in range(num_modules):
        if img.get_at((bounds[1]+(x*width), bounds[0]+(y*height))) != (255, 255, 255):
            matrix[y].append(1)
        else:
            matrix[y].append(0)

# Find arrangement patterns
for y in range(num_modules):
    for x in range(num_modules):
        string = ""
        for i in range(5):
            for j in range(5):
                try:
                    string += str(matrix[y+i][x+j])
                except:
                    pass

        if len(string) == 25:
            if string == "1111110001101011000111111":
                print('yep')
                alignment_pattern_positions.append([x, y])

# Modules to ignore
ignore_list = []

# Top corner
for i in range(9):
    for j in range(9):
        ignore_list.append([j, i])

for i in range(8):
    for j in range(9):
        ignore_list.append([j, num_modules-1-i])

for i in range(9):
    for j in range(8):
        ignore_list.append([num_modules-1-j, i])

for pos in alignment_pattern_positions:
    for i in range(5):
        for j in range(5):
            ignore_list.append([pos[0]+j, pos[1]+i])

# Timing pattern must also be ignored
for i in range(num_modules):
    ignore_list.append([i, 6])
    ignore_list.append([6, i])

mask = str(matrix[8][2])+str(matrix[8][3])+str(matrix[8][4])

# create the mask
for y in range(num_modules):
    mask_matrix.append([])
    for x in range(num_modules):
        index = [x%6, y%6]
        if mask == "001":
            index = [x%6, y%8]
        mask_matrix[y].append(mask_patterns[mask][index[1]][index[0]])

# Encoding
nibble = str(matrix[num_modules-2][num_modules-2])+str(matrix[num_modules-2][num_modules-1])+str(matrix[num_modules-1][num_modules-2])+str(matrix[num_modules-1][num_modules-1])
mask_nibble = str(mask_matrix[num_modules-2][num_modules-2])+str(mask_matrix[num_modules-2][num_modules-1])+str(mask_matrix[num_modules-1][num_modules-2])+str(mask_matrix[num_modules-1][num_modules-1])
encoding = ""

for row in mask_matrix:
    print(row)

for i in range(4):
    encoding += XOR(nibble[i], mask_nibble[i])

print(mask, encodings[encoding], encoding)

# Read the qr code now:
reading = True
data = ""

decoded_matrix = []
image = pygame.Surface((num_modules*8, num_modules*8))

image.fill((255, 255, 255))

for y in range(num_modules):
    decoded_matrix.append([])
    for x in range(num_modules):
        bit = str(matrix[y][x])
        mask_bit = str(mask_matrix[y][x])
        b = XOR(bit, mask_bit)
        if b == "1" and [x, y] not in ignore_list:
            pygame.draw.rect(image, (0, 0, 0), (x*8, y*8, 8, 8))
        elif [x, y] in ignore_list:
            if bit == "1":
                pygame.draw.rect(image, (255, 0, 0), (x*8, y*8, 8, 8))
                #pygame.draw.rect(image, (140, 140, 140), (x*4, y*4, 4, 4), 1)
        pygame.draw.rect(image, (140, 140, 140), (x*8, y*8, 8, 8), 1)
        decoded_matrix[y].append(b)

for row in decoded_matrix:
    print(row)

pygame.image.save(image, "decoded_mask.png")

index = [num_modules-1, num_modules-3]
up = True
down = False

while reading:
    if up and (down == False):
        for i in range(2):
            x = index[0]-i
            if x < 0:
                reading = False
            if [x, index[1]] not in ignore_list:
                bit = str(matrix[index[1]][x])
                mask_bit = str(mask_matrix[index[1]][x])
                data += XOR(bit, mask_bit)
        index[1] -= 1

        if index[1] < 0:
            index[1] = 0
            index[0] -= 2
            if index[0] == 6:
                index[0] = 5
                print("arrived")
            if index[0] < 0:
                reading = False
            up = False
            down = True
    if down and (up == False):
        for i in range(2):
            x = index[0]-i
            if x < 0:
                reading = False
            if [x, index[1]] not in ignore_list:
                bit = str(matrix[index[1]][x])
                mask_bit = str(mask_matrix[index[1]][x])
                data += XOR(bit, mask_bit)
        index[1] += 1

        if index[1] >= num_modules:
            index[1] = num_modules-1
            index[0] -= 2
            if index[0] == 6:
                index[0] = 5
                print("arrived down")
            if index[0] < 0:
                reading = False
            up = True
            down = False

def binary_to_num(bin):
    if len(bin) != 8:
        return "NUL"
    num = 0
    for i in range(8):
        if bin[7-i] == "1":
            num += 2**i
        else:
            pass
    return num

# Now, decode data from binary to actual characters
length = data[0:8]
#length = length[::-1]
size = binary_to_num(length)
print(len(data)/8, "stuff", size, length)

codes = []

string = ""

start = 8
for i in range(size):
    byte = data[start:(start+8)]
    print(byte)
    codes.append(binary_to_num(byte))
    start += 8

for code in codes:
    #print(str(code))
    if str(code) in ascii_table:
        string += ascii_table[str(code)]

print(string)

pygame.quit()







from pwn import *

# matrix = [[761675, 530862, 128344, 941539],
# [940476, 704591, 139158, 548989],
# [456464, 660507, 757385, 985097],
# [592973, 400372, 457564, 773330],
# [177071, 337474, 317206, 446912]]

def sol(matrix):
    s = 0
    for row in matrix :
        # print(f"min in row {row} = {min(row)} ")
        s += min(row)
    return s

SRC = "code.deadface.io"
PORT = "50000"

matrix = []

r = remote(SRC, PORT)
for i in range(5):
    s = r.readlineS().strip().replace(']',"").replace("[","").replace(" ","").split(',')
    for i in range(len(s)):
        # print(type(item))
        s[i] = int(s[i])
        # print(type(item))
    matrix.append(s)

print(matrix)
s = str(sol(matrix)).encode()
print(s)
r.sendline(s)
# print(matrix)
# print(s)
flag = r.recv()
print(flag)
r.close()


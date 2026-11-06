mov rax, 4
mov rbx, 8
add rax, rbx
mov rdx, 0x8000
mov qword ptr [rdx], rax
mov rcx, qword ptr [rdx]
cmp rcx, 12
jne finish
inc rcx
finish:
nop

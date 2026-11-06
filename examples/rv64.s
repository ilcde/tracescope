addi x5, x0, 4
addi x6, x0, 8
add x7, x5, x6
lui x8, 8
sd x7, 0(x8)
ld x9, 0(x8)
addi x10, x0, 12
bne x9, x10, end
jal x1, incval
jal x0, end
incval:
addi x9, x9, 1
jalr x0, 0(x1)
end:
nop
.data
	a: .word32 25
	b: .word32 30

.code
	lw $s0, a(r0)
	lw $s1, b(r0)
check:
	slt $t7, $s0, $s1
	BEQZ $t7, end
loop:
	lw $t7, a(r0)
	lw $t6, b(r0)
	slt $t7, $t7, $t6
	BEQZ $t7, end_if0
then0:
	;soma de dois imediatos
	addi $t0, $zero, #4
	addi $t0, $t0, #4
	sw $t0, a(r0)
	add $t0, $zero, $zero
end_if0:
	j check
end:
	SYSCALL 0

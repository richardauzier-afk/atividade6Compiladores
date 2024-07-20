.data
	b: .word32 2
	c: .word32 4

.code
	lw $t7, a(r0)
	slti $t7, $t7, #9
	BNEZ $t7, end_if0
then0:
	lw $t5, a(r0)
	lw $t6, b(r0)
	BNE $t5, $t6, end_if1
then1:
	;soma de dois imediatos
	addi $t0, $zero, #3
	addi $t1, $t0, #2
	sw $t1, b(r0)
	add $t0, $zero, $zero
	add $t1, $zero, $zero

end_if1:
end_if0:
	SYSCALL 0

.data
	a: .word32 10
	b: .word32 50
	f: .space 4
	s: .space 4

.code
	lw $t5, a(r0)
	lw $t6, b(r0)
	slt $t7, $t5, $t6
	BEQZ $t7, L2
L1:
	;soma de dois imediatos
	addi $t0, $zero, #1
	addi $t1, $t0, #6
	sw $t1, a(r0)
	add $t0, $zero, $zero
	add $t1, $zero, $zero

L2:
	;soma de dois imediatos
	addi $t0, $zero, #1
	addi $t1, $t0, #1
	sw $t1, f(r0)
	add $t0, $zero, $zero
	add $t1, $zero, $zero

	;soma de dois imediatos
	addi $t0, $zero, #2
	addi $t1, $t0, #2
	sw $t1, s(r0)
	add $t0, $zero, $zero
	add $t1, $zero, $zero

	SYSCALL 0

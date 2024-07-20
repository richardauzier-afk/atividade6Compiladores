.data
	a: .space 4
	LT1: .word32 4
	LT2: .word32 9

.code
	lw $t0, LT1(r0)
	lw $t1, LT2(r0)
	mult $t0, $t1
	mflo $t0
	sw $t0, a(r0)
	add $t0, $zero, $zero
	add $t1, $zero, $zero

	SYSCALL 0

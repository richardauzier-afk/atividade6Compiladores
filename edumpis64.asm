.data
	a: .space 4
	LM1: .word32 4
	LM2: .word32 5

.code
	lw $t0, LM1(r0)
	lw $t1, LM2(r0)

	mult $t0, $t1
	mflo $t0

	sw $t0, a(r0)

	;;;;;;;;;

	lw $t0, LM1(r0)
	lw $t1, LM2(r0)

	mult $t0, $t1
	mflo $t0

	sw $t0, a(r0)

	;;;;;;;;;

	addi $t1, $t0, #5
	addi $t2, $t1, #6

	sw $t2, a(r0)


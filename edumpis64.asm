.data
	e: .space 4
	k: .space 4
	i: .space 4
	LT1: .word32 2
	LT2: .word32 1
	LT3: .word32 2
	LT4: .word32 3
	LT5: .word32 6
	LT6: .word32 2

.code
	;divisao
	lw $t0, LT1(r0)
	lw $t1, LT2(r0)
	div $t1, $t2
	mflo $t0
	;;;;;;;;;

	lw $t0, LT3(r0)
	lw $t1, LT4(r0)
	mult $t0, $t1
	mflo $t0
	sw $t0, k(r0)

	;;;;;;;;;

	;subtracao
	lw $t0, LT5(r0)
	lw $t1, LT6(r0)
	sub $t0, $t0, $t1
	sw $t1, i(r0)


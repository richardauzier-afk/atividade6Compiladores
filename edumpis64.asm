.data
	a: .space 4

.code
	addi $t1, $t0, #4
	addi $t2, $t1, #5
	sw $t2, a(r0)

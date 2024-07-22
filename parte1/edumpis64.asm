.data
	a: .space 3

.code
	;soma de dois imediatos
	addi $t0, $zero, #4
	addi $t0, $t0, #4
	sw $t0, a(r0)
	add $t0, $zero, $zero
	SYSCALL 0

.data
 
    
    format_string: .asciiz "O resultado de %s eh: %i\n"
    prim_operacao: .asciiz "5+1"
    seg_operacao: .asciiz "7-1"
    ter_operacao: .asciiz "3x3"
    quart_operacao: .asciiz "9/2"
    format_addr: .space 4 ; espaço vazio para receber o endereço do format_string
    operacao_addr: .space 4
    resultado: .space 4

    

.code
    daddi r5, r0, format_string ; soma r0 com o endereço de format_string
    sw r5, format_addr(r0)      ; salva o valor de r5 no format_addr
    
    ;soma
    daddi r5, r0, prim_operacao ; soma r0 com o endereço de prim_operacao
    sw r5, operacao_addr(r0)
    
    addi $t0, r0, #5
    addi $t0, $t0, #1
    sw $t0, resultado(r0)

    daddi r14, r0, format_addr
    SYSCALL 5

import sys
import re


'''
    problemas:
        - repetição da mesma linha: de store e load
'''

data_section_header = f'.data\n' #string que só vai ser concatenada quando a data_section estiver pronta
code_section_header = f'\n.code\n'
data_section_body = ""         
code_section_body = ""

label = ''
count_label = 0


dic_var_valor = {}

def nova_label():
    global count_label, label
    count_label += 1
    label = f'\tLT{count_label}: .word32'
    return label

'''
def novo_temp():
    global count_temp
    if count_temp <= 9:
        count_temp += 1
        return f'$t{count_temp-1} '
''' 



def parse_input_file(arquivo_tres_enderecos):
    # Define a expressão regular que considera ==, operadores e números como tokens separados
    padrao = re.compile(r'>=|<=|==|\b\w+\b|[=+\-*/<]')


    with open(arquivo_tres_enderecos, 'r') as f:
        linhas = [padrao.findall(linha.strip()) for linha in f.readlines() if linha.strip() != ""]

    return linhas
 

def executa_operacao_aritmetica(operando1, operando2, operador):
    match operador:
        case '+':
            return str(int(operando1) + int(operando2))
        case '*':
            return str(int(operando1) * int(operando2))
        case '-':
            return str(int(operando1) - int(operando2))
        case '/':
            return str(round(int(operando1) / int(operando2)))
        
        
#Função que trata as operações de atribuição de cópia
def atribuicao_e_copia(lista_atribcopia):
    global data_section_body
    
    #caso uma variável que já exista esteja recebendo outra atribuição
    #é preciso procurar pela sua definição no .data e substituir pelo novo valor
    if lista_atribcopia[0] in dic_var_valor:
        pattern = rf'^{re.escape(lista_atribcopia[0])}'
        # Dividir a string em linhas e verificar cada linha
        lines = data_section_body.split('\n')
        
        # Modificar a linha encontrada
        for i, line in enumerate(lines):
            if re.search(pattern, line.strip()):
                #Substituir o inteiro ou char na linha encontrada pelo último elemento da lista lista_atribcopia
                parts = line.split()
                
                #Caso seja uma variável recebendo outra varíavel
                if lista_atribcopia[-1] in dic_var_valor:
                    valor = dic_var_valor[lista_atribcopia[-1]]
                    parts[-1] = valor
                    dic_var_valor[lista_atribcopia[0]] = valor 
                #caso seja uma variável recebendo um número
                else:
                    parts[-1] = lista_atribcopia[-1]
                    dic_var_valor[lista_atribcopia[0]] = lista_atribcopia[-1]
                     
                lines[i] = '\t' + ' '.join(parts)
        data_section_body = '\n'.join(lines) #Devolução da nova string para a string original
    else:
        try:
        #Se o ultimo elemento for um int
            if int(lista_atribcopia[-1]):
                data_section_body += f'\t{lista_atribcopia[0]}: .word32 {lista_atribcopia[-1]}\n'
                dic_var_valor[lista_atribcopia[0]] = lista_atribcopia[-1]
        except ValueError:
            #Se o último elemento for um char
            if "'" in lista_atribcopia[-1]:
                data_section_body += f'\t{lista_atribcopia[0]}: .ascii {lista_atribcopia[-1]}\n'
                dic_var_valor[lista_atribcopia[0]] = lista_atribcopia[-1]
            #Se o último elemento for uma variável
            else:
                valor = dic_var_valor[lista_atribcopia[-1]]
                data_section_body += f'\t{lista_atribcopia[0]}: .word32 {valor}\n'

def operacao_aritm(operacao):
    global data_section_body, code_section_body, data_section_header
    
    if operacao[0] not in dic_var_valor:
        data_section_body += f'\t{operacao[0]}: .space 4\n'

    if operacao[2] in dic_var_valor:
        valor_1 = dic_var_valor[operacao[2]]
    elif operacao[2] not in dic_var_valor:
        valor_1 = operacao[2]

    
    if operacao[4] in dic_var_valor:
        valor_2 = dic_var_valor[operacao[4]]
    elif operacao[4] not in dic_var_valor:
        valor_2 = operacao[4]

    if operacao[3] == '+': #adição
        if operacao[2] not in dic_var_valor and operacao[4] not in dic_var_valor: #Significa que os valores são imediatos
            #temp1 = novo_temp()
            #temp2 = novo_temp()
            #print(temp1, temp2)
            code_section_body += f'\t;soma de dois imediatos\n'
            code_section_body += f'\taddi $t0, $zero, #{valor_1}\n'
            code_section_body += f'\taddi $t1, $t0, #{valor_2}\n'
            code_section_body += f'\tsw $t1, {operacao[0]}(r0)\n'
            code_section_body += f'\tadd $t0, $zero, $zero\n'
            code_section_body += f'\tadd $t1, $zero, $zero\n\n'    
        elif operacao[2] in dic_var_valor and operacao[4] not in dic_var_valor:
            #temp1 = novo_temp()
            #temp2 = novo_temp()
            code_section_body += f'\t;soma com uma variável\n'
            code_section_body += f'\tlw $t0, {operacao[2]}(r0)\n'
            code_section_body += f'\taddi $t0, $t0, #{valor_2}\n'
            code_section_body += f'\tsw $t0, {operacao[0]}(r0)\n'
            code_section_body += f'\tadd $t0, $zero, $zero\n\n'
        elif operacao[4] in dic_var_valor and operacao[2] not in dic_var_valor:
            code_section_body += f'\t;soma com uma outra variável\n'
            code_section_body += f'\tlw $t0, {operacao[4]}(r0)\n'
            code_section_body += f'\taddi $t0, $t0, #{valor_1}\n'
            code_section_body += f'\tsw $t0, {operacao[0]}(r0)\n'
            code_section_body += f'\tadd $t0, $zero, $zero\n\n'
        elif operacao[2] in dic_var_valor and operacao[4] in dic_var_valor:
            code_section_body += f'\t;soma com duas variáveis\n'
            code_section_body += f'\tlw $t0, {operacao[2]}(r0)\n'
            code_section_body += f'\tlw $t1, {operacao[4]}(r0)\n'
            code_section_body += f'\tadd $t0, $t0, $t1\n'
            code_section_body += f'\tsw $t0, {operacao[0]}(r0)\n'
            code_section_body += f'\tadd $t0, $zero, $zero\n'
            code_section_body += f'\tadd $t1, $zero, $zero\n\n'
        temp = executa_operacao_aritmetica(valor_1, valor_2, operacao[3])
        dic_var_valor[operacao[0]] = temp

    
    elif operacao[3] == '*' or operacao[3] == '/' or operacao[3] == '-':  # multiplicação
        if operacao[3] == '*':
            data_section_body += f'{nova_label()} {valor_1}\n'
            code_section_body += f'\tlw $t0, LT{count_label}(r0)\n'
            data_section_body += f'{nova_label()} {valor_2}\n' 
            code_section_body += f'\tlw $t1, LT{count_label}(r0)\n'
            code_section_body += f'\tmult $t0, $t1\n'
            code_section_body += f'\tmflo $t0\n'
            code_section_body += f'\tsw $t0, {operacao[0]}(r0)\n'
            code_section_body += f'\tadd $t0, $zero, $zero\n'
            code_section_body += f'\tadd $t1, $zero, $zero\n'
            code_section_body += f'\t;;;;;;;;;\n'
            dic_var_valor[operacao[0]] = executa_operacao_aritmetica(valor_1, valor_2, operacao[3])
        elif operacao[3] == '/': # divisão
            data_section_body += f'{nova_label()} {valor_1}\n'
            code_section_body += f'\t;divisao\n'
            code_section_body += f'\tlw $t0, LT{count_label}(r0)\n'
            data_section_body += f'{nova_label()} {valor_2}\n'
            code_section_body += f'\tlw $t1, LT{count_label}(r0)\n'
            code_section_body += f'\tdiv $t1, $t2\n'
            code_section_body += f'\tmflo $t0\n'
            code_section_body += f'sw $t0, {operacao[0]}(r0)'
            code_section_body += f'\tadd $t0, $zero, $zero\n'
            code_section_body += f'\tadd $t1, $zero, $zero\n'
            code_section_body += f'\t;;;;;;;;;\n'
            dic_var_valor[operacao[0]] = executa_operacao_aritmetica(valor_1, valor_2, operacao[3])
        elif operacao[3] == '-': # subtração
            data_section_body += f'{nova_label()} {valor_1}\n'
            code_section_body += f'\t;subtracao\n'
            code_section_body += f'\tlw $t0, LT{(count_label)}(r0)\n'
            data_section_body += f'{nova_label()} {valor_2}\n'
            code_section_body += f'\tlw $t1, LT{count_label}(r0)\n'
            code_section_body += f'\tsub $t0, $t0, $t1\n'
            code_section_body += f'\tsw $t0, {operacao[0]}(r0)\n'
            code_section_body += f'\tadd $t0, $zero, $zero\n'
            code_section_body += f'\tadd $t1, $zero, $zero\n'
            dic_var_valor[operacao[0]] = executa_operacao_aritmetica(valor_1, valor_2, operacao[3])

def controle_de_fluxo(condicao):
    global code_section_body
    if condicao[0] == 'if' or (condicao[0] == 'goto' and condicao[1] != 'end_if'):
        if condicao[0] == 'goto':
            code_section_body += f'{condicao[1]}\n'
        elif condicao[2] == '<':
            code_section_body += f'\tlw $t5, {condicao[1]}(r0)\n'
            code_section_body += f'\tlw $t6, {condicao[3]}(r0)\n'
            code_section_body += f'\tslt $t7, $t5, $t6\n'
            code_section_body += f'\tBEQZ $t7, '
        elif condicao[2] == '==':
          code_section_body += f'\tlw $t5, {condicao[1]}(r0)\n'
          code_section_body += f'\tlw $t6, {condicao[3]}(r0)\n'
          code_section_body += f'\tBNE $t5, $t6, '
        elif condicao[2] == '<=':
            code_section_body += f'\tlw $t5, {condicao[1]}(r0)\n'
            code_section_body += f'\tlw $t6, {condicao[3]}(r0)\n'
            code_section_body += f'\tslt $t7, $t6, $t5\n'
            code_section_body += f'\tBNEZ $t7, '
        elif condicao[2] == '>=':
            code_section_body += f'\tlw $t5, {condicao[1]}(r0)\n'
            code_section_body += f'\tlw $t6, {condicao[3]}(r0)\n'
            code_section_body += f'\tslt $t7, $t5, $t6\n'
            code_section_body += f'\tBNEZ $t7, '

        
    elif ' '.join(condicao).startswith('L') or ' '.join(condicao) == 'goto end_if':
        print("heehhe")
        if len(condicao) > 1 and condicao[1] == 'end_if':
            print("olá")
            code_section_body += f'\tj end_if\n'
        elif len(condicao) > 1 and condicao[1] != 'end_if':
            if len(condicao) == 4:
                code_section_body += f'{condicao[0]}:\n'
                atribuicao_e_copia(condicao[1:])
                
            
            elif condicao[4] in ['+','-','*','/']:
                code_section_body += f'{condicao[0]}:\n'
                operacao_aritm(condicao[1:])
                
            else:
                print("Não tem")
        else:
            code_section_body += f'{condicao[0]}:\n'
    elif condicao[0] == 'end_if':
        code_section_body += f'{condicao[0]}:\n'       
    
def main(argv):
    global data_section_header
    global code_section_body
    # Captura o nome do arquivo de entrada
    input_file = argv[1]

    linhas = parse_input_file(input_file) #Trata o arquivo
    print(linhas)
    print
    for l in linhas: 
        print(l)
        #Se for igual a 3 é uma atribuição ou cópia
        if len(l) == 3:
            print("Atribuição e cópia\n")
            atribuicao_e_copia(l)
        #Se for uma operação aritmética
        elif len(l) > 3 and l[1] == '=':
            print("Operação aritmética\n")
            operacao_aritm(l)
        elif 'if' in l[0] or (('goto' in l[0]) and ((l[1] != 'end_if'))):
            print("If ou goto")
            controle_de_fluxo(l)
        elif ' '.join(l).startswith('L') or 'end_if' in l:
            print("Label")
            controle_de_fluxo(l)
        

    code_section_body += f'\tSYSCALL 0\n'
    data_section_header += data_section_body + code_section_header + code_section_body #concatena as operações com a string '.data'
    
    save_to_file("edumpis64.asm")

def save_to_file(filename):
        with open(filename, 'w') as f:
            f.write(''.join(data_section_header))  
       
# Executa a função principal
if __name__ == '__main__':
    main(sys.argv)

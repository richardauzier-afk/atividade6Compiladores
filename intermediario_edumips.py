import sys
import re


'''problemas:
        - repetição da mesma linha: de store e load
'''

data_section_header = f'.data\n' #string que só vai ser concatenada quando a data_section estiver pronta
code_section_header = f'\n.code\n'
data_section_body = ""         
code_section_body = ""

label = ''
label_end_if = ''
count_label = 0
count_end_if = 0
dic_var_valor = {}
contador_label = 0

def eh_inteiro(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def nova_label():
    global count_label, label
    count_label += 1
    label = f'\tLT{count_label}: .word32'
    return label

def nova_label_end_if():
    global count_end_if, label_end_if
    label_end_if = f'end_if{count_end_if}'
    count_end_if += 1
    return label_end_if

pilha_labels = []

def gerar_labels_unicos():
    global contador_label
    then_label = f'then{contador_label}'
    else_label = f'else{contador_label}'
    end_if_label = f'end_if{contador_label}'
    contador_label += 1
    return then_label, else_label, end_if_label



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
            code_section_body += f'\t;soma de dois imediatos\n'
            code_section_body += f'\taddi $t0, $zero, #{valor_1}\n'
            code_section_body += f'\taddi $t1, $t0, #{valor_2}\n'
            code_section_body += f'\tsw $t1, {operacao[0]}(r0)\n'
            code_section_body += f'\tadd $t0, $zero, $zero\n'
            code_section_body += f'\tadd $t1, $zero, $zero\n\n'    
        elif operacao[2] in dic_var_valor and operacao[4] not in dic_var_valor:
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
            code_section_body += f'\tadd $t1, $zero, $zero\n\n'
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
            code_section_body += f'\tadd $t1, $zero, $zero\n\n'
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
            code_section_body += f'\tadd $t1, $zero, $zero\n\n'
            dic_var_valor[operacao[0]] = executa_operacao_aritmetica(valor_1, valor_2, operacao[3])

'''
def controle_de_fluxo(condicao):
    global code_section_body
    
    if condicao[0][0] == 'if':
        if condicao[0][2] == '<':
            if eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][3]}\n'
            elif eh_inteiro(condicao[0][1]) and not(eh_inteiro(condicao[0][3])):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            elif not(eh_inteiro(condicao[0][1])) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\tlw $t7, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][3]}\n'
            else:
                code_section_body += f'\tlw $t7, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            code_section_body += f'\tBEQZ $t7, {condicao[1][1]}\n'
        elif condicao[0][2] == '==':
            if eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
              code_section_body += f'\taddi $t5, $zero, #{condicao[0][1]}\n'
              code_section_body += f'\taddi $t6, $zero, #{condicao[0][3]}\n'
            elif eh_inteiro(condicao[0][1]) and not(eh_inteiro(condicao[0][3])):
                code_section_body += f'\taddi $t5, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
            elif not(eh_inteiro(condicao[0][1])) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\tlw $t5, {condicao[0][1]}(r0)\n'
                code_section_body += f'\taddi $t6, $zero, #{condicao[0][3]}\n'
            else:
                code_section_body += f'\tlw $t5, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
            code_section_body += f'\tBNE $t5, $t6, {condicao[1][1]}\n'
        elif condicao[0][2] == '<=':
            if eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][3]}\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][1]}\n'
            elif eh_inteiro(condicao[0][1]) and not(eh_inteiro(condicao[0][3])):
                code_section_body += f'\tlw $t7, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][1]}\n'
            elif not(eh_inteiro(condicao[0][1])) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][3]}\n'
                code_section_body += f'\tlw $t6, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            else:
                code_section_body += f'\tlw $t7, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tlw $t6, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            code_section_body += f'\tBNEZ $t7, {condicao[1][1]}\n'
        elif condicao[0][2] == '>=':
            if eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][3]}\n'
            elif eh_inteiro(condicao[0][1]) and not(eh_inteiro(condicao[0][3])):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            elif not(eh_inteiro(condicao[0][1])) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\tlw $t7, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][3]}\n'
            else:
                code_section_body += f'\tlw $t7, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            code_section_body += f'\tBNEZ $t7, {condicao[1][1]}\n'
        
        code_section_body += f'{condicao[2][0]}:\n'
        
        if condicao[1][1] != 'end_if':
            indice = condicao[3:].index(['else'])
            print(condicao[3:3+indice-1])
            for l in condicao[3:3+indice-1]:
                if l[3] in ['+','-','*','/']:
                    operacao_aritm(l)
                #se for um if chama a funcao recursivamente
            code_section_body += f'\tj end_if\n\n'
            code_section_body += f'else:\n'
            print(condicao[3+indice+1:-1])
            for l1 in condicao[3+indice+1:-1]:
                print(l1)
                if l1[3] in ['+','-','*','/']:
                    operacao_aritm(l1)
                #se for um if chama a funcao recursivamente
            code_section_body += f'end_if:\n'
        else:
            for l in condicao[3:-1]:
                if l[3] in ['+','-','*','/']:
                    operacao_aritm(l)
                #se for um if chama a funcao recursivamente
            code_section_body += f'end_if:\n'

'''
def controle_de_fluxo(condicao):
    global code_section_body
    global pilha_labels

    #end_if_label = f'end_if{nivel}'
    #then_label = f'then{nivel}'
    #else_label = f'else{nivel}'

    
    if condicao[0][0] == 'if':
        then_label, else_label, end_if_label = gerar_labels_unicos()
        print(then_label,else_label,end_if_label)
        pilha_labels.append((then_label, else_label, end_if_label))
        if condicao[0][2] == '<':
            if eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][3]}\n'
            elif eh_inteiro(condicao[0][1]) and not eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            elif not eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\tlw $t7, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][3]}\n'
            else:
                code_section_body += f'\tlw $t7, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            code_section_body += f'\tBEQZ $t7, {condicao[1][1]}\n'
        elif condicao[0][2] == '==':
            if eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t5, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\taddi $t6, $zero, #{condicao[0][3]}\n'
            elif eh_inteiro(condicao[0][1]) and not eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t5, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
            elif not eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\tlw $t5, {condicao[0][1]}(r0)\n'
                code_section_body += f'\taddi $t6, $zero, #{condicao[0][3]}\n'
            else:
                code_section_body += f'\tlw $t5, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
            code_section_body += f'\tBNE $t5, $t6, {condicao[1][1]}\n'
        elif condicao[0][2] == '<=':
            if eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][3]}\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][1]}\n'
            elif eh_inteiro(condicao[0][1]) and not eh_inteiro(condicao[0][3]):
                code_section_body += f'\tlw $t7, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][1]}\n'
            elif not eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][3]}\n'
                code_section_body += f'\tlw $t6, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            else:
                code_section_body += f'\tlw $t7, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tlw $t6, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            code_section_body += f'\tBNEZ $t7, {condicao[1][1]}\n'
        elif condicao[0][2] == '>=':
            if eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][3]}\n'
            elif eh_inteiro(condicao[0][1]) and not eh_inteiro(condicao[0][3]):
                code_section_body += f'\taddi $t7, $zero, #{condicao[0][1]}\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            elif not eh_inteiro(condicao[0][1]) and eh_inteiro(condicao[0][3]):
                code_section_body += f'\tlw $t7, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tslti $t7, $t7, #{condicao[0][3]}\n'
            else:
                code_section_body += f'\tlw $t7, {condicao[0][1]}(r0)\n'
                code_section_body += f'\tlw $t6, {condicao[0][3]}(r0)\n'
                code_section_body += f'\tslt $t7, $t7, $t6\n'
            code_section_body += f'\tBNEZ $t7, {condicao[1][1]}\n'
        
        
        code_section_body += f'{condicao[2][0]}:\n'
        
        if condicao[1][1] != end_if_label:
            i = 0
            j = 0
            indice_then = condicao.index([then_label])
            indice_else = condicao.index([else_label])
            print(indice_then,indice_else)
            bloco_then = condicao[indice_then+1:indice_else-1]
            
            bloco_else = condicao[indice_else + 1:-1]
            print(bloco_then)
            print(bloco_else)
            
            while i < len(bloco_then):
                if 'if' in bloco_then[i][0]: #se for um if
                    controle_de_fluxo(bloco_then)
                    #nivel += 1
                    i += len(bloco_then)+1
                elif len(bloco_then[i]) > 3 and bloco_then[i][3] in ['+','-','*','/']: #se for uma operação aritmética
                    operacao_aritm(bloco_then[i])
                    i += 1
                elif len(bloco_then[i]) == 3:
                    atribuicao_e_copia(bloco_then[i])
                    i += 1
            code_section_body += f'\tj {end_if_label}\n'
            code_section_body += f'{else_label}:\n'
            
            while j < len(bloco_else):
                if 'if' in bloco_else[j][0]: #se for um if
                    print("opa")
                    controle_de_fluxo(bloco_else)
                    #nivel += 1
                    j += len(bloco_else)+1
                elif len(bloco_else[j]) > 3 and bloco_else[j][3] in ['+','-','*','/']: #se for uma operação aritmética
                    operacao_aritm(bloco_else[j])
                    j += 1
                elif len(bloco_else[j]) == 3:
                    atribuicao_e_copia(bloco_else[j])
                    j += 1
            
            code_section_body += f'{end_if_label}:\n'
         
        else:
            print("cabras")
            i = 0
            indic = condicao.index([f'{then_label}'])
            print(indic)
            print(f'Bloco then: {condicao[indic+1:-1]}')
            bloco_then = condicao[indic+1:-1]
            while i < len(bloco_then):
                if 'if' in bloco_then[i][0]: #se for um if
                    controle_de_fluxo(bloco_then)
                    i += len(bloco_then)+1
                elif len(bloco_then[i]) > 3 and bloco_then[i][3] in ['+','-','*','/']: #se for uma operação aritmética
                    operacao_aritm(bloco_then[i])
                    i += 1
                elif len(bloco_then[i]) == 3:
                    atribuicao_e_copia(bloco_then[i])
                    i += 1
            

            code_section_body += f'{end_if_label}:\n'
            pilha_labels.pop()

        
        
    
def main(argv):
    global data_section_header
    global code_section_body
    
    i = 0
    # Captura o nome do arquivo de entrada
    input_file = argv[1]

    linhas = parse_input_file(input_file) #Trata o arquivo
    print(linhas)
    print(f'Tamanho da string: {len(linhas)}')
    
    
    while i < len(linhas):
        if len(linhas[i]) == 3:

            atribuicao_e_copia(linhas[i])
            i += 1
        #Se for uma operação aritmética
        elif len(linhas[i]) > 3 and linhas[i][1] == '=':
            operacao_aritm(linhas[i])
            i += 1
        elif ''.join(linhas[i]).startswith('if'): #se for um if
            end_if = nova_label_end_if()
            indice = linhas[i:].index([end_if]) #{linhas[i+1][1]}
            print("Lá da main: ",linhas[i:indice+i+1])
            controle_de_fluxo(linhas[i:indice+i+1])
            i += indice 
            
        else:
            i += 1
        

    code_section_body += f'\tSYSCALL 0\n'
    data_section_header += data_section_body + code_section_header + code_section_body #concatena as operações com a string '.data'
    
    save_to_file("edumpis64.asm")

def save_to_file(filename):
        with open(filename, 'w') as f:
            f.write(''.join(data_section_header))  
       
# Executa a função principal
if __name__ == '__main__':
    main(sys.argv)

import sys
import re


'''
problemas:
        - Pensar numa maneira mais inteligente de criar as labels do controle de fluxo
'''

data_section_header = f'.data\n' #Cabeçalho da seção data
code_section_header = f'\n.code\n' #Cabeçalho da seção code
data_section_body = ""  #Código edumips64 da seção data       
code_section_body = "" #Código edumips63 da seção code

label_op_mult_div_sub = '' #Essas operações obrigam os operandos estarem em memória
count_label_op_mult_div_sub = 0 #Contador para gerar labels únicas
label_end_if = '' #Label para identificar o fim de um bloco if
count_end_if = 0 #Contador para gerar labels únicas
dic_var_valor = {} #Dicionário para guardar o valor das operações nas respectivas variáveis
contador_label_controle_fluxo = 0 #Contador para gerar labels únicas no controle de fluxo 
pilha_labels_controle_fluxo = [] #Estrutura para guardar as labels do controle de fluxo 


def eh_inteiro(s):
    #Função para indetificar se uma string pode ou não virar um inteiro
    try:
        int(s)
        return True
    except ValueError:
        return False

def nova_label():
    #Função que gera as labels para as operações de multiplicação, divisão, subtração
    global count_label, label_op_mult_div_sub
    count_label += 1
    label_op_mult_div_sub = f'\tLT{count_label}: .word32'
    return label_op_mult_div_sub

def nova_label_end_if():
    #Função que gera as labels para o fim de um bloco if
    global count_end_if, label_end_if
    label_end_if = f'end_if{count_end_if}'
    count_end_if += 1
    return label_end_if

def gerar_labels_unicos_controle_fluxo():
    #Função que gera as labels no contexto de controle fluxo
    global contador_label_controle_fluxo
    then_label = f'then{contador_label_controle_fluxo}'
    else_label = f'else{contador_label_controle_fluxo}'
    end_if_label = f'end_if{contador_label_controle_fluxo}'
    contador_label_controle_fluxo += 1
    return then_label, else_label, end_if_label

def parse_input_file(arquivo_tres_enderecos):
    #Função que trata o arquivo
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
        
        
def atribuicao_e_copia(lista_atribcopia):
    #Função que trata as operações de atribuição e de cópia
    global data_section_body
    
    '''
        Caso uma variável que já exista esteja recebendo outra atribuição
        é preciso procurar pela sua definição no .data e substituir pelo novo valor
    '''
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
                #Caso seja uma variável recebendo um número
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
    #Função que trata as operações aritméticas
    global data_section_body, code_section_body, data_section_header
    
    '''
        Caso a variável não tenha sido inicializada através de atribuição
        é preciso definir um espaço em branco na memória do edumips64
    '''
    if operacao[0] not in dic_var_valor:
        data_section_body += f'\t{operacao[0]}: .space 4\n'

    '''
        Recupera os valores, tanto os valores que as varíaveis guardam quanto um imediato
    '''
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
        elif operacao[2] in dic_var_valor and operacao[4] not in dic_var_valor: #O primeiro é imediato e o outro não
            code_section_body += f'\t;soma com uma variável\n'
            code_section_body += f'\tlw $t0, {operacao[2]}(r0)\n'
            code_section_body += f'\taddi $t0, $t0, #{valor_2}\n'
            code_section_body += f'\tsw $t0, {operacao[0]}(r0)\n'
            code_section_body += f'\tadd $t0, $zero, $zero\n\n'
        elif operacao[4] in dic_var_valor and operacao[2] not in dic_var_valor: #O segundo é imediato e o primeiro não
            code_section_body += f'\t;soma com uma outra variável\n'
            code_section_body += f'\tlw $t0, {operacao[4]}(r0)\n'
            code_section_body += f'\taddi $t0, $t0, #{valor_1}\n'
            code_section_body += f'\tsw $t0, {operacao[0]}(r0)\n'
            code_section_body += f'\tadd $t0, $zero, $zero\n\n'
        elif operacao[2] in dic_var_valor and operacao[4] in dic_var_valor: #Os dois são variáveis
            code_section_body += f'\t;soma com duas variáveis\n'
            code_section_body += f'\tlw $t0, {operacao[2]}(r0)\n'
            code_section_body += f'\tlw $t1, {operacao[4]}(r0)\n'
            code_section_body += f'\tadd $t0, $t0, $t1\n'
            code_section_body += f'\tsw $t0, {operacao[0]}(r0)\n'
            code_section_body += f'\tadd $t0, $zero, $zero\n'
            code_section_body += f'\tadd $t1, $zero, $zero\n\n'
        temp = executa_operacao_aritmetica(valor_1, valor_2, operacao[3])
        dic_var_valor[operacao[0]] = temp #Atualiza o valor variável que recebeu a operação de adição

    
    elif operacao[3] == '*' or operacao[3] == '/' or operacao[3] == '-':  # multiplicação, divisão ou subtração
        if operacao[3] == '*': #Multiplicação
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
        elif operacao[3] == '/': #Divisão
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
        elif operacao[3] == '-': #Subtração
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


def controle_de_fluxo(condicao):
    global code_section_body
    global pilha_labels_controle_fluxo

    if condicao[0][0] == 'if':
        then_label, else_label, end_if_label = gerar_labels_unicos_controle_fluxo()
        print(then_label,else_label,end_if_label)
        pilha_labels_controle_fluxo.append((then_label, else_label, end_if_label))
        
        '''
            Trata as operações possíveis do código de 3 endereços
            <, <=, == e >=
        '''
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
        
        
        code_section_body += f'{condicao[2][0]}:\n' #Label then
        
        if condicao[1][1] != end_if_label: #Se o bloco if tiver um else
            i = 0 #Contador para percorrer o bloco then
            j = 0 #Contador para percorrer o bloco else
            indice_then = condicao.index([then_label])
            indice_else = condicao.index([else_label])
            print(indice_then,indice_else)
            
            bloco_then = condicao[indice_then+1:indice_else-1] #Captura somente o código dentro do bloco then
            bloco_else = condicao[indice_else + 1:-1] #Captura somente o código dentro do bloco else
            
            print(bloco_then)
            print(bloco_else)
            
            while i < len(bloco_then): #Trata o código do bloco then
                if 'if' in bloco_then[i][0]: #se for um if
                    controle_de_fluxo(bloco_then) #Chamada recursiva
                    i += len(bloco_then)+1
                elif len(bloco_then[i]) > 3 and bloco_then[i][3] in ['+','-','*','/']: #Se for uma operação aritmética
                    operacao_aritm(bloco_then[i])
                    i += 1
                elif len(bloco_then[i]) == 3: #Se for uma atribuição ou cópia
                    atribuicao_e_copia(bloco_then[i])
                    i += 1
            code_section_body += f'\tj {end_if_label}\n' #Salto incondicional
            code_section_body += f'{else_label}:\n' #label else
            
            while j < len(bloco_else): #Trata o código do bloco else
                if 'if' in bloco_else[j][0]: #Se for um if
                    controle_de_fluxo(bloco_else) #Chamada recursiva
                    j += len(bloco_else)+1
                elif len(bloco_else[j]) > 3 and bloco_else[j][3] in ['+','-','*','/']: #Se for uma operação aritmética
                    operacao_aritm(bloco_else[j])
                    j += 1
                elif len(bloco_else[j]) == 3: #Se for uma atribuição ou cópia
                    atribuicao_e_copia(bloco_else[j])
                    j += 1
            
            code_section_body += f'{end_if_label}:\n'
         
        else: #Caso o bloco if não tenha um else
            i = 0 #Contador para percorrer o bloco then
            indic = condicao.index([f'{then_label}'])
            print(f'Bloco then: {condicao[indic+1:-1]}')
            bloco_then = condicao[indic+1:-1]
            while i < len(bloco_then):
                if 'if' in bloco_then[i][0]: #Se for um if
                    controle_de_fluxo(bloco_then) #Chamada recursiva
                    i += len(bloco_then)+1
                elif len(bloco_then[i]) > 3 and bloco_then[i][3] in ['+','-','*','/']: #Se for uma operação aritmética
                    operacao_aritm(bloco_then[i])
                    i += 1
                elif len(bloco_then[i]) == 3: #Se for uma atribuição ou cópia
                    atribuicao_e_copia(bloco_then[i])
                    i += 1
            

            code_section_body += f'{end_if_label}:\n'
            pilha_labels_controle_fluxo.pop() #Pop na pilha

        
        
    
def main(argv):
    global data_section_header
    global code_section_body
    
    i = 0 #Contador para gerenciar o caminhar pela lista de linhas
    # Captura o nome do arquivo de entrada
    input_file = argv[1]

    linhas = parse_input_file(input_file) #Trata o arquivo
    print(linhas)
    
    while i < len(linhas): #Irá percorrer as linhas e tratar cada caso
        #Se for uma atribuição ou cópia
        if len(linhas[i]) == 3:
            atribuicao_e_copia(linhas[i])
            i += 1
        #Se for uma operação aritmética
        elif len(linhas[i]) > 3 and linhas[i][1] == '=':
            operacao_aritm(linhas[i])
            i += 1
        elif ''.join(linhas[i]).startswith('if'): #se for um if
            end_if = nova_label_end_if() #Label que delimita o fim de um bloco if
            indice = linhas[i:].index([end_if]) #{linhas[i+1][1]}
            print("Lá da main: ",linhas[i:indice+i+1])
            controle_de_fluxo(linhas[i:indice+i+1])
            i += indice 
        #Qualquer outra linha que não se encaixa    
        else:
            i += 1
        

    code_section_body += f'\tSYSCALL 0\n' #Fim do código edumips64
    data_section_header += data_section_body + code_section_header + code_section_body #concatena tudo
    
    save_to_file("edumpis64.asm") #Salva a string em um arquivo

def save_to_file(filename):
    #Função para salvar o código edumips64 em um arquivo
        with open(filename, 'w') as f:
            f.write(''.join(data_section_header))  
       
# Executa a função principal
if __name__ == '__main__':
    main(sys.argv)

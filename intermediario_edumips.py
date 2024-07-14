import sys
import re
import logging

data_section_header = f'.data\n' #string que só vai ser concatenada quando a data_section estiver pronta
code_section_header = f'\n.code\n'
data_section_body = ""         
code_section_body = ""

dic_var_valor = {}

# trata o arquivo 3 endereços
def parse_input_file(arquivo_tres_enderecos): 
    with open(arquivo_tres_enderecos,'r') as f:
        linhas = [linha.strip().lower().split() for linha in f.readlines() if linha.strip() != ""]
    return linhas

def executa_operacao_aritmetica(operando1, operando2, operador):
    match operador:
        case '+':
            return operando1 + operando2

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
    global data_section_body
    global data_section_header
    global code_section_body
    
    if operacao[0] not in dic_var_valor:
        if operacao[3] == '+':  
            data_section_header += f'\t{operacao[0]}: .space 4\n'
            code_section_body += f'\taddi $t1, $t0, #{operacao[2]}\n'
            code_section_body += f'\taddi $t2, $t1, #{operacao[4]}\n'
            code_section_body += f'\tsw $t2, {operacao[0]}(r0)\n'
            
            temp = executa_operacao_aritmetica(operacao[2], operacao[4], operacao[2])
            dic_var_valor[operacao[0]] = temp


def main(argv):
    global data_section_header
    # Captura o nome do arquivo de entrada
    input_file = argv[1]

    linhas = parse_input_file(input_file) #Trata o arquivo

    for l in linhas: 
        print(l)
        # se for igual a 3 é uma atribuição ou cópia
        if len(l) == 3:
            atribuicao_e_copia(l)
        elif len(l) > 3 and '=' in l:
            operacao_aritm(l)        
        

        
    data_section_header += data_section_body + code_section_header + code_section_body #concatena as operações com a string '.data'
    
    save_to_file("edumpis64.asm")

def save_to_file(filename):
        with open(filename, 'w') as f:
            f.write(''.join(data_section_header))  
       
# Executa a função principal
if __name__ == '__main__':
    main(sys.argv)

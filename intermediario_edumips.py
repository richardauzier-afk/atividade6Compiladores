import sys
import re

data_section_header = f'.data\n' #string que só vai ser concatenada quando a data_section estiver pronta
data_section_body = ""          
dic_var_valor = {}

# trata o arquivo 3 endereços
def parse_input_file(arquivo_tres_enderecos): 
    with open(arquivo_tres_enderecos,'r') as f:
        linhas = [linha.strip().lower().split() for linha in f.readlines() if linha.strip() != ""]
    return linhas

def atribuicao_e_copia(atrib):
    global data_section_body
    # Procurar atrib[0] no início de cada linha
    #caso uma variavel que já exista esteja recebendo outra atribuição
    if atrib[0] in dic_var_valor:
        pattern = rf'^{re.escape(atrib[0])}'
        # Dividir a string em linhas e verificar cada linha
        lines = data_section_body.split('\n')
        #print(lines)
        

        # Modificar a linha encontrada
        for i, line in enumerate(lines):
            #print(line)
            print(i)
            #print(line.split())
            if re.search(pattern, line.strip()):  # strip() remove espaços em branco no início e fim da linha
                #print(line)
                # Substituir o número na linha encontrada pelo último elemento da lista atrib
                parts = line.split()
                
                if atrib[-1] in dic_var_valor:
                    valor = dic_var_valor[atrib[-1]]
                    #print(valor)
                    parts[-1] = valor
                    dic_var_valor[atrib[0]] = valor 
                    #data_section_body += f'\t{atrib[0]}: .word32 {valor}\n'
                else:
                    parts[-1] = atrib[-1]
                    dic_var_valor[atrib[0]] = atrib[-1]
                    #dic_var_valor[atrib[-1]] = parts[-1] 
                lines[i] = '\t' + ' '.join(parts)
        data_section_body = '\n'.join(lines)
    else:
        try:
        # se o ultimo elemento for um int
            if int(atrib[-1]):
                data_section_body += f'\t{atrib[0]}: .word32 {atrib[-1]}\n'
                dic_var_valor[atrib[0]] = atrib[-1]
        except ValueError:
            #se o último elemento for um char
            if "'" in atrib[-1]:
                data_section_body += f'\t{atrib[0]}: .ascii {atrib[-1]}\n'
                dic_var_valor[atrib[0]] = atrib[-1]
            #se o último elemento for uma variável
            else:
                valor = dic_var_valor[atrib[-1]]
                data_section_body += f'\t{atrib[0]}: .word32 {valor}\n'

    
    
def main(argv):
    global data_section_header
    # Captura o nome do arquivo de entrada
    input_file = argv[1]

    linhas = parse_input_file(input_file)

    for l in linhas: 
        print(l)
        # se for igual a 3 é uma atribuição
        if len(l) == 3:
            atribuicao_e_copia(l)
    data_section_header += data_section_body
    save_to_file("edumpis64.asm")

def save_to_file(filename):
        with open(filename, 'w') as f:
            f.write(''.join(data_section_header))  
       
# Executa a função principal
if __name__ == '__main__':
    main(sys.argv)

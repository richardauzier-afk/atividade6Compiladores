import sys

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

    try:
        # se o ultimo elemento for um int
        if int(atrib[-1]):
            data_section_body += f'\t{atrib[0]}: .word32 {atrib[-1]}\n'
            dic_var_valor[atrib[0]] = atrib[-1]
    except ValueError:
        #se o último elemento for um char
        if atrib[-1] not in dic_var_valor:
            data_section_body += f'\t{atrib[0]}: .ascii {atrib[-1]}\n'
        #se o último elemento for uma variável
        else:
            valor = dic_var_valor[-1]
            data_section_body += f'\t{atrib[0]}: .word32 {valor}'

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

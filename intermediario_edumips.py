import sys

# trata o arquivo 3 endereços
def parse_input_file(arquivo_tres_enderecos): 
    with open(arquivo_tres_enderecos,'r') as f:
        linhas = [linha.strip().lower().split() for linha in f.readlines() if linha.strip() != ""]
    return linhas

def main(argv):
    # Captura o nome do arquivo de entrada
    input_file = argv[1]

    linhas = parse_input_file(input_file)
    
       
# Executa a função principal
if __name__ == '__main__':
    main(sys.argv)

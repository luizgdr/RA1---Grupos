# Luís Felipe Yoshio Sato, Luiz Guilherme Durau Rodrigues, Pedro Lunardelli Antunes, Thiago Vinícius Pereira Borges

# converte uma linha de expressão em uma lista de tokens
def lexical_analyzer(line: str) -> list:
    tokens = []
    i = 0
    length = len(line)
    while i < length:
        char = line[i]
        # ignora whitespace
        if char.isspace():
            i += 1
            continue

        # valida a proposição
        if char.isdigit():
            start = i
            i += 1
            # continua enquanto houver dígitos ou letras minúsculas
            while i < length and (line[i].isdigit() or (line[i].isalpha() and line[i].islower())):
                i += 1
            token_val = line[start:i]
            tokens.append(token_val)
            # continue pois i já está na posição após o último caractere do token
            continue

        # reconhece constante(true/false) ou identifica token inválido começando por letra
        if char.isalpha():
            start = i
            i += 1
            while i < length and line[i].isalpha():
                i += 1
            token_val = line[start:i]
            if token_val == "true" or token_val == "false":
                tokens.append(token_val)
            else:
                # sequência de letras que não forma true nem false = token inválido
                raise ValueError(f"Erro léxico: token inválido '{token_val}'")
            continue

        # reconhece operador lógico (começa com '\\' + nome do operador)
        if char == '\\':
            i += 1
            start = i
            # verifica letras após a barra
            while i < length and line[i].isalpha():
                i += 1
            op_name = line[start:i]       # parte textual do operador (sem a barra)
            if op_name == "":
                # \ isolado sem seguir de letras
                raise ValueError("Erro léxico: '\\' não seguido de um operador válido")
            token_val = '\\' + op_name    # coloca a barra de volta
            # verifica se corresponde a um dos operadores
            operadores_validos = ["\\neg", "\\wedge", "\\vee", "\\rightarrow", "\\leftrightarrow"]
            if token_val in operadores_validos:
                tokens.append(token_val)
            else:
                raise ValueError(f"Erro léxico: operador desconhecido '{token_val}'")
            continue

        # reconhece parênteses
        if char == '(' or char == ')':
            tokens.append(char)
            i += 1
            continue

        # qualquer outro caractere é inválido
        raise ValueError(f"Erro léxico: caractere inválido '{char}'")

    return tokens

class LL1Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.index = 0  # índice atual no fluxo de tokens
        # conjuntos de tokens para verificação
        self.UNARY_OPS = {"\\neg"}
        self.BINARY_OPS = {"\\wedge", "\\vee", "\\rightarrow", "\\leftrightarrow"}
        self.CONSTANTES = {"true", "false"}

    # faz análise recursiva da fórmula a partir do token atual. True se for válida; valueError caso tenha erro sintático
    def parse_formula(self) -> bool:
        if self.index >= len(self.tokens):
            # chegou ao fim inesperadamente (esperava uma fórmula)
            raise ValueError("Sintaxe inválida: fórmula incompleta")

        token = self.tokens[self.index]

        # se for uma constante
        if token in self.CONSTANTES:
            self.index += 1
            return True

        # se for uma proposição
        if token and token[0].isdigit():
            # o analisador lexico já garante que toda sequência iniciada por dígito será composta apenas de dígitos e letras válidas.
            self.index += 1
            return True

        # se o token for ( então espera uma fórmula unária ou binária
        if token == '(':
            self.index += 1
            if self.index >= len(self.tokens):
                # após ( deve haver algo (operador) antes de terminar a entrada
                raise ValueError("Sintaxe inválida: esperado operador após '('")

            # verifica o próximo token após (
            op_token = self.tokens[self.index]
            # caso de operador unário
            if op_token in self.UNARY_OPS:
                self.index += 1
                # analise recursiva da fórmula
                self.parse_formula()
                # espera um )
                if self.index >= len(self.tokens) or self.tokens[self.index] != ')':
                    raise ValueError("Sintaxe inválida: esperado ')' após fórmula unária")
                self.index += 1
                return True

            # caso de operador binário
            elif op_token in self.BINARY_OPS:
                self.index += 1
                # analise da primeira subfórmula
                self.parse_formula()
                # analisa da segunda subfórmula
                self.parse_formula()
                # espera um )
                if self.index >= len(self.tokens) or self.tokens[self.index] != ')':
                    raise ValueError("Sintaxe inválida: esperado ')' após fórmulas binárias")
                self.index += 1
                return True

            # se o token após ( não for um operador válido, erro
            else:
                raise ValueError(f"Sintaxe inválida: operador desconhecido ou fora de lugar '{op_token}'")

        # se nenhum dos casos acima baterem, o token atual não pode iniciar uma fórmula válida
        raise ValueError(f"Sintaxe inválida: token inesperado '{token}'")

# Valida a linha
def validate_expression(expr: str) -> str:
    try:
        tokens = lexical_analyzer(expr)
    except ValueError:
        # erro léxico
        return "invalida"
    parser = LL1Parser(tokens)
    try:
        parser.parse_formula()
        # verifica se todos os tokens foram consumidos
        if parser.index != len(tokens):
            # sobrou tokens não utilizados
            return "invalida"
        return "valida"
    except ValueError:
        # erro sintático
        return "invalida"

# Valida a linha
def validate_expression(expr: str) -> str:
    try:
        tokens = lexical_analyzer(expr)
    except ValueError:
        # erro léxico
        return "invalida"
    parser = LL1Parser(tokens)
    try:
        parser.parse_formula()
        # verifica se todos os tokens foram consumidos
        if parser.index != len(tokens):
            # sobrou tokens não utilizados
            return "invalida"
        return "valida"
    except ValueError:
        # erro sintático
        return "invalida"

def process_file(filename: str):
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    if not lines:
        # print("Arquivo vazio ou formato inválido")
        return
    # primeira linha deve ser um inteiro
    try:
        count = int(lines[0].strip())
    except ValueError:
        # print("Formato inválido: a primeira linha não é um número inteiro")
        return
    expressions = lines[1:]
    if count > len(expressions):
        # print("Aviso: O arquivo declara mais expressões do que as fornecidas")
        count = len(expressions)
    # processa cada expressão
    for i in range(min(count, len(expressions))):
        expr = expressions[i]
        result = validate_expression(expr)
        print(result)

def main():
    process_file("arquivo1.txt")

if __name__ == "__main__":
    main()
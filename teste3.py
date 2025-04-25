import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

def saudacao_usuario():
    """
    Solicita o nome do usuário e imprime uma saudação.

    Returns:
        str: Nome do usuário.
    """
    nome = input("Digite seu nome: ").strip()
    print(f"\nOlá, {nome}! Vamos começar o monitoramento de valores.\n")
    return nome

def parsear_numero(valor_str):
    """
    Converte uma string representando um número com separadores brasileiros/europeus
    para float. Retorna None se a conversão falhar.

    Args:
        valor_str (str): Número como string (ex: "1.234,56").

    Returns:
        float or None: Valor numérico convertido ou None se falhar.
    """
    valor_str = valor_str.replace('.', '').replace(',', '.')
    try:
        return float(valor_str)
    except ValueError:
        return None

def registrar_log(mensagem):
    """
    Registra uma mensagem no log com timestamp.

    Args:
        mensagem (str): Mensagem a ser registrada no log.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("log_monitoramento.txt", "a", encoding='utf-8') as log_file:
        log_file.write(f"[{timestamp}] {mensagem}\n")

def extrair_numeros(url, termos_busca):
    """
    Acessa a URL fornecida, extrai o texto da página e identifica os números
    próximos aos termos de busca usando expressões regulares.

    Args:
        url (str): URL da página a ser monitorada.
        termos_busca (list): Lista de palavras-chave para buscar números próximos.

    Returns:
        tuple: Lista de todos os números encontrados e dicionário com números por termo.
    """
    try:
        # Header para evitar bloqueios por bots
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lança exceção se falhar

        soup = BeautifulSoup(response.text, 'html.parser')
        texto = soup.get_text()

        # Captura todos os números da página com ou sem símbolo
        numeros_brutos = re.findall(r'[\$€R\$%]?\s?(\d{1,3}(?:[\.,]\d{3})*[\.,]?\d*)', texto)
        numeros = [parsear_numero(n) for n in numeros_brutos if parsear_numero(n) is not None]
        
        resultados = {}
        for termo in termos_busca:
            # Busca até 50 caracteres após o termo para encontrar número próximo
            padrao = re.compile(
                rf"{termo}.{{0,50}}?([\$€R\$%]?\s?\d{{1,3}}(?:[\.,]\d{{3}})*[\.,]?\d*)",
                re.IGNORECASE
            )
            matches = padrao.findall(texto)
            if matches:
                resultados[termo] = matches
        
        return numeros, resultados

    except requests.RequestException as e:
        erro_msg = f"Erro ao acessar a URL: {e}"
        print(erro_msg)
        registrar_log(erro_msg)
        return [], {}

def monitorar_variacoes(url, termos_busca, intervalo=30):
    """
    Monitora continuamente a URL em busca de mudanças nos valores associados aos termos.

    Args:
        url (str): URL a ser monitorada.
        termos_busca (list): Lista de termos a serem rastreados.
        intervalo (int): Intervalo entre verificações, em segundos.
    """
    valores_anteriores = {}
    
    while True:
        numeros_atuais, resultados_atuais = extrair_numeros(url, termos_busca)
        
        for termo in termos_busca:
            if termo in resultados_atuais:
                # Verifica se houve mudança desde a última verificação
                if termo not in valores_anteriores or resultados_atuais[termo] != valores_anteriores[termo]:
                    msg = f"📌 Alteração no valor de '{termo}': {', '.join(resultados_atuais[termo])}"
                    print(f"\n{msg}")
                    registrar_log(msg)
                    valores_anteriores[termo] = resultados_atuais[termo]
        
        if not resultados_atuais:
            msg = "Nenhuma alteração detectada nos termos monitorados."
            print(msg)
            registrar_log(msg)

        # Aguarda pelo intervalo antes de verificar novamente
        time.sleep(intervalo)

# ======= Programa Principal =======

# Solicita informações do usuário
usuario = saudacao_usuario()

# Pede a URL de monitoramento
url = input("Digite a URL para monitoramento de valores: ").strip()

# Coleta os termos a serem monitorados
termos_input = input("Digite os termos para monitorar (separados por vírgula): ").strip()
termos_busca = [termo.strip() for termo in termos_input.split(',') if termo.strip()]

# Log de início
print("\nIniciando monitoramento...")
print(f"URL: {url}")
registrar_log(f"Usuário '{usuario}' iniciou monitoramento da URL: {url} com termos: {', '.join(termos_busca)}")

# Inicia o monitoramento
monitorar_variacoes(url, termos_busca)


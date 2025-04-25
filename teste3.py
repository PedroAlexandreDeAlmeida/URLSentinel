import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

def saudacao_usuario():
    nome = input("Digite seu nome: ").strip()
    print(f"\nOlá, {nome}! Vamos começar o monitoramento de valores.\n")
    return nome

def parsear_numero(valor_str):
    valor_str = valor_str.replace('.', '').replace(',', '.')
    try:
        return float(valor_str)
    except ValueError:
        return None

def registrar_log(mensagem):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("log_monitoramento.txt", "a", encoding='utf-8') as log_file:
        log_file.write(f"[{timestamp}] {mensagem}\n")

def extrair_numeros(url, termos_busca):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        texto = soup.get_text()

        numeros_brutos = re.findall(r'[\$€R\$%]?\s?(\d{1,3}(?:[\.,]\d{3})*[\.,]?\d*)', texto)
        numeros = [parsear_numero(n) for n in numeros_brutos if parsear_numero(n) is not None]
        
        resultados = {}
        for termo in termos_busca:
            if re.search(termo, texto, re.IGNORECASE):
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
    valores_anteriores = {}
    
    while True:
        numeros_atuais, resultados_atuais = extrair_numeros(url, termos_busca)
        
        for termo in termos_busca:
            if termo in resultados_atuais:
                if termo not in valores_anteriores or resultados_atuais[termo] != valores_anteriores[termo]:
                    msg = f"📌 Alteração no valor de '{termo}': {', '.join(resultados_atuais[termo])}"
                    print(f"\n{msg}")
                    registrar_log(msg)
                    valores_anteriores[termo] = resultados_atuais[termo]
        
        if not resultados_atuais:
            msg = "Nenhuma alteração detectada nos termos monitorados."
            print(msg)
            registrar_log(msg)
        
        time.sleep(intervalo)

# Programa principal
usuario = saudacao_usuario()
url = input("Digite a URL para monitoramento de valores: ").strip()

termos_input = input("Digite os termos para monitorar (separados por vírgula): ").strip()
termos_busca = [termo.strip() for termo in termos_input.split(',') if termo.strip()]

print("\nIniciando monitoramento...")
print(f"URL: {url}")
registrar_log(f"Usuário '{usuario}' iniciou monitoramento da URL: {url} com termos: {', '.join(termos_busca)}")

monitorar_variacoes(url, termos_busca)

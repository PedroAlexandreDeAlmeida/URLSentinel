import requests # Extrai todo o texto puro da página
from bs4 import BeautifulSoup # Faz o parser (leitura estruturada) do HTML
import re # Usado para expressões regulares, encontrar padrões no texto
import time # Usado para pausar o código entre os ciclos de monitoramento


def saudacao_usuario():
    nome = input("Digite seu nome: ").strip()
    print(f"\nOlá, {nome}! Vamos começar o monitoramento de valores.\n")
    return nome
    
def extrair_numeros(url):
    try:
        response = requests.get(url) # Acessa a URL fornecida
        soup = BeautifulSoup(response.text, 'html.parser') # Lê o conteúdo HTML da página
        texto = soup.get_text() # Extrai todo o texto puro da página

        # Encontra todos os números com vírgula, ponto, porcentagem, moeda, etc.
        numeros = re.findall(r'[\$€R\$%]?\s?(\d{1,3}(?:[\.,]\d{3})*[\.,]?\d*)', texto)
        return numeros
    except Exception as e:
        print(f"Erro ao acessar a URL: {e}")
        return []

def monitorar_variacoes(url, intervalo=60):
    valores_anteriores = set() # Armazena os valores numéricos anteriores, sem repetições
    
    while True:
        numeros_atuais = extrair_numeros(url)
        novos_valores = set(numeros_atuais) - valores_anteriores
        
        if novos_valores:
            print(f"\n🔔 Novos valores detectados: {', '.join(novos_valores)}")
            valores_anteriores.update(novos_valores)  # Atualiza o conjunto de valores monitorados
        else:
            print(f"Nenhuma alteração detectada... Total monitorado: {len(valores_anteriores)}")
        
        time.sleep(intervalo)
        
        # Qualquer url especifica, que tenham valores que alterem de acordo com tempo
usuario = saudacao_usuario()
url = input("Digite a URL para monitoramento de valores: ").strip()

# Monitora a variação dos valores a cada 1 minutos
monitorar_variacoes(url, intervalo=60)

#1º Requisições para o usário de URL e valor a serem monitorados;
#2º Identificar (strings) dos valores lidos: dólar, clima, etc;
#3º Login do usuário;
#4º Como fazer o código identiticar e ler apenas o valor inserido pelo usuário;
#5º Docstrings para documentação

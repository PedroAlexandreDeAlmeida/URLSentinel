import requests
from bs4 import BeautifulSoup # Faz o parser (leitura estruturada) do HTML
import re
import time

def saudacao_usuario():
    nome = input("Digite seu nome: ").strip()
    print(f"\nOlá, {nome}! Vamos começar o monitoramento de valores.\n")
    return nome
    
def extrair_numeros(url, termos_busca):
    try:
        # Adicionando cabeçalho User-Agent para simular um navegador
        headers = {
            'User -Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lança um erro se a requisição falhar
        soup = BeautifulSoup(response.text, 'html.parser')
        texto = soup.get_text()

        # Encontra todos os números com vírgula, ponto, porcentagem, moeda, etc.
        numeros = re.findall(r'[\$€R\$%]?\s?(\d{1,3}(?:[\.,]\d{3})*[\.,]?\d*)', texto)
        
        # Agora vamos tentar associar os números aos termos buscados
        resultados = {}
        for termo in termos_busca:
            # Procura o termo no texto (case insensitive)
            if re.search(termo, texto, re.IGNORECASE):
                # Encontra números próximos ao termo (dentro de 50 caracteres)
                padrao = re.compile(f"{termo}.{{0,50}}?([\$€R\$%]?\s?\d{{1,3}}(?:[\.,]\d{{3}})*[\.,]?\d*)", re.IGNORECASE)
                matches = padrao.findall(texto)
                if matches:
                    resultados[termo] = matches
        
        return numeros, resultados
    except requests.RequestException as e:
        print(f"Erro ao acessar a URL: {e}")
        return [], {}

def monitorar_variacoes(url, termos_busca, intervalo=60):
    valores_anteriores = {}
    
    while True:
        numeros_atuais, resultados_atuais = extrair_numeros(url, termos_busca)
        
        # Verifica mudanças nos termos específicos
        for termo in termos_busca:
            if termo in resultados_atuais:
                if termo not in valores_anteriores or resultados_atuais[termo] != valores_anteriores[termo]:
                    print(f"\n📌 Alteração no valor de '{termo}': {', '.join(resultados_atuais[termo])}")
                    valores_anteriores[termo] = resultados_atuais[termo]
        
        if not resultados_atuais:
            print("Nenhuma alteração detectada nos termos monitorados.")
        
        time.sleep(intervalo)

# Programa principal
usuario = saudacao_usuario()
url = input("Digite a URL para monitoramento de valores: ").strip()

# Solicita os termos específicos para monitorar (como "dólar", "temperatura", etc.)
termos_input = input("Digite os termos para monitorar (separados por vírgula): ").strip()
termos_busca = [termo.strip() for termo in termos_input.split(',') if termo.strip()]

print("\nIniciando monitoramento...")
print(f"URL: {url}")
print(f"Termos monitorados: {', '.join(termos_busca) if termos_busca else 'Todos os valores numéricos'}")
print("Pressione Ctrl+C para parar o monitoramento.\n")

# Monitora a variação dos valores
try:
    monitorar_variacoes(url, termos_busca, intervalo=60)
except KeyboardInterrupt:
    print("\nMonitoramento encerrado pelo usuário.")

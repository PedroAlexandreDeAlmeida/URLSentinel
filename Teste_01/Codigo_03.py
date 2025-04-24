import requests
from bs4 import BeautifulSoup
import re
import time

def saudacao_usuario():
    nome = input("Digite seu nome: ").strip()
    print(f"\nOlá, {nome}! Vamos começar o monitoramento de valores.\n")
    return nome
    
def extrair_numeros(url, termos_busca):
    try:
        response = requests.get(url)
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
    except Exception as e:
        print(f"Erro ao acessar a URL: {e}")
        return [], {}

def monitorar_variacoes(url, termos_busca, intervalo=60):
    valores_anteriores = set()
    resultados_anteriores = {}
    
    while True:
        numeros_atuais, resultados_atuais = extrair_numeros(url, termos_busca)
        novos_valores = set(numeros_atuais) - valores_anteriores
        
        # Verifica mudanças nos números gerais
        if novos_valores:
            print(f"\n🔔 Novos valores detectados: {', '.join(novos_valores)}")
            valores_anteriores.update(novos_valores)
        
        # Verifica mudanças nos termos específicos
        for termo in termos_busca:
            if termo in resultados_atuais and (termo not in resultados_anteriores or 
                                             resultados_atuais[termo] != resultados_anteriores[termo]):
                print(f"\n📌 Alteração no valor de '{termo}': {', '.join(resultados_atuais[termo])}")
        
        resultados_anteriores = resultados_atuais
        
        if not novos_valores and resultados_anteriores == resultados_atuais:
            print(f"Nenhuma alteração detectada... Total monitorado: {len(valores_anteriores)}")
        
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

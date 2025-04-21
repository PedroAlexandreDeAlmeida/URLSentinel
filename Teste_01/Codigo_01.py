import requests
from bs4 import BeautifulSoup
import re
import time

def extrair_numeros(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        texto = soup.get_text()

        # Encontra todos os números com vírgula, ponto, porcentagem, moeda, etc.
        numeros = re.findall(r'[\$€R\$%]?\s?(\d{1,3}(?:[\.,]\d{3})*[\.,]?\d*)', texto)
        return numeros
    except Exception as e:
        print(f"Erro ao acessar a URL: {e}")
        return []

def monitorar_variacoes(url, intervalo=60):
    valores_anteriores = set()
    
    while True:
        numeros_atuais = extrair_numeros(url)
        novos_valores = set(numeros_atuais) - valores_anteriores
        
        if novos_valores:
            print(f"\n🔔 Novos valores detectados: {', '.join(novos_valores)}")
            valores_anteriores.update(novos_valores)
        else:
            print(f"Nenhuma alteração detectada... Total monitorado: {len(valores_anteriores)}")
        
        time.sleep(intervalo)
        
        # Qualquer url especifica, que tenham valores que alterem de acordo com tempo
url = "https://economia.uol.com.br/cotacoes/bolsas/"  

# Monitora a variação dos valores a cada 1 minutos
monitorar_variacoes(url, intervalo=60)

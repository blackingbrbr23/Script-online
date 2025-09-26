from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def buscar_links_google_maps(palavra_chave):
    url = f"https://www.google.com/maps/search/{palavra_chave.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"Erro ao acessar o Google Maps: {e}")
        return []

    soup = BeautifulSoup(r.text, 'html.parser')
    links = set(a['href'] for a in soup.find_all('a', href=True) if 'maps/place' in a['href'])
    return list(links)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/coletar', methods=['POST'])
def coletar():
    palavra_chave = request.form.get('palavra_chave', '').strip()
    if not palavra_chave:
        return render_template('result.html', links=[], error="Nenhuma palavra-chave fornecida.")

    links = buscar_links_google_maps(palavra_chave)
    if not links:
        return render_template('result.html', links=[], error="Nenhum link encontrado.")
    return render_template('result.html', links=links, error=None)

# Painel Web — Coletor de Links (Arquivos)

Abaixo estão os arquivos prontos para você subir para um projeto (por exemplo no Render.com). Eu incluí uma **versão simples** (sincrona) para testes locais/pequenos e notas com uma **arquitetura recomendada** para produção (Flask + Redis + worker).

---

## 1) `app.py` (Flask - versão simples para testes)

```python
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import threading
import time
import os
import sys
import re
import subprocess
import logging
import json
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DADOS_DIR = os.path.join(BASE_DIR, 'dados')
os.makedirs(DADOS_DIR, exist_ok=True)
LINKS_FILE = os.path.join(DADOS_DIR, 'links.txt')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# função para coletar (adaptada do seu script)
def coletar_links_por_busca(busca, driver, logger_fn=print):
    logger_fn(f"🔍 Buscando: {busca}")
    campo = driver.find_element(By.ID, 'searchboxinput')
    campo.clear()
    campo.send_keys(busca)
    campo.send_keys(Keys.ENTER)
    time.sleep(5)

    prev = 0
    for i in range(20):
        perfis = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
        curr = len(perfis)
        logger_fn(f"  ▶️ Scroll {i+1}: {curr} perfis carregados")
        if curr == prev:
            break
        prev = curr
        driver.execute_script("arguments[0].scrollIntoView();", perfis[-1])
        time.sleep(2)

    links = {p.get_attribute('href') for p in perfis if p.get_attribute('href')}
    return links


def save_new_links(new_links):
    existing = set()
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'r', encoding='utf-8') as f:
            existing = set(l.strip() for l in f if l.strip())
    to_add = new_links - existing
    if to_add:
        with open(LINKS_FILE, 'a', encoding='utf-8') as f:
            for link in sorted(to_add):
                f.write(link + '\n')
    return len(to_add), len(existing | new_links)


# Função que executa Selenium (modo *headless*). CUIDADO: exige Firefox/geckodriver no servidor
def run_selenium_collect(keywords, progress_cb=None):
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    driver.get("https://www.google.com/maps/@-16.4932735,-39.3111171,12z?hl=pt-BR")
    time.sleep(5)

    all_links = set()
    for idx, chave in enumerate(keywords, 1):
        if progress_cb:
            progress_cb(f"=== EXECUTANDO {idx}/{len(keywords)}: '{chave}' ===")
        links = coletar_links_por_busca(chave, driver, progress_cb or print)
        all_links |= links
    driver.quit()

    added, total = save_new_links(all_links)
    if progress_cb:
        progress_cb(f"Adicionados {added} links. Total: {total}")
    return {'added': added, 'total': total, 'found': len(all_links)}


# Rota principal (formulário simples)
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Rota para iniciar coleta (síncrono — bloqueia a requisição até terminar)
@app.route('/coletar', methods=['POST'])
def coletar():
    keywords_text = request.form.get('keywords', '')
    keywords = [l.strip() for l in keywords_text.splitlines() if l.strip()]
    if not keywords:
        return redirect(url_for('index'))

    # Execução síncrona: útil para testes. Para produção, veja instruções abaixo.
    result = run_selenium_collect(keywords)
    return render_template('result.html', result=result)

# Rota para download do arquivo links.txt
@app.route('/download')
def download():
    if os.path.exists(LINKS_FILE):
        return send_file(LINKS_FILE, as_attachment=True)
    return "Arquivo não encontrado", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

## 2) `templates/index.html`

```html
<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Coletor de Links - Web</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-light">
    <div class="container py-5">
      <h1 class="mb-4">Coletor de Links — Online (teste)</h1>
      <form method="post" action="/coletar">
        <div class="mb-3">
          <label class="form-label">Palavras-chave (uma por linha)</label>
          <textarea name="keywords" class="form-control" rows="6" placeholder="ex: padaria, pizzaria"></textarea>
        </div>
        <button class="btn btn-primary">Iniciar Coleta</button>
      </form>

      <hr>
      <a href="/download" class="btn btn-outline-secondary">Baixar links.txt</a>
      <p class="mt-3 text-muted">Observação: esta versão roda o Selenium no servidor. Para produção é recomendado usar um worker separado.</p>
    </div>
  </body>
</html>
```

---

## 3) `templates/result.html`

```html
<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Resultado</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-light">
    <div class="container py-5">
      <h1>Resultado</h1>
      <ul>
        <li>Links encontrados: {{ result.found }}</li>
        <li>Novos adicionados: {{ result.added }}</li>
        <li>Total no arquivo: {{ result.total }}</li>
      </ul>
      <a href="/" class="btn btn-secondary">Voltar</a>
      <a href="/download" class="btn btn-outline-primary">Baixar links.txt</a>
    </div>
  </body>
</html>
```

---

## 4) `requirements.txt`

```
Flask==2.2.5
selenium==4.12.0
webdriver-manager==4.0.0
requests==2.31.0
```

---

## 5) `Procfile` (para Render, Heroku etc.)

```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

---

## Notas IMPORTANTES e Recomendações (Leia!)

1. **Selenium no servidor**: rodar Firefox/geckodriver em servidores (Render, Heroku, etc.) exige dependências do sistema (libglib, xvfb, etc.). Em muitos PaaS você precisa usar um *docker container* com Firefox instalado ou usar um worker com capacidade para executar navegadores headless. A versão de `app.py` acima funciona localmente e em um servidor que já tenha Firefox/geckodriver.

2. **Timeouts / execução longa**: o scraping pode demorar > 30s. Plataformas serverless podem encerrar a requisição. Para produção, **não** execute o Selenium diretamente dentro do handler HTTP. Em vez disso:

   * Coloque um job na fila (Redis + RQ, ou Celery) e retorne imediatamente um ID de job.
   * Um worker separado consumirá a fila e executará o Selenium (pode usar Docker com Xvfb).
   * Forneça endpoints para verificar status/resultado do job.

3. **Segurança**: cuidado com expor um scraping público que permite execução arbitrária. Coloque autenticação (token / login), limite uso (rate limit) e sanitize inputs.

4. **Hospedagem recomendada**: Para seu caso (Render.com) eu recomendo criar dois serviços:

   * `web` (Flask) — recebe requisições e insere jobs em Redis.
   * `worker` (Python) — conecta no Redis e executa jobs rodando Selenium em um container com Firefox.

5. **Alternativas sem Selenium**: para coletar links do Google Maps você pode usar APIs (Places API do Google) ou bibliotecas/serviços que retornem resultados sem abrir um navegador — isso costuma ser mais simples e escalável (pago).

---

## Próximo passo — quer que eu:

* (A) Gere o `Dockerfile` e `docker-compose.yml` pronto para rodar localmente com Firefox + Xvfb e worker + redis? (bom para testar e para implantar no Render como Docker).
* (B) Forneça código com fila Redis + RQ (ex.: `tasks.py` + `worker.py`) e endpoints para criar/verificar job status?
* (C) Ou você prefere que eu adapte tudo para rodar direto no Render (com instruções passo-a-passo de deploy)?

Diga qual opção prefere que eu já gero os arquivos e instruções completas.

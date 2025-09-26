from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
perfis = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
curr = len(perfis)
logger_fn(f" ▶️ Scroll {i+1}: {curr} perfis carregados")
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

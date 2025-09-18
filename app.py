from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from flask_cors import CORS  # Importe o CORS

app = Flask(__name__)

# Habilitar CORS para todas as rotas
CORS(app, resources={r"/*": {"origins": "*"}})  # Permite qualquer origem

@app.route('/start-automation', methods=['GET'])
def start_automation():
    # Configurar o caminho para o WebDriver
    driver = webdriver.Chrome(executable_path='/path/to/chromedriver')  # Atualize o caminho

    # Acesse o Google
    driver.get("https://www.google.com")

    # Encontrar a barra de pesquisa e buscar "dentista"
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("dentista")
    search_box.send_keys(Keys.RETURN)

    # Espera a página carregar
    time.sleep(3)

    # Captura o título do primeiro resultado
    result_title = driver.find_element(By.CSS_SELECTOR, 'h3').text

    # Fechar o navegador
    driver.quit()

    # Retorna o título para o frontend
    return jsonify({'title': result_title})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

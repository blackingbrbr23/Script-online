import threading, requests, time

SERVER_BASE = "https://SEU-DOMINIO-RENDER.onrender.com"
POLL_INTERVAL = 10

mac = get_mac()
if mac:
    # registra no servidor
    try:
        ip = requests.get("https://api.ipify.org", timeout=5).text
    except:
        ip = ""
    requests.post(f"{SERVER_BASE}/register", json={"mac": mac, "name": "Meu PC", "public_ip": ip}, timeout=8)
    
    # inicia thread que verifica comando SCAN
    def poll_commands():
        while True:
            try:
                r = requests.get(f"{SERVER_BASE}/get_command", params={"mac": mac}, timeout=8)
                cmd = r.json().get('command','')
                if cmd.upper() == "SCAN":
                    app.write("Comando SCAN recebido! Iniciando...", 'INFO')
                    keywords = app.get_keywords() or ["restaurantes", "lojas"]
                    run_process(app, keywords)
                    # envia links.txt
                    if os.path.exists(LINKS_FILE):
                        files = {'file': open(LINKS_FILE, 'rb')}
                        data = {'mac': mac}
                        requests.post(f"{SERVER_BASE}/upload_results", files=files, data=data, timeout=60)
            except:
                pass
            time.sleep(POLL_INTERVAL)
    threading.Thread(target=poll_commands, daemon=True).start()

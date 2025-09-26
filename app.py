import os
import sqlite3
from flask import Flask, request, jsonify, g, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from datetime import datetime

DATABASE = 'server.db'
UPLOADS_DIR = 'uploads'
os.makedirs(UPLOADS_DIR, exist_ok=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB

ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'troque_isto_por_um_token_seguro')

# --- DB helpers ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS clients (
        mac TEXT PRIMARY KEY,
        name TEXT,
        public_ip TEXT,
        last_seen TEXT,
        command TEXT
    );
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mac TEXT,
        filename TEXT,
        uploaded_at TEXT
    );
    """)
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Endpoints ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    mac = data.get('mac')
    name = data.get('name', '')
    public_ip = data.get('public_ip', '')
    if not mac:
        return jsonify({'error': 'mac required'}), 400
    db = get_db()
    now = datetime.utcnow().isoformat()
    db.execute("INSERT OR REPLACE INTO clients (mac, name, public_ip, last_seen, command) VALUES (?,?,?,?,COALESCE((SELECT command FROM clients WHERE mac=?), ''))",
               (mac, name, public_ip, now, mac))
    db.commit()
    return jsonify({'ok': True})

@app.route('/get_command', methods=['GET'])
def get_command():
    mac = request.args.get('mac')
    if not mac:
        return jsonify({'error': 'mac required'}), 400
    db = get_db()
    cur = db.execute("SELECT command FROM clients WHERE mac=?", (mac,))
    row = cur.fetchone()
    command = row['command'] if row else ''
    if command:
        db.execute("UPDATE clients SET command='' , last_seen=? WHERE mac=?", (datetime.utcnow().isoformat(), mac))
        db.commit()
    return jsonify({'command': command or ''})

@app.route('/set_command', methods=['POST'])
def set_command():
    token = request.headers.get('X-ADMIN-TOKEN')
    if token != ADMIN_TOKEN:
        return jsonify({'error': 'unauthorized'}), 401
    data = request.get_json(force=True)
    mac = data.get('mac')
    command = data.get('command', '')
    if not mac:
        return jsonify({'error': 'mac required'}), 400
    db = get_db()
    db.execute("UPDATE clients SET command=? WHERE mac=?", (command, mac))
    db.commit()
    return jsonify({'ok': True})

@app.route('/upload_results', methods=['POST'])
def upload_results():
    mac = request.form.get('mac')
    if 'file' not in request.files or not mac:
        return jsonify({'error': 'file and mac required'}), 400
    f = request.files['file']
    filename = secure_filename(f.filename)
    save_to = os.path.join(UPLOADS_DIR, f"{mac}__{datetime.utcnow().strftime('%Y%m%d%H%M%S')}__{filename}")
    f.save(save_to)
    db = get_db()
    db.execute("INSERT INTO results (mac, filename, uploaded_at) VALUES (?,?,?)", (mac, save_to, datetime.utcnow().isoformat()))
    db.execute("UPDATE clients SET last_seen=? WHERE mac=?", (datetime.utcnow().isoformat(), mac))
    db.commit()
    return jsonify({'ok': True})

# --- Dashboard ---
DASH_TEMPLATE = """
<!doctype html>
<title>Painel de Clientes</title>
<h1>Clientes</h1>
<table border=1 cellpadding=8>
<tr><th>MAC</th><th>Nome</th><th>IP Público</th><th>Último seen (UTC)</th><th>Ações</th></tr>
{% for c in clients %}
<tr>
<td>{{c.mac}}</td>
<td>{{c.name}}</td>
<td>{{c.public_ip}}</td>
<td>{{c.last_seen}}</td>
<td>
<form method="post" action="/set_command" onsubmit="sendCommand(event, '{{c.mac}}')">
<button type="submit">SCANEAR</button>
</form>
<a href="/results/{{c.mac}}">Ver resultados</a>
</td>
</tr>
{% endfor %}
</table>
<script>
async function sendCommand(e, mac){
    e.preventDefault();
    const token = prompt("Admin Token:");
    const resp = await fetch('/set_command', {
        method:'POST',
        headers:{'Content-Type':'application/json','X-ADMIN-TOKEN':token},
        body: JSON.stringify({mac: mac, command:'SCAN'})
    });
    alert(await resp.text());
    location.reload();
}
</script>
"""

@app.route('/')
def index():
    db = get_db()
    cur = db.execute("SELECT mac, name, public_ip, last_seen FROM clients ORDER BY last_seen DESC")
    clients = cur.fetchall()
    return render_template_string(DASH_TEMPLATE, clients=clients)

@app.route('/results/<mac>')
def results(mac):
    db = get_db()
    cur = db.execute("SELECT filename, uploaded_at FROM results WHERE mac=? ORDER BY uploaded_at DESC", (mac,))
    rows = cur.fetchall()
    out = "<h1>Resultados para {}</h1><ul>".format(mac)
    for r in rows:
        out += f"<li>{r['uploaded_at']} - <a href='/download?file={r['filename']}'>Download</a></li>"
    out += "</ul><a href='/'>Voltar</a>"
    return out

@app.route('/download')
def download():
    path = request.args.get('file')
    if not path or not os.path.exists(path):
        return "Arquivo não encontrado", 404
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    return send_from_directory(directory, filename, as_attachment=True)

# --- start ---
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5000)

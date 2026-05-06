import json
import random
import time
import uuid
from pathlib import Path
from datetime import datetime
from flask import Flask, request, render_template_string, make_response
from werkzeug.serving import WSGIRequestHandler

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "http_honeypot.log"
FP_LOG_FILE = LOG_DIR / "fingerprint.log"
SOCIAL_LOG_FILE = LOG_DIR / "social_probe.log"

with open(BASE_DIR / "config" / "config.json") as f:
    CONFIG = json.load(f)

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"),
            static_folder=str(BASE_DIR / "static"))

LOGIN_PATH = CONFIG.get("active_login_path", "/login")
LOGIN_PATHS = CONFIG.get("login_paths", ["/login"])
PROB_ERROR = CONFIG["probability"]["error_page"]
PROB_500 = CONFIG["probability"]["server_error"]
PROB_DELAY = CONFIG["probability"]["delay"]
DELAY_MIN = CONFIG["delay_range"]["min"]
DELAY_MAX = CONFIG["delay_range"]["max"]

_server_header_cache = {}
_HEADERS_POOL = CONFIG.get("server_headers", ["nginx/1.24.0"])
_HEADER_WINDOW = 86400


def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    if request.headers.get('X-Real-IP'):
        return request.headers['X-Real-IP'].strip()
    return request.remote_addr or 'unknown'


def get_server_header(ip):
    now = time.time()
    if ip in _server_header_cache:
        header, ts = _server_header_cache[ip]
        if now - ts < _HEADER_WINDOW:
            return header
    header = random.choice(_HEADERS_POOL)
    _server_header_cache[ip] = (header, now)
    return header


def log_attack(ip, username, password, action='login_attempt', extra=None):
    entry = {
        'time': datetime.now().isoformat(),
        'ip': ip,
        'username': username,
        'password': password,
        'user_agent': request.headers.get('User-Agent', ''),
        'action': action,
        'headers': {
            'accept_language': request.headers.get('Accept-Language', ''),
            'accept_encoding': request.headers.get('Accept-Encoding', ''),
            'referer': request.headers.get('Referer', ''),
            'x_forwarded_for': request.headers.get('X-Forwarded-For', ''),
            'x_real_ip': request.headers.get('X-Real-IP', ''),
        }
    }
    if extra:
        entry.update(extra)
    
    if action == 'fingerprint':
        log_file = FP_LOG_FILE
    elif action == 'social_probe':
        log_file = SOCIAL_LOG_FILE
    else:
        log_file = LOG_FILE
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        f.flush()
    print(f"[LOG] {action} - {ip} - {username}:{password}")


def get_fingerprint_script():
    fp_path = BASE_DIR / "static" / "js" / "fingerprint.js"
    if fp_path.exists():
        return fp_path.read_text(encoding='utf-8')
    return '''<script>
(function() {
    if (window.__scallop_fp_done) return;
    window.__scallop_fp_done = true;
    var fp = {};
    try {
        fp.ua = navigator.userAgent;
        fp.vendor = navigator.vendor || '';
        fp.platform = navigator.platform || '';
        fp.language = navigator.language || '';
        fp.languages = (navigator.languages || []).join(',');
        fp.screenW = screen.width;
        fp.screenH = screen.height;
        fp.availW = screen.availWidth;
        fp.availH = screen.availHeight;
        fp.colorDepth = screen.colorDepth;
        fp.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
        fp.hardwareConcurrency = navigator.hardwareConcurrency || 0;
        fp.deviceMemory = navigator.deviceMemory || 0;
        fp.plugins = [];
        if (navigator.plugins) {
            for (var i = 0; i < navigator.plugins.length && i < 10; i++) {
                fp.plugins.push(navigator.plugins[i].name);
            }
        }
    } catch(e) {}
    try {
        var canvas = document.createElement('canvas');
        canvas.width = 280;
        canvas.height = 60;
        canvas.style.display = 'none';
        var ctx = canvas.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillStyle = '#f60';
        ctx.fillRect(0, 0, 100, 20);
        ctx.fillStyle = '#069';
        ctx.fillText('Scallop', 2, 15);
        fp.canvasHash = canvas.toDataURL().slice(-32);
    } catch(e) {}
    try {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/_fp', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(fp));
    } catch(e) {}
})();
</script>'''


def get_social_script():
    social_path = BASE_DIR / "static" / "js" / "social.js"
    if social_path.exists():
        return social_path.read_text(encoding='utf-8')
    targets = CONFIG.get("social_probe", {}).get("targets", [])
    enabled = CONFIG.get("social_probe", {}).get("enabled", True)
    if not enabled or not targets:
        return ''
    target_js = []
    for t in targets:
        target_js.append(f'{{name:"{t["name"]}",url:"{t["url"]}"}}')
    target_list = ',\n'.join(target_js)
    return f'''<script>
(function() {{
    if (window.__scallop_social_done) return;
    window.__scallop_social_done = true;
    var targets = [{target_list}];
    var results = {{}};
    var timeout = 2000;
    function probe(target) {{
        return new Promise(function(resolve) {{
            var cbName = '__sc_cb_' + Date.now() + '_' + Math.random().toString(36).slice(2);
            var called = false;
            window[cbName] = function() {{
                called = true;
                results[target.name] = true;
                resolve(true);
                delete window[cbName];
            }};
            var script = document.createElement('script');
            script.src = target.url.replace('__scallop_probe', cbName);
            script.onerror = function() {{
                if (!called) results[target.name] = false;
                resolve(false);
                delete window[cbName];
            }};
            document.head.appendChild(script);
            setTimeout(function() {{
                if (!called) {{ results[target.name] = false; resolve(false); }}
            }}, timeout);
        }});
    }}
    var probes = targets.map(function(t) {{ return probe(t); }});
    Promise.allSettled(probes).then(function() {{
        try {{
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/_social', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify(results));
        }} catch(e) {{}}
    }});
}})();
</script>'''


def render_login(error=None):
    extra_scripts = get_fingerprint_script() + get_social_script()
    html_path = BASE_DIR / "templates" / "login.html"
    if html_path.exists():
        html = html_path.read_text(encoding='utf-8')
        return render_template_string(html, error=error, login_path=LOGIN_PATH,
                                      extra_scripts=extra_scripts)
    extra_scripts = get_fingerprint_script() + get_social_script()
    error_html = f'<div style="color:#d93025;font-size:13px;text-align:center;margin-bottom:16px;padding:10px;background:#fce8e6;border-radius:6px;">{error}</div>' if error else ''
    return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sign In</title></head>
<body>
    {error_html}
    <form action="{LOGIN_PATH}" method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Sign In</button>
    </form>
    {extra_scripts}
</body></html>'''


def render_error(message):
    extra_scripts = get_fingerprint_script() + get_social_script()
    html_path = BASE_DIR / "templates" / "error.html"
    if html_path.exists():
        html = html_path.read_text(encoding='utf-8')
        return render_template_string(html, message=message, extra_scripts=extra_scripts)
    return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Error</title></head>
<body><p>{message}</p>{extra_scripts}</body></html>'''


def update_server_header():
    """更新 Werkzeug 开发服务器的 Server 头"""
    ip = get_client_ip()
    header = get_server_header(ip)
    WSGIRequestHandler.server_version = header
    WSGIRequestHandler.sys_version = ""


@app.before_request
def before_request_set_server():
    """每个请求前更新 Server 头"""
    update_server_header()


@app.route('/')
def index():
    ip = get_client_ip()
    log_attack(ip, '', '', 'page_view', {'path': '/'})
    return render_login()


@app.route(LOGIN_PATH, methods=['GET'])
def login_page():
    ip = get_client_ip()
    log_attack(ip, '', '', 'page_view', {'path': LOGIN_PATH})
    return render_login()


@app.route(LOGIN_PATH, methods=['POST'])
def login_submit():
    ip = get_client_ip()
    username = (request.form.get('username') or '').strip()
    password = (request.form.get('password') or '').strip()
    headers = dict(request.headers)

    if not username and not password:
        username = (request.form.get('user') or '').strip()
        password = (request.form.get('pass') or '').strip()

    if not username:
        log_attack(ip, '', password, 'login_empty')
    else:
        log_attack(ip, username, password, 'login_attempt')

    roll = random.random()
    resp = None

    if roll < PROB_DELAY:
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    if roll < PROB_500:
        resp = make_response('Internal Server Error', 500)
    elif roll < PROB_500 + PROB_ERROR:
        resp = make_response(render_error('Incorrect username or password.'))
    else:
        resp = make_response(render_login(error='Incorrect username or password.'))

    return resp


@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /admin\nDisallow: /config\nDisallow: /backup\n", 200


@app.route('/_fp', methods=['POST'])
def fingerprint_collect():
    ip = get_client_ip()
    try:
        data = request.get_json(force=True, silent=True) or {}
    except:
        data = {}
    log_attack(ip, '', '', 'fingerprint', {'fingerprint': data})
    return '', 204


@app.route('/_social', methods=['POST'])
def social_collect():
    ip = get_client_ip()
    try:
        data = request.get_json(force=True, silent=True) or {}
    except:
        data = {}
    log_attack(ip, '', '', 'social_probe', {'social_result': data})
    return '', 204


for lp in LOGIN_PATHS:
    if lp and lp != LOGIN_PATH and lp != '/':
        @app.route(lp, methods=['GET'], endpoint=f'_login_alias_{lp.replace("/","_")}')
        def _alias(path=lp):
            ip = get_client_ip()
            log_attack(ip, '', '', 'page_view', {'path': path})
            return render_login()


@app.route('/<path:unknown>')
def catch_all(unknown):
    ip = get_client_ip()
    log_attack(ip, '', '', 'unknown_path', {'path': f'/{unknown}'})
    return 'Not Found', 404


if __name__ == '__main__':
    print(f"HTTP 蜜罐运行中，端口 {CONFIG['server']['port']}...")
    print(f"登录路径: {LOGIN_PATH}")
    print(f"Server 头池: {_HEADERS_POOL}")
    app.run(
        host=CONFIG['server']['host'],
        port=CONFIG['server']['port'],
        debug=False
    )

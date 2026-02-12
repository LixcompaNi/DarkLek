import os
import telebot
from flask import Flask, render_template_string, request, redirect, session, abort
from werkzeug.security import generate_password_hash, check_password_hash

# --- КОНФИГУРАЦИЯ (ЗАПОЛНИ СВОИ ДАННЫЕ) ---
BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА"  # Получи у @BotFather
CH_ID = "-1002232535000"       # Твой канал
ADMIN_PASS_HASH = generate_password_hash("CORE_ADMIN_SET_99") # Твой пароль админа
CUSTOM_USER_AGENT = "anoNetBrowser/1.0" # Сайт откроется только если браузер шлет этот заголовок

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Имитация БД в оперативной памяти
users = {}
ads = []

# --- ФИЛЬТР "ТОЛЬКО МОЙ БРАУЗЕР" ---
@app.before_request
def restrict_access():
    # Если User-Agent не совпадает с твоим — сайт "не существует"
    if request.headers.get('User-Agent') != CUSTOM_USER_AGENT:
        return "<h1>404 Not Found</h1><p>The requested URL was not found on this server.</p>", 404

# --- HTML ШАБЛОНЫ (В СТИЛЕ DARK) ---
HTML_LAYOUT = """
<!DOCTYPE html>
<html style="background: #0a0a0a; color: #00ff41; font-family: monospace;">
<head><title>anoNet.a | CLOSED</title></head>
<body>
    <div style="border: 1px solid #00ff41; padding: 20px; margin: 20px;">
        <h2>[ anoNet_System_v1.0 ]</h2>
        <hr color="#00ff41">
        {{ content | safe }}
    </div>
</body>
</html>
"""

# --- МАРШРУТЫ ---

@app.route('/')
def index():
    if 'user' not in session:
        return render_template_string(HTML_LAYOUT, content='''
            <h3>ВХОД В СИСТЕМУ</h3>
            <form action="/login" method="post">
                Логин: <input type="text" name="u"><br>
                Пароль: <input type="password" name="p"><br>
                <input type="submit" value="ENTER">
            </form>
            <p><a href="/reg" style="color: #00ff41;">Регистрация нового узла</a></p>
        ''')
    return render_template_string(HTML_LAYOUT, content=f'''
        <h3>Добро пожаловать, {session['user']}</h3>
        <p>Ваш ID: {users[session['user']]['id']}</p>
        <p>Ваш баланс: BTC {users[session['user']]['balance']}</p>
        <hr>
        <h4>ОБЪЯВЛЕНИЯ</h4>
        <form action="/post_ad" method="post">
            <input type="text" name="text" placeholder="Что продаем?">
            <input type="submit" value="ОПУБЛИКОВАТЬ">
        </form>
        <ul>
            {''.join([f"<li>{a}</li>" for a in ads])}
        </ul>
    ''')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        u = request.form['u']
        p = request.form['p']
        phone = request.form['phone']
        uid = os.urandom(4).hex()
        
        users[u] = {
            "id": uid,
            "pass": generate_password_hash(p),
            "phone": phone,
            "balance": 0.0
        }
        
        # СУРОВО: Отправка всех данных в твой ТГ
        log_msg = f"🛰 НОВЫЙ ПОЛЬЗОВАТЕЛЬ:\nID: {uid}\nLogin: {u}\nPass_Hash: {users[u]['pass'][:15]}...\nPhone: {phone}"
        bot.send_message(CH_ID, log_msg)
        
        return redirect('/')
    return render_template_string(HTML_LAYOUT, content='''
        <h3>РЕГИСТРАЦИЯ</h3>
        <form method="post">
            Логин: <input type="text" name="u" required><br>
            Пароль: <input type="password" name="p" required><br>
            Телефон: <input type="text" name="phone" required><br>
            <input type="submit" value="СОЗДАТЬ АККАУНТ">
        </form>
    ''')

@app.route('/login', methods=['POST'])
def login():
    u = request.form['u']
    p = request.form['p']
    if u in users and check_password_hash(users[u]['pass'], p):
        session['user'] = u
        return redirect('/')
    return "ОШИБКА ДОСТУПА"

# --- СУРОВАЯ СКРЫТАЯ АДМИНКА ---
@app.route('/root_shadow_panel_X9', methods=['GET', 'POST'])
def admin():
    # Проверка пароля админа через заголовок или сессию
    if request.args.get('key') != "ROOT_ACCESS_CODE":
        abort(403)
        
    action = request.args.get('action')
    target = request.args.get('target')

    if action == "ban":
        if target in users:
            del users[target]
            bot.send_message(CH_ID, f"❌ УНИЧТОЖЕН: {target}")
    
    if action == "wipe":
        if target in users:
            users[target]['balance'] = 0
            bot.send_message(CH_ID, f"💸 ОБНУЛЕН: {target}")

    return render_template_string(HTML_LAYOUT, content=f"<h3>ROOT PANEL</h3><p>Users online: {len(users)}</p>")

if __name__ == '__main__':
    # Сайт запускается на 80 порту
    app.run(host='0.0.0.0', port=80)

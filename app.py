import os
import time
import telebot
from flask import Flask, render_template_string, request, redirect, session, abort
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================================
# КОНФИГУРАЦИЯ БЕЗОПАСНОСТИ
# ==========================================================
BOT_TOKEN = "8425879350:AAFGD4ciCaBKW5ZeKLwgddLOIS4N4-dwPBQ"  # Получить у @BotFather
CH_ID = "https://t.me/+fW1WSB8ahMFhM2Uy"      # Твой канал-хранилище
ADMIN_CODE = "ROOT_SECRET_99_X" # Твой сложный пароль для админки
MY_BROWSER_ID = "anoNetBrowser/1.0" # Ключ-заголовок для входа

bot = telebot.TeleBot(8425879350:AAFGD4ciCaBKW5ZeKLwgddLOIS4N4-dwPBQ)
app = Flask(__name__)
app.secret_key = os.urandom(32)

# Временное хранилище (в памяти)
users = {https://t.me/+fW1WSB8ahMFhM2Uy}
ads = []
failed_attempts = {8} # Счётчик неудачных входов в админку

# ==========================================================
# ЗАЩИТНЫЙ СЛОЙ (Middleware)
# ==========================================================
@app.before_request
def security_layer():
    # Если зашли через обычный Chrome/Safari - выдаем 404
    if request.headers.get('User-Agent') != MY_BROWSER_ID:
        return "<h1>404 Not Found</h1>", 404

# ==========================================================
# ДИЗАЙН (Matrix/Dark Style)
# ==========================================================
def render_terminal(content, color="#00ff41"):
    return render_template_string(f'''
    <!DOCTYPE html>
    <html style="background: #050505; color: {color}; font-family: 'Courier New', monospace;">
    <head><title>anoNet_Core</title></head>
    <body style="padding: 30px;">
        <div style="border: 2px solid {color}; padding: 20px; box-shadow: 0 0 15px {color};">
            <h1 style="text-shadow: 2px 2px 5px {color};">[ anoNet.a ]</h1>
            <hr border="1" color="{color}">
            {content}
        </div>
    </body>
    </html>
    ''')

# ==========================================================
# ЛОГИКА САЙТА
# ==========================================================

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/auth')
    
    current_user = None
    for u in users.values():
        if u['id'] == session['user_id']:
            current_user = u
            break
            
    content = f'''
    <h3>СТАТУС: В СЕТИ | ID: {current_user['id']}</h3>
    <p>ЛОГИН: {current_user['name']} | БАЛАНС: {current_user['balance']} BTC</p>
    <hr color="#00ff41">
    <h4>МАРКЕТПЛЕЙС</h4>
    <form action="/add_post" method="post">
        <input type="text" name="msg" placeholder="Текст объявления..." style="width: 70%; background: #000; color: #fff; border: 1px solid #00ff41;">
        <input type="submit" value="ОПУБЛИКОВАТЬ" style="background: #00ff41; color: #000; border: none; cursor: pointer;">
    </form>
    <ul>
        {''.join([f"<li>[ID:{a['id']}] {a['text']}</li>" for a in ads])}
    </ul>
    <br>
    <a href="/logout" style="color: #555;">[ВЫХОД]</a>
    '''
    return render_terminal(content)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        action = request.form.get('action')
        name = request.form.get('name')
        password = request.form.get('pass')

        if action == 'reg':
            uid = os.urandom(3).hex().upper()
            phone = request.form.get('phone')
            email = request.form.get('email')
            
            users[name] = {
                "id": uid, "name": name, "phone": phone, 
                "email": email, "pass": generate_password_hash(password), "balance": 0.0
            }
            # СУРОВО: Отправка всех данных в ТГ
            msg = f"🛰 РЕГИСТРАЦИЯ:\nID: {uid}\nName: {name}\nPhone: {phone}\nEmail: {email}\nPass_Hash: {users[name]['pass'][:20]}..."
            bot.send_message(CH_ID, msg)
            return "АККАУНТ СОЗДАН. ПЕРЕЗАГРУЗИТЕ СТРАНИЦУ."

        elif action == 'login':
            if name in users and check_password_hash(users[name]['pass'], password):
                session['user_id'] = users[name]['id']
                return redirect('/')
            return "ДОСТУП ЗАПРЕЩЕН"

    return render_terminal('''
        <h3>АВТОРИЗАЦИЯ / РЕГИСТРАЦИЯ</h3>
        <form method="post">
            <input type="hidden" name="action" value="login">
            <input type="text" name="name" placeholder="Имя" required><br>
            <input type="password" name="pass" placeholder="Пароль" required><br>
            <input type="submit" value="ВХОД">
        </form>
        <hr color="#00ff41">
        <h4>НОВЫЙ УЗЕЛ</h4>
        <form method="post">
            <input type="hidden" name="action" value="reg">
            <input type="text" name="name" placeholder="Имя" required><br>
            <input type="text" name="phone" placeholder="Телефон" required><br>
            <input type="email" name="email" placeholder="Email" required><br>
            <input type="password" name="pass" placeholder="Пароль" required><br>
            <input type="submit" value="СОЗДАТЬ">
        </form>
    ''')

# ==========================================================
# СКРЫТАЯ АДМИНКА (ROOT PANEL)
# ==========================================================
@app.route('/gate_of_shadows', methods=['GET', 'POST'])
def admin_panel():
    ip = request.remote_addr
    
    if request.method == 'POST':
        code = request.form.get('root_code')
        if code == ADMIN_CODE:
            bot.send_message(CH_ID, f"🔓 ВНИМАНИЕ: Админ-вход выполнен! IP: {ip}")
            
            user_rows = ""
            for uname, udata in users.items():
                user_rows += f"<li>{uname} | ID: {udata['id']} | <a href='/root_cmd?act=del&t={uname}'>[УДАЛИТЬ]</a> | <a href='/root_cmd?act=wipe&t={uname}'>[ОБНУЛИТЬ]</a></li>"
            
            return render_terminal(f"<h3>ROOT TERMINAL</h3><ul>{user_rows}</ul>", color="red")
        else:
            # СУРОВО: Счетчик провалов
            failed_attempts[ip] = failed_attempts.get(ip, 0) + 1
            bot.send_message(CH_ID, f"🧨 ПОПЫТКА ВЗЛОМА! IP: {ip}, Попытка: {failed_attempts[ip]}")
            return "<h1>СИСТЕМА ЗАБЛОКИРОВАНА ДЛЯ ВАШЕГО IP</h1>", 403

    return render_terminal('''
        <h2 style="color: red;">[ RESTRICTED AREA ]</h2>
        <form method="post">
            ENTER ADMIN HASH: <input type="password" name="root_code" style="background:#000; color:red; border:1px solid red;">
            <input type="submit" value="DECRYPT">
        </form>
    ''', color="red")

@app.route('/root_cmd')
def root_cmd():
    # Добавь сюда проверку сессии админа для доп. безопасности
    act = request.args.get('act')
    target = request.args.get('t')
    
    if act == "del" and target in users:
        del users[target]
        bot.send_message(CH_ID, f"💥 УДАЛЕНИЕ: Пользователь {target} уничтожен.")
    if act == "wipe" and target in users:
        users[target]['balance'] = 0
        bot.send_message(CH_ID, f"💸 ОБНУЛЕНИЕ: Баланс {target} стерт.")
        
    return redirect('/gate_of_shadows')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    # Запуск на порту 80 (требует прав админа в системе)
    app.run(host='0.0.0.0', port=80)

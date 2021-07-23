from flask import Flask, render_template, request, redirect, jsonify
from flask_socketio import SocketIO, emit

import os
import uuid
import json
import string
import random
import sqlite3


USER_TYPES = {'undergraduate', 'graduate', 'professor'}
TYPE_NAMES = ('undergraduate', 'graduate', 'professor')
CHAT_ROOMS = ('방 1', '방 2')


PROGRAM_DIR = os.path.abspath(os.path.dirname(__file__)) + '/'
REGISTER_FILE = PROGRAM_DIR + 'data/register_request.json'
REGISTER_DIR = PROGRAM_DIR + 'data/register_request/'
USER_DB = PROGRAM_DIR + 'data/users.sqlite'

app = Flask(__name__)
app.secret_key = (
    b'\x1d\xbe\xbc\xb7b\x9b\x94M\x15z\x93\xc8\x804\xd1\xceq:0H\x06\xef\x80f'
    b'^\xfaA\xaao\xbfP\xac\xe9\x13l\xa1r\xa89\xd6\xbf\x86\r\x894\xb9\x82Y'
    b'\xb4\xb2\xae\xe3qL\x9e\x1a\x8d\xff\x8b\xe9mS\xda7'
)
socketio = SocketIO(app)
uids = {}
usernames = set()
registered_users = {}
nicknames = set()


# load users
con = sqlite3.connect(USER_DB)
cur = con.cursor()
for name, passwd, usertype, nickname\
        in cur.execute('SELECT * FROM users').fetchall():
    registered_users[name] = passwd, TYPE_NAMES[usertype], nickname
    nicknames.add(nickname)
    usernames.add(nickname)
# end load user


@app.route('/')
def main():
    return render_template('welcome.html')


@app.route('/login')
def login():
    if request.cookies.get('chat_hys_uid', '') in uids:
        return render_template('login.html')
    else:
        return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # process register
        file = request.files['fileInput']
        ext = os.path.splitext(file.filename)[1]
        name = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=32)
        ) + ext
        while os.path.exists(name):
            name = ''.join(
                random.choices(string.ascii_uppercase + string.digits)
            ) + ext
        file.save(REGISTER_DIR + name)

        form = request.form
        username = form['username']
        usertype = form['usertype']
        nickname = form['nickname']

        with open(REGISTER_FILE, 'r', encoding='utf-8') as file:
            priv_data = json.load(file)

        if username in registered_users:
            return jsonify({'success': False, 'message': '중복되는 아이디입니다'})
        if usertype not in USER_TYPES:
            return jsonify({'success': False, 'message': '잘못된 사용자 타입'})
        if nickname in nicknames:
            return jsonify({'success': False, 'message': '이미 존재하는 닉네임입니다'})

        with open(REGISTER_FILE, 'w', encoding='utf-8') as file:
            json.dump(priv_data + [{
                'username': username,
                'password': form['password'],
                'usertype': usertype,
                'nickname': nickname,
                'filename': name
            }], file, indent=4, ensure_ascii=False)

        return jsonify({'success': True})
    elif request.cookies.get('chat_hys_uid', '') in uids:
        return render_template('register.html')
    else:
        return redirect('/')


@app.route('/guest')
def guest():
    if request.cookies.get('chat_hys_uid', '') in uids:
        return render_template('guest.html')
    else:
        return redirect('/')


@app.route('/chat')
def chat():
    if uids.get(request.cookies.get('chat_hys_uid', ''), None):
        return render_template('chat.html')
    else:
        return redirect('/')


@socketio.on('uniqueid')
def uid_generator():
    uid = str(uuid.uuid4())
    while uid in uids:
        uid = str(uuid.uuid4())
    uids[uid] = None
    return {'success': True, 'uniqueid': uid}


@socketio.on('guest_auth')
def guest_auth_handler(auth_data):
    if (
        'uniqueid' not in auth_data
        or 'usertype' not in auth_data
        or 'anonname' not in auth_data
    ):
        return {'success': False, 'message': '데이터 오류', 'redirect': '/'}

    uid = auth_data['uniqueid']
    usertype = auth_data['usertype']
    username = auth_data['anonname']

    if username in usernames:
        return {
            'success': False,
            'message': '사용자명이 중복됩니다.\n다른 이름을 선택해 주세요'
        }
    usernames.add(username)

    if usertype not in USER_TYPES or uid not in uids:
        return {'success': False, 'message': '세션 오류', 'redirect': '/'}

    uids[uid] = {
        'isguest': True,
        'usertype': usertype,
        'username': username
    }
    return {'success': True}


@socketio.on('user_auth')
def user_auth_handler(auth_data):
    if (
        'uniqueid' not in auth_data
        or 'username' not in auth_data
        or 'password' not in auth_data
    ):
        return {'success': False, 'message': '데이터 오류', 'redirect': '/'}

    uid = auth_data['uniqueid']
    username = auth_data['username']
    password = auth_data['password']

    if uid not in uids:
        return {'success': False, 'message': '세션 오류', 'redirect': '/'}
    if username not in registered_users:
        return {'success': False, 'message': '사용자명을 확인해 주세요.'}

    correct_passwd, usertype, nickname = registered_users[username]
    if password != correct_passwd:
        return {'success': False, 'message': '비밀번호를 확인해 주세요.'}

    uids[uid] = {
        'isguest': False,
        'usertype': usertype,
        'username': nickname
    }

    return {'success': True}


@socketio.on('logout')
def logout_handler(data):
    if 'uniqueid' not in data:
        return {'success': False, 'message': '데이터 오류', 'redirect': '/'}

    uid = data['uniqueid']
    if uid not in uids:
        return {'success': False, 'message': '세션 오류', 'redirect': '/'}

    userinfo = uids[uid]
    if userinfo['isguest']:
        usernames.remove(['username'])
    uids[uid] = None
    return {'success': True}


@socketio.on('retrieve_rooms')
def retrieve_rooms_handler():
    if uids.get(request.cookies.get('chat_hys_uid', ''), None):
        return {'success': True, 'chatrooms': CHAT_ROOMS}
    else:
        return {
            'success': False,
            'message': '세션이 초기화되었습니다.',
            'redirect': '/'
        }


@socketio.on('chat')
def chat_handler(data):
    user_info = uids[data['uniqueid']]

    emit('chat', {
        'roomid': data['roomid'],
        'sender': user_info,
        'message': data['message']
    }, broadcast=True, include_self=False)


if __name__ == "__main__":
    # app.run(debug=True)
    app.run()

from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit, join_room  # , leave_room

import sys
import json
import string
import random


app = Flask(__name__)
app.secret_key = (
    b'\x1d\xbe\xbc\xb7b\x9b\x94M\x15z\x93\xc8\x804\xd1\xceq:0H\x06\xef\x80f'
    b'^\xfaA\xaao\xbfP\xac\xe9\x13l\xa1r\xa89\xd6\xbf\x86\r\x894\xb9\x82Y'
    b'\xb4\xb2\xae\xe3qL\x9e\x1a\x8d\xff\x8b\xe9mS\xda7'
)
socketio = SocketIO(app)
uids = {}


USER_TYPES = {'undergraduate', 'graduate', 'professor'}


@app.route('/')
def main():
    return render_template('welcome.html')


@app.route('/login')
def login():
    if request.cookies.get('chat_hys_uid', '') in uids:
        return render_template('login.html')
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
    if request.cookies.get('chat_hys_uid', '') in uids:
        return render_template('chat.html')
    else:
        return redirect('/')


@socketio.on('uniqueid')
def uid_generator():
    uid = ''.join(random.choices(string.ascii_letters, k=64))
    while uid in uids:
        uid = ''.join(random.choices(string.ascii_letters, k=64))
    uids[uid] = {'user_type': None, 'user_name': None}
    join_room(uid)
    emit('uniqueid', {'success': True, 'uniqueid': uid})


@socketio.on('guest_auth')
def guest_auth_handler(raw_data):
    auth_data = json.loads(raw_data)
    print(auth_data, type(auth_data))
    if (
        'uniqueid' not in auth_data
        or 'user_type' not in auth_data
        or 'anon_name' not in auth_data
    ):
        return

    uid = auth_data['uniqueid']
    usertype = auth_data['user_type']
    username = auth_data['anon_name']

    print(uid, usertype, username)

    join_room(uid)

    if usertype not in USER_TYPES or uid not in uids:
        emit('auth_respond', {
            'success': False, 'message': '알 수 없는 오류', 'redirect': '/'
        })

    uids[uid] = {'usertype': usertype, 'username': username}
    emit('auth_respond', {'success': True})
    print(uids)


@socketio.on('user_auth')
def user_auth_handler(auth_data):
    if (
        'uniqueid' not in auth_data
        or 'usertype' not in auth_data
        or 'username' not in auth_data
    ):
        return

    uid = auth_data['uniqueid']
    usertype = auth_data['usertype']
    username = auth_data['username']

    join_room(uid)

    if usertype not in USER_TYPES or uid not in uids:
        emit('auth_respond', {
            'success': False, 'message': '알 수 없는 오류', 'redirect': '/'
        })

    uids[uid] = {'usertype': usertype, 'username': username}
    emit('auth_respond', {'success': True})


@socketio.on('chat')
def chat_handler(data):
    print('Message chat:', data, type(data), file=sys.stdout)


if __name__ == "__main__":
    app.run(debug=True)

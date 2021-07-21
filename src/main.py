from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit  # , join_room, leave_room

import sys
import uuid


USER_TYPES = {'undergraduate', 'graduate', 'professor'}
CHAT_ROOMS = ('방 1', '방 2')


app = Flask(__name__)
app.secret_key = (
    b'\x1d\xbe\xbc\xb7b\x9b\x94M\x15z\x93\xc8\x804\xd1\xceq:0H\x06\xef\x80f'
    b'^\xfaA\xaao\xbfP\xac\xe9\x13l\xa1r\xa89\xd6\xbf\x86\r\x894\xb9\x82Y'
    b'\xb4\xb2\xae\xe3qL\x9e\x1a\x8d\xff\x8b\xe9mS\xda7'
)
socketio = SocketIO(app)
uids = {}
usernames = set()


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
    if uids.get(request.cookies.get('chat_hys_uid', ''), {}):
        return render_template('chat.html')
    else:
        return redirect('/')


@socketio.on('uniqueid')
def uid_generator():
    print(request.sid)
    uid = str(uuid.uuid4())
    while uid in uids:
        uid = str(uuid.uuid4())
    uids[uid] = None
    return {'success': True, 'uniqueid': uid}


@socketio.on('guest_auth')
def guest_auth_handler(auth_data):
    print(request.sid)
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

    uids[uid] = {'isguest': True, 'usertype': usertype, 'username': username}
    return {'success': True}


'''
@socketio.on('user_auth')
def user_auth_handler(auth_data):
'''


@socketio.on('logout')
def logout_handler(data):
    print(f'Logout {data}', file=sys.stdout)
    if 'uniqueid' not in data:
        return {
            'success': False, 'message': '데이터 오류', 'redirect': '/'
        }

    uid = data['uniqueid']
    # os.system('cls')
    print(f'Logout User: {uid}', file=sys.stdout)

    if uid not in uids:
        return {
            'success': False, 'message': '세션 오류', 'redirect': '/'
        }

    usernames.remove(uids[uid]['username'])
    uids[uid] = None
    return {'success': True}


@socketio.on('retrieve_rooms')
def retrieve_rooms_handler():
    print(CHAT_ROOMS)
    if uids.get(request.cookies.get('chat_hys_uid', ''), {}):
        return {'success': True, 'chatrooms': CHAT_ROOMS}
    else:
        return {
            'success': False,
            'message': '로그인되지 않았습니다.',
            'redirect': '/'
        }


@socketio.on('chat')
def chat_handler(data):
    print('Message chat:', data, type(data), file=sys.stdout)

    user_info = uids[data['uniqueid']]

    emit('chat', {
        'roomid': data['roomid'],
        'sender': user_info,
        'message': data['message']
    }, broadcast=True, include_self=False)


if __name__ == "__main__":
    app.run(debug=True)

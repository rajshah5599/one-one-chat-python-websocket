from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

users = {}
connected_pairs = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    recipient = data['recipient']
    users[request.sid] = username
    connected_pairs[username] = recipient
    print("username ==>> ",username)
    print("request.sid ==>> ",request.sid)
    print("users ==>> ",    users)

    join_room(username)

    if recipient in connected_pairs and connected_pairs[recipient] == username:
        emit('connection_status', {'message': f'{username} is connected to {recipient}'}, room=username)
        emit('connection_status', {'message': f'{recipient} is connected to {username}'}, room=recipient)

@socketio.on('send_message')
def handle_send_message(data):
    recipient = data['recipient']
    message = data['message']
    sender = users.get(request.sid, 'Unknown')

    if recipient in users.values():
        emit('receive_message', {'sender': sender, 'message': message}, room=recipient)
        emit('receive_message', {'sender': sender, 'message': message}, room=sender)
    else:
        emit('receive_message', {'sender': 'System', 'message': f'{recipient} is not connected.'}, room=sender)

@socketio.on('disconnect')
def handle_disconnect():
    username = users.pop(request.sid, 'Unknown')
    if username != 'Unknown':
        send(f'{username} has left the chat.', to=username)
        connected_pairs.pop(username, None)
        for user, partner in connected_pairs.items():
            if partner == username:
                emit('connection_status', {'message': f'{username} has disconnected.'}, room=user)

if __name__ == '__main__':
    socketio.run(app, debug=True)

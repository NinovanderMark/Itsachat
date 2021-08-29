from enum import *
from aiohttp import web
import socketio

from serverclasses.roommanager import RoomManager
from serverclasses.userlist import UserList
from serverclasses.user import User


class LogLevel(IntEnum):
    NOTHING = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4


# Initialize Socket IO over an Asynchronous Webserver
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

# Sets up our own Server's variables
serverversion = '110'
servername = 'Awesome Itsachat Server'
loglevel = LogLevel.DEBUG
roommanager = RoomManager()
userlist = UserList('ItsaUser')


async def index(request):
    """Serve the client-side application."""
    try:
        with open('index.html') as f:
            return web.Response(text=f.read(), content_type='text/html')
    except FileNotFoundError:
        return web.Response(text="<title>404 Error</title><h1>404 - Page not found</h1>", status=404,
                            content_type='text/html')


@sio.on('connect')
async def connect(sid, request):
    if loglevel >= loglevel.INFO:
        print("Client connected ", sid)

    nickname = userlist.get_unique_name()
    newuser = User(sid, nickname)
    userlist.add_user(newuser)
    await sio.emit('connected', {'servername': servername, 'my_sid': sid, 'nickname': nickname}, room=sid)


@sio.on('disconnect')
async def disconnect(sid):
    if loglevel >= loglevel.INFO:
        print('Client disconnected ', sid)

    for room in userlist.get_user_sid(sid).get_rooms():
        roomname = room
        await leave_room(sid, data={'room': roomname})

    roommanager.leave_all(userlist.get_user_sid(sid))
    userlist.remove_user(sid)


@sio.on('join room')
async def enter_room(sid, data):
    # Get the data that we need to join a room
    if type(data) is not dict:
        roomname = data.lower()
    elif 'room' in data:
        roomname = data['room'].lower()
    else:
        if loglevel >= LogLevel.ERROR:
            print('Bad request received, no roomname found in data', data)

        return await sio.emit('bad request', data={'request': 'join room', 'error': 'Requires a room name, or object '
                                                                                    'with property \'room\''})

    userobject = userlist.get_user_sid(sid).get_object()

    if roomname in userobject['rooms']:
        if loglevel >= LogLevel.ERROR:
            print("User", sid, "is trying to join a channel that they are already in")

        return await sio.emit('bad request', data={'request': 'join room', 'error': 'Cannot join a channel that you are '
                                                                                    'already in'})

    # Join the user to the room
    room = roommanager.join_room(userlist.get_user_sid(sid), roomname)
    roomtopic = room.topic
    roomusers = room.get_user_list()
    sio.enter_room(sid, roomname)

    if loglevel >= LogLevel.INFO:
        print("User", userobject, "joins room", roomname, "with topic '" + roomtopic + "' and users", roomusers)

    await sio.emit('joined room', data={'room': roomname, 'topic': roomtopic,
                                        'users': roomusers}, room=sid)

    await sio.emit('user joined room', data={'user': userobject, 'room': roomname}, room=roomname)


@sio.on('leave room')
async def leave_room(sid, data):
    if type(data) is not dict:
        roomname = data.lower()
    elif 'room' in data:
        roomname = data['room'].lower()
    else:
        if loglevel >= LogLevel.ERROR:
            print('Bad request received, no roomname found in data', data)

        return await sio.emit('bad request', data={'request': 'leave room', 'error': 'Requires a room name, or object '
                                                                                     'with property \'room\''})
    userobject = userlist.get_user_sid(sid).get_object()

    if sid == roomname:
        if loglevel >= LogLevel.ERROR:
            print("User", userobject, "tried to leave room with their SID")

        return await sio.emit('unauthorized', data={'request': 'leave room', 'error': 'Cannot leave room with user SID'}
                              , room=sid)
    else:
        if roomname not in userobject['rooms']:
            if loglevel >= LogLevel.ERROR:
                print("User", sid, "is trying to leave a room that they aren't in")

            return await sio.emit('bad request', data={'request': 'leave room', 'error': 'Cannot leave room that user '
                                                                                         'is not in'})

        if loglevel >= LogLevel.INFO:
            print("User", userobject, "leaves room", roomname)

        await sio.emit('user left room', data={'user': userobject, 'room': roomname}, room=roomname)

        # Wait until that message is sent before removing the user from the room
        sio.leave_room(sid, roomname)
        roommanager.leave_room(userlist.get_user_sid(sid), roomname)


@sio.on('change nickname')
async def change_nickname(sid, data):
    # Get the data we need to perform a nickname change
    nickpass = ''
    if type(data) is not dict:
        newnick = data
    elif 'nickname' in data:
        newnick = data['nickname']
        if 'password' in data:
            nickpass = data['password']
    else:
        if loglevel >= LogLevel.ERROR:
            print('Bad request received, no nickname found in data object', data)

        return await sio.emit('bad request', data={'request': 'change nickname', 'error': 'Requires a nickname, or '
                                                                                          'object with property '
                                                                                          '\'nickname\''})
    # Check to see if the nickname is already in use
    if userlist.find_nickname(newnick):
            return await sio.emit('unavailable', data={'request': 'change nickname', 'error': 'Nickname \'' + newnick +
                                                                                              '\' is already in use'})
    userlist.get_user_sid(sid).nickname = newnick

    if loglevel >= loglevel.INFO:
        print("User", sid, "changed their nickname to", newnick)

    for room in userlist.get_user_sid(sid).get_object()['rooms']:
        await sio.emit('user changed nickname', data={'sid': sid, 'nickname': newnick}, room=room)


@sio.on('chat message')
async def message(sid, data):
    if data is not dict:
        if loglevel >= LogLevel.ERROR:
            print('Bad request, user attempting to send chat message with incomplete data', data)

        return await sio.emit('bad request', data={'request': 'chat message', 'error': 'Requires object with properties'
                                                                                       ' \'text\' and \'room\''})
    elif 'room' not in data:
        if loglevel >= LogLevel.ERROR:
            print('Bad request, user attempting to send chat message without room property', data)

        return await sio.emit('bad request', data={'request': 'chat message', 'error': 'Requires object with \'room\' '
                                                                                       'roperty'})
    elif 'text' not in data:
        if loglevel >= LogLevel.ERROR:
            print('Bad request, user attempting to send chat message without text property', data)

        return await sio.emit('bad request', data={'request': 'chat message', 'error': 'Requires object with \'text\' '
                                                                                       'roperty'})

    roomname = data['room'].lower()
    userobject = userlist.get_user_sid(sid).get_object()
    usernick = userobject['nickname']

    if roomname not in userobject['rooms']:
        if loglevel >= LogLevel.ERROR:
            print("User", sid, "is trying to talk to a room that they are not in")

        return await sio.emit('bad request', data={'request': 'leave room', 'error': 'Cannot talk to room that user '
                                                                                     'is not in'})

    if loglevel >= LogLevel.INFO:
        print("User", userobject, "sent chat message", data)

    await sio.emit('chat message', data={'text': data['text'], 'sid': sid, 'nickname': usernick,
                                         'room': roomname}, room=roomname)


@sio.on('list rooms')
async def list_rooms(sid):
    roomlist = roommanager.get_room_list()

    if loglevel >= LogLevel.INFO:
        print("User", sid, "requested the room list")
        if loglevel >= LogLevel.DEBUG:
            print("Roomlist: ", roomlist)

    await sio.emit('room list', data=roomlist)


@sio.on('get room')
async def return_room(sid, data):
    if loglevel >= LogLevel.INFO:
        print("User", sid, "retrieved the room object for", data['room'])

    await sio.emit(sio.rooms(data['room']))


app.router.add_get('/', index)

if __name__ == '__main__':
    print("Starting Itsachat Server version " + serverversion + "...")
    web.run_app(app)

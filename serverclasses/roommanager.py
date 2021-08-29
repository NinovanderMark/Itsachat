from serverclasses.chatroom import ChatRoom


class RoomManager:
    """ Manages creation/removal of rooms """
    def __init__(self):
        self._roomlist = dict()

    def join_room(self, user, roomname) -> ChatRoom:
        """ Adds a User object to a ChatRoom, creates the ChatRoom if it doesn't exist"""
        if roomname not in self._roomlist:
            self._roomlist[roomname] = ChatRoom(roomname)

        self._roomlist[roomname].add_user(user)
        return self._roomlist[roomname]

    def leave_room(self, user, roomname):
        """ Removes a User object from a ChatRoom, removes the ChatRoom if no more users are in it """
        if roomname not in self._roomlist:
            return 'Room ' + roomname + ' does not exist'

        self._roomlist[roomname].remove_user(user)
        if self._roomlist[roomname].get_user_count() < 1:
            del self._roomlist[roomname]

        return 0

    def leave_all(self, user):
        """ Removes a User object from all ChatRooms """
        for room in self._roomlist:
            self._roomlist[room].remove_user(user)

    def get_room_list(self) -> []:
        """ Returns a list of all the ChatRooms and their public properties """
        sendlist = []
        for roomname, room in self._roomlist.items():
            sendlist.append({'room': room.name, 'topic': room.topic, 'users': room.get_user_count()})

        return sendlist

    def get_room(self, roomname) -> ChatRoom:
        """ Returns the ChatRoom if it exists, otherwise returns None """
        if roomname in self._roomlist:
            return self._roomlist[roomname]
        else:
            return None

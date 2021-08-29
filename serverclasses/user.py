class User:
    """ Contains additional user data """
    def __init__(self, sid: str, nickname: str):
        self._sid = sid
        self._nickname = nickname
        self._rooms = []

    def get_sid(self) -> str:
        """ Returns the user's unique SID """
        return self._sid

    @property
    def nickname(self) -> str:
        """ Returns the user's nickname """
        return self._nickname

    @nickname.setter
    def nickname(self, newnick: str):
        """ Changes the user's nickname """
        self._nickname = newnick

    def join_room(self, roomname: str):
        """ Adds a joined room to the user """
        self._rooms.append(roomname)

    def leave_room(self, roomname: str):
        """ Removes a previously joined room from the user """
        self._rooms.remove(roomname)

    def get_rooms(self) -> []:
        """ Returns all rooms a user is in """
        return list(self._rooms)

    def is_in_room(self, roomname: str) -> bool:
        """ Returns whether a user is in a given room """
        return roomname in self._rooms

    def get_object(self) -> dict:
        """ Returns the JSON-able object for this user """
        return {'sid': self._sid, 'nickname': self._nickname, 'rooms': self._rooms}

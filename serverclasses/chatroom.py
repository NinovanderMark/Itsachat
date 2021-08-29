from serverclasses.user import User


class ChatRoom:
    """ Stores additional data for a chatroom in Socket IO """
    def __init__(self, name: str):
        self._name = name
        self._users = dict()
        self._operators = []
        self._topic = "Chat Room for " + name

    def add_user(self, user: User):
        """ Adds a User object to the ChatRoom """
        if user.get_sid() not in self._users:
            self._users[user.get_sid()] = user
            user.join_room(self._name)

    def remove_user(self, user: User):
        """ Removes a User object from the ChatRoom """
        if user.get_sid() in self._users:
            del self._users[user.get_sid()]
            user.leave_room(self._name)

    def get_user_count(self) -> int:
        """ Returns the amount of users in the ChatRoom """
        return len(self._users)

    def get_user_list(self) -> []:
        """ Returns a list with all the users as generic objects in this ChatRoom """
        returnlist = []
        for sid, user in self._users.items():
            returnlist.append(user.get_object())

        return returnlist

    @property
    def topic(self) -> str:
        return self._topic

    @topic.setter
    def topic(self, newtopic: str):
        self._topic = newtopic

    @property
    def name(self) -> str:
        return self._name

    def promote_user(self, username: str):
        """ Adds the username to the operators list """
        if username not in self._operators:
            self._operators.append(username)

    def demote_user(self, username: str):
        """ Adds the username to the operators list """
        if username in self._operators:
            self._operators.remove(username)

    def is_operator(self, username: str) -> bool:
        """ Returns whether the username is considered an operator """
        return username in self._operators

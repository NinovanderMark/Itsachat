from serverclasses.user import User


class UserList:
    def __init__(self, nameprefix: str):
        self._users = dict()
        self._uniquenumber = 1000
        self._nameprefix = nameprefix

    def add_user(self, user: User):
        """ Adds a user to the list """
        self._users[user.get_sid()] = user

    def get_user_sid(self, sid: str) -> User:
        """ Retrieves a user from the list by their SID """
        if sid in self._users:
            return self._users[sid]
        else:
            return None

    def get_user_nickname(self, nickname: str, case_sensitive: bool = False) -> User:
        """ Retrieves a user from the list by their Nickname """
        for sid, user in self._users.items():
            if case_sensitive:
                if nickname == user.nickname:
                    return user
            else:
                if nickname.lower() == user.nickname.lower():
                    return user

        return None

    def remove_user(self, sid: str):
        """ Removes a user from the list """
        if sid in self._users:
            del self._users[sid]

    def find_nickname(self, nickname: str, case_sensitive: bool = False) -> bool:
        """ Returns whether there is a user with this nickname """
        return type(self.get_user_nickname(nickname, case_sensitive)) is User

    def get_unique_name(self) -> str:
        self._uniquenumber += 1
        return self._nameprefix + str(self._uniquenumber)


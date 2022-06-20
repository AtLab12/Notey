import asyncio
import requests
import pyrebase
import json
from typing import Optional


class User:
    def __init__(self):
        self.__data = {}
        self.__user_id: Optional[str] = None
        self.__token: Optional[str] = None

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data: dict[str, str]):
        self.__data = data

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, id: str):
        self.__user_id = id

    @property
    def token(self):
        return self.__token

    @token.setter
    def token(self, token: str):
        self.__token = token

    def show_profile_details(self) -> None:
        """
        Presents only identifying data associated with currently logged user
        :return:
        """
        if self.data != {}:
            print("\nNickname: ", self.data["nick"])
            print("Name: ", self.data["name"])
            print("Lastname: ", self.data["last_name"], "\n")
        else:
            print("\n Unexpected error occurred \n")


user = User()


class UserDataManagement:

    async def get_user_by_nick(self, nick: str) -> tuple[dict[str, str], str]:
        """
        Checks if there is a user with provided nickname in the database
        :param nick:
        Users of interest nickname
        :return:
        If user exists then his data and id if not then None
        """
        loop = asyncio.get_event_loop()
        check_task = loop.run_in_executor(None, self.get_user_by_nick_call, nick)
        result = await check_task
        if not result.val():
            print("User with this nick name does not exist\n")
            return None
        else:
            id = next(iter((result.val().keys())))
            return result.val().get(id), id

    def get_user_by_nick_call(self, nick: str) -> dict[str, str]:
        """
        :param nick:
        Nick of interest
        :return:
        Returns specified users data
        """
        try:
            loc_user = db.child("users").order_by_child("nick").equal_to(nick).get()
            return loc_user
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)
            return

    async def refresh_data(self) -> None:
        """
        Refreshes local data of the currently logged-in user
        :return:
        """
        loc_nick = user.data["nick"]
        task = self.get_user_by_nick(loc_nick)
        result = await task
        user.data = result[0]

    async def get_user_by_email(self, email: str) -> tuple[dict[str, str], str]:
        """
        Downloads users with specified email data
        :param email:
        Email of interest.
        :return:
        Returns data and id.
        """
        loop = asyncio.get_event_loop()
        user_data_task = loop.run_in_executor(None, self.get_user_call, email)
        result = await user_data_task
        id = next(iter((result.val().keys())))
        return result.val().get(id), id

    def get_user_call(self, email: str) -> dict[str, str]:
        """
        Firebase synchronous call to get users with specified email data
        :param email:
        Email of interest
        :return:
        Users data
        """
        try:
            user_loc = db \
                .child("users") \
                .order_by_child("email") \
                .equal_to(email).get()
            return user_loc
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)
            return

    async def get_all_users(self) -> list[str]:
        """
        :return:
        Returns a list of all used nicks
        """
        nicks = []
        loop = asyncio.get_event_loop()
        get_all_users_task = loop.run_in_executor(None, self.get_all_users_call)
        result = await get_all_users_task
        for value in result.val().values():
            nicks.append(value['nick'])
        return nicks

    def get_all_users_call(self) -> dict[str, dict[str, str]]:
        """
        Firebase synchronous call to get all users data
        :return:
        Users data
        """
        try:
            users = db.child("users").get()
            return users
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)
            return


# initial firebase configuration
firebaseConfig = {
    'apiKey': "AIzaSyCkXdB3mIonc9F6Ic9D_0rDYc2HLInuxdc",
    'authDomain': "notey-ee724.firebaseapp.com",
    'databaseURL': "https://notey-ee724-default-rtdb.europe-west1.firebasedatabase.app/",
    'projectId': "notey-ee724",
    'storageBucket': "notey-ee724.appspot.com",
    'messagingSenderId': "161243066116",
    'appId': "1:161243066116:web:d19d76f55139e0c50f2a51",
    'measurementId': "G-73LBDN21LX"
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
data_management = UserDataManagement()

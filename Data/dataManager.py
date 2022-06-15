import asyncio
import requests
import pyrebase
import json


class User:
    def __init__(self):
        self.__data = {}
        self.__user_id: str = None
        self.__token: str = None

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
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

    def show_profile_details(self):
        """
        Presents ony identifying data associated with currently logged user
        :return:
        """
        if self.data != {}:
            print("\nNickname: ", self.data["nick"])
            print("Name: ", self.data["name"])
            print("Lastname: ", self.data["last_name"], "\n")
        else:
            print("\n Unexpected error occured \n")


class UserDataManagement:


    async def get_user_by_nick(self, nick: str):
        """
        Checks if there is a user with provided nickname in the database
        :param nick:
        Users of interest nickname
        :return:
        If user exists then his id if not None
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

    def get_user_by_nick_call(self, nick: str):
        try:
            loc_user = db.child("users").order_by_child("nick").equal_to(nick).get()
            return loc_user
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)
            return

    async def refresh_data(self):
        global user
        loc_nick = user.data["nick"]
        task = self.get_user_by_nick(loc_nick)
        result = await task
        user = result[0]

    async def get_user_by_email(self, email: str):
        """
        Downloads users data.
        :param email:
        :return:
        """
        loop = asyncio.get_event_loop()
        user_data_task = loop.run_in_executor(None, self.get_user_call, email)
        result = await user_data_task
        id = next(iter((result.val().keys())))
        return result.val().get(id), id

    def get_user_call(self, email: str):
        try:
            user_loc = db\
                .child("users")\
                .order_by_child("email")\
                .equal_to(email).get()
            return user_loc
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)
            return

    async def get_all_users(self):
        nicks = []
        loop = asyncio.get_event_loop()
        get_all_users_task = loop.run_in_executor(None, self.get_all_users_call)
        result = await get_all_users_task
        for value in result.val().values():
            nicks.append(value['nick'])
        return nicks

    def get_all_users_call(self):
        try:
            users = db.child("users").get()
            return users
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)
            return


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
user = User()
data_management = UserDataManagement()
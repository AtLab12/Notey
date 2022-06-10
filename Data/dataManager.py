import asyncio
import requests
import pyrebase
import json
#wydzielić kod na klasy żeby to poukładać
#jest dobra szansa na 4 bo projekt idzie w dobrym kierunku
#skupić się na funkcjonalnościach nie na GUI

user = {}
user_id: str = None

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


def show_profile_details():
    """
    Presents ony identifying data associated with currently logged user
    :return:
    """
    if user != {}:
        print("\nNickname: ", user["nick"])
        print("Name: ", user["name"])
        print("Lastname: ", user["last_name"], "\n")
    else:
        print("\n Unexpected error occured \n")


async def get_user(nick: str):
    """
    Checks if there is a user with provided nickname in the database
    :param nick:
    Users of interest nickname
    :return:
    If user exists then his id if not None
    """
    loop = asyncio.get_event_loop()
    check_task = loop.run_in_executor(None, get_user_by_nick_call, nick)
    result = await check_task
    if not result.val():
        print("User with this nick name does not exist\n")
        return None
    else:
        id = next(iter((result.val().keys())))
        return result.val().get(id), id

async def refresh_data():
    global user
    task = get_user(user["nick"])
    result = await task
    user = result[0]


def get_user_by_nick_call(nick: str):
    try:
        user = db.child("users").order_by_child("nick").equal_to(nick).get()
        return user
    except requests.exceptions.HTTPError as e:
        error_json = e.args[1]
        error_message = json.loads(error_json)['error']['message']
        print(error_message)
        return
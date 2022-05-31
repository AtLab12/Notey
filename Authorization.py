import json
import pyrebase
import re
import requests
import asyncio

firebaseConfig = {
    'apiKey': "AIzaSyCkXdB3mIonc9F6Ic9D_0rDYc2HLInuxdc",
    'authDomain': "notey-ee724.firebaseapp.com",
    'databaseURL': "https://notey-ee724-default-rtdb.europe-west1.firebasedatabase.app/",
    'projectId': "notey-ee724",
    'storageBucket': "notey-ee724.appspot.com",
    'messagingSenderId': "161243066116",
    'appId': "1:161243066116:web:d19d76f55139e0c50f2a51",
    'measurementId': "G-73LBDN21LX"
  };

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

async def signUp():
    print("""
    You are about to begin the registration process.
    Please make sure you fill all filed correctly
    """)
    email = input("Please provide email: ")

    while(not validateEmail(email)):
        print("\n !!! Invalid email provided, please try again !!! \n")
        email = input("Please provide email: ")

    password = input("Pleas provide password: ")
    passwordValidation = input("Pleas provide password again: ")

    while (password != passwordValidation or len(password) < 8):
        print("\n !!! Passwords don't mach, please try again !!! \n ")
        password = input("Pleas provide password: ")
        passwordValidation = input("Pleas provide password again: ")

    try:
        loop = asyncio.get_event_loop()
        userTask = loop.run_in_executor(None, auth.create_user_with_email_and_password, email, password)
    except requests.exceptions.HTTPError as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']['message']
        if error == "EMAIL_EXISTS":
            print("Email already exists")

    await userTask
    dataTaskCreation = asyncio.create_task(createUserDetails(email))
    await dataTaskCreation

    print(userTask.result()["email"])


def login():
    email = input("Please provide email: ")

    if email == "back":
        return

    while (not validateEmail(email)):
        print("\n !!! Invalid email provided, please try again !!! \n")
        email = input("Please provide email: ")

    password = input("Pleas provide password: ")

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        print("Welcome back!")
        return user
    except:
        print("Invalid email or password")

async def createUserDetails(email):
    nick = input("Please provide nick name: ")
    loop = asyncio.get_event_loop()
    userTask = loop.run_in_executor(None, validateNickName, nick)
    await userTask

    while len(userTask.result().val()) != 0:
        print("This username is already taken. Please try a different one")
        nick = input("Please provide nick name: ")
        userTask = loop.run_in_executor(None, validateNickName, nick)
        await userTask

    name = input("Please provide your name: ")
    lastName = input("Please provide your last name: ")

    data = { "nick": nick, "name": name, "lastName": lastName, "email": email}
    try:
        db.child("users").push(data)
    except:
        raise

def validateNickName(nick):
    try:
         owner = db.child("users").order_by_child("nick").equal_to(nick).get()
         return owner
    except:
        raise

#1@pwr.edu.pl

def validateEmail(email):
    regex = '^(.*?)@(.*?)(pl)' # dodac pwr.edu.pl
    if email != None:
        if re.match(regex, email):
            return True
    else:
        return False


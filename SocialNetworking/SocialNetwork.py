import asyncio
import Authorization as au
import requests
import json
import Data.dataManager as dataM
import DataFlow as dataF

import pyrebase


# search friends

# send request

async def send_request(nick: str):
    """
    method checks if user with provided email exists
    checks if currently logged in user haven't already requested a friendship
    send friendship request to desired user
    :param nick:
    :return:
    """
    loop = asyncio.get_event_loop()
    check_task = dataM.get_user(nick)
    user_data = await check_task

    if user_data[0] is not None:
        req = user_data[0]["requests"]
        my_nick = dataM.user["nick"]
        if my_nick not in req:
            req.append(dataM.user["nick"])
            dataM.db.child("users").child(user_data[1]).update({"requests": req})
            print("Requests sent")
        else:
            print("You already sent request to this user")

async def handle_myrequests():
    """
    Refreshes users current data
    Shows all requests
    Handles request acceptance
    :return:
    """
    task = dataF.getUserdata(dataM.user["email"])
    result = await task
    dataM.user = result[0]
    index = 0
    my_nick = dataM.user["nick"]
    if "requests" in list(dataM.user.keys()):
        print("\nPeople who want to be your friends: ")
        for req_nick in dataM.user["requests"]:
            print(index, ": ", req_nick)
            index += 1
    else:
        print("\nNo new requests\n")
        return

    print("Who do you want to accept as a friend? (type noOne to quit)")
    new_friend = input()
    if new_friend == "noOne" or new_friend == 0:
        return
    else:
        if not new_friend.isdigit():
            print("Invalid choice")
            return
        else:
            if int(new_friend) >= index:
                print("uups. I'm afraid you are not interesting enough to have ", new_friend, "new requests.\n")
            else:
                if "friends" in dataM.user.keys():
                    friends = dataM.user["friends"]
                else:
                    friends = []
                friends.append(dataM.user["requests"][int(new_friend)])
                dataM.db.child("users").child(dataM.user_id).update({"friends": friends})
                del dataM.user["requests"][int(new_friend)]
                dataM.db.child("users").child(dataM.user_id).update({"requests": dataM.user["requests"]})

def run_remove_friend():
    if "friends" in dataM.user.keys():
        index = 0
        for friend in dataM.user["friends"]:
            print(index, ": ", friend)
            index += 1
        selection = input("Who do you want to remove? \n")
        if selection == "back": return
        if selection.isdigit() and int(selection) < index:
            del dataM.user["friends"][int(selection)]
            dataM.db.child("users").child(dataM.user_id).update({"friends": dataM.user["friends"]})
        else:
            print("Invalid input")
    else:
        print("You don't have any friends to remove yet")


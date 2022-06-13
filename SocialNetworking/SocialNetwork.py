import asyncio
import Data.dataManager as dataM
import MenusUtility.MenuUtility as m_utility

async def send_request(nick: str):
    """
    method checks if user with provided email exists
    checks if currently logged in user haven't already requested a friendship
    send friendship request to desired user
    :param nick:
    :return:
    """
    if nick == dataM.user.data["nick"]:
        print("You can't add yourself as friend silly ;)")
        return

    loop = asyncio.get_event_loop()
    check_task = dataM.data_management.get_user_by_nick(nick)
    user_data = await check_task

    if user_data is not None:
        if "requests" in user_data[0]:
            req = user_data[0]["requests"]
        else:
            req = []

        my_nick = dataM.user.data["nick"]
        if my_nick not in req:
            req.append(dataM.user.data["nick"])
            dataM.db.child("users").child(user_data[1]).update({"requests": req})
            print("Requests sent")
        else:
            print("You already sent request to this user")
    else:
        # make request to get all users
        # check if any of the have acceptable modyfication dystans
        # if not don't show anything
        # if yes present and give option to opt out
        # end
        print("Did you mean to send request to one of these users? \n")
        m_utility.handle_selection()


async def handle_myrequests():
    """
    Refreshes users current data
    Shows all requests
    Handles request acceptance for both users
    :return:
    """
    task = dataM.data_management.get_user_by_email(dataM.user.data["email"])
    result = await task
    dataM.user.data = result[0]
    index = 0
    my_nick = dataM.user.data["nick"]
    if "requests" in list(dataM.user.data.keys()):
        print("\nPeople who want to be your friends: ")
        for req_nick in dataM.user.data["requests"]:
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
                new_friend_nick = dataM.user.data["requests"][int(new_friend)]
                new_friend_data_task = dataM.user.get_user_by_nick(new_friend_nick)
                new_friend_data_task_result = await new_friend_data_task
                new_friend_id = new_friend_data_task_result[1]
                new_friend_data = new_friend_data_task_result[0]

                if "friends" in new_friend_data.keys():
                    new_friend_friends = new_friend_data["friends"]
                else:
                    new_friend_friends = []

                new_friend_friends.append(my_nick)

                if "friends" in dataM.user.keys():
                    friends = dataM.user["friends"]
                else:
                    friends = []

                friends.append(new_friend_nick)
                dataM.db.child("users").child(dataM.user.user_id).update({"friends": friends})
                dataM.db.child("users").child(new_friend_id).update({"friends": new_friend_friends})
                del dataM.user.data["requests"][int(new_friend)]
                dataM.db.child("users").child(dataM.user.user_id).update({"requests": dataM.user["requests"]})
                await dataM.refresh_data()


async def run_remove_friend():
    """
    Deletes friend based on user selection.
    Automatically deletes currenty logged in user from the currently beeing deleted friends list.
    :return:
    """
    if "friends" in dataM.user.keys():
        index = 0
        for friend in dataM.user["friends"]:
            print(index, ": ", friend)
            index += 1
        selection = input("Who do you want to remove? \n")
        if selection == "back": return
        if selection.isdigit() and int(selection) < index:
            selected_friend_nick = dataM.user["friends"][int(selection)]
            selected_friend_task = dataM.get_user(selected_friend_nick)
            selected_friend_task_result = await selected_friend_task

            selected_friend_id = selected_friend_task_result[1]
            selected_friend_data = selected_friend_task_result[0]

            selected_friends = selected_friend_data["friends"]
            selected_friends.remove(dataM.user["nick"])

            del dataM.user["friends"][int(selection)]
            dataM.db.child("users").child(dataM.user_id).update({"friends": dataM.user["friends"]})
            dataM.db.child("users").child(selected_friend_id).update({"friends": selected_friends})
        else:
            print("Invalid input")
    else:
        print("You don't have any friends to remove yet")


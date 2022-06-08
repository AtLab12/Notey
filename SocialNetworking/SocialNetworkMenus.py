import asyncio
import MenusUtility.MenuUtility as mUtility
import Data.dataManager as dataM
import SocialNetworking.SocialNetwork as socialNet

def print_friend_menu():
    menu = {
        1: "See your friends",
        2: "Check for new requests",
        3: "Send request",
        4: "Remove friend",
        5: "Back"
    }

    for key in menu.keys():
        print(key, menu[key])
    print('\n')


async def run_friends():
    """
    Presents frinds section menu
    :return:
    """
    print("Please select one of the following options: ")
    print_friend_menu()
    choice = mUtility.handle_selection()

    while True:
        if choice == 1:
            pass
        if choice == 2:
            pass
        if choice == 3:
            print("\n Please provide your friend nickname: ")
            nick = input("Type here: ")
            request_task = socialNet.checkIfUserExists(nick)
            await request_task
        if choice == 4:
            pass
        if choice == 5:
            pass

        print_friend_menu()
        choice = mUtility.handle_selection()
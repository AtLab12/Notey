import MenusUtility.MenuUtility as mUtility
import Data.dataManager as dataM
import SocialNetworking.SocialNetwork as socialNet

socialNetwork = socialNet.SocialNetwork()

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
    Presents friends section menu
    :return:
    """
    print("Please select one of the following options: ")
    print_friend_menu()
    choice = mUtility.handle_selection()

    while True:
        if choice == 1:
            if "friends" in dataM.user.data.keys():
                print("Your friends: ")
                for friend in dataM.user.data["friends"]:
                    print(friend)
            else:
                print("Currently you don't have any friends")
        if choice == 2:
            await socialNetwork.handle_myrequests()
        if choice == 3:
            print("\n Please provide your friend nickname: ")
            nick = input("Type here: ")
            request_task = socialNetwork.send_request(nick)
            await request_task
        if choice == 4:
            await socialNetwork.run_remove_friend()
        if choice == 5:
            break

        print_friend_menu()
        choice = mUtility.handle_selection()
import asyncio
import MenusUtility.MenuUtility as mUtility
import Data.dataManager as dataM

def printFriendMenu():
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


async def runFriends():
    """
    Presents frinds section menu
    :return:
    """
    print("Please select one of the following options: ")
    printFriendMenu()
    choice = mUtility.handleSelection()

    while True:
        if choice == 1:
            pass
        if choice == 2:
            pass
        if choice == 3:
            pass
        if choice == 4:
            pass
        if choice == 5:
            pass

        printFriendMenu()
        choice = mUtility.handleSelection()
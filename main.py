import asyncio
import Authorization as authC
import DataFlow as dataF
from SocialNetworking import SocialNetworkMenus as socialNMenus
import MenusUtility.MenuUtility as mUtility
import Data.dataManager as dataM

def printMenu():
    menu = {
        1: 'Register',
        2: 'Login',
        3: 'Forgot password',
        4: 'Finish'
    }
    for key in menu.keys():
        print(key, menu[key])
    print('\n')

#       259431@student.pwr.edu.pl

async def runNotey():
    """
    Method enables login or registration.
    :return:
    """
    print("Welcome to Notey!")

    printMenu()
    choice = mUtility.handleSelection()

    while True:
        if choice == 1:
            registrationTask = asyncio.create_task(authC.signUp())
            await registrationTask
            if registrationTask.result() == '':
                print("Registration unsuccessful. Please try again")
        elif choice == 2:
            loginTask = asyncio.create_task(authC.login())
            await loginTask
            email = loginTask.result()['email']
            if email != '':
                getUserTask = dataF.getUserdata(email)
                dataM.user = await getUserTask
                await runMain()
        elif choice == 3:
            pasResettask = asyncio.create_task(authC.passwordReset())
            await pasResettask
        elif choice == 4:
            break
        else:
            print("Invalid selection. Please try again.")

        printMenu()
        choice = mUtility.handleSelection()


def printMainMenu():
    menu = {
        1: 'Friends',
        2: 'Notes',
        3: 'View profile details',
        4: 'Logout'
    }
    for key in menu.keys():
        print(key, menu[key])
    print('\n')

async def runMain():
    """
    This method is the center of the whole project.
    It handles all functionalities for logged in user.
    :return:
    """
    print("Please select one of the following options: ")
    printMainMenu()
    choice = mUtility.handleSelection()

    while True:
        if choice == 1:
            await socialNMenus.runFriends()
        if choice == 2:
            pass
        if choice == 3:
            dataM.showProfileDetails()
        if choice == 4:
            dataM.user = {}
            break
        printMainMenu()
        choice = mUtility.handleSelection()



asyncio.run(runNotey())
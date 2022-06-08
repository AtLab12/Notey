import asyncio
import Authorization as authC
import DataFlow as dataF

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
    choice = handleSelection()

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
                await getUserTask
                await runMain()
        elif choice == 3:
            pasResettask = asyncio.create_task(authC.passwordReset())
            await pasResettask
        elif choice == 4:
            break
        else:
            print("Invalid selection. Please try again.")

        printMenu()
        choice = handleSelection()


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
    choice = handleSelection()

    while True:
        if choice == 1:
            pass
        if choice == 2:
            pass
        printMainMenu()
        choice = handleSelection()

def handleSelection():
    """
    Method protects program from invalid input
    :return:
    """
    selection = input("Please type your selection: ")
    while not selection.isdigit():
        print("\n Invalid input \n")
        selection = input("Please type your selection: ")

    return int(selection)

asyncio.run(runNotey())
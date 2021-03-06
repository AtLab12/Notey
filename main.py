import asyncio
import Authorization as authC
from SocialNetworking import SocialNetworkMenus as socialNMenus
from Notes import NotesMenus as noteMenu
import MenusUtility.MenuUtility as mUtility
import Data.dataManager as dataM

auth = authC.Authorization()


def print_menu() -> None:
    """
    Function displays initial menu.
    :return:
    """
    menu = {
        1: 'Register',
        2: 'Login',
        3: 'Forgot password',
        4: 'Finish'
    }
    for key in menu.keys():
        print(key, menu[key])
    print('\n')


async def run_notey() -> None:
    """
    Function enables login, registration, resetting password and quiting application.
    :return:
    """
    print("Welcome to Notey!")

    print_menu()
    choice = mUtility.handle_selection()

    while True:
        if choice == 1:
            registration_task = asyncio.create_task(auth.sign_up())
            await registration_task
            if not registration_task.result():
                print("Registration unsuccessful. Please try again!")
        elif choice == 2:
            login_task = asyncio.create_task(auth.login())
            await login_task
            result = login_task.result()
            if result is not None:
                email = result['email']
                dataM.user.token = result['idToken']
                get_user_task = dataM.data_management.get_user_by_email(email)
                result = await get_user_task
                dataM.user.data = result[0]
                dataM.user.user_id = result[1]
                await run_main()
        elif choice == 3:
            pas_reset_task = asyncio.create_task(auth.password_reset())
            await pas_reset_task
        elif choice == 4:
            break
        else:
            print("Invalid selection. Please try again.")

        print_menu()
        choice = mUtility.handle_selection()


def print_main_menu() -> None:
    """
    Function displays main menu for logged user.
    This menu is only accessible by a logged-in user.
    :return:
    """
    menu = {
        1: 'Friends',
        2: 'Notes',
        3: 'View profile details',
        4: 'Logout'
    }
    for key in menu.keys():
        print(key, menu[key])
    print('\n')


async def run_main() -> None:
    """
    This method is the navigation center of the whole project.
    It handles all functionalities for logged-in user.
    :return:
    """
    print("Please select one of the following options: ")
    print_main_menu()
    choice = mUtility.handle_selection()

    while True:
        if choice == 1:
            await socialNMenus.run_friends()
        if choice == 2:
            await noteMenu.run_notes()
        if choice == 3:
            dataM.user.show_profile_details()
        if choice == 4:
            dataM.user.data = None
            break
        print_main_menu()
        choice = mUtility.handle_selection()

# here we run the whole app
asyncio.run(run_notey())

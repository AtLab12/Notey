import Authorization as authC

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


def runNotey():
    print("Welcome to Notey!")

    printMenu()
    choice = int(input("Please type your selection: "))

    while True:
        if choice == 1:
            user = authC.signUp()
            if user is None:
                print("Registration unsuccessful. Please try again")
        elif choice == 2:
            authC.login()
        elif choice == 4:
            break
        else:
            print("Invalid selection. Please try again.")

        printMenu()



runNotey()
import asyncio
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

#259431@student.pwr.edu.pl
async def runNotey():
    print("Welcome to Notey!")

    printMenu()
    choice = int(input("Please type your selection: "))

    while True:
        if choice == 1:
            registrationTask = asyncio.create_task(authC.signUp())
            await registrationTask
            if registrationTask.result() == '':
                print("Registration unsuccessful. Please try again")
        elif choice == 2:
            loginTask = asyncio.create_task(authC.login())
            await loginTask
            if loginTask.result()['email'] != '':
                print(loginTask.result()['email'])
        elif choice == 3:
            pasResettask = asyncio.create_task(authC.passwordReset())
            await pasResettask
        elif choice == 4:
            break
        else:
            print("Invalid selection. Please try again.")

        printMenu()
        choice = int(input("Please type your selection: "))

async def runMain():
    print("Please select one of the following options: ")

asyncio.run(runNotey())
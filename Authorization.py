import json
import re
import requests
import asyncio
import Data.dataManager as dataM
from typing import Optional


class Authorization:
    """
    Class contains all methods responsible for handling any authentication actions. Like:
    1. Registration
    2. Logging in
    3. Sending "forgot password email"
    4. Checking if nick is available
    5. Creating detailed user entity in database
    6. Validating email address
    """

    async def sign_up(self) -> bool:
        """
        Method handles the whole sign up process
        Creates auth object used later to authenticate using email and password
        Calls to create detailed user entity in database
        :return:
        Returns info weather registration was successful
        """

        print("""
        You are about to begin the registration process.
        Please make sure you fill all fields correctly
        """)
        email = input("Please provide email: ")
        email_cloud_validated = False

        # checking if email conforms to set email format
        while not self.validate_email(email):
            print("\n !!! Invalid email provided, please try again !!! \n")
            email = input("Please provide email: ")

        password = input("Please provide password: ")
        password_validation = input("Pleas provide password again: ")

        # checks if passwords match and if are long enough
        while password != password_validation or len(password) < 8:
            print("\n !!! Passwords don't mach, please try again !!! \n ")
            password = input("Pleas provide password: ")
            password_validation = input("Pleas provide password again: ")

        # checks if user with provided email already exists
        while not email_cloud_validated:
            try:
                loop = asyncio.get_event_loop()
                user_task = loop.run_in_executor(None, dataM.auth.create_user_with_email_and_password, email, password)
                task_result = await user_task
                email_cloud_validated = True

                # calling to create detailed user entity in database
                data_task_creation = asyncio.create_task(self.create_user_details(email))
                await data_task_creation

                if task_result["email"] == '':
                    return False
                else:
                    return True
            except requests.exceptions.HTTPError as e:
                error_json = e.args[1]
                error = json.loads(error_json)['error']['message']
                if error == "EMAIL_EXISTS":
                    email_cloud_validated = False
                    print("Email already exists")
                    email = input("Please provide email: ")

    async def login(self) -> Optional[dict[str, str]]:
        """
        Method handles the whole login process
        :return:
        """
        email = input("Please provide email: ")

        if email == "back":
            return

        while not self.validate_email(email):
            print("\n !!! Invalid email provided, please try again !!! \n")
            email = input("Please provide email: ")

        password = input("Please provide password: ")

        try:
            loop = asyncio.get_event_loop()
            user_logintask = loop.run_in_executor(None, dataM.auth.sign_in_with_email_and_password, email, password)
            result = await user_logintask
            return result
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            if error == "INVALID_PASSWORD":
                print("Invalid password")
            else:
                print("Invalid email")
            return

    async def create_user_details(self, email):
        """
        Creates user with specified parameters in the database.
        :param email:
        String representing users email address
        :return:
        """

        nick = input("Please provide nick name: ")
        loop = asyncio.get_event_loop()

        # checking if username with provided email already exists
        user_task = loop.run_in_executor(None, self.validate_nick_name, nick)
        result = await user_task

        while len(result.values()) != 0:
            print("This username is already taken. Please try a different one")
            nick = input("Please provide nick name: ")
            user_task = loop.run_in_executor(None, self.validate_nick_name, nick)
            await user_task

        name = input("Please provide your name: ")
        last_name = input("Please provide your last name: ")
        path = input("Pleas provide path to folder where you will save your notes: ")
        data = {
            "nick": nick,
            "name": name,
            "last_name": last_name,
            "email": email,
            "path": path
        }
        dataM.db.child("users").push(data)

    async def password_reset(self) -> None:
        """
        Sends to an email provided via user input with password reset link.
        :return:
        """
        email = input("Please provide email: ")

        if email == "back":
            return

        while not self.validate_email(email):
            print("\n !!! Invalid email provided, please try again !!! \n")
            email = input("Please provide email: ")

        loop = asyncio.get_event_loop()
        task = loop.run_in_executor(None, dataM.auth.send_password_reset_email, email)
        await task

    def validate_nick_name(self, nick: str) -> Optional[dict[str, str]]:
        """
        Checks if user with certain nickname doesn't already exist
        :param nick:
        String representing users nickname
        :return:
        If user with specified nickname exists returns its data
        """

        owner = dataM.db.child("users").order_by_child("nick").equal_to(nick).get()
        return owner

    def validate_email(self, email: str) -> bool:
        """
        Checks if provided email fits the standard
        :param email:
        String representing users email address
        :return:
        """
        regex = '^(.*?)@(.*?)(.pl)'
        if email is not None:
            if re.match(regex, email):
                return True
        else:
            return False

import json
import re
import requests
import asyncio
import Data.dataManager as dataM


class Authorization:
    async def sign_up(self):
        """
        Method handles the whole sign up process
        Creates auth object used later to authenticate using email and password
        :return:
        """

        print("""
        You are about to begin the registration process.
        Please make sure you fill all fields correctly
        """)
        email = input("Please provide email: ")
        email_cloud_validated = False

        while not self.validate_email(email):
            print("\n !!! Invalid email provided, please try again !!! \n")
            email = input("Please provide email: ")

        password = input("Please provide password: ")
        password_validation = input("Pleas provide password again: ")

        while password != password_validation or len(password) < 8:
            print("\n !!! Passwords don't mach, please try again !!! \n ")
            password = input("Pleas provide password: ")
            password_validation = input("Pleas provide password again: ")

        while not email_cloud_validated:
            try:
                loop = asyncio.get_event_loop()
                user_task = loop.run_in_executor(None, dataM.auth.create_user_with_email_and_password, email, password)
                await user_task
                email_cloud_validated = True
            except requests.exceptions.HTTPError as e:
                error_json = e.args[1]
                error = json.loads(error_json)['error']['message']
                if error == "EMAIL_EXISTS":
                    email_cloud_validated = False
                    print("Email already exists")
                    email = input("Please provide email: ")

        data_task_creation = asyncio.create_task(self.create_user_details(email))
        await data_task_creation
        return user_task.result()["email"]

    async def login(self):
        """
        Method handles the whole login process
        :return:
        """

        # email = input("Please provide email: ")
        #email = "259431@student.pwr.edu.pl"
        email = "mikolaj.adawaz@gmail.com"

        if email == "back":
            return

        while not self.validate_email(email):
            print("\n !!! Invalid email provided, please try again !!! \n")
            email = input("Please provide email: ")

        # password = input("Please provide password: ")
        password = "12345678"
        #password = "87654321"

        try:
            loop = asyncio.get_event_loop()
            user_logintask = loop.run_in_executor(None, dataM.auth.sign_in_with_email_and_password, email, password)
            await user_logintask
            return user_logintask.result()
        except:
            print("Invalid email or password. Please try again.")
            return None

    async def create_user_details(self, email):
        """
        Creates user with specified parameters in the database.
        :param email:
        String representing users email address
        :return:
        """

        nick = input("Please provide nick name: ")
        loop = asyncio.get_event_loop()
        user_task = loop.run_in_executor(None, self.validate_nick_name, nick)
        await user_task

        while len(user_task.result().val()) != 0:
            print("This username is already taken. Please try a different one")
            nick = input("Please provide nick name: ")
            user_task = loop.run_in_executor(None, self.validate_nick_name, nick)
            await user_task

        name = input("Please provide your name: ")
        last_name = input("Please provide your last name: ")
        path = input("Pleas eprovide path to folder where you will save your notes: ")
        data = {
            "nick": nick,
            "name": name,
            "last_name": last_name,
            "email": email,
            "path": path
        }
        try:
            dataM.db.child("users").push(data)
        except:
            raise

    async def password_reset(self):
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

    def validate_nick_name(self, nick: str):
        """
        Checks if user with certain nickname doesn't already exist
        :param nick:
        String representing users nickname
        :return:
        """
        try:
            owner = dataM.db.child("users").order_by_child("nick").equal_to(nick).get()
            return owner
        except:
            raise

    def validate_email(self, email: str):
        """
        Checks if provided email fits the standarized form
        :param email:
        String representing users email address
        :return:
        """
        regex = '^(.*?)@(.*?)'  # dodac (pwr.edu.pl) po (.*?)
        if email is not None:
            if re.match(regex, email):
                return True
        else:
            return False

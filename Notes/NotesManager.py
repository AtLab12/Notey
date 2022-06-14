import json
import re
import requests
import asyncio
import pyrebase
import Data.dataManager as dataM
from datetime import date
import MenusUtility.MenuUtility as m_utility

storage = dataM.firebase.storage()


class NotesManager:
    async def createNote(self):
        """
        method creates new note on local machine
        sends start note to database and creates details
        :return:
        """
        name = input("How do you want to name your file? : ")
        validation_task = await self.get_note_by_name(str(name))

        #checking if note with provided name already exists
        while validation_task is not None:
            print("\n !!Note with this name already exists!! \n")
            name = input("How do you want to name your file? : ")
            validation_task = await self.get_note_by_name(name)
            if name == "back":
                return

        #setting destination path for new file
        final_path = dataM.user.data['path'] + "/" + name + ".txt"
        with open(final_path, 'w') as f:
            f.write("This is your new note! ", )

        #sending file to database
        storage.child(name).put(final_path)
        link = storage.child(name).get_url(None)
        data = {
            "author": dataM.user.data['nick'],
            'name': name,
            "version": 1,
            "lastModified": str(date.today()),
            "link": link,
            "archive": [link]
        }

        dataM.db.child("notes").push(data)

    async def get_note_by_name(self, name: str):
        """
        returns None if note doesn't exist and result if exists
        :param name:
        :return:
        """
        loop = asyncio.get_event_loop()
        note_task = loop.run_in_executor(None, self.__get_note_by_name_call, name)
        result = await note_task
        if not result.val():
            return None
        else:
            id = next(iter((result.val().keys())))
            return result.val().get(id), id

    def __get_note_by_name_call(self, name: str):
        """
        Returns note with specified name
        :param name:
        :return:
        """
        try:
            note = dataM.db.child("notes").order_by_child("name").equal_to(name).get()
            return note
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)

    async def get_notes_for_user_with_nick(self, nick: str):
        """
        returns all notes with author whos nick is the same as parameter
        :param nick:
        :return:
        """
        loop = asyncio.get_event_loop()
        call_task = loop.run_in_executor(None, self.__get_notes_by_nick, nick)
        result = await call_task
        notes = []
        for item in result.val().items():
            notes.append(item)
        return notes

    def __get_notes_by_nick(self, nick: str):
        """
        database call for all notes with author whos nick is the same as parameter
        :param nick:
        :return:
        """
        try:
            notes = dataM.db.child("notes").order_by_child("author").equal_to(nick).get()
            return notes
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)

    async def remove_note(self):
        """
        enables user to remove note with specific name
        :return:
        """

        notes = await self.get_notes_for_user_with_nick(dataM.user.data["nick"])
        index = 0
        if len(notes) == 0:
            print("You don't have any notes")
            return
        else:
            for note in notes:
                print(index, ": ", note[1]["name"])
                index += 1

        print("Which note do you want to remove? ")
        choice = m_utility.handle_selection()

        if choice >= index:
            return
        else:
            storage.child(notes[choice][1]["name"]).delete(notes[choice][1]["name"], dataM.user.token)
            dataM.db.child("notes").child(notes[choice][0]).remove()
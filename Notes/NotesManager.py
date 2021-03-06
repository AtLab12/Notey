import json
import requests
import asyncio
import Data.dataManager as dataM
from datetime import date
import MenusUtility.MenuUtility as m_utility
import os
from typing import Optional

storage = dataM.firebase.storage()


class NotesManager:
    async def createNote(self) -> None:
        """
        method creates new note on local machine
        sends start note to database and creates note entity
        removes local copy in order to force only one note source to exist
        :return:
        """
        name = input("How do you want to name your file? : ")
        name = name + "_v1"
        validation_task = await self.get_note_by_name(str(name))

        # checking if note with provided name already exists
        while validation_task is not None:
            print("\n !!Note with this name already exists!! \n")
            name = input("How do you want to name your file? : ")
            name = name + "_v1"
            validation_task = await self.get_note_by_name(name)
            if name == "back":
                return

        # setting destination path for new file
        final_path = dataM.user.data['path'] + "/" + name + ".txt"
        with open(final_path, 'w') as f:
            f.write("This is your new note! ", )

        # sending file to database and creating note entity
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

        # removing local copy in order
        os.remove(final_path)

    async def get_note_by_name(self, name: str) -> Optional[tuple[dict[str, str], str]]:
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

    def __get_note_by_name_call(self, name: str) -> Optional[dict[str, dict[str, str]]]:
        """
        :param name:
        Name of interest
        :return:
        Returns note with specified name
        """
        try:
            note = dataM.db.child("notes").order_by_child("name").equal_to(name).get()
            return note
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)

    async def get_notes_for_user_with_nick(self, nick: str) -> list[str]:
        """
        :param nick:
        Nickname of interest
        :return:
        returns all notes with author whose nick is the same as parameter
        """
        loop = asyncio.get_event_loop()
        call_task = loop.run_in_executor(None, self.__get_notes_by_nick, nick)
        result = await call_task
        notes = []
        if len(result.val()) != 0:
            for item in result.val().items():
                notes.append(item[1]["name"])
        if dataM.user.data['nick'] == nick:
            if "remotes" in dataM.user.data.keys():
                for note in dataM.user.data["remotes"]:
                    notes.append(note)
        return notes

    def __get_notes_by_nick(self, nick: str) -> Optional[dict[str, dict[str, str]]]:
        """
        database call for all notes with author whose nick is the same as parameter
        :param nick:
        Nickname of interest
        :return:
        """
        try:
            notes = dataM.db.child("notes").order_by_child("author").equal_to(nick).get()
            return notes
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)

    async def remove_note(self) -> None:
        """
        Enables user to remove note with specific name
        :return:
        """

        # checks if there are any notes in database
        notes = await self.get_notes_for_user_with_nick(dataM.user.data["nick"])
        index = 0
        if len(notes) == 0:
            print("You don't have any notes")
            return
        else:
            for note in notes:
                print(index, ": ", note)
                index += 1

        print("Which note do you want to remove? ")
        choice = m_utility.handle_selection()

        if choice >= index:
            return
        else:
            # we delete both the file and the note entity
            note_task = await self.get_note_by_name(notes[choice])
            note_data = note_task[0]
            note_id = note_task[1]

            # deleting all archived versions of note
            for version in range(int(note_data['version']) + 1):
                note_name = notes[choice]
                note_name = note_name[:-1] + str(version)
                try:
                    storage.child(note_name).delete(note_name, dataM.user.token)
                except:
                    pass

            dataM.db.child("notes").child(note_id).remove()

            # deleting local copy
            file_path = dataM.user.data["path"] + "/" + notes[choice] + ".txt"
            if os.path.exists(file_path):
                os.remove(file_path)


notes_manager = NotesManager()

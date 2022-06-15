import asyncio
import requests
import json
import Data.dataManager as dataM
import os
import urllib
from Notes import NotesManager as notesM
import MenusUtility.MenuUtility as m_utility


class NotesConfigManager:

    def __init__(self, note_id: str, note_data):
        self.__note_id: str = note_id
        self.__note_data = note_data

    @property
    def note_id(self):
        return self.__note_id

    @note_id.setter
    def note_id(self, id):
        self.__note_id = id

    @property
    def note_data(self):
        return self.__note_data

    @note_data.setter
    def note_data(self, data):
        self.__note_data = data

    async def download_note(self):
        """
        Donwloads note using unique url to specific path
        :return:
        """
        path = dataM.user.data["path"] + "/" + self.note_data["name"] + ".txt"
        await self.download_note_call(path)

    async def download_note_call(self, path: str):
        """
        Helper method for downloading data
        :param path:
        :return:
        """
        url = self.note_data["link"]
        print(url)
        try:
            urllib.request.urlretrieve(url, path)
        except:
            pass

    async def save_note(self):
        """
        Handles all actions connected to saving note as new version
        :return:
        """

        old_name = self.note_data["name"]
        name_components = old_name.split("_")
        version_components = name_components[1].split("v")
        new_version_number = int(version_components[-1])+1
        new_name = name_components[0] + "_v" + str(new_version_number)

        # upload current version to cloud and get usefull data
        final_path = dataM.user.data['path'] + "/" + old_name + ".txt"
        notesM.storage.child(new_name).put(final_path)
        new_link = notesM.storage.child(new_name).get_url(None)

        #update archive
        new_archive = self.note_data["archive"]
        new_archive.append(new_link)
        print(new_archive)
        dataM.db.child("notes").child(self.note_id).update({"archive": new_archive})
        dataM.db.child("notes").child(self.note_id).update({"version": new_version_number})
        dataM.db.child("notes").child(self.note_id).update({"name": new_name})

        #update link
        dataM.db.child("notes").child(self.note_id).update({"link": new_link})

        #delete local copy
        os.remove(final_path)

        #refresh local data
        await self.refresh_local_data_with_name(new_name)

    async def refresh_local_data_with_name(self, name: str):
        new_note_data = await notesM.notes_manager.get_note_by_name(name)
        self.note_data = new_note_data[0]

    async def add_friend_to_note(self):
        """
        Lets user add a friend to note so that friend can also edit notes
        :return:
        """
        print("Which friend do you want to add?")
        index = 0
        loc_friends = dataM.user.data["friends"]
        for friend in loc_friends:
            print(index, ": ", friend)
            index += 1

        choice = m_utility.handle_selection()

        if choice >= index:
            return
        else:
            if "write_list" in self.note_data.keys():
                loc_write_list = self.note_data["write_list"]
            else:
                loc_write_list = []

            if "read_list" in self.note_data.keys():
                loc_read_list = self.note_data["read_list"]
            else:
                loc_read_list = []

            if loc_friends[choice] in loc_read_list or loc_friends[choice] in loc_write_list:
                print("This user already has access")
                pass

            new_user_data_task = dataM.data_management.get_user_by_nick(dataM.user.data["friends"][choice])
            new_user_data_task_result = await new_user_data_task
            new_user_id = new_user_data_task_result[1]
            new_user_data = new_user_data_task_result[0]

            if "remotes" in new_user_data.keys():
                remotes = new_user_data["remotes"]
            else:
                remotes = []

            # updating new participants remote list
            remotes.append(self.note_data["name"])
            dataM.db.child("users").child(new_user_id).update({"remotes": remotes})

            # updating read and write list
            loc_read_list.append(new_user_data["nick"])
            loc_write_list.append(new_user_data["nick"])
            dataM.db.child("notes").child(self.note_id).update({"write_list": loc_write_list})
            dataM.db.child("notes").child(self.note_id).update({"read_list": loc_read_list})

            #refresh local data
            await self.refresh_local_data_with_name(self.note_data["name"])




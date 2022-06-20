import Data.dataManager as dataM
import os
import requests
import json
import urllib
from Notes import NotesManager as notesM
import MenusUtility.MenuUtility as m_utility
from fpdf import FPDF
from gtts import gTTS
import subprocess
import sh


class NotesConfigManager:

    def __init__(self, note_id: str, note_data: dict[str, str]):
        self.__note_id: str = note_id
        self.__note_data: dict[str, str] = note_data

    @property
    def note_id(self):
        return self.__note_id

    @note_id.setter
    def note_id(self, id: str):
        self.__note_id = id

    @property
    def note_data(self):
        return self.__note_data

    @note_data.setter
    def note_data(self, data: dict[str, str]):
        self.__note_data = data

    async def download_note(self) -> None:
        """
        Downloads note using unique url to specific path
        """
        path = dataM.user.data["path"] + "/" + self.note_data["name"] + ".txt"
        await self.download_note_call(path)

    async def download_note_call(self, path: str) -> None:
        """
        Helper method for downloading data
        :param path:
        Path to which the file is supposed to be downloaded
        """
        url = self.note_data["link"]
        try:
            urllib.request.urlretrieve(url, path)
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            print(error_message)
            return

    async def save_note(self) -> None:
        """
        Handles all actions connected to saving note as new version
        """

        # checks if logged-in user can edit chosen note
        if "write_list" in self.note_data.keys():
            if self.note_data["author"] != dataM.user.data["nick"] \
                    and dataM.user.data["nick"] not in self.note_data["write_list"]:
                print("You can't edit this note. Please contact the author")
                return
        else:
            if self.note_data["author"] != dataM.user.data["nick"]:
                print("You can't edit this note. Please contact the author")
                return

        old_name = self.note_data["name"]
        new_data = self.__get_name_modyfied(old_name)
        new_name = new_data[0]
        new_version_number = new_data[1]
        final_path = dataM.user.data['path'] + "/" + old_name + ".txt"

        # check if file exists
        if not os.path.exists(final_path):
            print("\n First you have to download the file!! \n")
            return

        # upload current version to cloud and get useful data
        notesM.storage.child(new_name).put(final_path)
        new_link = notesM.storage.child(new_name).get_url(None)

        # update archive
        new_archive = self.note_data["archive"]
        new_archive.append(new_link)
        dataM.db.child("notes").child(self.note_id).update(
            {
                "archive": new_archive,
                "version": new_version_number,
                "name": new_name,
                "link": new_link
            }
        )

        # delete local copy
        os.remove(final_path)

        # refresh local data and remotes
        await self.refresh_local_data_with_name(new_name)
        await self.update_remotes(old_name, new_name)

    async def refresh_local_data_with_name(self, name: str) -> None:
        """
        Refreshing local note data
        :param name:
        Name of the note
        """
        new_note_data = await notesM.notes_manager.get_note_by_name(name)
        self.note_data = new_note_data[0]

    async def update_remotes(self, old_name: str, new_name: str) -> None:
        """
        Updating all occurrences of edited note in users remotes
        :param old_name:
        Old note name
        :param new_name:
        Notes name after edit
        """
        result = dataM.db.child("users").get()

        for key in result.val().keys():
            tmp_user_data = result.val().get(key)
            if "remotes" in tmp_user_data.keys():
                remotes = tmp_user_data["remotes"]
                if old_name in remotes:
                    remotes.remove(old_name)
                    remotes.append(new_name)
                    dataM.db.child("users").child(key).update({"remotes": remotes})

    async def add_friend_to_note(self) -> None:
        """
        Lets user add a friend to note so that friend can also edit notes
        """

        if self.note_data["author"] != dataM.user.data["nick"]:
            print("\n Only author can perform this action \n")
            return

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
                return

            # get new users data
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

            # refresh local data
            await self.refresh_local_data_with_name(self.note_data["name"])

    async def remove_friend_from_note(self) -> None:
        """
        Method revokes certain friends access to both read and write to note
        """
        # checking if user wanting to make notifications is the author
        if self.note_data["author"] != dataM.user.data["nick"]:
            print("\n Only author can perform this action \n")
            return

        if "write_list" in self.note_data.keys():
            loc_write_list = self.note_data["write_list"]
        else:
            loc_write_list = []

        if "read_list" in self.note_data.keys():
            loc_read_list = self.note_data["read_list"]
        else:
            loc_read_list = []

        combined_access = list(set(loc_read_list + loc_write_list))
        index = 0

        if len(combined_access) == 0:
            print("Only you have access to this note")
            return

        print("Who do you want to remove?")
        for friend in combined_access:
            print(index, ": ", friend)
            index += 1
        choice = m_utility.handle_selection()

        if choice >= index:
            return

        selection = combined_access[choice]

        # removing from write list
        if selection in loc_write_list:
            dataM.db.child("notes").child(self.note_id).update({"write_list": loc_write_list.remove(selection)})

        # removing from read list
        if selection in loc_read_list:
            dataM.db.child("notes").child(self.note_id).update({"read_list": loc_read_list.remove(selection)})

        # removing note from remotes
        user_data_task = dataM.data_management.get_user_by_nick(selection)
        user_data_task_result = await user_data_task
        user_id = user_data_task_result[1]
        user_data = user_data_task_result[0]
        user_remotes = user_data["remotes"]
        dataM.db.child("users").child(user_id).update({"remotes": user_remotes.remove(self.note_data["name"])})

        # refreshing local note data
        await self.refresh_local_data_with_name(self.note_data["name"])

    async def change_friends_access(self) -> None:
        """
        Method lets owner specify weather certain user can write or only read note
        """
        # checking if user wanting to make notifications is the author
        if self.note_data["author"] != dataM.user.data["nick"]:
            print("\n Only author can perform this action \n")
            return

        # selecting required data
        if "write_list" in self.note_data.keys():
            loc_write_list = self.note_data["write_list"]
        else:
            loc_write_list = []

        if "read_list" in self.note_data.keys():
            loc_read_list = self.note_data["read_list"]
        else:
            print("Only you have access to this note.")
            return

        index = 0
        print("Whos access do you want to change?")
        for friend in loc_read_list:
            print(index, ": ", friend)
            index += 1
        choice = m_utility.handle_selection()

        if choice >= index:
            return

        selection_can_write = False

        # checking if selected user can modify note
        if loc_read_list[choice] in loc_write_list:
            selection_can_write = True

        if selection_can_write:
            print("Selected user can edit note do you want to change that?")
        else:
            print("Selected user can't edit note do you want to change that?")

        decision: str = input("Y or N: ")

        # modifying local copy
        if decision == "Y":
            if selection_can_write:
                loc_write_list.remove(loc_read_list[choice])
            else:
                loc_write_list.append(loc_read_list[choice])
        elif decision == "N":
            return
        else:
            print("Invalid input")
            return

        # updating database
        dataM.db.child("notes").child(self.note_id).update({"write_list": loc_write_list})

        # refreshing local data
        await self.refresh_local_data_with_name(self.note_data["name"])

    async def go_back_to_old_version(self) -> None:
        """
        Lets user set one of the old versions of the note as a new one
        """
        current_version: int = int(self.note_data["version"])

        print("Current version is ", current_version, ". To which previous version do you want to go back to?")
        choice: int = m_utility.handle_selection()

        if choice > current_version:
            return

        # removing local copy of now old version
        final_path: str = dataM.user.data['path'] + "/" + self.note_data["name"] + ".txt"

        if os.path.exists(final_path):
            os.remove(final_path)

        # preparing new data
        version_history = self.note_data["archive"]
        new_version_link = version_history[choice]
        version_history.append(new_version_link)
        current_version += 1
        old_name = self.note_data["name"]
        new_name = self.__get_name_modyfied(old_name)[0]

        # updating version history and current link
        dataM.db.child("notes").child(self.note_id).update(
            {
                "version": current_version,
                "name": new_name,
                "archive": version_history,
                "link": new_version_link
            }
        )

        # refreshing local note data
        await self.refresh_local_data_with_name(new_name)
        await self.update_remotes(old_name, new_name)

    def __get_name_modyfied(self, name: str) -> tuple[str, int]:
        """
        Modification basically increases version number at the end.
        :param name:
        Name to be modified
        :return:
        Returns modified name of a note and new version number.
        """
        old_name = name
        name_components = old_name.split("_")
        version_components = name_components[1].split("v")
        new_version_number = int(version_components[-1]) + 1
        new_name = name_components[0] + "_v" + str(new_version_number)
        return new_name, new_version_number

    def prepare_to_go_back(self) -> None:
        """
        Deletes local copy of the file currently being configured
        """
        final_path = dataM.user.data['path'] + "/" + self.note_data["name"] + ".txt"
        if os.path.exists(final_path):
            os.remove(final_path)

    def export_to_pdf(self) -> None:
        """
        If note is downloaded method exports text from note into new pdf file.
        """
        # checks if note is downloaded
        note_name = self.note_data["name"]
        final_path = dataM.user.data['path'] + "/" + note_name + ".txt"
        if not os.path.exists(final_path):
            print("\nFirst you have to download the note!!\n")
            return

        # generates pdf
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        pdf.cell(200, 10, txt=note_name, ln=1, align='C')
        f = open(final_path, "r")
        for x in f:
            pdf.cell(200, 10, txt=x, ln=1, align='C')
        pdf_path = dataM.user.data["path"] + "/" + note_name + ".pdf"
        pdf.output(name=pdf_path, dest='F').encode('latin-1')

    def read_note(self) -> None:
        """
        Method reads specified note using google text to speech library
        """
        # checks if note is downloaded
        final_path: str = dataM.user.data['path'] + "/" + self.note_data["name"] + ".txt"
        if not os.path.exists(final_path):
            print("\nFirst you have to download the note!!\n")
            return

        # generates speech
        file = open(final_path, "r")
        text_to_read = file.read().replace("\n", " ")
        result = gTTS(text=text_to_read, lang='en', slow=False)
        result_path = dataM.user.data['path'] + "/" + self.note_data["name"] + ".mp3"
        file.close()
        result.save(result_path)

        # plays generated file
        subprocess.run(["afplay", result_path])
        os.remove(result_path)

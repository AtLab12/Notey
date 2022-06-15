import asyncio
import requests
import json

import urllib3.request

import Data.dataManager as dataM
import os
import urllib
from Notes import NotesManager as notesM


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
        self.note_data = data

    async def download_note(self):
        path = dataM.user.data["path"] + "/" + self.note_data["name"] + ".txt"
        await self.download_note_call(path)

    async def download_note_call(self, path: str):
        url = self.note_data["link"]
        urllib.request.urlretrieve(url, path)



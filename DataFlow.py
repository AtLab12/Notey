import json
import pyrebase
import re
import requests
import asyncio
import Authorization as au

async def getUserdata(email):
    loop = asyncio.get_event_loop()
    userDataTask = loop.run_in_executor(None, getUserCall, email)
    await userDataTask
    return userDataTask.result()

def getUserCall(email):
    try:
        user = au.db.child("users").order_by_child("email").equal_to(email).get()
        return user
    except requests.exceptions.HTTPError as e:
        error_json = e.args[1]
        errorMessage = json.loads(error_json)['error']['message']
        print(errorMessage)
        return
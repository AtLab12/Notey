import json
import requests
import asyncio
import Data.dataManager as dataM

async def get_user_data(email: str):
    """
    Downloads users data.
    :param email:
    :return:
    """
    loop = asyncio.get_event_loop()
    userDataTask = loop.run_in_executor(None, get_user_call, email)
    result = await userDataTask
    id = next(iter((result.val().keys())))
    return result.val().get(id), id

def get_user_call(email: str):
    try:
        user = dataM.db.child("users").order_by_child("email").equal_to(email).get()
        return user
    except requests.exceptions.HTTPError as e:
        error_json = e.args[1]
        errorMessage = json.loads(error_json)['error']['message']
        print(errorMessage)
        return
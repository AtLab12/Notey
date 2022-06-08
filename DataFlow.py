import json
import requests
import asyncio
import Data.dataManager as dataM

async def getUserdata(email: str):
    """
    Downloads users data.
    :param email:
    :return:
    """
    loop = asyncio.get_event_loop()
    userDataTask = loop.run_in_executor(None, getUserCall, email)
    result = await userDataTask
    id = next(iter((result.val().keys())))
    return result.val().get(id)

def getUserCall(email: str):
    try:
        user = dataM.db.child("users").order_by_child("email").equal_to(email).get()
        return user
    except requests.exceptions.HTTPError as e:
        error_json = e.args[1]
        errorMessage = json.loads(error_json)['error']['message']
        print(errorMessage)
        return
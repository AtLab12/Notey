"""
stores users data synchronized with app's state
"""

user = {}

def showProfileDetails():
    """
    Presents ony identifying data associated with currently logged user
    :return:
    """
    if user != {}:
        print("Nickname: ", user["nick"])
        print("Name: ", user["name"])
        print("Lastname: ", user["lastName"])
    else:
        print("\n Unexpected error occured \n")
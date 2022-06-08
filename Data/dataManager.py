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
        print("\nNickname: ", user["nick"])
        print("Name: ", user["name"])
        print("Lastname: ", user["lastName"], "\n")
    else:
        print("\n Unexpected error occured \n")
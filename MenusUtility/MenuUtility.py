def handleSelection():
    """
    Method protects program from invalid input
    :return:
    """
    selection = input("Please type your selection: ")
    while not selection.isdigit():
        print("\n Invalid input \n")
        selection = input("Please type your selection: ")

    return int(selection)
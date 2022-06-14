import MenusUtility.MenuUtility as mUtility
from Notes import NotesManager as notesM
import Data.dataManager as dataM

notes_manager = notesM.NotesManager()

def print_main_notes_menu():
    menu = {
        1: "See your notes",
        2: "Create new note",
        3: "Delete note",
        4: "Note configuration",
        5: "Back"
    }

    for key in menu.keys():
        print(key, menu[key])
    print('\n')


async def run_notes():
    print("Please select one of the following options: ")
    print_main_notes_menu()
    choice = mUtility.handle_selection()

    while True:
        if choice == 1:
            notes = await notes_manager.get_notes_for_user_with_nick(dataM.user.data["nick"])
            if len(notes) == 0:
                print("You don't have any notes yet")
            else:
                for note in notes:
                    print(note[1]["name"])
        if choice == 2:
            await notes_manager.createNote()
        if choice == 3:
            await notes_manager.remove_note()
        if choice == 4:
            await run_select_note()
        if choice == 5:
            break

        print_main_notes_menu()
        choice = mUtility.handle_selection()


def print_select_note_menu():
    menu = {
        1: "Open note",
        2: "Save note",
        3: "Add friend to note",
        4: "Remove friend from note",
        5: "Change friends access level",
        6: "Go back to old version",
        7: "Export note to PDF",
        8: "Read note",
        9: "Back"
    }

    for key in menu.keys():
        print(key, menu[key])
    print('\n')


async def run_select_note():
    print("Please select one of the following options: ")
    print_select_note_menu()
    choice = mUtility.handle_selection()

    while True:
        if choice == 1:
            await notes_manager.createNote()
        if choice == 2:
            pass
        if choice == 3:
            pass
        if choice == 4:
            pass
        if choice == 5:
            pass
        if choice == 6:
            pass
        if choice == 7:
            pass
        if choice == 8:
            pass
        if choice == 9:
            break

        print_select_note_menu()
        choice = mUtility.handle_selection()
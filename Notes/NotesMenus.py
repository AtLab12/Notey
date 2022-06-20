import MenusUtility.MenuUtility as mUtility
from Notes import NotesManager as notesM
from Notes import NotesConfigManager as notesConfM
import Data.dataManager as dataM


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
            notes = await notesM.notes_manager.get_notes_for_user_with_nick(dataM.user.data["nick"])
            if len(notes) == 0:
                print("You don't have any notes yet")
            else:
                for note in notes:
                    print(note)
        if choice == 2:
            await notesM.notes_manager.createNote()
        if choice == 3:
            await notesM.notes_manager.remove_note()
        if choice == 4:
            await run_select_note()
        if choice == 5:
            break

        print_main_notes_menu()
        choice = mUtility.handle_selection()


def print_select_note_menu():
    menu = {
        1: "Download note",
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
    """
    Before function shows menu it checks if user has any existing notes.
    Only if he does, will he be shown the config menu
    :return:
    """
    # getting all users notes
    notes = await notesM.notes_manager.get_notes_for_user_with_nick(dataM.user.data["nick"])

    if len(notes) == 0:
        print("You don't have any notes. Please create one to proceed")
        return

    print("Which note do you want to perform actions on?")
    index = 0
    for note in notes:
        print(index, ": ", note)
        index += 1
    print("\n")
    selected_note = mUtility.handle_selection()
    # leaving config
    if selected_note >= index:
        return

    selected_note = await notesM.notes_manager.get_note_by_name(notes[selected_note])

    selected_note_data = selected_note[0]
    selected_note_id = selected_note[1]

    notes_config_manager = notesConfM.NotesConfigManager(selected_note_id,selected_note_data)

    print("(Selected: ", notes_config_manager.note_data["name"], ")")
    print_select_note_menu()
    choice = mUtility.handle_selection()

    while True:
        if choice == 1:
            await notes_config_manager.download_note()
        if choice == 2:
            await notes_config_manager.save_note()
        if choice == 3:
            await notes_config_manager.add_friend_to_note()
        if choice == 4:
            await notes_config_manager.remove_friend_from_note()
        if choice == 5:
            await notes_config_manager.change_friends_access()
        if choice == 6:
            await notes_config_manager.go_back_to_old_version()
        if choice == 7:
            notes_config_manager.export_to_pdf()
        if choice == 8:
            notes_config_manager.read_note()
        if choice == 9:
            notes_config_manager.prepare_to_go_back()
            break

        print("(Selected: ", notes_config_manager.note_data["name"], ")")
        print_select_note_menu()
        choice = mUtility.handle_selection()

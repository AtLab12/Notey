import asyncio
import Data.dataManager as dataM
import MenusUtility.MenuUtility as m_utility


class SocialNetwork:
    async def send_request(self, nick: str) -> None:
        """
        method checks if user with provided email exists
        checks if currently logged in user haven't already requested a friendship
        send friendship request to desired user
        :param nick:
        Nick of a user one want to add as a friend
        :return:
        """
        # checks if user want to add himself as a friend
        if nick == dataM.user.data["nick"]:
            print("You can't add yourself as friend silly ;)")
            return

        loop = asyncio.get_event_loop()
        check_task = dataM.data_management.get_user_by_nick(nick)
        user_data = await check_task

        # checks if user with provided email exists
        if user_data is not None:
            if "requests" in user_data[0]:
                req = user_data[0]["requests"]
            else:
                req = []

            my_nick = dataM.user.data["nick"]
            if my_nick not in req:
                req.append(dataM.user.data["nick"])
                dataM.db.child("users").child(user_data[1]).update({"requests": req})
                print("Requests sent")
            else:
                print("You already sent request to this user")
        else:
            # checks if there are any users with similar nicknames
            # by calculating levenshtein distance for every nickname
            get_all_task = dataM.data_management.get_all_users()
            result = await get_all_task
            candidates = self.__sort_words_by_distance(result, nick)
            finalists: [str] = []

            # if there are users with similar nicknames fives option
            # to add one as a friend
            if len(candidates) > 0:
                for key in candidates.keys():
                    if candidates[key] <= 6 and key != dataM.user.data["nick"]:
                        finalists.append(key)

                print("Did you mean to send request to one of these users? \n")
                index = 0
                for name in finalists:
                    print(index, ": ", name)
                    index += 1
                choice = m_utility.handle_selection()
                if choice >= index:
                    return
                else:
                    await self.send_request(finalists[choice])
            else:
                return

    async def handle_myrequests(self) -> None:
        """
        Refreshes users current data
        Shows all requests
        Handles request acceptance for both users
        :return:
        """
        # gets newest request data
        task = dataM.data_management.get_user_by_email(dataM.user.data["email"])
        result = await task
        dataM.user.data = result[0]
        index = 0
        my_nick = dataM.user.data["nick"]

        # shows all requests
        if "requests" in list(dataM.user.data.keys()):
            print("\nPeople who want to be your friends: ")
            for req_nick in dataM.user.data["requests"]:
                print(index, ": ", req_nick)
                index += 1
        else:
            print("\nNo new requests\n")
            return

        # adds specified friend to friend list or goes back to friend menu
        print("Who do you want to accept as a friend? (type noOne to quit)")
        new_friend = input()
        if new_friend == "noOne" or new_friend == 0:
            return
        else:
            if not new_friend.isdigit():
                print("Invalid choice")
                return
            else:
                if int(new_friend) >= index:
                    print("uups. I'm afraid you are not interesting enough to have ", new_friend, "new requests.\n")
                else:
                    new_friend_nick = dataM.user.data["requests"][int(new_friend)]
                    new_friend_data_task = dataM.data_management.get_user_by_nick(new_friend_nick)
                    new_friend_data_task_result = await new_friend_data_task

                    new_friend_id = new_friend_data_task_result[1]
                    new_friend_data = new_friend_data_task_result[0]

                    if "friends" in new_friend_data.keys():
                        new_friend_friends = new_friend_data["friends"]
                    else:
                        new_friend_friends = []

                    new_friend_friends.append(my_nick)

                    if "friends" in dataM.user.data.keys():
                        friends = dataM.user.data["friends"]
                    else:
                        friends = []

                    # data synchronization between user and new friend
                    friends.append(new_friend_nick)
                    loc_id = dataM.user.user_id
                    dataM.db.child("users").child(loc_id).update({"friends": friends})
                    dataM.db.child("users").child(new_friend_id).update({"friends": new_friend_friends})
                    del dataM.user.data["requests"][int(new_friend)]
                    loc_req = dataM.user.data["requests"]
                    dataM.db.child("users").child(loc_id).update({"requests": loc_req})
                    await dataM.data_management.refresh_data()

    async def run_remove_friend(self) -> None:
        """
        Deletes friend based on user selection.
        Automatically deletes current logged-in user from the currently being deleted friends list.
        :return:
        """

        if "friends" in dataM.user.data.keys():
            index = 0
            for friend in dataM.user.data["friends"]:
                print(index, ": ", friend)
                index += 1
            selection = input("Who do you want to remove? \n")

            if selection == "back":
                return

            # synchronizes data between user and friend being deleted
            if selection.isdigit() and int(selection) < index:
                selected_friend_nick = dataM.user.data["friends"][int(selection)]
                selected_friend_task = dataM.data_management.get_user_by_nick(selected_friend_nick)
                selected_friend_task_result = await selected_friend_task

                selected_friend_id = selected_friend_task_result[1]
                selected_friend_data = selected_friend_task_result[0]

                selected_friends = selected_friend_data["friends"]
                selected_friends.remove(dataM.user.data["nick"])

                del dataM.user.data["friends"][int(selection)]
                loc_id = dataM.user.user_id
                dataM.db.child("users").child(loc_id).update({"friends": dataM.user.data["friends"]})
                dataM.db.child("users").child(selected_friend_id).update({"friends": selected_friends})
            else:
                print("Invalid input")
        else:
            print("You don't have any friends to remove yet")

        await dataM.data_management.refresh_data()

    def __sort_words_by_distance(self, words: [str], input_word) -> dict[str, int]:
        """
        :param words:
        Words to calculate levenshtein distance.
        :param input_word:
        Users original input.
        :return:
        Returns a sorted dictionary with a word distance from original input
        from smallest to biggest.
        """
        values = {}
        for word in words:
            values[word] = self.__calculate_distance(word, input_word)

        result = dict(sorted(values.items(), key=lambda x: x[1]))
        return result

    def __calculate_distance(self, word: str, input_word) -> int:
        """
        :param word:
        First word
        :param input_word:
        Second word.
        :return:
        Returns levenshtein distance between first and second word.
        """

        def create_matrix_for_word(word1, word2):
            num_of_rows = len(str(word1))
            num_of_collumns = len(str(word2))
            matrix = []
            tmp = []
            for col_num in range(0, num_of_collumns + 1):
                tmp.append(col_num)
            matrix.append(tmp)
            for numOfRows in range(1, num_of_rows + 1):
                matrix.append([numOfRows])
            return matrix

        def find_minimum(matrix, cor, val):
            matrix[cor[0]].append(val)
            base = matrix[cor[0]][cor[1]]
            tmp = [
                matrix[cor[0]][cor[1] - 1],
                matrix[cor[0] - 1][cor[1] - 1],
                matrix[cor[0] - 1][cor[1]]
            ]
            matrix[cor[0]][cor[1]] = min(tmp) + base

        matrix = create_matrix_for_word(word, input_word)

        for colNum in range(1, matrix[0][-1] + 1):
            for rowNum in range(1, matrix[-1][0] + 1):
                if word[rowNum - 1] == input_word[colNum - 1]:
                    find_minimum(matrix, tuple((rowNum, colNum)), 0)
                else:
                    find_minimum(matrix, tuple((rowNum, colNum)), 1)

        result = matrix[-1][-1]
        return result

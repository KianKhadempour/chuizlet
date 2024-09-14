question_list: list[tuple[str, str]] = []
with open("test.txt", "r", errors="replace") as f:
    for i in range(100):
        content = f.readline()
        # print(content)
        if "Multiple Choice" in content:
            break
    for i in range(100):
        content = f.readline()
        print(content)
        if "Multiple Choice" in content:
            break
        if "." in content:
            period_position = [pos for pos, char in enumerate(content) if char == "."]
            if "DELETED" in content:
                location_of_deleted = content.find("DELETED")
                i = period_position.__len__() - 1
                for period in reversed(period_position):
                    print(period, i)
                    if period < location_of_deleted:
                        del period_position[i]
                        break
                    i -= 1
                content.replace("DELETED", "")
            for period in period_position:
                if period == 1:
                    question_number = content[period - 1 : period]
                else:
                    question_number = content[period - 2 : period]
                potential_answers = [
                    pos
                    for pos, char in enumerate(content[period:])
                    if char == "A" or char == "B" or char == "C" or char == "D"
                ]
                question_answer = content[potential_answers[0] + period]
                question_list.append((question_number, question_answer))

            print(question_list)

import pathlib


class Parser:
    def __init__(self, enter_doc: str, result_name: str):
        self.doc = enter_doc
        self.result_name = result_name

    def get_doc(self) -> str:
        """
        Возвращает файл xml в одну строку
        """
        with open(self.doc) as doc:
            res = doc.readlines()[1:]  # убираем версию xml

        for i, el in enumerate(res):
            res[i] = el.strip()
        res = "".join(res)
        return res

    def check_array(self, token: str) -> bool:
        """
        Проверка содержания списка types в токенах
        """
        types = ["type", "partnumber", "id"]
        res = any(x in token.lower() for x in types)
        return res

    def convert_join(self) -> None:
        stack: list[str] = []
        res: str = self.get_doc()
        end_stack: str = ""
        end_stack_for_array: str = ""

        with open(self.result_name, "w") as doc:
            doc.write("{\n")
            for indx, symbol in enumerate(res):
                if symbol == "<" and res[indx + 1] == "/":  # закрывающий токен </
                    left_key = indx - 1
                    right_key = indx  # <
                    if res[indx - 1] not in (
                        "<>/"
                    ):  # ищем и записываем значение внутри токена
                        while res[left_key] != ">":
                            left_key -= 1
                        doc.write(f'"{res[left_key + 1: right_key]}"')

                    cursor = doc.tell()
                    end_stack = stack.pop()

                    next_open_key = indx + 1 if len(res) > indx + 1 else indx

                    while (
                        len(res) - 1 > next_open_key + 1 and res[next_open_key] != "<"
                    ):  # далее выполнится проверка следующего токена, если есть (проверка будет на то, что является ли следующий символ закрывающем токен /)
                        next_open_key += 1  # <

                    next_closed_key = next_open_key  # <
                    while (
                        len(res) - 1 > next_closed_key + 1
                        and res[next_closed_key] != ">"
                    ):  # непосредственно следующий токен
                        next_closed_key += 1  # >

                    second_next_closed_token = (
                        next_closed_key + 1
                        if len(res) > next_closed_key + 1
                        else next_closed_key
                    )  # ищем значение следующего следующего токена ))))
                    while (
                        len(res) - 1 > second_next_closed_token + 1
                        and res[second_next_closed_token] != ">"
                    ):
                        second_next_closed_token += 1

                    if (
                        res[next_open_key + 1 : next_closed_key].strip("<>/")
                        == end_stack_for_array
                        and res[next_closed_key + 1 : second_next_closed_token]
                        .split()[0]
                        .strip("<>/")
                        != end_stack_for_array
                    ):  # закрывать
                        # массив после того как перчисления закончились
                        doc.write(
                            f"\n{len(stack) * '\t'}}}\n{(len(stack) - 1) * '\t'}]"
                        )

                    elif (
                        res[next_open_key + 1] == "/" or next_open_key == len(res) - 2
                    ):  # если следующий токен тоже закрывающий,то закрываем абзац
                        doc.write(f'\n{len(stack) * "\t"}}}')

                    else:
                        doc.seek(cursor)
                        doc.write(",\n")

                elif symbol == "<":  # открывающий токен <
                    key = indx
                    while res[key] != ">":
                        key += 1
                    token = res[indx : key + 1]
                    line = f'{len(stack) * "\t"}"{token.split()[0].strip('<>')}": '  # записываем токен
                    if end_stack and token.split()[0].strip("<>") == end_stack.split()[
                        0
                    ].strip(
                        "<>"
                    ):  # если токен равен предыдущему закрытому токену, только что удаленным из стека,
                        # просто открываем новый словарь без названия токена { чтобы ключи были уникальными </Address> <Address Type="Billing">
                        doc.write(f'{(len(stack) + 1) * "\t"}{{\n')
                    elif self.check_array(
                        token
                    ):  # если type иди другой тип в токене - то открываем список
                        end_stack_for_array = token.split()[0].strip("<>/")
                        doc.write(line + f"[\n{(len(stack) + 1) * '\t'}{{\n")
                    elif res[key + 1] not in (
                        "<>/"
                    ):  # если следующий индекс не токен - значит этот токен в открытом абзаце - записываем в файл этот токен и двоеточие перед его значением
                        doc.write(line)
                    else:
                        doc.write(
                            line + "{\n"
                        )  # если следующий индекс токен, то открываем абзац
                    stack.append(token)
                    level_inner = len(stack)


BASE_DIR = pathlib.Path(__file__).parent.parent
document = BASE_DIR / "order.xml"
book = BASE_DIR / "book.xml"
company = BASE_DIR / "company.xml"

p = Parser(document, "order_converted.json")
p.convert_join()
p1 = Parser(book, "book_converted.json")
p1.convert_join()
p_compane = Parser(company, "company_converted.json")
p_compane.convert_join()

import pathlib


class Parser:
    def __init__(self, enter_doc: str, result_name: str):
        self.doc = enter_doc
        self.result_name = result_name
    

    def get_doc(self):
        """
            Возвращает файл xml в одну строку
        """
        with open(self.doc) as doc:
            res = doc.readlines()[1:] # убираем версию xml

        for i, el in enumerate(res):
            res[i] = el.strip()
        res = "".join(res)
        return res
    

    def check_array(self, token: str, doc: str):
        res = doc.split(f"</{token}>")

        

    def convert_join(self):
        stack = []
        res = self.get_doc()
        end_stack = ""
        check_array = False, ""

        with open(self.result_name, "w") as doc:
            doc.write("{\n")
            for indx, symbol in enumerate(res):
                if symbol == "<" and res[indx + 1] == "/": # закрывающий токен </
                    left_key = indx - 1
                    right_key = indx # <
                    if res[indx - 1] not in ("<>/"): # ищем и записываем значение внутри токена 
                        while res[left_key] != ">":
                            left_key -= 1
                        doc.write(f'"{res[left_key + 1: right_key]}"')
                    
                    cursor = doc.tell()
                    end_stack = stack.pop()

                    next_key = indx + 1 if len(res) > indx + 1 else indx
                    right_next_key = next_key + 1 # <

                    while len(res) - 1 > next_key + 1 and res[next_key] != "<": # проверка следующего токена, если есть
                        next_key += 1 # <
                    while len(res) - 1 > right_next_key + 1 and res[right_next_key] != ">":
                        right_next_key += 1

                    
                    if res[next_key + 1] == "/" or next_key == len(res) - 2: # если следующий токен тоже закрывающий,то закрываем абзац
                        if res[next_key + 1: right_next_key].strip("<>/") == check_array[1] and check_array[0]:
                            print("enter to if")
                            doc.write(f']\n')
                            check_array = False, ""
                        else:
                            doc.write(f'\n{len(stack) * "\t"}}}')
                    else:
                        doc.seek(cursor)
                        doc.write(",\n")
                    
                    
                                        
                elif symbol == "<": # открывающий токен <
                    key = indx
                    while res[key] != ">":
                        key += 1
                    line = f'{len(stack) * "\t"}"{res[indx: key + 1].split()[0].strip('<>')}": '  # записываем токен
                    if end_stack and res[indx: key + 1].split()[0].strip("<>") == end_stack.split()[0].strip("<>"): # если токен равен предыдущему закрытому токену, только что удаленным из стека, 
                        # просто открываем новый словарь без названия токена { чтобы ключи были уникальными </Address> <Address Type="Billing">
                        doc.write(f'{(len(stack) + 1) * "\t"}{{\n')
                        check_array = True, res[indx: key + 1].split()[0].strip("<>")
                    elif res[key + 1] not in ("<>/"): # если следующий индекс не токен - значит этот токен в открытом абзаце - записываем в файл этот токен и двоеточие перед его значением
                        doc.write(line)
                    else:
                        doc.write(line + '{\n') # если следующий индекс токен, то открываем абзац
                    stack.append(res[indx: key + 1])
                    


BASE_DIR = pathlib.Path(__file__).parent.parent
document = BASE_DIR / "order.xml"
book = BASE_DIR / "book.xml"

p = Parser(document, "order_converted.json")
p.convert_join()
# p1 = Parser(book, "book_converted.json")
# p1.convert_join()



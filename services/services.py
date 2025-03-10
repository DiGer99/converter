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
        

    def convert_join(self):
        stack = []
        res = self.get_doc()

        with open(self.result_name, "w") as doc:
            doc.write("{\n")
            for indx, symbol in enumerate(res):
                if symbol == "<" and res[indx + 1] == "/": # закрывающий токен </
                    left_key = indx - 1
                    right_key = indx # <
                    if res[indx - 1] not in ("<>/"):
                        while res[left_key] != ">":
                            left_key -= 1
                        doc.write(f'"{res[left_key + 1: right_key]}"')
                    
                    cursor = doc.tell()
                    stack.pop()

                    next_key = indx + 1 if len(res) > indx + 1 else indx
                    while len(res) - 1 > next_key + 1 and res[next_key] != "<": # проверка следующего токена, если есть
                        next_key += 1
                    
                    if res[next_key + 1] == "/" or next_key == len(res) - 2: # если следующий токен тоже закрывающий,то закрываем абзац
                        doc.write(f'\n{len(stack) * "\t"}}}')
                    else:
                        doc.seek(cursor)
                        doc.write(",\n")
                                        
                elif symbol == "<": # открывающий токен <
                    key = indx
                    while res[key] != ">":
                        key += 1
                    query = f'{len(stack) * "\t"}"{res[indx: key + 1].split()[0].strip('<>')}": ' # если есть пробелы внутри токена - split() 
                    if res[key + 1] not in ("<>/"):
                        doc.write(query)
                    else:
                        doc.write(query + '{\n')
                    stack.append(res[indx: key + 1])        


BASE_DIR = pathlib.Path(__file__).parent.parent
document = BASE_DIR / "order.xml"
book = BASE_DIR / "book.xml"

p = Parser(document, "order_converted.json")
p.convert_join()
p1 = Parser(book, "book_converted.json")
p1.convert_join()



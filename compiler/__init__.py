
class MediumLevelLanguage:
    def __init__(self, source, globals=None, outer_scope=None):
        self.source = source

        self.asm = []
        self.outer_scope = {} if not outer_scope else outer_scope
        self.globals = {} if not globals else globals
        self.scope = {}
        self.ast = []

        self.types = {
            "int": 0 # Default Value
        }

        self.operators = ["+", "-", "*", "/", "==", "!=", "<=", "<", ">=", ">"]  # The order matters!, smallest last


    def __grab_internals(self, source, start, open_char, close_char):
        depth = 1
        index = start

        in_string = False
        string_token = None

        closed = False

        while index < len(source):
            char = source[index]

            if char == open_char and not in_string:
                depth += 1

            if char == close_char and not in_string:
                closed = True
                depth -= 1


            if char == '"' and string_token != "'":
                in_string = not in_string

                if in_string:
                    string_token = char
                else:
                    string_token = None

            if char == "'" and string_token != '"':
                in_string = not in_string

                if in_string:
                    string_token = char
                else:
                    string_token = None

            index += 1

            if depth == 0 and closed:
                return source[start:index-1]

        raise SyntaxError("Check your brackets")

    @staticmethod
    def combine_scopes(primary: dict, secondary: dict) -> dict:
        new_scope = {
            key: value
            for key, value in secondary.items()
        }
        for key, value in primary.items():
            new_scope[key] = value

        return new_scope

    def read_until(self, source, start, target):
        index = start
        buffer = ""
        while index < len(source) - 1:
            char = source[index]

            if char == target:
                return buffer

            buffer += char
            index += 1

        return buffer

    def skip_until_after(self, source, start, target) -> int:
        return start + len(self.read_until(source, start, target)) + 1

    def __operator_split(self, string, operator):
        chunks = []
        chunk = ""

        for i, char in enumerate(list(string)):
            chunk += char

            if char.endswith(operator):
                if string[i+1] != "=":
                    chunks.append(chunk.removesuffix(operator))
                    chunks.append(operator)
                    chunk = ""

        chunks.append(chunk)
        return chunks


    def __multi_operator_split(self, string, operators):
        chunks = [string]

        for operator in operators:
            next_chunks = []
            for chunk in chunks:
                next_chunks.extend(self.__operator_split(chunk, operator))
            chunks = next_chunks

        return chunks

    def __parse_definition(self, definition) -> dict:
        if definition in self.scope:
            return self.scope[definition]

        if definition in self.outer_scope:
            return self.outer_scope[definition]

        chunks = self.__multi_operator_split(definition, self.operators)
        print(chunks)

        return {
            "type": "operation",
            "value": {
                "operator": None
            }
        }

    def __define_from_type(self, type_name:str, source: str, start: int) -> int:
        index = start

        index = self.skip_until_after(source, index, " ")
        info = self.read_until(source, index, ";")

        if "=" not in info:
            if info in self.scope:
                raise NameError(f"Something already has the name '{info}' in this scope")

            self.scope[info] = {
                "type": "constant",
                "value": {
                    "type": type_name,
                    "value": self.types[type_name]
                }
            }

        else: # Time to define some shit
            if info.count("=") > 1:
                raise SyntaxError(f"Too many equals signs while defining '{info}'")

            name, definition = info.split("=")

            if name in self.scope:
                raise NameError(f"Something already has the name '{name}' in this scope")

            self.scope[name] = self.__parse_definition(definition.replace(" ", ""))

        return index + len(info)

    def __parse_ast(self, source):
        source = source.replace("\n", "")

        ast = []

        index = 0
        next_index = 0
        token = ""

        while next_index < len(source) - 1:
            index = next_index
            next_index = index + 1

            char = source[index]

            if char == "{":
                internals = self.__grab_internals(source, index+1, "{", "}")
                sub_program = MediumLevelLanguage(internals,
                                                  globals=self.globals,
                                                  outer_scope=self.combine_scopes(self.scope, self.outer_scope))
                ast.append(sub_program.parse_ast())

                next_index += len(internals) + 2
                continue

            if char == " ":
                continue

            token += char

            if token in self.types:
                next_index = self.__define_from_type(token, source, index+1) + 1
                token = ""

            elif token in self.globals:
                pass # todo






        return ast

    def constant_label_int(self, value):
        name_mash = f"MLL.CONSTANT.INT.{value}"

        if name_mash not in self.globals:
            self.globals[name_mash] = value

        return name_mash

    def parse_ast(self):
        return self.__parse_ast(self.source)


    def build(self):
        self.asm = []
        self.scope = {}

        self.ast = self.parse_ast()

        return "\n".join(self.asm)



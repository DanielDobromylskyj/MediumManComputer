"""
>> Commands:

HLT         - End Program

LDA         - Load Memery Address / Pointer To Reg A
LDB         - Load Memery Address / Pointer To Reg B
LDC         - Load Memery Address / Pointer To Reg C

STA         - Store Reg A to Memory Address / Pointer

SWB         - Swap Reg A and Reg B
SWC         - Swap Reg A and Reg C

ADD         - Add value at Memory Address / Pointer to Reg A
SUB         - Sub value at Memory Address / Pointer from Reg A

ADA         - Add Reg A to Reg A
ADB         - Add Reg B to Reg A
ADC         - Add Reg C to Reg A

SBA         - Sub Reg A from Reg A
SBB         - Sub Reg B from Reg A
SBC         - Sub Reg C from Reg A

LSB         - Shift Reg A to the Left by Reg B
LSC         - Shift Reg A to the Left by Reg C

RSB         - Shift Reg A to the Right by Reg B
RSC         - Shift Reg A to the Right by Reg C

INP         - Take a Number Input And Store it into reg A
OUT         - Output Number stored in reg A
OTC         - Output character represented by value in reg A

JMP         - Jump to Memory Address / Pointer
BRZ         - Branch to Memory Address / Pointer if value in reg A is 0
BRP         - Branch to Memory Address / Pointer if value in reg A greater than or equal to 0

DAT         - Not a command, but sets the value at a given mem / label.


>> Format:

No Label:
    INP

With Label:
get_input  INP


Memory Pointers (Labels):
data    DAT    5
        LDA    $data  // $ Implies it's a label / pointer

Memory Pointers (Raw):
        DAT    5
        LDA    0      // Value "0" is the line addr


"""


class Compiler:
    def __init__(self, source: str):
        self.source = source

        self.__LOOKUP = {
            "HLT": 0,
            "DAT": None,

            "LDA": 1,
            "LDB": 2,
            "LDC": 3,

            "STA": 4,

            "SWB": (5, 0),
            "SWC": (5, 1),

            "ADA": (6, 0),
            "ADB": (6, 1),
            "ADC": (6, 2),
            "ADD": 7,

            "SBA": (8, 0),
            "SBB": (8, 1),
            "SBC": (8, 2),
            "SUB": 9,

            "LSB": (10, 0),
            "LSC": (10, 1),
            "RSB": (10, 2),
            "RSC": (10, 3),

            "INP": (12, 0),
            "OUT": (12, 1),
            "OTC": (12, 2),

            "BRZ": 13,
            "BRP": 14,
            "JMP": 15
        }

        self.program = []

    def parse_line(self, line):
        chunks = []
        chunk = ""
        for char in list(line.replace("\t", " ")):
            if char == " ":
                if chunk:
                    chunks.append(chunk)
                    chunk = ""

            else:
                chunk += char

                if chunk.endswith("//"):
                    chunk = chunk[:-2]
                    break

        if chunk:
            chunks.append(chunk)

        if len(chunks) == 0:
            return None

        label = None
        data = 0

        if chunks[0] in self.__LOOKUP:
            command = self.__LOOKUP[chunks[0]]

            if len(chunks) == 2:
                data = chunks[1]

        else:
            if chunks[1] in self.__LOOKUP:
                command = self.__LOOKUP[chunks[1]]
                label = chunks[0]
                
                if len(chunks) == 3:
                    data = chunks[2]
            else:
                raise SyntaxError(f"Malformed command / Line: {line}")

        if type(data) is str:
            if data.isdigit():
                data = int(data)

            else:
                if not data.startswith("$"):
                    raise SyntaxError(f"Malformed command / Line: {line}")

        return {
            "op": command,
            "data": data,
            "label": label
        }


    def build(self):
        lines = []
        labels = {}
        skipped = 0

        for index, line in enumerate(self.source.split("\n")):
            if line == "":
                skipped += 1
                continue

            data = self.parse_line(line)

            if not data:
                skipped += 1
                continue

            lines.append(data)
            
            if data["label"]:
                labels[f"${data["label"]}"] = index - skipped

        self.program = []
        for data in lines:
            cmd_data = data["data"]
            if type(cmd_data) is str:  # Update pointers
                if cmd_data not in labels:
                    raise SyntaxError(f"Unknown Label: {cmd_data}")

                cmd_data = labels[cmd_data]

            opcode = data["op"]
            if opcode is None:  # DAT
                self.program.append(cmd_data)

            else:
                if type(opcode) is tuple:
                    opcode, cmd_data = opcode

                raw = (opcode << 12) + cmd_data

                self.program.append(raw)

        return self.program

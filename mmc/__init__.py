
"""

Instruction Set

0  - HLT - End execution
1  - LDA - Load memory address to reg A
2  - LDB - Load memory address to reg B
3  - LDC - Load memory address to reg C
4  - STA - Store reg A to memory address
5  - SWB/SWC - Swap reg A and reg B/C values - to select, data = 0/1 for B/C
6  - ADR - Add reg A/B/C to reg A, Output in A - to select, data = 0/1/2 for A/B/C
7  - ADM - Add value at memory address to reg A
8  - SBR - Sub reg A/B/C from reg A, Output in A - to select, data = 0/1/2 for A/B/C
9  - SBM - sub value at memory address from reg A
10 - SFT - Bit shift left/right reg A by reg B/C - to select, data = (0/1 for B/C) + (0/2 for left/right) # bits
11 - ???
12 - INP/OUT/OTC - Take Input/Output/Output Character (to/from reg A) - to select, data = 0/1/2 for INO/OUT/OTC
13 - BRZ - Branch / Jump if value in A is equal to 0 to memory address
14 - BRP - Branch / Jump (if value in A is greater than or equal to 0) to memory address
15 - JMP - Jump to memory address

"""



class MMC:
    def __init__(self):
        self.mem_size_bytes = 4096
        self.memory = [ 0 for i in range(self.mem_size_bytes) ]

        self.output_lines = []

        self.MAX_VALUE = 2 ** 16
        self.output_width = 4  # Same as LMC

        self.current_instruction_pointer = 0
        self.next_instruction_pointer = 0

        self.register_a = 0
        self.register_b = 0
        self.register_c = 0

        self.running = False

    def write_program(self, program: list[int]) -> None:
        if len(program) > self.mem_size_bytes:
            raise Exception('Program is too long')

        for i, data in enumerate(program):
            self.memory[i] = data

    def hlt(self):
        self.running = False

    def fetch_mem(self, addr):
        if 0 <= addr < self.mem_size_bytes:
            return self.memory[addr]

        raise IndexError('Address out of range')

    def write_mem(self, addr, data):
        if 0 <= addr < self.mem_size_bytes:
            if 0 <= data < self.MAX_VALUE:
                self.memory[addr] = data
            else:
                raise ValueError('Data out of range')

        else:
            raise IndexError('Address out of range')

    def validate_value(self, v):
        clamped =  v % self.MAX_VALUE

        if clamped < 0:
            return clamped + self.MAX_VALUE
        return clamped

    def take_input(self):
        self.update_display()
        print()
        v =  input("Input: ")

        if not v.isdigit():
            return self.take_input()

        return int(v)

    def print_output(self):
        for line in self.output_lines:
            print(line)

    def clear_screen(self):
        print("\n"*10)  # bodge :(

    def output(self, data: str):
        for char in list(data):
            if len(self.output_lines) == 0:
                self.output_lines.append(char)

            else:
                if len(self.output_lines[-1]) == self.output_width:
                    self.output_lines.append(char)

                else:
                    self.output_lines[-1] += char

    def update_display(self):
        self.clear_screen()
        self.print_output()

    def step(self):
        self.current_instruction_pointer = self.next_instruction_pointer
        self.next_instruction_pointer = self.current_instruction_pointer + 1

        instruction = self.memory[self.current_instruction_pointer]

        command = instruction >> 12
        data = instruction & 0xFFF


        match command:
            case 0:
                self.hlt()

            case 1:
                self.register_a = self.fetch_mem(data)
            case 2:
                self.register_b = self.fetch_mem(data)
            case 3:
                self.register_c = self.fetch_mem(data)

            case 4:
                self.write_mem(data, self.register_a)

            case 5:
                swap_reg = self.register_c if (data & 0b1) else self.register_b
                self.register_a, swap_reg = swap_reg, self.register_a

            case 6:
                match data:
                    case 0:
                        self.register_a = self.validate_value(self.register_a + self.register_a)
                    case 1:
                        self.register_a = self.validate_value(self.register_a + self.register_b)
                    case 2:
                        self.register_a = self.validate_value(self.register_a + self.register_c)
                    case _:
                        raise Exception('Invalid register selection when adding')

            case 7:
                self.register_a = self.validate_value(self.register_a + self.fetch_mem(data))

            case 8:
                match data:
                    case 0:
                        self.register_a = self.validate_value(self.register_a - self.register_a)
                    case 1:
                        self.register_a = self.validate_value(self.register_a - self.register_b)
                    case 2:
                        self.register_a = self.validate_value(self.register_a - self.register_c)
                    case _:
                        raise Exception('Invalid register selection when subtracting')

            case 9:
                self.register_a = self.validate_value(self.register_a - self.fetch_mem(data))

            case 10:
                quantity = self.register_c if data & 0b1 else self.register_b

                if data & 0b10:
                    self.register_a = self.validate_value(self.register_a >> quantity)

                else:
                    self.register_a = self.validate_value(self.register_a << quantity)

            case 11:
                pass

            case 12:
                match data:
                    case 0:
                        self.register_a = self.validate_value(self.take_input())
                    case 1:
                        self.output(str(self.register_a))
                        self.update_display()
                    case 2:
                        self.output(chr(self.register_a))
                        self.update_display()
                    case _:
                        raise Exception('Invalid selection when inputting / outputting')

            case 13:
                if self.register_a == 0:
                    self.next_instruction_pointer = data

            case 14:
                if self.register_a >= 0:
                    self.next_instruction_pointer = data

            case 15:
                self.next_instruction_pointer = data


    def run(self):
        self.current_instruction_pointer = 0
        self.running = True

        while self.running:
            self.step()
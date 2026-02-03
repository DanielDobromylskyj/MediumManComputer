import mmc

from mmc.asm_comp import Compiler as AsmCompiler
from compiler import MediumLevelLanguage as MMLCompiler

src = """

int a;
int b = 42;
int c = a + b - 3;

a = b + 8;

func add(int a, int b) returns int {
    return a + b
}

"""

comp1 = MMLCompiler(src)
asm_src = comp1.build()

print(">> START ASM PROGRAM")
for i, line in enumerate(asm_src):
    print(f"{i}: {line}")

comp2 = AsmCompiler(asm_src)
program = comp2.build()

print(">> START PROGRAM")
for i, line in enumerate(program):
    print(f"{i}: {line}")

x = mmc.MMC()
x.write_program(program)

x.run()

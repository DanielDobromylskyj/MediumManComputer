import mmc
from mmc.asm_comp import Compiler

src = """
        INP
        STA $num1
        OUT

        LDA $plus
        OTC

        INP
        STA $num2
        OUT
        
        LDA $equals
        OTC
        
        LDA $num1
        ADD $num2
        STA $output
        OUT
    
        HLT
num1    DAT 1
num2    DAT 2
output  DAT 0
plus    DAT 43
equals  DAT 61
"""

comp = Compiler(src)
program = comp.build()

print(">> START PROGRAM")
for i, line in enumerate(program):
    print(f"{i}: {line}")
print(">> END PROGRAM")

x = mmc.MMC()
x.write_program(program)

x.run()

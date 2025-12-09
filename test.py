# ==================== 示例使用 ====================
from MultiEdit_Decomposer import InstructionDecomposer

# 初始化指令分解器
decomposer = InstructionDecomposer()

tests = [
    "把红球变成蓝的，然后黄色大立方体改成绿色，再把金属小球变成紫色",
    "Turn the big red ball into purple, and change blue cylinder to orange",
    "red ball to blue and make the large yellow cube to green",
    "将红色的小球改为蓝色，将黄色金属立方体改为橙色",
]

for t in tests:
    s, d = decomposer.generate_decomposed_instruction(t)
    print(s)
    print("-" * 50)
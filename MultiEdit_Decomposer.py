# ==================== MultiEdit_Decomposer_Final.py ====================
import re
from typing import List, Tuple
from collections import OrderedDict
import jieba
import jieba.posseg as pseg

# jieba 安全补丁
original_cut = jieba.posseg.cut
def safe_cut(*args, **kwargs):
    for item in original_cut(*args, **kwargs):
        yield (item.word, item.flag)
jieba.posseg.cut = safe_cut


class InstructionDecomposer:
    def __init__(self):
        self.colors = {
            '红', '赤', '橙', '黄', '绿', '青', '蓝', '紫', '黑', '白', '灰', '棕', '粉', '金', '银', '铜',
            '红色', '橙色', '黄色', '绿色', '蓝色', '紫色', '黑色', '白色', '灰色', '棕色', '粉色', '金色', '银色',
            'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'black', 'white', 'gray', 'grey', 'brown', 'pink',
            'gold', 'silver', 'cyan', 'magenta', 'bronze'
        }
        self.objects = {
            '球', '圆球', '小球', '大球', '方块', '立方体', '正方体', '方体', '圆柱', '圆柱体', '物体',
            'ball', 'sphere', 'cube', 'block', 'cylinder', 'object', 'item', 'thing'
        }
        self.modifiers = {'大', '小', '金属', '橡胶', '木', '塑料', '金属的', '橡胶的', '大的', '小的',
                         'big', 'small', 'large', 'tiny', 'metal', 'rubber', 'wooden', 'plastic'}

        self.sentence_splitter = re.compile(r'[；;。！!？?\n]+')
        self.connectors = re.compile(r'\s*(然后|接着|之后|随后|再|且|并|同时|以及|和|，|,|and|then)\s*')

    def preprocess(self, text: str) -> str:
        text = text.strip()
        text = text.replace('，', ',').replace('（', '(').replace('）', ')')
        text = re.sub(r'\s+', ' ', text)
        return text

    def split_sentences(self, text: str) -> List[str]:
        return [s.strip() for s in self.sentence_splitter.split(text) if s.strip()]

    def split_sub_operations(self, sentence: str) -> List[str]:
        parts = self.connectors.split(sentence)
        bad = {'然后','接着','之后','随后','再','且','并','同时','以及','和',',','，','and','then'}
        return [p.strip() for p in parts if p.strip() and p.strip() not in bad]

    # ========================== 中文解析（终极版）==========================
    def extract_chinese_operations(self, text: str) -> List[str]:
        ops = OrderedDict()  # 用 OrderedDict 自动去重 + 保留顺序
        text = text.strip()

        # 1. 强正则匹配（覆盖 95% 以上情况）
        patterns = [
            r'把\s*(.+?)\s*变成\s*(.+?)(?=然后|接着|之后|再|，|,|和|$)',
            r'将\s*(.+?)\s*变成\s*(.+?)(?=然后|接着|之后|再|，|,|和|$)',
            r'把\s*(.+?)\s*改[为|成]\s*(.+?)(?=然后|接着|之后|再|，|,|和|$)',
            r'将\s*(.+?)\s*改[为|成]\s*(.+?)(?=然后|接着|之后|再|，|,|和|$)',
            r'使\s*(.+?)\s*成为\s*(.+?)(?=然后|接着|之后|再|，|,|和|$)',
            r'(.+?)\s*变成\s*(.+?)(?=然后|接着|之后|再|，|,|和|$)',
        ]

        for pat in patterns:
            for m in re.finditer(pat, text):
                src = m.group(1).strip()
                dst = m.group(2).strip()
                # 简单清理“的”结尾
                if dst.endswith('的'): dst = dst[:-1]
                ops[src] = f"{src} → {dst}"

        # 2. 如果正则没抓到，用词性兜底（极少触发）
        if not ops:
            words = [(w, f) for w, f in pseg.cut(text)]
            i = 0
            while i < len(words):
                word, flag = words[i]
                # 找到颜色 + 物体组合
                if word in self.colors:
                    obj_parts = [word]
                    j = i + 1
                    while j < len(words) and (words[j][0] in self.modifiers or words[j][0] in self.objects or words[j][1].startswith('n')):
                        obj_parts.append(words[j][0])
                        j += 1
                    if len(obj_parts) > 1:
                        src_desc = ''.join(obj_parts)
                        # 往后找动词 + 目标颜色
                        for k in range(j, len(words)):
                            if words[k][1].startswith('v'):
                                for m in range(k+1, min(k+6, len(words))):
                                    if words[m][0] in self.colors:
                                        dst_color = words[m][0]
                                        ops[src_desc] = f"{src_desc} → {dst_color}"
                                        break
                                break
                    i = j
                else:
                    i += 1

        return list(ops.values())

    # ========================== 英文解析 ==========================
    def extract_english_operations(self, text: str) -> List[str]:
        seen = OrderedDict()
        text = text.lower().replace("grey", "gray")

        COLORS = {
            "red", "orange", "yellow", "green", "blue", "purple",
            "black", "white", "gray", "brown", "pink", "gold",
            "silver", "cyan", "magenta", "bronze"
        }

        # Regex to capture individual operations
        pattern = re.compile(r"""
            (?:^|\b(?:and|make|turn|change|please|can\s+you\s+)?\s+)   # 前缀词（关键：保留 make）
            (?:the|this|that|a|an|it|them)?\s*                         # 冠词或 it/them

            ((?:                                                       # 修饰词组（大小、材质、颜色，可多个）
                (?:big|small|large|tiny|huge|little|
                   metal|rubber|wooden|plastic|shiny|matte)\s+
                |
                (?:red|orange|yellow|green|blue|purple|black|white|
                   gray|brown|pink|gold|silver|cyan|magenta|bronze)\s+
            )*)

            \b(ball|sphere|cube|block|cylinder)\b                      # 物体类型（核心）

            \s*

            (?:
                # 分支1：正常带 to/into 的情况（turn/change + to/into）
                \s+(?:to|into|become|becomes?|\bas)\b
                |
                \s+(?:change|turn)(?:\s+(?:it|them))?\s+(?:to|into)\b
                |
                # 分支2：关键修复！make 在前面时的直接接颜色（最常用！）
                \s+make\b(?:\s+(?:it|them))?
                |
                # 分支3：make 在后面的兼容（保留你原来能用的情况）
                make\b(?:\s+(?:it|them))?
            )\s+

            \b(red|orange|yellow|green|blue|purple|black|white|
               gray|brown|pink|gold|silver|cyan|magenta|bronze)\b
        """, re.VERBOSE | re.IGNORECASE)

        # Split the text into individual instructions based on conjunctions like "and" or "then"
        instructions = re.split(r"\band\b|\bthen\b", text)

        # Iterate over each instruction
        for instruction in instructions:
            match = pattern.search(instruction.strip())
            if match:
                prefix_raw = (match.group(1) or "").strip()
                obj_type = match.group(2)
                target_color = match.group(3)

                # Extract modifiers and source color from the prefix
                words = prefix_raw.split()
                source_color = None
                modifiers = []

                for w in words:
                    if w in COLORS:
                        source_color = w
                    else:
                        modifiers.append(w)

                # Construct the source description: modifiers + color + object
                src_parts = modifiers[:]
                if source_color:
                    src_parts.append(source_color)
                src_parts.append(obj_type)

                src = " ".join(src_parts) if src_parts else obj_type
                result_str = f"{src} → {target_color}"

                # Save the operation result in the ordered dict
                seen[src] = result_str

        # Return the results in the order they were processed
        return list(seen.values())

    # ========================== 主函数 ==========================
    def decompose_instruction(self, instruction: str) -> List[str]:
        instruction = self.preprocess(instruction)
        all_ops = []

        for sent in self.split_sentences(instruction):
            if re.search(r'[a-zA-Z]', sent):
                all_ops.extend(self.extract_english_operations(sent))
            else:
                for sub in self.split_sub_operations(sent):
                    all_ops.extend(self.extract_chinese_operations(sub))

        # 去重，确保每步操作唯一
        seen = set()
        unique = []
        for op in all_ops:
            # 假设每个操作是"物体 → 颜色"格式，提取物体和颜色
            parts = op.split(" → ")
            if len(parts) == 2:
                src, dst = parts[0].strip(), parts[1].strip()
                # 去除“把”字样并标准化
                if src.startswith("把"):
                    src = src[1:].strip()
                # 将物体和颜色组合成元组
                operation = (src, dst)

                if operation not in seen:
                    seen.add(operation)
                    unique.append(op)

        return unique

    def generate_decomposed_instruction(self, instruction: str) -> Tuple[str, List[str]]:
        decomposed = self.decompose_instruction(instruction)
        if not decomposed:
            return instruction, []

        result = "【复合指令分解结果】\n"
        for i, op in enumerate(decomposed, 1):
            result += f"{i}. {op}\n"
        result += "【请严格按以上顺序依次执行每一步操作】"
        return result, decomposed
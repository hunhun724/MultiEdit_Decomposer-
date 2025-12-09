
---

# MultiEdit_Decomposer 复合指令分解器

![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![Jieba](https://img.shields.io/badge/Dependency-Jieba-green) ![License](https://img.shields.io/badge/license-MIT-orange)

这是一个基于规则和 NLP（自然语言处理）的指令分解工具。它能够将复杂的自然语言指令（中文或英文）解析为结构化的原子操作步骤。

该工具主要针对 **物体属性编辑** 场景（如：“把红色的球变成蓝色”），特别适用于图像编辑类数据集的逻辑处理。

## ✨ 核心特性

- **🌍 双语支持**：完美支持中文和英文指令解析。
- **🔗 复合指令处理**：能够处理包含“然后”、“接着”、“and”、“then”等连接词的长难句。
- **🧩 混合解析策略**：
  - **中文**：结合正则表达式与 `jieba` 词性标注，精准提取“把 A 变成 B”等句式。
  - **英文**：基于复杂的正则表达式，支持多种语法结构（make X Y, change X to Y, etc.）。
- **🛡️ 容错性**：内置错别字兼容（如 grey/gray）及 Jieba 安全补丁。

## 📦 安装依赖

本项目仅依赖 `jieba` 进行中文分词，其他均为 Python 标准库。

```bash
pip install jieba
```

## 🚀 快速开始

### 1. 引入类库

确保 `MultiEdit_Decomposer_Final.py` 在你的项目目录下。

```python
from MultiEdit_Decomposer_Final import InstructionDecomposer

# 初始化分解器
decomposer = InstructionDecomposer()
```

### 2. 解析指令

使用 `generate_decomposed_instruction` 方法获取格式化文本和列表数据。

```python
# 示例输入（中文）
instruction_cn = "把红色的球变成蓝色，然后将小的正方体改为绿色"

result_text, result_list = decomposer.generate_decomposed_instruction(instruction_cn)

print(result_text)
# 输出格式化的阅读文本

print(result_list)
# 输出列表: ['红色的球 → 蓝色', '小的正方体 → 绿色']
```

## 💡 使用示例 (Demos)

### 中文场景

| 输入指令 | 解析结果 |
| :--- | :--- |
| `把大球变成金色` | `['大球 → 金色']` |
| `将金属圆柱改为红色，并把橡胶方块变成蓝色` | `['金属圆柱 → 红色', '橡胶方块 → 蓝色']` |

### 英文场景

| 输入指令 | 解析结果 |
| :--- | :--- |
| `Make the red sphere blue` | `['red sphere → blue']` |
| `Change the tiny metal cube to green and make the big ball yellow` | `['tiny metal cube → green', 'big ball → yellow']` |

## 🛠️ 代码结构说明

- **`InstructionDecomposer`**: 主类。
  - `preprocess()`: 文本清洗，统一标点符号。
  - `extract_chinese_operations()`: 核心中文解析逻辑（正则优先，词性兜底）。
  - `extract_english_operations()`: 核心英文解析逻辑（基于 RegEx 模式匹配）。
  - `decompose_instruction()`: 入口函数，负责断句、去重和整合。

## 📝 词汇覆盖

该工具内置了对以下属性的识别能力：

*   **颜色**: 红, 蓝, 绿, 黄, 金, 银, red, blue, green, gold...
*   **形状**: 球, 方块, 圆柱, sphere, cube, cylinder...
*   **材质/修饰**: 金属, 橡胶, 大, 小, metal, rubber, big, small...

## 🤝 贡献

欢迎提交 Issue 或 Pull Request 来增加更多的句式支持或优化正则表达式！

## 📄 许可证

本项目遵循 MIT 许可证。

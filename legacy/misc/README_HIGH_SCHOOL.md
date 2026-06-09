# 高中教学系统数据结构说明

## 目录结构

```
data/
├── ds_data/              # 原有数据结构数据（保留作为参考）
├── high_school_data/     # 高中教学系统数据
│   ├── math/             # 数学
│   │   ├── chapters/
│   │   │   └── chapters.json
│   │   ├── questions/
│   │   │   ├── m01.json
│   │   │   ├── m02.json
│   │   │   └── ...
│   │   └── knowledgepoints/
│   │       ├── m01.json
│   │       ├── m02.json
│   │       └── ...
│   ├── physics/          # 物理
│   ├── chemistry/        # 化学
│   ├── biology/          # 生物
│   ├── english/         # 英语
│   ├── chinese/         # 语文
│   ├── question_template.json      # 题目模板
│   └── knowledgepoint_template.json # 知识点模板
└── examples/
    └── data_structure/   # 原有数据结构数据示例
```

## 创建数据结构

运行以下命令创建高中教学系统的数据结构：

```bash
python data/create_high_school_data.py
```

这将创建：
- 6个科目的目录结构
- 每个科目8个章节
- 空的题目和知识点文件（待填充）
- 模板文件（用于参考数据格式）

## 数据格式

### 题目格式 (question_template.json)

```json
{
    "id": "q_m01_001",
    "title": "题目标题",
    "content": "题目内容",
    "difficulty": 3,
    "type": "choice",
    "subject": "math",
    "grade": "grade2",
    "tags": ["函数", "方程"],
    "source": "manual",
    "options": {
        "A": "选项A",
        "B": "选项B"
    },
    "knowledge_points": ["kc_m01_001"],
    "reference_answer": {
        "content": "答案",
        "key_points": ["关键点"],
        "explanation": "解析"
    },
    "chapter": "m01"
}
```

### 知识点格式 (knowledgepoint_template.json)

```json
{
    "id": "kc_m01_001",
    "title": "知识点标题",
    "chapter_id": "m01",
    "description": "详细描述",
    "related_points": [],
    "questions": ["q_m01_001"]
}
```

## 添加题目的方式

### 方式1：文件上传（推荐）

1. 访问 `http://localhost:3003/upload`
2. 上传PDF或图片文件
3. 系统自动提取题目并保存

### 方式2：题目生成

1. 使用API生成相似题目：
   ```bash
   curl -X POST "http://localhost:3003/api/questions/generate" \
     -H "Content-Type: application/json" \
     -d '{"question_id": "existing_id", "variations": 5}'
   ```

### 方式3：手动编辑

1. 查看模板文件了解格式
2. 编辑对应的JSON文件
3. 确保ID格式正确：`q_{章节ID}_{序号}`

## 科目代码

- `math` - 数学
- `physics` - 物理
- `chemistry` - 化学
- `biology` - 生物
- `english` - 英语
- `chinese` - 语文

## 年级代码

- `grade1` - 高一
- `grade2` - 高二
- `grade3` - 高三
- `""` - 通用（所有年级）

## 题目类型

- `choice` - 选择题
- `fill` - 填空题
- `essay` - 解答题
- `calculation` - 计算题

## 难度等级

- `1` - 非常简单
- `2` - 简单
- `3` - 中等
- `4` - 困难
- `5` - 非常困难

## 注意事项

1. **ID格式**：
   - 题目ID：`q_{章节ID}_{序号}`，如 `q_m01_001`
   - 知识点ID：`kc_{章节ID}_{序号}`，如 `kc_m01_001`

2. **章节ID格式**：
   - 数学：`m01`, `m02`, ...
   - 物理：`p01`, `p02`, ...
   - 化学：`c01`, `c02`, ...
   - 生物：`b01`, `b02`, ...
   - 英语：`e01`, `e02`, ...
   - 语文：`h01`, `h02`, ...

3. **数据一致性**：
   - 题目的 `chapter` 字段必须对应章节ID
   - 题目的 `knowledge_points` 必须对应存在的知识点ID
   - 知识点的 `questions` 必须对应存在的题目ID

## 数据迁移

原有的数据结构数据已迁移到 `examples/data_structure/` 作为参考。

如果需要将原有数据结构题目转换为高中题目格式，可以：
1. 查看原有数据格式
2. 参考模板文件
3. 手动转换或编写转换脚本

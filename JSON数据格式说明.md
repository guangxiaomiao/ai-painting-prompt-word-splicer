# AI Prompt 词库 JSON 数据格式说明

## 概述

本文档描述了 AI Prompt 词库管理器的 JSON 数据交换格式。JSON 文件用于导入和导出词库数据，支持权重调节和正/负向词条分类。

---

## 完整 JSON 结构

```json
{
  "version": "2.0",
  "exported_at": "2024-01-15T10:30:00",
  "categories": [],
  "prompts": [],
  "templates": [],
  "random_rules": []
}
```

### 顶层字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| version | string | 是 | 数据格式版本，当前为 **"2.0"** |
| exported_at | string | 是 | 导出时间，ISO 8601 格式 |
| categories | array | 是 | 分类列表 |
| prompts | array | 是 | Prompt 词条列表 |
| templates | array | 否 | 模板列表 |
| random_rules | array | 否 | 随机规则列表 |

---

## 分类 (Category)

分类用于组织 Prompt 词条，支持树形结构（父分类-子分类）。

### 示例

```json
{
  "id": 1,
  "name": "quality",
  "name_cn": "画质",
  "parent_id": null,
  "order": 0,
  "expanded": true,
  "enabled": true,
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | integer | 是 | 分类唯一标识符 |
| name | string | 是 | 分类英文名称（唯一） |
| name_cn | string | 否 | 分类中文名称 |
| parent_id | integer/null | 否 | 父分类ID，为 null 表示顶级分类 |
| order | integer | 否 | 排序序号，数字越小越靠前（默认0） |
| expanded | boolean | 否 | 树形视图中是否默认展开（默认true） |
| enabled | boolean | 否 | 是否启用（默认true） |
| created_at | string | 否 | 创建时间，ISO 8601 格式 |
| updated_at | string | 否 | 更新时间，ISO 8601 格式 |

### 嵌套分类示例

```json
{
  "id": 2,
  "name": "character",
  "name_cn": "人物",
  "parent_id": null,
  "order": 1,
  "expanded": true,
  "enabled": true
},
{
  "id": 3,
  "name": "character_hair",
  "name_cn": "发型",
  "parent_id": 2,
  "order": 0,
  "expanded": true,
  "enabled": true
}
```

---

## Prompt 词条 (Prompt)

每个 Prompt 词条代表一个可用的 AI 绘图提示词。

### 正向词条示例

```json
{
  "id": 1,
  "english": "1girl",
  "chinese": "1女孩",
  "note": "单人女性主体",
  "aliases": "solo, single girl",
  "tags": "人物,女性",
  "weight": 1.2,
  "prompt_type": "positive",
  "enabled": true,
  "favorite": true,
  "probability": 1.0,
  "random_weight": 2.0,
  "author": "unknown",
  "source": "common",
  "version": "1.0",
  "category_id": 2,
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### 负向词条示例

```json
{
  "id": 100,
  "english": "worst quality",
  "chinese": "最低质量",
  "note": "负面标签，用于排除",
  "aliases": "low quality, bad quality",
  "tags": "负面,质量",
  "weight": 1.0,
  "prompt_type": "negative",
  "enabled": true,
  "favorite": false,
  "probability": 1.0,
  "random_weight": 1.0,
  "author": "unknown",
  "source": "common",
  "version": "1.0",
  "category_id": 5,
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | integer | 是 | 词条唯一标识符 |
| english | string | **是** | 英文 Prompt（必须） |
| chinese | string | 否 | 中文翻译 |
| note | string | 否 | 备注说明 |
| aliases | string | 否 | 别名，多个用逗号分隔 |
| tags | string | 否 | 标签，多个用逗号分隔 |
| **weight** | float | **可选** | **权重值，范围 0.0~2.0（默认1.0）** |
| **prompt_type** | string | **可选** | **词条类型：`positive`(正向) 或 `negative`(负向)，默认`positive`** |
| enabled | boolean | 否 | 是否启用（默认true） |
| favorite | boolean | 否 | 是否收藏（默认false） |
| probability | float | 否 | 出现概率，0.0-1.0（默认1.0） |
| random_weight | float | 否 | 随机权重，用于随机生成时的概率（默认1.0） |
| author | string | 否 | 作者 |
| source | string | 否 | 来源 |
| version | string | 否 | 版本号 |
| category_id | integer | 是 | 所属分类ID |
| created_at | string | 否 | 创建时间，ISO 8601 格式 |
| updated_at | string | 否 | 更新时间，ISO 8601 格式 |

---

## 权重 (Weight) 说明

### 权重规则

权重用于调节 Prompt 在生成时的强度或重要性。

| 权重值 | 效果 | 输出格式 |
|--------|------|----------|
| `1.0` | 标准权重 | `(cat)` → `cat` |
| `1.2` | 增强权重 | `(cat:1.2)` |
| `0.8` | 减弱权重 | `(cat:0.8)` |
| `0.0` | 禁用 | 不输出 |

### 输出语法

生成最终提示词时：

```
weight != 1.0  →  输出 (英文词:权重)
weight == 1.0  →  只输出英文词本身
```

### 示例

| weight | english | 最终输出 |
|--------|---------|----------|
| 1.0 | cat | `cat` |
| 1.2 | cat | `(cat:1.2)` |
| 0.8 | blue eyes | `(blue eyes:0.8)` |
| 1.5 | masterpiece | `(masterpiece:1.5)` |

### 权重应用场景

- **1.0~1.5**: 增强重要特征（如 `masterpiece:1.3`）
- **0.5~0.9**: 减弱次要特征（如 `blurry:0.5`）
- **1.5~2.0**: 强烈强调（如 `solo:1.8`）

---

## 正向/负向词条 (prompt_type) 说明

### 方案选择

本系统采用 **方案A**：在词条层级增加 `prompt_type` 字段来区分正向和负向词条。

### prompt_type 字段值

| 值 | 说明 | 用途 |
|----|------|------|
| `positive` | 正向词条 | 要生成的特征 |
| `negative` | 负向词条 | 要排除的特征 |

### 生成输出格式

最终生成的提示词分为两段，中间用 `--neg` 分隔：

```
正向词条1, 正向词条2, (正向词条3:1.2) --neg 负向词条1, 负向词条2, (负向词条3:0.8)
```

### 示例

```
输入:
  - 1girl (positive, weight=1.2)
  - solo (positive, weight=1.0)
  - masterpiece (positive, weight=1.5)
  - worst quality (negative, weight=1.0)
  - blurry (negative, weight=0.8)

输出:
  (1girl:1.2), solo, (masterpiece:1.5) --neg worst quality, (blurry:0.8)
```

---

## 模板 (Template)

模板是预设的 Prompt 组合方案。

### 示例

```json
{
  "id": 1,
  "name": "portrait_template",
  "name_cn": "人像模板",
  "description": "标准人像生成模板",
  "enabled": true,
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | integer | 是 | 模板唯一标识符 |
| name | string | 是 | 模板英文名称 |
| name_cn | string | 否 | 模板中文名称 |
| description | string | 否 | 模板描述 |
| enabled | boolean | 否 | 是否启用（默认true） |
| created_at | string | 否 | 创建时间 |
| updated_at | string | 否 | 更新时间 |

---

## 随机规则 (RandomRule)

随机规则控制随机生成时每个分类的行为。

### 示例

```json
{
  "id": 1,
  "category_id": 1,
  "mode": "optional",
  "min_count": 0,
  "max_count": 3,
  "probability": 0.8,
  "use_weight": true
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | integer | 是 | 规则唯一标识符 |
| category_id | integer | 是 | 关联的分类ID |
| mode | string | 否 | 模式：`must`(必须) / `optional`(可选) / `fixed`(固定)（默认optional） |
| min_count | integer | 否 | 最小随机数量（默认0） |
| max_count | integer | 否 | 最大随机数量（默认1） |
| probability | float | 否 | 该分类参与随机的概率，0.0-1.0（默认1.0） |
| use_weight | boolean | 否 | 是否使用随机权重（默认true） |

### mode 模式说明

| 模式 | 说明 |
|------|------|
| `must` | 必须生成，该分类的 Prompt 必定包含 |
| `optional` | 可选生成，根据概率和随机权重决定是否包含 |
| `fixed` | 固定生成，按照 min_count 和 max_count 固定生成指定数量 |

---

## 完整示例（含所有新字段）

```json
{
  "version": "2.0",
  "exported_at": "2024-01-15T10:30:00",
  "categories": [
    {
      "id": 1,
      "name": "quality",
      "name_cn": "画质",
      "parent_id": null,
      "order": 0,
      "expanded": true,
      "enabled": true
    },
    {
      "id": 2,
      "name": "character",
      "name_cn": "人物",
      "parent_id": null,
      "order": 1,
      "expanded": true,
      "enabled": true
    },
    {
      "id": 5,
      "name": "negative",
      "name_cn": "负面词库",
      "parent_id": null,
      "order": 99,
      "expanded": true,
      "enabled": true
    }
  ],
  "prompts": [
    {
      "id": 1,
      "english": "masterpiece",
      "chinese": "杰作",
      "note": "最高画质标签，必备",
      "aliases": "best quality, high quality",
      "tags": "画质,精品",
      "weight": 1.5,
      "prompt_type": "positive",
      "enabled": true,
      "favorite": true,
      "probability": 1.0,
      "random_weight": 2.0,
      "author": "unknown",
      "source": "common",
      "version": "1.0",
      "category_id": 1
    },
    {
      "id": 2,
      "english": "1girl",
      "chinese": "1女孩",
      "note": "单人女性",
      "aliases": "solo, single girl",
      "tags": "人物,女性",
      "weight": 1.2,
      "prompt_type": "positive",
      "enabled": true,
      "favorite": false,
      "probability": 1.0,
      "random_weight": 1.0,
      "author": "unknown",
      "source": "common",
      "version": "1.0",
      "category_id": 2
    },
    {
      "id": 3,
      "english": "solo",
      "chinese": "单人",
      "note": "单独主体",
      "aliases": "alone",
      "tags": "人物",
      "weight": 1.0,
      "prompt_type": "positive",
      "enabled": true,
      "favorite": false,
      "probability": 0.8,
      "random_weight": 1.0,
      "author": "unknown",
      "source": "common",
      "version": "1.0",
      "category_id": 2
    },
    {
      "id": 100,
      "english": "worst quality",
      "chinese": "最低质量",
      "note": "负面标签，用于排除低质量",
      "aliases": "low quality, bad quality",
      "tags": "负面,质量",
      "weight": 1.0,
      "prompt_type": "negative",
      "enabled": true,
      "favorite": false,
      "probability": 1.0,
      "random_weight": 1.0,
      "author": "unknown",
      "source": "common",
      "version": "1.0",
      "category_id": 5
    },
    {
      "id": 101,
      "english": "blurry",
      "chinese": "模糊",
      "note": "模糊效果负面标签",
      "aliases": "unclear, fuzzy",
      "tags": "负面,效果",
      "weight": 0.8,
      "prompt_type": "negative",
      "enabled": true,
      "favorite": false,
      "probability": 0.5,
      "random_weight": 0.5,
      "author": "unknown",
      "source": "common",
      "version": "1.0",
      "category_id": 5
    },
    {
      "id": 102,
      "english": "nsfw",
      "chinese": "不适宜内容",
      "note": "NSFW负面标签",
      "aliases": "explicit, adult",
      "tags": "负面,内容过滤",
      "weight": 1.0,
      "prompt_type": "negative",
      "enabled": true,
      "favorite": false,
      "probability": 0.3,
      "random_weight": 0.3,
      "author": "unknown",
      "source": "common",
      "version": "1.0",
      "category_id": 5
    }
  ],
  "templates": [
    {
      "id": 1,
      "name": "portrait",
      "name_cn": "人像模板",
      "description": "标准人像生成模板，包含正向词和负向词",
      "enabled": true
    }
  ],
  "random_rules": [
    {
      "id": 1,
      "category_id": 1,
      "mode": "must",
      "min_count": 1,
      "max_count": 1,
      "probability": 1.0,
      "use_weight": true
    }
  ]
}
```

---

## 导入数据格式

### 新格式要求 (v2.0)

新格式 JSON 必须包含以下字段：

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| version | string | 是 | - | 必须为 "2.0" |
| prompts | array | 是 | - | Prompt 词条数组 |
| weight | float | **可选** | 1.0 | 权重值，范围 0.0~2.0 |
| prompt_type | string | **可选** | "positive" | "positive" 或 "negative" |

### 新旧格式兼容性

| 字段 | 旧格式 (v1.0) | 新格式 (v2.0) | 兼容性处理 |
|------|---------------|---------------|------------|
| weight | 无 | 有 | 旧格式默认 1.0 |
| prompt_type | 无 | 有 | 旧格式默认 "positive" |
| version | "1.0" | "2.0" | 自动升级兼容 |

**兼容性规则**：
- 导入时若 `weight` 字段不存在，默认设为 `1.0`
- 导入时若 `prompt_type` 字段不存在，默认设为 `"positive"`
- 导出时总是包含所有字段

---

## 语法规则

### 1. JSON 基本语法

- 使用双引号包裹字符串
- 对象用 `{}` 表示
- 数组用 `[]` 表示
- 键值对用 `:` 分隔
- 多条目用 `,` 分隔

### 2. 常见错误

#### ❌ 错误：使用了单引号

```json
{
  'name': 'value'  // 错误！JSON 必须使用双引号
}
```

✅ 正确：

```json
{
  "name": "value"
}
```

#### ❌ 错误：末尾多余的逗号

```json
{
  "name": "value",  // 错误！JSON 不允许末尾逗号
}
```

#### ❌ 错误：注释

```json
{
  // 这是注释  // 错误！JSON 不支持注释
  "name": "value"
}
```

✅ 正确：移除注释

#### ❌ 错误：多余逗号

```json
{
  "name": "value",  // 错误！
  "age": 25,        // 错误！最后一个字段不能有逗号
}
```

#### ❌ 错误：weight 值超出范围

```json
{
  "weight": 3.0  // 错误！超出 0.0~2.0 范围
}
```

#### ❌ 错误：prompt_type 值无效

```json
{
  "prompt_type": "pos"  // 错误！必须是 "positive" 或 "negative"
}
```

✅ 正确：

```json
{
  "prompt_type": "positive"
}
```

或

```json
{
  "prompt_type": "negative"
}
```

### 3. 数据类型

| JSON 类型 | Python 类型 | 示例 |
|-----------|-------------|------|
| string | str | `"hello"` |
| number | int/float | `123` 或 `1.5` |
| boolean | bool | `true` / `false` |
| null | None | `null` |
| array | list | `[1, 2, 3]` |
| object | dict | `{"key": "value"}}` |

### 4. 布尔值注意

- JSON 使用 `true` / `false`（小写）
- Python 使用 `True` / `False`（首字母大写）
- JavaScript 使用 `true` / `false`（小写）

### 5. 空值

- JSON 使用 `null` 表示空值
- Python 使用 `None` 表示空值

---

## 导入模式

导入时支持两种模式：

| 模式 | 说明 |
|------|------|
| `merge` | 合并模式：存在相同名称的分类/Prompt 时更新，不存在时新增 |
| `overwrite` | 覆盖模式：先删除所有现有数据，再导入新数据 |

---

## 常见导入错误排查

### 错误1：Expecting value

**错误信息**：
```
JSONDecodeError: Expecting value: line X column Y (char Z)
```

**原因**：JSON 格式错误

**排查方法**：
1. 检查第 X 行是否有尾随逗号
2. 检查是否有未闭合的引号或括号
3. 检查是否有 JSON 不支持的注释
4. 使用在线 JSON 验证工具检查

### 错误2：Unexpected field

**错误信息**：
```
KeyError: 'xxx'
```

**原因**：导入了包含未知字段的 JSON

**排查方法**：
1. 确保 version 字段正确
2. 确保 prompts 数组中每个对象包含必需字段

### 错误3：Field validation failed

**错误信息**：
```
ValidationError: weight must be between 0.0 and 2.0
```

**原因**：weight 值超出允许范围

**排查方法**：
1. 检查 weight 值是否在 0.0~2.0 范围内
2. 确保 weight 是数字类型，不是字符串

### 错误4：Invalid prompt_type

**错误信息**：
```
ValidationError: prompt_type must be 'positive' or 'negative'
```

**原因**：prompt_type 值无效

**排查方法**：
1. 确保 prompt_type 值为 `"positive"` 或 `"negative"`
2. 不要使用简写如 `"pos"` 或 `"neg"`

---

## 验证 JSON 文件

### 在线验证工具

- https://jsonformatter.curiousconcept.com/
- https://jsonlint.com/

### 命令行验证

```bash
# Linux/macOS
python3 -m json.tool yourfile.json

# Windows PowerShell
python -c "import json; json.load(open('yourfile.json', 'r', encoding='utf-8'))"
```

### Python 验证脚本

```python
import json

def validate_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("✓ JSON 格式有效")

        # 检查必需字段
        required = ['version', 'categories', 'prompts']
        for field in required:
            if field not in data:
                print(f"✗ 缺少必需字段: {field}")

        # 检查 prompts 字段
        if 'prompts' in data:
            for i, prompt in enumerate(data['prompts']):
                # 检查 weight 范围
                weight = prompt.get('weight', 1.0)
                if weight is not None and (weight < 0.0 or weight > 2.0):
                    print(f"✗ Prompt {i} weight 值超出范围: {weight}")

                # 检查 prompt_type 值
                prompt_type = prompt.get('prompt_type', 'positive')
                if prompt_type not in ['positive', 'negative']:
                    print(f"✗ Prompt {i} prompt_type 无效: {prompt_type}")

        return True
    except json.JSONDecodeError as e:
        print(f"✗ JSON 格式错误: {e}")
        return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

validate_json('yourfile.json')
```

---

## 功能说明（用户界面）

### 正向词库 / 负向词库

应用界面应支持：

1. **正向词库区域**：显示 `prompt_type="positive"` 的词条
2. **负向词库区域**：显示 `prompt_type="negative"` 的词条
3. **权重调节**：用户可为每个词条设置 0.0~2.0 的权重
4. **类型切换**：用户可将词条在正/负向之间切换

### 生成输出

生成最终提示词时：

```
正向部分: (词条1:权重), 词条2, (词条3:权重) --neg 负向部分: (词条4:权重), 词条5
```

**示例**：
```
输入: 1girl(weight=1.2), solo(weight=1.0), masterpiece(weight=1.5) --neg worst quality(weight=1.0), blurry(weight=0.8)

输出:
(masterpiece:1.5), (1girl:1.2), solo --neg worst quality, (blurry:0.8)
```

---

## 最佳实践

1. **保持 UTF-8 编码**：确保 JSON 文件保存为 UTF-8 编码
2. **不要添加注释**：JSON 不支持注释，添加会导致解析失败
3. **验证后再导入**：使用验证工具检查 JSON 格式后再导入
4. **备份数据**：导入前先导出备份
5. **权重合理使用**：推荐范围 0.5~1.5，避免极端值
6. **分类管理**：建议创建独立的"负面词库"分类存放负向词条

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2024-01-15 | 初始版本 |
| 2.0 | 2024-06-24 | 增加权重(weight)和正/负向(prompt_type)支持 |

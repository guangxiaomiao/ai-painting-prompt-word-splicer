# AI Prompt Generator - 绘画提示辅助器

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/Version-1.6-orange)

一款基于 PySide6 的 AI 绘画提示词管理工具，支持提示词分类管理、随机生成、Ollama 本地 AI 集成、数据导入导出等功能。

## 截图

（请在此处添加应用截图）

## 功能特性

### 提示词管理
- **分类管理**：支持多层分类（人物、动作、姿势、服装、发型、背景、天气、画质、画风、艺术家等）
- **双语支持**：每个提示词支持中英文显示，可切换显示模式
- **搜索过滤**：按关键词快速搜索提示词
- **权重设置**：支持为每个提示词设置随机权重

### 随机生成
- **分类筛选**：选择指定分类进行随机生成
- **自定义规则**：支持设置每个分类的随机规则（数量、概率、权重模式）
- **加权随机**：支持按权重进行随机抽取

### Ollama AI 集成
- **本地模型**：连接本地 Ollama 服务，使用本地部署的大语言模型
- **提示词生成**：AI 辅助生成绘画提示词
- **提示词翻译**：中英文提示词互译
- **流式输出**：支持流式输出，实时显示生成结果
- **批量处理**：支持批量生成和翻译

### 导入导出
- **JSON 格式**：完整数据导入导出
- **CSV 格式**：支持标准 CSV、Danbooru 格式、Danbooru 中文格式
- **Danbooru 标签**：导入 Danbooru 标签数据
- **e621 标签**：导入 e621 标签数据

### 其他功能
- **新人模式**：引导式操作，快速生成提示词
- **主题切换**：支持明亮/暗黑主题
- **自动保存**：定时自动保存数据
- **自动备份**：定时自动备份数据库
- **编辑器**：支持编辑和组合多条提示词

## 环境要求

- **操作系统**：Windows 10/11 64位
- **Python**：3.10 或更高版本
- **依赖库**：见 [requirements.txt](requirements.txt)

## 安装使用

### 方式一：直接运行（需要 Python 环境）

```bash
# 克隆仓库
git clone https://github.com/yourusername/AI_Prompt_Generator.git
cd AI_Prompt_Generator

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 方式二：使用打包版本（无需 Python 环境）

从 [Releases](https://github.com/yourusername/AI_Prompt_Generator/releases) 页面下载最新版本的安装程序 `AI_Prompt_Generator_Setup.exe`，双击安装即可使用。

### 使用 Ollama 功能（可选）

1. 下载并安装 [Ollama](https://ollama.com/)
2. 启动 Ollama 服务
3. 下载所需模型，例如：
   ```bash
   ollama pull llama3
   ollama pull deepseek-r1:7b
   ```
4. 在软件的设置页面配置 Ollama 服务地址（默认：`http://localhost:11434`）

## 项目结构

```
AI_Prompt_Generator/
├── main.py                    # 程序入口
├── requirements.txt           # Python 依赖
├── prompt_generator.spec      # PyInstaller 打包配置（完整版）
├── AI_Prompt_Generator.spec   # PyInstaller 打包配置（精简版）
├── 免责声明.txt               # 免责声明与词库来源说明
├── JSON数据格式说明.md         # JSON 数据格式文档
├── dbq/
│   └── 提示词.iss             # Inno Setup 安装包制作脚本
├── src/
│   ├── app.py                # 主窗口和应用程序
│   ├── controllers/          # 业务逻辑层
│   │   ├── data_manager.py   # 数据管理
│   │   ├── random_generator.py # 随机生成器
│   │   ├── ollama_client.py  # Ollama AI 客户端
│   │   ├── data_importer.py  # 数据导入
│   │   └── backup_manager.py # 备份管理
│   ├── models/               # 数据模型层
│   │   ├── base.py           # 数据库基础配置
│   │   ├── category.py       # 分类模型
│   │   ├── prompt.py         # 提示词模型
│   │   ├── template.py       # 模板模型
│   │   ├── template_item.py  # 模板项模型
│   │   ├── random_rule.py    # 随机规则模型
│   │   └── settings.py       # 设置模型
│   ├── views/                # 视图层
│   │   ├── category_tree.py  # 分类树视图
│   │   ├── prompt_list.py    # 提示词列表
│   │   ├── prompt_editor.py  # 提示词编辑器
│   │   ├── toolbar.py        # 工具栏和状态栏
│   │   ├── settings_dialog.py # 设置对话框
│   │   ├── random_dialog.py  # 随机生成对话框
│   │   ├── import_dialog.py  # 导入对话框
│   │   ├── ollama_panel.py   # Ollama AI 面板
│   │   └── beginner_dialog.py # 新人模式对话框
│   ├── utils/                # 工具模块
│   └── data/                 # 数据文件
│       └── prompt_db.sqlite  # SQLite 数据库
└── dist/                     # 打包输出目录
    └── AI_Prompt_Generator/  # 打包后的应用文件
```

## 自定义打包

本项目提供两种 PyInstaller 打包配置：

- **prompt_generator.spec**（完整版）：包含详细的依赖排除列表
- **AI_Prompt_Generator.spec**（精简版）：自动排除常见不需要的模块

```bash
# 安装 PyInstaller
pip install pyinstaller

# 执行打包（选择其中一个）
pyinstaller prompt_generator.spec
# 或
pyinstaller AI_Prompt_Generator.spec

# 使用 Inno Setup 编译安装程序（需要安装 Inno Setup）
# 打开 dbq/提示词.iss 在 Inno Setup Compiler 中编译
```

## 技术栈

- **GUI 框架**：PySide6（Qt for Python）
- **数据库**：SQLAlchemy + SQLite
- **AI 集成**：Ollama API（HTTP 请求）
- **数据格式**：JSON / CSV
- **打包工具**：PyInstaller + Inno Setup

## 数据来源

应用内置了一些基础提示词数据作为示例，用户可以通过导入功能导入以下来源的标签数据：

- [Danbooru](https://danbooru.donmai.us/) - 动画/漫画图片标签库
- [e621](https://e621.net/) -  furry 图片标签库

## 许可证

[MIT](LICENSE)

## 更新日志

### v1.6 - 新人模式版
- 新增新人模式，引导用户快速生成提示词
- 新增 Ollama AI 集成，支持本地大模型
- 优化界面布局和用户体验
- 新增暗黑主题支持

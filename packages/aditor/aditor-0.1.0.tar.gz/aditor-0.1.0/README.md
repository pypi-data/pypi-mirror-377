# Aditor

一个示例Python包，用于演示如何创建和发布Python包到PyPI。

## 功能特性

- 🎉 简单的问候功能
- 🧮 基础数学计算
- 📦 易于安装和使用
- 🐍 支持Python 3.7+

## 安装

### 从PyPI安装（推荐）

```bash
pip install aditor
```

### 从源码安装

```bash
git clone https://github.com/yourusername/aditor.git
cd aditor
pip install -e .
```

## 快速开始

```python
from aditor import hello_world, calculate_sum

# 问候功能
print(hello_world("Python"))  # 输出: 你好, Python!

# 数学计算
result = calculate_sum(1.5, 2.5)
print(f"1.5 + 2.5 = {result}")  # 输出: 1.5 + 2.5 = 4.0
```

## 命令行使用

```bash
aditor --help
```

## 开发

### 设置开发环境

```bash
git clone https://github.com/yourusername/aditor.git
cd aditor
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black aditor/
```

### 类型检查

```bash
mypy aditor/
```

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 这个仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证

本项目使用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 作者

您的名字 - your.email@example.com

项目链接: [https://github.com/yourusername/aditor](https://github.com/yourusername/aditor)

## 更新日志

### 0.1.0 (2024-01-01)

- 初始版本发布
- 添加基础问候功能
- 添加数学计算功能

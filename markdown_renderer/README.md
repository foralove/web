# Django Markdown渲染模块

## 简介

这是一个功能完整的Django Markdown渲染模块，支持数学公式、代码高亮、表格和多种编码格式。该模块设计为完全可移植，可以轻松集成到任何Django项目中。

## 功能特点

- 标准Markdown语法支持
- 数学公式渲染（使用KaTeX）
- 代码语法高亮（多种编程语言）
- 表格和目录（TOC）生成
- 多种文件编码自动检测
- 文件安全验证

## 安装指南

### 1. 安装依赖

确保安装所有必需的依赖项：

```bash
pip install -r requirements.txt
```

### 2. 注册应用

在Django项目的`settings.py`中注册应用：

```python
INSTALLED_APPS = [
    # ...其他应用
    'markdown_renderer',
]
```

### 3. 配置设置

在`settings.py`中添加以下配置：

```python
MARKDOWN_RENDER = {
    'MAX_SIZE': 5 * 1024 * 1024,
    'ENABLE_UNSAFE_EXTENSIONS': False,
    'EXTENSION_CONFIGS': {
        'codehilite': {
            'linenums': True,
        },
        'mdx_math': {
            'enable_dollar_delimiter': True,
        },
        'toc': {
            'permalink': False,
        },
    },
}
```

### 4. 集成静态文件

确保在项目中包含必要的CSS文件，并运行：

```bash
python manage.py collectstatic
```

## 使用方法

### 在视图中使用

```python
from markdown_renderer.utils import render_markdown

def view_markdown(request, file_path):
    html_content = render_markdown(file_path)
    return render(request, 'your_template.html', {
        'html_content': html_content,
        'is_markdown': True,
    })
```

### 在模板中使用

1. 加载模板标签：

```html
{% load md_render %}
```

2. 渲染Markdown文件：

```html
{% render_markdown file_path="/path/to/file.md" %}
```

或者渲染Markdown文本：

```html
{{ markdown_text|markdown }}
```

## 测试

使用提供的`test_markdown.md`文件测试渲染功能，确保所有功能正常工作。 
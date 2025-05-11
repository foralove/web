# DocMgr 文档管理系统

一个基于Django的文档管理系统，具有可移植的Markdown渲染功能。

## 安装设置

1. 克隆代码仓库
2. 创建虚拟环境：
   ```
   python -m venv venv
   ```
3. 激活虚拟环境：
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
5. 运行数据库迁移：
   ```
   python manage.py migrate
   ```
6. 启动开发服务器：
   ```
   python manage.py runserver
   ```

## 功能特点

- 文档管理功能
- 用户认证
- 可移植的Markdown渲染模块
- 代码语法高亮
- 响应式设计

## 可移植的Markdown渲染模块

本项目包含一个完全可移植的Markdown渲染模块，任何Django项目都可以通过简单的几个步骤集成这一功能。

### 功能特性

- 标准Markdown语法支持
- 数学公式渲染（使用KaTeX）
- 代码语法高亮
- 表格和目录（TOC）
- 多种文件编码自动检测
- 文件安全验证

### 数学公式支持

系统支持行内和块级数学公式：

- 行内公式: `$E = mc^2$`
- 块级公式: `$$F = ma$$`

## 如何将Markdown模块集成到您的Django项目

### 1. 复制Markdown渲染模块

将以下文件和目录复制到您的Django项目中：
```
markdown_renderer/
├── __init__.py
├── templatetags/
│   ├── __init__.py
│   └── md_render.py
└── utils/
    ├── __init__.py
    ├── renderer.py
    └── sanitizer.py
```

### 2. 添加依赖项

确保您的项目安装了以下依赖：

```bash
pip install markdown python-markdown-math chardet
```

将这些依赖添加到您的`requirements.txt`文件中。

### 3. 注册应用

在您的`settings.py`文件中注册Markdown渲染器应用：

```python
INSTALLED_APPS = [
    'markdown_renderer',
]
```

### 4. 添加Markdown配置

在您的`settings.py`文件中添加Markdown渲染器配置：

```python
MARKDOWN_RENDER = {
    'MAX_SIZE': 5 * 1024 * 1024,
    'STYLE_THEME': 'github.css', 
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

### 5. 创建静态文件

在您的静态文件目录中创建Markdown样式文件：

```
static/
└── md_theme/
    └── github.css
```

### 6. 修改模板

在您的模板中添加KaTeX支持和CSS引用：

```html
{% load static %}

{% block extra_css %}
<link href="{% static 'md_theme/github.css' %}" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
{% endblock %}

{% block extra_js %}
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
    onload="renderMathInElement(document.body);"></script>
<script>
    document.addEventListener("DOMContentLoaded", function() {
        renderMathInElement(document.body, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true}
            ],
            throwOnError: false
        });
    });
</script>
{% endblock %}
```

### 7. 在视图中使用

在您的视图中使用Markdown渲染器：

```python
from markdown_renderer.utils import render_markdown

def view_markdown(request, file_path):
    html_content = render_markdown(file_path)
    
    return render(request, 'your_template.html', {
        'html_content': html_content,
        'is_markdown': True,
    })
```

或者在模板中使用标签：

```html
{% load md_render %}

{% render_markdown file_path="path/to/file.md" %}

{{ markdown_text|markdown }}
```

## 完整集成示例

请参考本项目中的`documents`应用，了解如何完整集成Markdown渲染功能：
- `documents/views.py` - 视图集成示例
- `templates/documents/document_view.html` - 模板集成示例 

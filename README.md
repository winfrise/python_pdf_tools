# 基于Python实现的PDF工具

- PyMuPDF
- Spire.PDF
- QPDF(项目中没有使用，在命令行中使用)


```
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活环境 (Windows)
source venv/bin/activate

# 3. 安装 PyMuPDF
pip install PyMuPDF

# 安装 spire.pdf
pip install spire.pdf


# 导出依赖列表
pip freeze > requirements.txt
```
## 命令

#### 查看和修改MetaData
```
# Author修改不了
python ./src/view_and_modify_pdf_meta.py
```

#### 提取PDF中的所有图片
```
python ./src/extract_images.py
```

#### 提取PDF中的所有图片
```
# 功能待测试
python ./src/analyze_and_remove_images.py
```


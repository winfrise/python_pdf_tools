# 基于Python实现的PDF工具

- PyMuPDF
- Spire.PDF
- QPDF(项目中没有使用，在命令行中使用)


```
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活环境 (Windows)
source venv/bin/activate

# 3. 安装 PyMuPDF(1.27.2.3)
pip install PyMuPDF

# 3. 安spire.pdf
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

#### 将PDF每一页转换成图片输出
```
python ./src/pdf2images.py
```

#### 给PDF文件添加页头页尾
```
python ./src/mask_header_footer_images.py
```

#### 添加图片水印
```
python ./src/add_image_watermark.py
```

#### 转扫描件
```
python ./src/pdf_to_scanned.py
```

#### 分割页面【一页一个PDF文件】（不影响签名）
```
python ./src/split_page.py
```

#### 通过图片尺寸删除图片（删除水印）
```
# 功能待测试
python ./src/analyze_and_remove_images.py
```


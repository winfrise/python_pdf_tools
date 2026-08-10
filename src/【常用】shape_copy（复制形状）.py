import pymupdf  # PyMuPDF

# 1. 打开源文档和目标文档
src_doc = pymupdf.open("/Users/teacher/Desktop/图纸修改/3#浅圆仓、4#提升发放塔、5#提升发放塔_2_建施01_建筑设计说明、建筑设计防火设计专篇、节能设计专篇、防水设计专篇、选用标准图集、工程做法表、门窗表、门窗分格示意图 第2版1481KB.pdf")
dst_doc = pymupdf.open("/Users/teacher/Desktop/图纸修改/mask.pdf")

# 2. 获取源页面和目标页面
src_page = src_doc[0]
dst_page = dst_doc[0]

# 3. 提取源页面所有矢量图形
drawings = src_page.get_drawings()

# 4. 在目标页面创建新的绘图画布
shape = dst_page.new_shape()

# 5. 遍历并重绘每个图形
for path in drawings:
    # 你可以根据需要过滤特定图形，比如按颜色、位置等
    # if path["color"] != (1, 0, 0): continue  # 例如只复制红色图形

    for item in path["items"]:
        kind = item[0]
        if kind == "l":  # 直线
            p1, p2 = item[1], item[2]
            shape.draw_line(p1, p2)
        elif kind == "c":  # 贝塞尔曲线
            p1, p2, p3, p4 = item[1], item[2], item[3], item[4]
            shape.draw_bezier(p1, p2, p3, p4)
        elif kind == "re":  # 矩形
            rect = item[1]
            shape.draw_rect(rect)
        elif kind == "qu":  # 四边形
            quad = item[1]
            shape.draw_quad(quad)

    # 设置样式（颜色、线宽、填充等）
    shape.finish(
        color=path.get("color", (0, 0, 0)),     # 描边颜色
        fill=path.get("fill", None),             # 填充颜色
        width=path.get("width", 1),              # 线宽
        lineJoin=path.get("lineJoin", 0),        # 连接样式
        lineCap=path.get("lineCap", 0)           # 端点样式
    )

# 6. 提交绘制并保存
shape.commit()
dst_doc.save("/Users/teacher/Desktop/图纸修改/test_output.pdf")
src_doc.close()
dst_doc.close()
import pymupdf  # PyMuPDF


def shape_copy(input_pdf, shape_config):
    # 1. 打开源文档和目标文档
    doc = pymupdf.open(input_pdf)

    # 2. 获取源页面和目标页面
    page = doc[0]

    # 4. 在目标页面创建新的绘图画布
    shape = page.new_shape()


    shape_pdf_file = shape_config.get('pdf_file')
    shape_start_x = shape_config.get('x', 0)
    shape_start_y = shape_config.get('y', 0)
    shape_width = shape_config.get('width')
    shape_height = shape_config.get('height')

    shape_doc = pymupdf.open(shape_pdf_file)
    shape_page = shape_doc[0]

    drawings = shape_page.get_drawings()

    print(f"共{len(drawings)}个形状")

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

        shape.finish(color=(0,0,0), width=1, fill=None, closePath=True)
        # 设置样式（颜色、线宽、填充等）
        # shape.finish(
        #     color=path.get("color", (0, 0, 0)),     # 描边颜色
        #     fill=path.get("fill", None),             # 填充颜色
        #     width=path.get("width", 1),              # 线宽
        #     lineJoin=path.get("lineJoin", 0),        # 连接样式
        #     lineCap=path.get("lineCap", 0),           # 端点样式
        #     closePath=True,
        # )

    # 6. 提交绘制并保存
    shape.commit()

    output_file = input_pdf.replace('.pdf', '_output_copy_shape.pdf')
    doc.save(output_file)
    doc.close()
    shape_doc.close()


if __name__ == "__main__":
    input_pdf = "/Users/teacher/Desktop/图纸修改/look_bold.pdf"
    shape_config = {
        "pdf_file": "/Users/teacher/Desktop/图纸修改/sign.pdf",
        "width": 500,
        # "height": 50,
        "x": 0,
        "y": 0,
    }
    shape_copy(
        input_pdf = input_pdf,
        shape_config = shape_config,
    )
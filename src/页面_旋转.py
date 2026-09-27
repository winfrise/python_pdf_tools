import pymupdf  # 推荐直接使用 pymupdf，兼容旧版 import fitz


def physical_rotate_pdf(input_pdf, output_pdf=None, angle=0):
    """
    对 PDF 文档中的所有页面进行【物理旋转】。

    与 page.set_rotation() 的"逻辑旋转"不同：
    逻辑旋转只是写入页面的 /Rotate 标志，告诉阅读器"显示时转一下"，
    页面真实的内容流与坐标系（MediaBox）并没有改变。
    物理旋转则把每一页的内容真正旋转，并把旋转后的内容重绘到一张
    尺寸为"旋转后尺寸"的新页面上，新页面的 /Rotate 恒为 0，
    即宽高与坐标内容都已真实改变，不再依赖阅读器的旋转显示。

    :param input_pdf: 输入 PDF 文件的路径
    :param output_pdf: 输出 PDF 文件的路径
    :param angle: 旋转角度（正数顺时针，负数逆时针）。
                  支持传入一个整数，或一个接收 page 返回角度的函数。
                  注意：物理旋转通过重绘实现，角度需为 90 的整数倍。
    """
    doc = None
    out = None
    try:
        # 1. 打开源 PDF 文件
        doc = pymupdf.open(input_pdf)
        out = pymupdf.open()  # 新建一个空文档，用来承载物理旋转后的页面

        last_angle = None
        # 2. 遍历每一页，做物理旋转重绘
        for page in doc:
            current_page_angle = angle
            if callable(current_page_angle):
                current_page_angle = current_page_angle(page)

            standard_angle = int(current_page_angle) % 360
            if standard_angle % 90 != 0:
                raise ValueError(
                    f"物理旋转需要 90 的整数倍角度，当前为 {standard_angle} 度"
                )

            # 计算旋转后的页面尺寸：旋转 90/270 时宽高需要交换
            rect = page.rect
            if standard_angle % 180 == 0:
                new_width, new_height = rect.width, rect.height
            else:
                new_width, new_height = rect.height, rect.width

            # 3. 新建一张"物理尺寸已旋转"的页面，并把原页内容旋转重绘进去
            new_page = out.new_page(width=new_width, height=new_height)
            # show_pdf_page 会把源页作为 XObject 旋转后填入指定矩形，
            # 这样内容流被真实旋转，新页面自身 rotation 保持为 0
            new_page.show_pdf_page(new_page.rect, doc, page.number,
                                   rotate= -standard_angle)
            last_angle = standard_angle

        # 4. 保存为新文件（garbage=3 清理冗余对象）
        if output_pdf is None:
            output_pdf = input_pdf.replace(".pdf", "_物理旋转.pdf")
        out.save(output_pdf, garbage=3, deflate=True)
        print(f"✅ 物理旋转成功！已将页面真实旋转 {last_angle} 度，"
              f"并保存至: {output_pdf}")

    except FileNotFoundError:
        print(f"❌ 错误：找不到输入文件 '{input_pdf}'，请检查路径是否正确。")
    except Exception as e:
        print(f"❌ 处理过程中发生未知错误: {e}")
    finally:
        # 确保文件句柄被正确释放
        if out is not None:
            out.close()
        if doc is not None:
            doc.close()


# --- 测试示例 ---
if __name__ == "__main__":

    def rotate_angle_func(page):
        page_num = page.number + 1
        # 第 2~36 页逆时针旋转 90 度（-90），其余不转
        if 2 <= page_num <= 36:
            return -90
        return 0

    input_pdf = "/Users/teacher/Desktop/百度网盘下载/页面分割/物理化学.pdf"

    rotate_angle = rotate_angle_func
    output_pdf = input_pdf.replace(".pdf", "_output_物理旋转.pdf")

    physical_rotate_pdf(
        input_pdf=input_pdf,
        output_pdf=output_pdf,
        angle=rotate_angle,
    )

    # # 逆时针旋转 90 度 (等同于顺时针 270 度)
    # physical_rotate_pdf("input.pdf", "output_ccw.pdf", -90)
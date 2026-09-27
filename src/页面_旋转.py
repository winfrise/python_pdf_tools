import pymupdf  # 推荐直接使用 pymupdf，兼容旧版 import fitz

def rotate_pdf_pages(input_pdf, output_pdf=None, angle = 0):
    """
    旋转 PDF 文档中的所有页面。
    
    :param input_pdf: 输入 PDF 文件的路径
    :param output_pdf: 输出 PDF 文件的路径
    :param angle: 旋转角度（正数顺时针，负数逆时针）
    """
    try:
        # 1. 打开源 PDF 文件
        doc = pymupdf.open(input_pdf)
        
        # 3. 遍历并旋转每一页
        for page in doc:
            current_page_angle = angle
            if callable(current_page_angle):
                current_page_angle = current_page_angle(page)

            standard_angle = int(current_page_angle) % 360


            # 如果原页面已有旋转角度，这里会直接覆盖。
            page.set_rotation(standard_angle) # 新设置旋转角度
            # page.set_rotation((page.rotation + standard_angle) % 360) # 累加旋转
            
            
        # 4. 保存为新文件
        doc.save(output_pdf)
        print(f"✅ 旋转成功！已将页面旋转 {standard_angle} 度，并保存至: {output_pdf}")
        
    except FileNotFoundError:
        print(f"❌ 错误：找不到输入文件 '{input_pdf}'，请检查路径是否正确。")
    except Exception as e:
        print(f"❌ 处理过程中发生未知错误: {e}")
    finally:
        # 确保文件句柄被正确释放
        if 'doc' in locals():
            doc.close()

# --- 测试示例 ---
if __name__ == "__main__":

    def rotate_angle_func(page):
        page_num = page.number + 1
        page_width = page.rect.width
        page_height = page.rect.height
        page_rotation = page.rotation

        if page_num >= 2 and page_num <= 36:
            return -90
        return 0

    input_pdf = "/Users/teacher/Desktop/百度网盘下载/页面分割/物理化学.pdf"

    rotate_angle = rotate_angle_func

    output_pdf = input_pdf.replace('.pdf', f'_output_旋转.pdf')

    # 顺时针旋转 90 度
    rotate_pdf_pages(
        input_pdf = input_pdf, 
        output_pdf = output_pdf,
        angle = rotate_angle,
    )
    
    # # 逆时针旋转 90 度 (等同于顺时针 270 度)
    # rotate_pdf_pages("input.pdf", "output_counterclockwise.pdf", -90)
    
    # # 传入超大角度或负数也能正确处理
    # rotate_pdf_pages("input.pdf", "output_large_angle.pdf", -450) 
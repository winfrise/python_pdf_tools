import os
from spire.pdf.common import *
from spire.pdf import *

def batch_update_pdf_background(input_root_dir, output_root_dir, target_color):
    """
    递归遍历文件夹，批量更新 PDF 背景颜色，并保持原有目录结构存储
    """
    # 1. 确保输出目录存在
    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)
        print(f"✅ 创建输出目录: {output_root_dir}")

    # 2. 递归遍历输入目录
    # os.walk 会自动处理子文件夹的递归
    for root_dir, sub_dirs, files in os.walk(input_root_dir):
        for filename in files:
            # 筛选 PDF 文件
            if filename.lower().endswith(".pdf"):
                
                # --- 获取文件完整路径 ---
                input_file_path = os.path.join(root_dir, filename)
                
                # --- 核心逻辑：计算相对路径，以保持目录结构 ---
                # 计算当前文件相对于输入根目录的路径 (例如: "子文件夹/测试.pdf")
                relative_path = os.path.relpath(input_file_path, input_root_dir)
                # 拼接输出文件的完整路径
                output_file_path = os.path.join(output_root_dir, relative_path)
                
                # --- 确保输出文件的子文件夹存在 ---
                output_sub_dir = os.path.dirname(output_file_path)
                if not os.path.exists(output_sub_dir):
                    os.makedirs(output_sub_dir)

                try:
                    # 3. 使用 Spire.PDF 处理文件
                    pdf_doc = PdfDocument()
                    pdf_doc.LoadFromFile(input_file_path)
                    
                    # 遍历每一页设置背景色
                    for i in range(pdf_doc.Pages.Count):
                        page = pdf_doc.Pages.get_Item(i)
                        page.BackgroundColor = target_color
                        
                        # 设置背景谍有透明度
                        # page.BackgroudOpacity = 0.5
                    
                    # 4. 保存文件
                    pdf_doc.SaveToFile(output_file_path)
                    pdf_doc.Close()
                    
                    print(f"🚀 成功处理: {relative_path}")
                    
                except Exception as e:
                    print(f"❌ 处理失败 {input_file_path}: {e}")

# ================= 配置区域 =================

# 1. 指定输入目录 (请修改为你自己的文件夹路径)
source_folder = r"/Users/teacher/Desktop/inputs"

# 2. 指定输出目录 (处理后的文件将保存在这里)
target_folder = r"/Users/teacher/Desktop/outputs"

# 3. 指定背景颜色 (Spire.PDF 提供多种预设颜色)
#【使用内置颜色】
# 可选颜色示例: Color.get_LightYellow(), Color.get_LightBlue(), Color.get_LightGreen()
bg_color = Color.get_DeepSkyBlue() 

# 【自定义颜色】
# 透明度值:  0-255
# bg_color = Color.FromArgb(100, 0, 153, 255)

# ================= 执行任务 =================

if __name__ == "__main__":
    print("⏳ 开始批量处理...")
    batch_update_pdf_background(source_folder, target_folder, bg_color)
    print("🎉 所有任务完成！")
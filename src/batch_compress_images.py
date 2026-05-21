from PIL import Image
import os

def batch_compress_images(folder_path, quality=75, max_width=None, max_height=None):
    """
    批量压缩文件夹内的图片
    :param folder_path: 输入图片的文件夹路径
    :param quality: 压缩质量 (1-100)
    :param max_width: 最大宽度 (int 或 None)
    :param max_height: 最大高度 (int 或 None)
    """
    if not os.path.exists(folder_path):
        print(f"错误：找不到文件夹 {folder_path}")
        return

    # 创建输出文件夹
    output_folder = os.path.join(folder_path, "compressed")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 支持压缩的图片后缀
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    processed_count = 0

    # 遍历文件夹内的所有文件
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(valid_extensions):
            input_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder, filename)

            # 跳过 compressed 文件夹本身
            if os.path.isdir(input_path):
                continue

            try:
                with Image.open(input_path) as img:
                    # 处理透明通道
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # --- 核心逻辑：判断是否需要缩放尺寸 ---
                    if max_width is not None or max_height is not None:
                        # 如果只传了一个，另一个设为极大的数，让 thumbnail 自动按比例适配
                        target_width = max_width if max_width is not None else 99999
                        target_height = max_height if max_height is not None else 99999
                        
                        # 使用 thumbnail 保持宽高比缩放
                        img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                    
                    # 保存图片
                    img.save(output_path, optimize=True, quality=quality)
                    
                    # 打印处理信息
                    original_size = os.path.getsize(input_path) / 1024  # KB
                    compressed_size = os.path.getsize(output_path) / 1024  # KB
                    print(f"✅ 已压缩: {filename} | 尺寸: {img.size[0]}x{img.size[1]} | 原大小: {original_size:.1f}KB -> 压缩后: {compressed_size:.1f}KB")
                    processed_count += 1

            except Exception as e:
                print(f"❌ 处理失败 {filename}: {e}")

    print(f"\n🎉 批量压缩完成！共处理了 {processed_count} 张图片。")

# --- 使用示例 ---
if __name__ == "__main__":
    # 在这里配置你的文件夹路径和压缩参数
    target_folder = "/Users/teacher/Desktop/未命名文件夹 3/extracted_images"  # 替换成你要处理的文件夹路径
    quality = 75
    max_width = 1240
    max_height = None
    batch_compress_images(target_folder, quality, max_width, max_height)

# 屏幕预览/网页显示	      分辨率(DPI): 72	像素尺寸(宽×高): 595 × 842
# Windows系统/办公软件	 分辨率 (DPI): 96	像素尺寸(宽×高): 794 × 1123
# 普通高质量打印	     分辨率 (DPI):150	像素尺寸(宽×高): 1240 × 1754
# 专业印刷/高清打印	     分辨率(DPI): 300	像素尺寸(宽×高): 2480 × 3508

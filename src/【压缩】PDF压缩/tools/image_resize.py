import os, sys
from PIL import Image
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import batch_process_file_with_callback


def resize_image(input_path, output_path, target_size):
    # 1. 打开图片
    img = Image.open(input_path)
    orig_width, orig_height = img.size

    # 获取目标宽/高
    if callable(target_size):
        target_size = target_size(orig_width, orig_height)

    target_attr = target_size[0]
    target_val = target_size[1]

    if target_attr.lower() == 'width':
        new_width = int(target_val)
        new_height = round(orig_height / orig_width * new_width)
    elif target_attr.lower() == 'height':
        new_height = int(target_val)
        new_width = round(orig_width / orig_height * new_height)
    else:
        print(f'参数无法识别: {target_attr}')

    # 改变图片大小
    new_img = img.resize((new_width, new_height), Image.LANCZOS)

    # 4. 确保输出目录存在并保存图片
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    base_name, ext = os.path.splitext(output_path)
    if ext.lower() == '.jpx':
        output_path = f"{base_name}.jpg"

    new_img.save(output_path, exif=b"")
    print(f"处理完成！已保存至: {output_path}")



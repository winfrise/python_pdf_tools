from PIL import Image
import os

def get_target_size(img_width, img_height):
    """
    图片大小函数
    根据横版/竖版返回：
      - standard_width / standard_height: 标准框尺寸（最终输出尺寸）
      - target_width  / target_height : 同比缩放后的尺寸（用于缩放原图）
    
    横版: 宽度缩放到 1279，标准框宽度=1279，高度=1280
    竖版: 高度缩放到 1280，标准框高度=1280，宽度=1279
    """
    is_landscape = img_width >= img_height

    if is_landscape:
        # 横版：宽度缩放到 1279
        target_width = 1279
        target_height = round(img_height * (1279 / img_width))
        standard_width, standard_height = 1279, 1280
    else:
        # 竖版：高度缩放到 1280
        target_height = 1280
        target_width = round(img_width * (1280 / img_height))
        standard_width, standard_height = 1279, 1280

    return {
        'is_landscape': is_landscape,
        'standard_width': standard_width,
        'standard_height': standard_height,
        'target_width': target_width,
        'target_height': target_height,
    }


def resize_image(input_path, output_path, size_func=get_target_size):
    """
    主函数：改变图片尺寸
    1. 调用 size_func 得到标准框尺寸和同比缩放后的尺寸
    2. 若原图尺寸不符合标准，则同比缩放到 target_width x target_height
    3. 以 standard_width x standard_height 为标准框：
       - 超出 → 居中裁剪
       - 不足 → 白色填充
    """
    img = Image.open(input_path)
    orig_w, orig_h = img.size

    size_info = size_func(orig_w, orig_h)
    is_landscape   = size_info['is_landscape']
    standard_w     = size_info['standard_width']
    standard_h     = size_info['standard_height']
    target_w       = size_info['target_width']
    target_h       = size_info['target_height']

    # 1. 判断原图是否符合标准尺寸（横版看宽，竖版看高）
    if is_landscape:
        already_standard = (orig_w == standard_w)
    else:
        already_standard = (orig_h == standard_h)

    # 2. 不符合则同比缩放
    if not already_standard:
        img = img.resize((target_w, target_h), Image.LANCZOS)

    # 3. 以 standard 尺寸为标准框：裁剪 / 填充
    cur_w, cur_h = img.size
    if cur_w > standard_w or cur_h > standard_h:
        # 超出 → 居中裁剪
        left = (cur_w - standard_w) // 2
        top  = (cur_h - standard_h) // 2
        img = img.crop((left, top, left + standard_w, top + standard_h))
    elif cur_w < standard_w or cur_h < standard_h:
        # 不足 → 白色填充
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGBA')
            canvas = Image.new('RGBA', (standard_w, standard_h), (255, 255, 255, 255))
        else:
            canvas = Image.new('RGB', (standard_w, standard_h), (255, 255, 255))
        paste_x = (standard_w - cur_w) // 2
        paste_y = (standard_h - cur_h) // 2
        mask = img if img.mode == 'RGBA' else None
        canvas.paste(img, (paste_x, paste_y), mask)
        img = canvas

    # 4. 保存
    img.save(output_path)
    print(f"完成: {output_path} | 原 {orig_w}x{orig_h} "
          f"-> 缩放 {target_w}x{target_h} -> 最终 {img.size[0]}x{img.size[1]}")
    return img.size


if __name__ == '__main__':
    input_path = "/Volumes/西数4T外置/百度网盘默认下载/1111111111111111111/竖版.jpg"
    base_name, ext = os.path.splitext(input_path)
    output_path = f"{base_name}_output{ext}"
    resize_image(
        input_path=input_path,
        output_path=output_path,
        size_func= get_target_size
    )
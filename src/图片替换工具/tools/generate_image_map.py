import os
from natsort import natsorted


def generate_image_map(folder_path: str) -> dict:
    """
    通过下划线分割文件名生成 image_map。
    支持格式: page16_img2_IM73.jpeg
    """
    image_map = {}

    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return image_map

    matched_count = 0
    skipped_count = 0

    for filename in os.listdir(folder_path):
        # 只处理常见图片格式
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
            continue

        # 核心逻辑：按 '_' 分割
        parts = filename.split('_')

        # 校验分割后的长度是否足够 (至少需要 pageX, imgY, Name.ext)
        if len(parts) < 3:
            print(f"⚠️ 格式异常跳过: {filename}")
            skipped_count += 1
            continue

        # 提取页码部分 (例如 "page16")
        page_key = parts[0]

        # 提取图片名称部分
        # 注意：如果图片名本身包含下划线（如 IM_73），需要把剩下的部分拼回去
        # parts[2] 是 "IM73.jpeg"，我们需要去掉后缀
        img_name_with_ext = '_'.join(parts[2:])
        img_name = os.path.splitext(img_name_with_ext)[0]  # 去掉 .jpeg 后缀

        abs_path = os.path.abspath(os.path.join(folder_path, filename))

        # 构建嵌套字典
        if page_key not in image_map:
            image_map[page_key] = {}

        image_map[page_key][img_name] = abs_path
        matched_count += 1

    # ====== 自然排序处理 ======
    sorted_image_map = {}
    for page_key in natsorted(image_map.keys()):
        sorted_names = natsorted(image_map[page_key].keys())
        sorted_image_map[page_key] = {
            name: image_map[page_key][name] for name in sorted_names
        }
    # ==========================

    print(f"✅ 成功解析 {matched_count} 张图片")
    if skipped_count > 0:
        print(f"⚠️ 跳过 {skipped_count} 个不符合规则的文件")

    return sorted_image_map


# ====== 测试运行 ======
if __name__ == "__main__":
    folder = r"./images"  # 替换为你的文件夹路径
    result = generate_image_map(folder)

    import json
    print("\n生成的 Map 预览:")
    print(json.dumps({k: result[k] for k in list(result.keys())[:3]}, indent=2, ensure_ascii=False))
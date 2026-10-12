

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import batch_process_file_with_callback

from tools.compress_trimage import trimage_compress
from tools.image_resize import resize_image

if __name__ == "__main__":


    INPUT_PATH = "/Users/teacher/Downloads/03/报告书__提取的图片"
    TARGET_SIZE = ['width', 1200]                  # 例：['height', 300] / ['width', 200] / TARGET_SIZE: Function

    if os.path.isfile(INPUT_PATH):
        base_name, ext = os.path.splitext(INPUT_PATH)
        output_path = f"{base_name}_压缩{ext}"

        # 改变尺寸
        resize_image(
            input_path=INPUT_PATH,
            output_path=output_path,
            target_size=TARGET_SIZE
        )

        # 无损压缩
        trimage_compress(output_path, output_path)

        

    elif os.path.isdir(INPUT_PATH):
        input_dir = INPUT_PATH

        def callback_func(input_file, output_file):
            # 改变尺寸
            resize_image(
                input_path=input_file,
                output_path=output_file,
                target_size=TARGET_SIZE
            )

            # 无损压缩
            trimage_compress(output_file, output_file)

        output_dir = f"{input_dir}_无损压缩"
        batch_process_file_with_callback(
            input_dir=input_dir,
            output_dir=output_dir,
            callback_func=callback_func,
        )
    else:
        print(f"地址无效: {INPUT_PATH}")
import os
import random

def delete_random_files(folder_path, num_files_to_delete):
    # 获取文件夹中的所有文件
    all_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    # 检查文件数量是否足够删除
    if len(all_files) < num_files_to_delete:
        print(f"文件夹中只有 {len(all_files)} 个文件，不足以删除 {num_files_to_delete} 个文件。")
        return
    
    # 随机选择要删除的文件
    files_to_delete = random.sample(all_files, num_files_to_delete)
    
    # 删除选中的文件
    for file_name in files_to_delete:
        file_path = os.path.join(folder_path, file_name)
        os.remove(file_path)
        print(f"已删除文件: {file_path}")

# 示例用法
folder_path = '/home/ubuntu/PRP_cnf'  # 替换为你的文件夹路径
num_files_to_delete = 144-80
delete_random_files(folder_path, num_files_to_delete)

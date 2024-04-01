import os
import json

def find_highest_score_texts(directory_path):
    highest_score = float('-inf')
    texts_with_highest_score = []

    # 遍历目录下的所有文件
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):  # 确保只处理JSON文件
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as file:
                try:
                    data = json.load(file)
                    score = data.get("score")
                    # 忽略score为None的情况并更新最高分数和对应的文本
                    if score is not None:
                        if score > highest_score:
                            highest_score = score
                            texts_with_highest_score = [data.get("function")]
                        elif score == highest_score:
                            texts_with_highest_score.append(data.get("function"))
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file: {file_path}")

    return highest_score, texts_with_highest_score

directory_path = '/mnt/data/linyanqiu/funsearch_vm_schecduling/logs/funsearch_local_llm/samples'
highest_score, texts = find_highest_score_texts(directory_path)

print("Highest Score:", highest_score)
# print("Texts with Highest Score:", texts)

# for tx in texts:
print("-------------------------")
# print(texts[0])
print("-------------------------")
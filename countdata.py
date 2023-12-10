import json

# 读取JSON文件
with open('routes.json', encoding='utf-8') as file:
    data = json.load(file)

# 检查数据类型并计算条目数
if isinstance(data, list):
    # 如果数据是一个列表，直接计算长度
    count = len(data)

print("Number of data entries:", count)
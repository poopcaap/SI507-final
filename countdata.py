import json
#this is for counting length of json
with open('routes.json', encoding='utf-8') as file:
    data = json.load(file)

if isinstance(data, list):
    count = len(data)

print("Number of data entries:", count)

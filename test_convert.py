import csv
import json

def csv_to_json_grouped(csv_file_path, json_file_path):
    # 初始化存储作者及其论文的字典
    author_papers = {}

    # 读取CSV文件
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            author_name = row['author_name']
            paper_title = row['paper_title']

            # 如果作者不存在于字典中，添加作者并初始化其论文列表
            if author_name not in author_papers:
                author_papers[author_name] = []

            # 将论文标题添加到作者的论文列表中
            author_papers[author_name].append(paper_title)

    # 转换为目标JSON格式
    json_data = [
        {
            "author_name": author_name,
            "papers": papers
        }
        for author_name, papers in author_papers.items()
    ]

    # 将结果写入JSON文件
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

# 示例使用
csv_file_path = r'C:\Users\ethan\PycharmProjects\university_ranking_static\data\author_papers.csv'  # 你的CSV文件路径
json_file_path = r'C:\Users\ethan\PycharmProjects\university_ranking_static\rankings\static\rankings\data\authors_papers.json'  # 输出的JSON文件路径

csv_to_json_grouped(csv_file_path, json_file_path)

import os
import csv
import json
import pandas as pd

# 定义文件路径
input_folder = 'data/'  # CSV 文件存放目录
output_folder = 'rankings/static/rankings/data/'  # JSON 文件存放目录

# 确保输出目录存在
os.makedirs(output_folder, exist_ok=True)

# 定义需要转换的单表 CSV 文件
csv_files = [
    'authors.csv',
    'papers.csv',
    'universities.csv',
    'authors_universities.csv',
    'paper_authors.csv',
    'conferences.csv'
]

# 转换单表 CSV 文件为 JSON 文件
for csv_file in csv_files:
    input_path = os.path.join(input_folder, csv_file)
    output_path = os.path.join(output_folder, csv_file.replace('.csv', '.json'))

    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        data = [row for row in reader]

    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)

    print(f"Converted {csv_file} to {output_path}")

# 加载 CSV 数据到 DataFrame
authors = pd.read_csv(os.path.join(input_folder, 'authors.csv'))
papers = pd.read_csv(os.path.join(input_folder, 'papers.csv'))
universities = pd.read_csv(os.path.join(input_folder, 'universities.csv'))
authors_universities = pd.read_csv(os.path.join(input_folder, 'authors_universities.csv'))
paper_authors = pd.read_csv(os.path.join(input_folder, 'paper_authors.csv'))

# === 生成合并数据 ===

# 1. author_paper_university.json
author_paper_university = (
    paper_authors
    .merge(authors, left_on='author_name', right_on='name')
    .merge(authors_universities, on='author_name')
    .merge(universities, left_on='university_name', right_on='name')
    .merge(papers, left_on='paper_title', right_on='title')
)
author_paper_university = author_paper_university[['author_name', 'paper_title', 'university_name', 'conference_name']]
author_paper_university.to_json(
    os.path.join(output_folder, 'author_paper_university.json'),
    orient='records', force_ascii=False, indent=4
)
print("Generated author_paper_university.json")

# 2. university_paper_authors.json
university_paper_authors = author_paper_university.groupby('university_name').agg({
    'author_name': lambda x: list(x.unique()),
    'paper_title': lambda x: list(x.unique())
}).reset_index()
university_paper_authors.to_json(
    os.path.join(output_folder, 'university_paper_authors.json'),
    orient='records', force_ascii=False, indent=4
)
print("Generated university_paper_authors.json")

# 3. conference_papers.json
conference_papers = papers.groupby('conference_name')['title'].apply(list).reset_index()
conference_papers.columns = ['conference_name', 'papers']
conference_papers.to_json(
    os.path.join(output_folder, 'conference_papers.json'),
    orient='records', force_ascii=False, indent=4
)
print("Generated conference_papers.json")

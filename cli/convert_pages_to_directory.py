#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 pages.json 转换为目录结构的 Markdown 文档
使用方法：
jq -r '.[] | {relativePath, content, frontmatter}' pages.json | python3 convert_pages_to_directory.py

或者直接运行：
python3 convert_pages_to_directory.py pages.json output_directory
"""

import json
import os
import sys
from pathlib import Path
import argparse

def create_frontmatter_yaml(frontmatter):
    """将 frontmatter 转换为 YAML 格式"""
    if not frontmatter:
        return ""

    yaml_lines = ["---"]
    for key, value in frontmatter.items():
        if value is not None:
            # 对于字符串值，添加引号
            if isinstance(value, str):
                yaml_lines.append(f"{key}: \"{value}\"")
            else:
                yaml_lines.append(f"{key}: {value}")
    yaml_lines.append("---")
    yaml_lines.append("")  # 添加空行
    return "\n".join(yaml_lines)

def process_page(page_data, output_dir):
    """处理单个页面"""
    relative_path = page_data.get('relativePath', '')
    content = page_data.get('content', '')
    frontmatter = page_data.get('frontmatter', {})

    if not relative_path:
        print(f"警告: 跳过没有相对路径的页面", file=sys.stderr)
        return

    # 构建输出文件路径
    output_path = Path(output_dir) / relative_path

    # 确保目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 生成 frontmatter YAML
    frontmatter_yaml = create_frontmatter_yaml(frontmatter)

    # 组合完整内容
    full_content = frontmatter_yaml + content

    # 写入文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        print(f"已创建: {output_path}")
    except Exception as e:
        print(f"错误: 写入文件失败 {output_path} - {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='将 pages.json 转换为目录结构的 Markdown 文档')
    parser.add_argument('--input', '-i', help='输入的 pages.json 文件路径 (如果不指定则从 stdin 读取)')
    parser.add_argument('--output', '-o', default='./output_docs',
                       help='输出目录路径 (默认: ./output_docs)')

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"输出目录: {output_dir.absolute()}")

    # 检查是否有输入文件参数
    if args.input:
        # 从文件读取
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"错误: 输入文件不存在 {input_path}", file=sys.stderr)
            sys.exit(1)

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                pages_data = json.load(f)

            for page_data in pages_data:
                process_page(page_data, output_dir)

        except json.JSONDecodeError as e:
            print(f"错误: JSON 解析失败 - {e}", file=sys.stderr)
            sys.exit(1)

    else:
        # 从标准输入读取 (用于管道操作)
        print("从标准输入读取数据...", file=sys.stderr)
        try:
            for line in sys.stdin:
                line = line.strip()
                if line:
                    try:
                        page_data = json.loads(line)
                        process_page(page_data, output_dir)
                    except json.JSONDecodeError as e:
                        print(f"警告: 跳过无效的 JSON 行 - {e}", file=sys.stderr)
                        continue
        except KeyboardInterrupt:
            print("\n用户中断", file=sys.stderr)
            sys.exit(1)

    print(f"\n转换完成！文档已保存到: {output_dir.absolute()}")

if __name__ == '__main__':
    main()

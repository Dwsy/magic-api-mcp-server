# Pages.json 转 Markdown 工具使用指南

## 快速开始

```bash
# 使用封装脚本（推荐）
./convert_pages.sh

# 或手动执行
jq -c '.[] | {relativePath, content, frontmatter}' pages.json | python3 convert_pages_to_directory.py --output output_dir
```

## 文件说明

- `convert_pages.sh`: 封装脚本，自动处理转换流程
- `convert_pages_to_directory.py`: Python 核心处理脚本
- `README.md`: 详细使用说明

## 依赖

- jq (JSON 处理)
- Python 3

## 输出

将生成完整的目录结构，每个 .md 文件包含 frontmatter 和内容。

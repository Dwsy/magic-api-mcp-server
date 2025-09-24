#!/bin/bash

# 将 pages.json 转换为目录结构的 Markdown 文档
# 使用方法:
# ./convert_pages.sh [input_file] [output_directory]
#
# 参数:
#   input_file: pages.json 文件路径 (默认: ./web-docs/pages.json)
#   output_directory: 输出目录路径 (默认: ./converted_docs)
#
# 示例:
# ./convert_pages.sh
# ./convert_pages.sh ./pages.json ./docs
# ./convert_pages.sh /path/to/pages.json /path/to/output

set -e  # 遇到错误立即退出

# 默认参数
INPUT_FILE="${1:-./web-docs/pages.json}"
OUTPUT_DIR="${2:-./converted_docs}"

# 检查输入文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
    echo "错误: 输入文件不存在: $INPUT_FILE"
    echo "使用方法: $0 [input_file] [output_directory]"
    exit 1
fi

# 检查 jq 是否安装
if ! command -v jq &> /dev/null; then
    echo "错误: 需要安装 jq 工具"
    echo "安装方法: brew install jq (macOS) 或 apt install jq (Ubuntu)"
    exit 1
fi

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要安装 Python 3"
    exit 1
fi

echo "开始转换..."
echo "输入文件: $INPUT_FILE"
echo "输出目录: $OUTPUT_DIR"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 执行转换
jq -c '.[] | {relativePath, content, frontmatter}' "$INPUT_FILE" | \
python3 convert_pages_to_directory.py --output "$OUTPUT_DIR"

echo ""
echo "转换完成！"
echo "文档已保存到: $(cd "$OUTPUT_DIR" && pwd)"

# 显示统计信息
FILE_COUNT=$(find "$OUTPUT_DIR" -name "*.md" | wc -l)
echo "共生成 $FILE_COUNT 个 Markdown 文件"

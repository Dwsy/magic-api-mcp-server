"""Web文档知识库模块 - 用于搜索web-docs目录下的Markdown文档。

这个模块提供搜索web-docs目录下Markdown文档的功能。
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

def read_md_file_content(file_path: str) -> Dict[str, Any]:
    """读取markdown文件的内容，解析frontmatter和正文。
    
    Args:
        file_path: markdown文件路径
        
    Returns:
        包含文件信息的字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析frontmatter（如果有）
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        frontmatter = {}
        body_content = content
        
        if frontmatter_match:
            frontmatter_str = frontmatter_match.group(1)
            body_content = frontmatter_match.group(2)
            
            # 简单解析frontmatter
            for line in frontmatter_str.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    frontmatter[key] = value
        
        # 尝试从文件路径推断分类
        relative_path = os.path.relpath(file_path)
        path_parts = relative_path.split(os.sep)
        
        # 提取目录名作为分类信息
        category = ""
        subcategory = ""
        if len(path_parts) >= 2:
            # 移除数字前缀，保留有意义的分类名
            category = re.sub(r'^\d+\.', '', path_parts[1]).strip()
        if len(path_parts) >= 3:
            subcategory = re.sub(r'^\d+\.', '', path_parts[2]).strip()
        
        return {
            "title": frontmatter.get("title", ""),
            "date": frontmatter.get("date", ""),
            "permalink": frontmatter.get("permalink", ""),
            "content": body_content,
            "raw_content": content,
            "file_path": file_path,
            "category": category,
            "subcategory": subcategory,
            "relative_path": relative_path
        }
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return {
            "title": "",
            "date": "",
            "permalink": "",
            "content": "",
            "raw_content": "",
            "file_path": file_path,
            "category": "",
            "subcategory": "",
            "relative_path": ""
        }


def load_all_web_docs(base_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """加载web-docs目录下的所有markdown文档。
    
    Args:
        base_path: web-docs目录的基础路径
        
    Returns:
        包含所有文档信息的列表
    """
    if base_path is None:
        # First, try the development/relative path approach
        current_dir = Path(__file__).parent
        dev_path = current_dir.parent.parent / "web-docs"
        
        if os.path.exists(dev_path):
            base_path = str(dev_path)
        else:
            # For installation, we need to handle the package data differently
            # The MANIFEST.in and pyproject.toml should ensure the files are included
            # Let's try to find the web-docs relative to the package
            import magicapi_tools
            package_dir = Path(magicapi_tools.__file__).parent
            installed_path = package_dir / "web-docs"
            
            if os.path.exists(installed_path):
                base_path = str(installed_path)
            else:
                # If both approaches fail, return empty list
                return []
    
    if isinstance(base_path, Path):
        base_path = str(base_path)
    
    docs = []
    
    # Walk through the directory to find all markdown files
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                doc_info = read_md_file_content(file_path)
                docs.append(doc_info)
    
    return docs


def search_web_docs(keyword: str, base_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """在web-docs的markdown文档中搜索关键词。
    
    Args:
        keyword: 搜索关键词
        base_path: web-docs目录的基础路径
        
    Returns:
        匹配的文档列表
    """
    docs = load_all_web_docs(base_path)
    results = []
    
    keyword_lower = keyword.lower()
    
    for doc in docs:
        # 在标题、分类、子分类和内容中搜索关键词
        title_match = keyword_lower in doc.get("title", "").lower()
        category_match = keyword_lower in doc.get("category", "").lower()
        subcategory_match = keyword_lower in doc.get("subcategory", "").lower()
        content_match = keyword_lower in doc.get("content", "").lower()
        
        if title_match or category_match or subcategory_match or content_match:
            result = {
                "category": "web_docs",
                "topic": doc.get("title", "Untitled"),
                "title": doc.get("title", ""),
                "description": doc.get("category", "") + " / " + doc.get("subcategory", ""),
                "content_preview": doc.get("content", "")[:200] + "..." if len(doc.get("content", "")) > 200 else doc.get("content", ""),
                "file_path": doc.get("relative_path", ""),
                "type": "文档",
                "full_content": doc.get("content", ""),
                "permalink": doc.get("permalink", ""),
                "date": doc.get("date", "")
            }
            results.append(result)
    
    return results


# 预加载web-docs内容以提高搜索性能
WEB_DOCS_KNOWLEDGE = load_all_web_docs()


def get_web_docs_knowledge() -> List[Dict[str, Any]]:
    """获取所有web-docs知识。
    
    Returns:
        web-docs知识列表
    """
    return WEB_DOCS_KNOWLEDGE


def search_web_docs_by_keyword(keyword: str) -> List[Dict[str, Any]]:
    """根据关键词搜索web-docs内容。
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        搜索结果列表
    """
    return search_web_docs(keyword)
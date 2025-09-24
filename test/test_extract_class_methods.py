#!/usr/bin/env python3
"""extract_class_methods.py 工具的测试脚本。"""

import json
import unittest
from unittest.mock import Mock, patch, mock_open
import sys
import os
import requests

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract_class_methods import (
    MagicAPIClassExplorerError,
    MagicAPIClassClient,
    MagicAPIClassExplorer,
    parse_args,
    validate_args,
    main
)


class TestMagicAPIClassClient(unittest.TestCase):
    """测试 MagicAPIClassClient 类。"""

    def setUp(self):
        """设置测试环境。"""
        self.client = MagicAPIClassClient("http://test.example.com", timeout=5)

    @patch('requests.Session.post')
    def test_get_all_classes_success(self, mock_post):
        """测试成功获取所有类信息。"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "classes": {"TestClass": {}},
                "extensions": {"TestExt": {}},
                "functions": {"testFunc": {}}
            }
        }
        mock_post.return_value = mock_response

        result = self.client.get_all_classes()

        self.assertIn("classes", result)
        self.assertIn("extensions", result)
        self.assertIn("functions", result)
        mock_post.assert_called_once()

    @patch('requests.Session.post')
    def test_get_all_classes_failure(self, mock_post):
        """测试获取类信息失败的情况。"""
        mock_post.side_effect = requests.RequestException("Connection failed")

        with self.assertRaises(MagicAPIClassExplorerError) as context:
            self.client.get_all_classes()
        self.assertIn("获取类信息失败", str(context.exception))

    @patch('requests.Session.post')
    def test_get_class_details_success(self, mock_post):
        """测试成功获取类详情。"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "success": True,
            "data": [{"methods": ["testMethod"]}]
        }
        mock_post.return_value = mock_response

        result = self.client.get_class_details("TestClass")

        self.assertEqual(len(result), 1)
        self.assertIn("methods", result[0])


class TestMagicAPIClassExplorer(unittest.TestCase):
    """测试 MagicAPIClassExplorer 类。"""

    def setUp(self):
        """设置测试环境。"""
        self.mock_client = Mock(spec=MagicAPIClassClient)
        self.explorer = MagicAPIClassExplorer(self.mock_client)

    def test_format_method_info_dict(self):
        """测试格式化方法信息（字典格式）。"""
        method = {
            "name": "testMethod",
            "returnType": "String",
            "parameters": [
                {"type": "String", "name": "param1"},
                {"type": "int", "name": "param2"}
            ]
        }

        result = self.explorer._format_method_info(method)
        expected = "String testMethod(String param1, int param2)"
        self.assertEqual(result, expected)

    def test_format_method_info_string(self):
        """测试格式化方法信息（字符串格式）。"""
        method = "testMethod"
        result = self.explorer._format_method_info(method)
        self.assertEqual(result, "testMethod")

    def test_has_method_true(self):
        """测试检查类是否包含方法（包含）。"""
        class_details = [{
            "methods": [
                {"name": "testMethod", "returnType": "void", "parameters": []}
            ]
        }]

        result = self.explorer._has_method(class_details, "test")
        self.assertTrue(result)

    def test_has_method_false(self):
        """测试检查类是否包含方法（不包含）。"""
        class_details = [{
            "methods": [
                {"name": "otherMethod", "returnType": "void", "parameters": []}
            ]
        }]

        result = self.explorer._has_method(class_details, "test")
        self.assertFalse(result)


class TestArgumentParsing(unittest.TestCase):
    """测试命令行参数解析。"""

    @patch('sys.argv', ['extract_class_methods.py', '--list'])
    def test_parse_args_list(self):
        """测试解析 --list 参数。"""
        args = parse_args()
        self.assertTrue(args.list)
        self.assertFalse(args.search)
        self.assertFalse(args.class_name)
        self.assertFalse(args.method)

    @patch('sys.argv', ['extract_class_methods.py', '--search', 'test'])
    def test_parse_args_search(self):
        """测试解析 --search 参数。"""
        args = parse_args()
        self.assertEqual(args.search, 'test')

    @patch('sys.argv', ['extract_class_methods.py', '--class', 'TestClass'])
    def test_parse_args_class(self):
        """测试解析 --class 参数。"""
        args = parse_args()
        self.assertEqual(args.class_name, 'TestClass')

    @patch('sys.argv', ['extract_class_methods.py', '--method', 'testMethod'])
    def test_parse_args_method(self):
        """测试解析 --method 参数。"""
        args = parse_args()
        self.assertEqual(args.method, 'testMethod')

    @patch('sys.argv', ['extract_class_methods.py', '--list'])
    def test_validate_args_valid(self):
        """测试有效的参数验证。"""
        args = parse_args()
        # 不应该抛出异常
        validate_args(args)

    @patch('sys.argv', ['extract_class_methods.py', '--list', '--search', 'test'])
    def test_validate_args_invalid_multiple(self):
        """测试无效的参数验证（多个操作）。"""
        args = parse_args()
        with self.assertRaises(MagicAPIClassExplorerError):
            validate_args(args)

    def test_validate_args_invalid_none(self):
        """测试无效的参数验证（无操作）。"""
        # 创建一个没有操作的模拟参数对象
        class MockArgs:
            def __init__(self):
                self.list = False
                self.search = None
                self.class_name = None
                self.method = None

        args = MockArgs()
        with self.assertRaises(MagicAPIClassExplorerError):
            validate_args(args)


class TestMainFunction(unittest.TestCase):
    """测试主函数。"""

    @patch('sys.stdout', new_callable=lambda: open(os.devnull, 'w'))
    @patch('extract_class_methods.MagicAPIClassExplorer')
    @patch('extract_class_methods.MagicAPIClassClient')
    def test_main_list(self, mock_client_class, mock_explorer_class, mock_stdout):
        """测试主函数的 --list 功能。"""
        # 模拟命令行参数
        with patch('sys.argv', ['extract_class_methods.py', '--list']):
            # 模拟类实例
            mock_client = Mock()
            mock_explorer = Mock()
            mock_client_class.return_value = mock_client
            mock_explorer_class.return_value = mock_explorer

            # 调用主函数
            try:
                main()
            except SystemExit:
                pass  # 正常退出

            # 验证调用
            mock_explorer.list_all_classes.assert_called_once_with(False)


if __name__ == '__main__':
    unittest.main()

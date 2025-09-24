#!/usr/bin/env python3
"""
测试Docker容器运行Magic-API MCP Server
"""

import subprocess
import sys
import time
import signal

def test_docker_stdio():
    """测试Docker容器stdio模式"""
    print("🧪 测试Docker容器stdio模式...")

    cmd = [
        'docker', 'run', '--rm', '--entrypoint', 'uvx',
        'magic-api-mcp-server:uvx',
        'magic-api-mcp-server', '--help'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and 'usage: magic-api-mcp-server' in result.stdout:
            print("✅ Docker容器stdio模式测试通过")
            return True
        else:
            print(f"❌ Docker容器stdio模式测试失败")
            print(f"stdout: {result.stdout[:200]}...")
            print(f"stderr: {result.stderr[:200]}...")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Docker容器stdio模式测试超时")
        return False
    except Exception as e:
        print(f"❌ Docker容器stdio模式测试异常: {e}")
        return False

def test_docker_http():
    """测试Docker容器HTTP模式启动"""
    print("🧪 测试Docker容器HTTP模式启动...")

    cmd = [
        'docker', 'run', '-d', '--name', 'test-mcp-server',
        '-p', '8006:8000', '--entrypoint', 'uvx',
        'magic-api-mcp-server:uvx',
        'magic-api-mcp-server', '--transport', 'http', '--port', '8000'
    ]

    cleanup_cmd = ['docker', 'stop', 'test-mcp-server']

    try:
        # 启动容器
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"❌ Docker容器HTTP模式启动失败: {result.stderr}")
            return False

        container_id = result.stdout.strip()
        print(f"✅ 容器启动成功，ID: {container_id}")

        # 等待几秒让服务启动
        time.sleep(5)

        # 检查容器是否还在运行
        check_cmd = ['docker', 'ps', '--filter', f'id={container_id}', '--format', '{{.Status}}']
        check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)

        if 'Up' in check_result.stdout:
            print("✅ Docker容器HTTP模式运行正常")

            # 清理容器
            subprocess.run(cleanup_cmd, capture_output=True)
            return True
        else:
            print("❌ Docker容器HTTP模式未能正常运行")

            # 查看日志
            log_cmd = ['docker', 'logs', container_id]
            log_result = subprocess.run(log_cmd, capture_output=True, text=True)
            print(f"容器日志: {log_result.stdout[-500:]}...")

            subprocess.run(cleanup_cmd, capture_output=True)
            return False

    except subprocess.TimeoutExpired:
        print("❌ Docker容器HTTP模式测试超时")
        subprocess.run(cleanup_cmd, capture_output=True)
        return False
    except Exception as e:
        print(f"❌ Docker容器HTTP模式测试异常: {e}")
        subprocess.run(cleanup_cmd, capture_output=True)
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试Docker容器运行")
    print("=" * 50)

    tests = [
        ("stdio模式", test_docker_stdio),
        ("HTTP模式", test_docker_http),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n🔍 执行测试: {test_name}")
        success = test_func()
        results[test_name] = success

    # 输出总结
    print("\n" + "=" * 50)
    print("📊 Docker测试结果总结")

    successful = 0
    for test_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}")
        if success:
            successful += 1

    print(f"\n🎯 总体结果: {successful}/{len(tests)} 个测试通过")

    if successful == len(tests):
        print("🎉 所有Docker测试都运行正常！")
        return 0
    else:
        print("⚠️ 部分Docker测试失败，请检查相关配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())

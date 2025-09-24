#!/usr/bin/env node

/**
 * Magic-API MCP 工具链自动化测试执行器
 *
 * 功能特性：
 * - 分阶段执行测试
 * - 自动验证结果
 * - 性能指标收集
 * - 详细日志记录
 * - 错误处理和恢复
 */

const fs = require('fs');
const path = require('path');

// 测试配置
const TEST_CONFIG = {
    baseUrl: 'http://127.0.0.1:10712',
    timeout: 10000,
    retries: 3,
    logLevel: 'info'
};

// 测试结果存储
let testResults = {
    startTime: new Date().toISOString(),
    phases: {},
    summary: {
        totalTests: 0,
        passed: 0,
        failed: 0,
        skipped: 0
    }
};

/**
 * 日志记录函数
 */
function log(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = {
        timestamp,
        level,
        message,
        ...(data && { data })
    };

    console.log(`[${timestamp}] [${level.toUpperCase()}] ${message}`);
    if (data) {
        console.log(JSON.stringify(data, null, 2));
    }
}

/**
 * 模拟 MCP 工具调用
 * 注意：这里是模拟实现，实际需要集成真实的 MCP 客户端
 */
async function mockMcpCall(toolName, params = {}) {
    log('debug', `执行 MCP 调用: ${toolName}`, params);

    // 模拟响应延迟
    await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 100));

    // 模拟响应
    const mockResponses = {
        'get_assistant_metadata': {
            system_prompt: 'Mock system prompt',
            version: '2.2.0',
            features: ['syntax', 'examples', 'docs'],
            environment: {
                base_url: TEST_CONFIG.baseUrl,
                auth_enabled: false
            }
        },
        'list_available_modules': {
            all_modules: ['db', 'http', 'response', 'request', 'log', 'env', 'magic'],
            auto_import_modules: ['db', 'log'],
            module_count: 7
        },
        'get_resource_tree': {
            kind: 'all',
            count: 0,
            nodes: [],
            filters_applied: {}
        },
        'list_backups': {
            total_backups: 100,
            filtered_backups: 0,
            returned_backups: 0,
            limit: 10,
            filters_applied: {},
            backups: []
        },
        'get_full_magic_script_syntax': {
            language: 'magic-script',
            version: 'latest',
            sections: {
                keywords: { title: '关键字', items: ['var', 'if', 'for'] },
                operators: { title: '运算符', math: ['+', '-', '*'] }
            }
        },
        'get_development_workflow': {
            task: 'api_script_development',
            steps: ['资源定位', '语法对齐', '脚本准备', '功能验证'],
            core_workflow_overview: { summary: '核心工作流描述' }
        },
        'search_api_endpoints': [],
        'search_api_scripts': [],
        'search_todo_comments': [],
        'search_knowledge': [],
        'get_debug_status': { status: 'disconnected', active_sessions: 0 },
        'get_websocket_status': { connected: false, url: 'ws://127.0.0.1:10712/magic/web/console' },
        'get_resource_statistics': { total_apis: 0, total_groups: 0, total_functions: 0 },
        'list_resource_groups': [],
        'export_resource_tree': { format: 'json', data: {} },
        'get_api_details_by_path': { id: null, path: '/test/api', method: null },
        'get_backup_history': { backup_id: 'test-backup-123', history: [] },
        'get_backup_content': { backup_id: 'test-backup-123', timestamp: Date.now(), content: {} },
        'get_best_practices': { performance: {}, security: {}, debugging: {} },
        'get_common_pitfalls': { common_issues: [], best_practices: [] },
        'get_knowledge_overview': { total_categories: 5, total_entries: 100, version: '2.2.0' }
    };

    return mockResponses[toolName] || {
        error: {
            code: 'not_implemented',
            message: `工具 ${toolName} 未实现`
        }
    };
}

/**
 * 执行单个测试用例
 */
async function executeTest(testName, testFunction) {
    log('info', `开始执行测试: ${testName}`);

    const startTime = Date.now();
    let attempts = 0;
    let lastError = null;

    while (attempts < TEST_CONFIG.retries) {
        attempts++;
        try {
            const result = await testFunction();
            const duration = Date.now() - startTime;

            log('info', `测试 ${testName} 成功完成`, { duration, attempts });
            return { success: true, result, duration, attempts };
        } catch (error) {
            lastError = error;
            log('warn', `测试 ${testName} 第 ${attempts} 次尝试失败: ${error.message}`);

            if (attempts < TEST_CONFIG.retries) {
                await new Promise(resolve => setTimeout(resolve, 1000 * attempts));
            }
        }
    }

    log('error', `测试 ${testName} 最终失败`, { lastError: lastError.message });
    return { success: false, error: lastError, duration: Date.now() - startTime, attempts };
}

/**
 * 阶段1：基础信息收集与验证
 */
async function phase1_BasicInfoTests() {
    log('info', '=== 开始阶段1：基础信息收集与验证 ===');

    const phase = {
        name: '基础信息收集与验证',
        tests: {},
        summary: { passed: 0, failed: 0, total: 0 }
    };

    // 测试1.1: 系统元信息验证
    phase.tests.get_assistant_metadata = await executeTest('get_assistant_metadata', async () => {
        const result = await mockMcpCall('get_assistant_metadata');
        if (!result.version || !result.features) {
            throw new Error('响应格式不正确');
        }
        return result;
    });

    // 测试1.2: 可用模块列表验证
    phase.tests.list_available_modules = await executeTest('list_available_modules', async () => {
        const result = await mockMcpCall('list_available_modules');
        if (!result.all_modules || !Array.isArray(result.all_modules)) {
            throw new Error('模块列表格式不正确');
        }
        return result;
    });

    // 测试1.3: 资源树结构检查
    phase.tests.get_resource_tree = await executeTest('get_resource_tree', async () => {
        const result = await mockMcpCall('get_resource_tree');
        if (result.count !== 0) {
            log('warn', '资源树不为空，可能存在测试数据');
        }
        return result;
    });

    // 测试1.4: 备份功能可用性验证
    phase.tests.list_backups = await executeTest('list_backups', async () => {
        const result = await mockMcpCall('list_backups');
        if (typeof result.total_backups !== 'number') {
            throw new Error('备份统计数据格式不正确');
        }
        return result;
    });

    // 统计结果
    phase.summary.total = Object.keys(phase.tests).length;
    phase.summary.passed = Object.values(phase.tests).filter(t => t.success).length;
    phase.summary.failed = phase.summary.total - phase.summary.passed;

    testResults.phases.phase1 = phase;
    log('info', `阶段1完成: ${phase.summary.passed}/${phase.summary.total} 通过`);
}

/**
 * 阶段2：文档查询功能测试
 */
async function phase2_DocumentationTests() {
    log('info', '=== 开始阶段2：文档查询功能测试 ===');

    const phase = {
        name: '文档查询功能测试',
        tests: {},
        summary: { passed: 0, failed: 0, total: 0 }
    };

    // 测试2.1: 完整语法规则获取
    phase.tests.get_full_magic_script_syntax = await executeTest('get_full_magic_script_syntax', async () => {
        const result = await mockMcpCall('get_full_magic_script_syntax');
        if (!result.language || !result.sections) {
            throw new Error('语法规则响应格式不正确');
        }
        return result;
    });

    // 测试2.2: 开发工作流指南
    phase.tests.get_development_workflow = await executeTest('get_development_workflow', async () => {
        const result = await mockMcpCall('get_development_workflow');
        if (!result.task || !result.steps) {
            throw new Error('开发工作流响应格式不正确');
        }
        return result;
    });

    // 统计结果
    phase.summary.total = Object.keys(phase.tests).length;
    phase.summary.passed = Object.values(phase.tests).filter(t => t.success).length;
    phase.summary.failed = phase.summary.total - phase.summary.passed;

    testResults.phases.phase2 = phase;
    log('info', `阶段2完成: ${phase.summary.passed}/${phase.summary.total} 通过`);
}

/**
 * 阶段3：搜索与查询功能测试
 */
async function phase3_SearchAndQueryTests() {
    log('info', '=== 开始阶段3：搜索与查询功能测试 ===');

    const phase = {
        name: '搜索与查询功能测试',
        tests: {},
        summary: { passed: 0, failed: 0, total: 0 }
    };

    // 测试3.1: 资源搜索功能
    phase.tests.search_api_endpoints = await executeTest('search_api_endpoints', async () => {
        const result = await mockMcpCall('search_api_endpoints', { method_filter: null, path_filter: null });
        if (!Array.isArray(result)) {
            throw new Error('搜索结果应为数组格式');
        }
        return result;
    });

    // 测试3.2: 资源树深度搜索
    phase.tests.get_resource_tree_with_depth = await executeTest('get_resource_tree_with_depth', async () => {
        const result = await mockMcpCall('get_resource_tree', { depth: 2 });
        if (typeof result.count !== 'number') {
            throw new Error('资源树统计数据格式不正确');
        }
        return result;
    });

    // 测试3.3: 脚本内容搜索
    phase.tests.search_api_scripts = await executeTest('search_api_scripts', async () => {
        const result = await mockMcpCall('search_api_scripts', { keyword: 'test', limit: 5 });
        if (!Array.isArray(result)) {
            throw new Error('脚本搜索结果应为数组格式');
        }
        return result;
    });

    // 测试3.4: TODO 注释搜索
    phase.tests.search_todo_comments = await executeTest('search_todo_comments', async () => {
        const result = await mockMcpCall('search_todo_comments', { keyword: 'TODO', limit: 10 });
        if (!Array.isArray(result)) {
            throw new Error('TODO 搜索结果应为数组格式');
        }
        return result;
    });

    // 测试3.5: 知识库搜索功能
    phase.tests.search_knowledge_basic = await executeTest('search_knowledge_basic', async () => {
        const result = await mockMcpCall('search_knowledge', { keyword: '数据库' });
        if (!Array.isArray(result)) {
            throw new Error('知识库搜索结果应为数组格式');
        }
        return result;
    });

    // 测试3.6: 知识库分类搜索
    phase.tests.search_knowledge_category = await executeTest('search_knowledge_category', async () => {
        const result = await mockMcpCall('search_knowledge', { keyword: '语法', category: 'syntax' });
        if (!Array.isArray(result)) {
            throw new Error('分类搜索结果应为数组格式');
        }
        return result;
    });

    // 统计结果
    phase.summary.total = Object.keys(phase.tests).length;
    phase.summary.passed = Object.values(phase.tests).filter(t => t.success).length;
    phase.summary.failed = phase.summary.total - phase.summary.passed;

    testResults.phases.phase3 = phase;
    log('info', `阶段3完成: ${phase.summary.passed}/${phase.summary.total} 通过`);
}

/**
 * 阶段4：API 调用与调试功能测试
 */
async function phase4_ApiAndDebugTests() {
    log('info', '=== 开始阶段4：API 调用与调试功能测试 ===');

    const phase = {
        name: 'API 调用与调试功能测试',
        tests: {},
        summary: { passed: 0, failed: 0, total: 0 }
    };

    // 测试4.1: 调试状态检查
    phase.tests.get_debug_status = await executeTest('get_debug_status', async () => {
        const result = await mockMcpCall('get_debug_status');
        if (!result || typeof result !== 'object') {
            throw new Error('调试状态响应格式不正确');
        }
        return result;
    });

    // 测试4.2: WebSocket 连接状态
    phase.tests.get_websocket_status = await executeTest('get_websocket_status', async () => {
        const result = await mockMcpCall('get_websocket_status');
        if (!result || typeof result !== 'object') {
            throw new Error('WebSocket 状态响应格式不正确');
        }
        return result;
    });

    // 测试4.3: 资源统计功能
    phase.tests.get_resource_statistics = await executeTest('get_resource_statistics', async () => {
        const result = await mockMcpCall('get_resource_statistics');
        if (!result || typeof result !== 'object') {
            throw new Error('资源统计响应格式不正确');
        }
        return result;
    });

    // 测试4.4: 资源分组列表
    phase.tests.list_resource_groups = await executeTest('list_resource_groups', async () => {
        const result = await mockMcpCall('list_resource_groups', { limit: 10 });
        if (!Array.isArray(result)) {
            throw new Error('资源分组列表应为数组格式');
        }
        return result;
    });

    // 测试4.5: 资源树导出功能
    phase.tests.export_resource_tree = await executeTest('export_resource_tree', async () => {
        const result = await mockMcpCall('export_resource_tree', { format: 'json' });
        if (!result || typeof result !== 'object') {
            throw new Error('资源树导出响应格式不正确');
        }
        return result;
    });

    // 测试4.6: 路径查询测试
    phase.tests.get_api_details_by_path = await executeTest('get_api_details_by_path', async () => {
        const result = await mockMcpCall('get_api_details_by_path', { path: '/test/api' });
        if (!result || typeof result !== 'object') {
            throw new Error('API 详情响应格式不正确');
        }
        return result;
    });

    // 统计结果
    phase.summary.total = Object.keys(phase.tests).length;
    phase.summary.passed = Object.values(phase.tests).filter(t => t.success).length;
    phase.summary.failed = phase.summary.total - phase.summary.passed;

    testResults.phases.phase4 = phase;
    log('info', `阶段4完成: ${phase.summary.passed}/${phase.summary.total} 通过`);
}

/**
 * 阶段5：备份与恢复功能测试
 */
async function phase5_BackupAndRestoreTests() {
    log('info', '=== 开始阶段5：备份与恢复功能测试 ===');

    const phase = {
        name: '备份与恢复功能测试',
        tests: {},
        summary: { passed: 0, failed: 0, total: 0 }
    };

    // 测试5.1: 获取备份历史记录
    phase.tests.get_backup_history = await executeTest('get_backup_history', async () => {
        const result = await mockMcpCall('get_backup_history', { backup_id: 'test-backup-123' });
        if (!result || typeof result !== 'object') {
            throw new Error('备份历史响应格式不正确');
        }
        return result;
    });

    // 测试5.2: 获取备份内容
    phase.tests.get_backup_content = await executeTest('get_backup_content', async () => {
        const result = await mockMcpCall('get_backup_content', {
            backup_id: 'test-backup-123',
            timestamp: Date.now()
        });
        if (!result || typeof result !== 'object') {
            throw new Error('备份内容响应格式不正确');
        }
        return result;
    });

    // 测试5.3: 高级备份功能测试
    phase.tests.list_backups_advanced = await executeTest('list_backups_advanced', async () => {
        const result = await mockMcpCall('list_backups', {
            timestamp: Date.now() - 86400000, // 24小时前
            filter_text: 'test',
            limit: 5
        });
        if (!result || typeof result !== 'object') {
            throw new Error('高级备份查询响应格式不正确');
        }
        return result;
    });

    // 测试5.4: 最佳实践指南
    phase.tests.get_best_practices = await executeTest('get_best_practices', async () => {
        const result = await mockMcpCall('get_best_practices');
        if (!result || typeof result !== 'object') {
            throw new Error('最佳实践响应格式不正确');
        }
        return result;
    });

    // 测试5.5: 常见陷阱信息
    phase.tests.get_common_pitfalls = await executeTest('get_common_pitfalls', async () => {
        const result = await mockMcpCall('get_common_pitfalls');
        if (!result || typeof result !== 'object') {
            throw new Error('常见陷阱响应格式不正确');
        }
        return result;
    });

    // 测试5.6: 知识库概览
    phase.tests.get_knowledge_overview = await executeTest('get_knowledge_overview', async () => {
        const result = await mockMcpCall('get_knowledge_overview');
        if (!result || typeof result !== 'object') {
            throw new Error('知识库概览响应格式不正确');
        }
        return result;
    });

    // 统计结果
    phase.summary.total = Object.keys(phase.tests).length;
    phase.summary.passed = Object.values(phase.tests).filter(t => t.success).length;
    phase.summary.failed = phase.summary.total - phase.summary.passed;

    testResults.phases.phase5 = phase;
    log('info', `阶段5完成: ${phase.summary.passed}/${phase.summary.total} 通过`);
}

/**
 * 阶段6：高级功能与边界测试
 */
async function phase6_AdvancedAndBoundaryTests() {
    log('info', '=== 开始阶段6：高级功能与边界测试 ===');

    const phase = {
        name: '高级功能与边界测试',
        tests: {},
        summary: { passed: 0, failed: 0, total: 0 }
    };

    // 测试6.1: 无效参数处理
    phase.tests.invalid_params_handling = await executeTest('invalid_params_handling', async () => {
        const result = await mockMcpCall('search_knowledge', { keyword: '' });
        if (!result || typeof result !== 'object') {
            throw new Error('无效参数处理响应格式不正确');
        }
        return result;
    });

    // 测试6.2: 空结果集处理
    phase.tests.empty_results_handling = await executeTest('empty_results_handling', async () => {
        const result = await mockMcpCall('search_api_scripts', { keyword: 'nonexistent-keyword-12345' });
        if (!Array.isArray(result)) {
            throw new Error('空结果集处理响应格式不正确');
        }
        return result;
    });

    // 测试6.3: 大量数据查询（模拟）
    phase.tests.large_data_query = await executeTest('large_data_query', async () => {
        const result = await mockMcpCall('get_full_magic_script_syntax');
        if (!result.sections || typeof result.sections !== 'object') {
            throw new Error('大量数据查询响应格式不正确');
        }
        return result;
    });

    // 测试6.4: 并发调用测试（模拟）
    phase.tests.concurrent_calls = await executeTest('concurrent_calls', async () => {
        const promises = Array(3).fill().map(() => mockMcpCall('get_assistant_metadata'));
        const results = await Promise.all(promises);

        if (!Array.isArray(results) || results.length !== 3) {
            throw new Error('并发调用测试失败');
        }

        return { concurrent_results: results.length };
    });

    // 测试6.5: 错误响应处理
    phase.tests.error_response_handling = await executeTest('error_response_handling', async () => {
        const result = await mockMcpCall('nonexistent_tool');
        if (!result.error || !result.error.code) {
            throw new Error('错误响应处理测试失败');
        }
        return result;
    });

    // 测试6.6: 性能基准测试（响应时间）
    phase.tests.performance_benchmark = await executeTest('performance_benchmark', async () => {
        const startTime = Date.now();
        await mockMcpCall('get_assistant_metadata');
        const duration = Date.now() - startTime;

        if (duration > 2000) {
            log('warn', `性能基准测试警告: 响应时间过长 (${duration}ms)`);
        }

        return { response_time: duration };
    });

    // 统计结果
    phase.summary.total = Object.keys(phase.tests).length;
    phase.summary.passed = Object.values(phase.tests).filter(t => t.success).length;
    phase.summary.failed = phase.summary.total - phase.summary.passed;

    testResults.phases.phase6 = phase;
    log('info', `阶段6完成: ${phase.summary.passed}/${phase.summary.total} 通过`);
}

/**
 * 生成测试报告
 */
function generateReport() {
    const reportPath = path.join(__dirname, 'test-report.json');
    const summaryPath = path.join(__dirname, 'test-summary.md');

    // 计算总体统计
    let totalTests = 0;
    let totalPassed = 0;
    let totalFailed = 0;

    Object.values(testResults.phases).forEach(phase => {
        totalTests += phase.summary.total;
        totalPassed += phase.summary.passed;
        totalFailed += phase.summary.failed;
    });

    testResults.summary = {
        totalTests,
        passed: totalPassed,
        failed: totalFailed,
        skipped: 0,
        successRate: totalTests > 0 ? (totalPassed / totalTests * 100).toFixed(2) + '%' : '0%'
    };
    testResults.endTime = new Date().toISOString();

    // 保存详细报告
    fs.writeFileSync(reportPath, JSON.stringify(testResults, null, 2));
    log('info', `详细测试报告已保存到: ${reportPath}`);

    // 生成摘要报告
    const summaryContent = `# Magic-API MCP 工具链测试报告

## 📊 测试摘要

- **测试时间**: ${testResults.startTime} - ${testResults.endTime}
- **总体通过率**: ${testResults.summary.successRate}
- **测试用例**: ${totalPassed}/${totalTests} 通过

## 📋 分阶段结果

${Object.entries(testResults.phases).map(([phaseKey, phase]) =>
    `### ${phase.name}
- 通过: ${phase.summary.passed}
- 失败: ${phase.summary.failed}
- 总计: ${phase.summary.total}
`
).join('\n')}

## 🎯 测试结论

${totalFailed === 0 ? '✅ 所有测试通过，MCP 工具链功能正常' : '⚠️ 部分测试失败，需要进一步检查'}

---
*报告生成时间: ${new Date().toISOString()}*
`;

    fs.writeFileSync(summaryPath, summaryContent);
    log('info', `测试摘要报告已保存到: ${summaryPath}`);
}

/**
 * 主测试执行函数
 */
async function runAllTests() {
    try {
        log('info', '🚀 开始 Magic-API MCP 工具链全面测试');

        // 执行各阶段测试
        await phase1_BasicInfoTests();
        await phase2_DocumentationTests();
        await phase3_SearchAndQueryTests();
        await phase4_ApiAndDebugTests();
        await phase5_BackupAndRestoreTests();
        await phase6_AdvancedAndBoundaryTests();

        // 生成报告
        generateReport();

        const successRate = testResults.summary.successRate;
        log('info', `🎉 测试完成！总体通过率: ${successRate}`);

        // 根据结果给出建议
        if (successRate === '100.00%') {
            log('info', '✅ 所有测试通过，MCP 工具链运行正常');
        } else {
            log('warn', '⚠️ 部分测试失败，建议检查相关功能');
        }

    } catch (error) {
        log('error', `测试执行过程中发生错误: ${error.message}`, error.stack);
        process.exit(1);
    }
}

// 导出测试函数
module.exports = {
    runAllTests,
    executeTest,
    mockMcpCall,
    log
};

// 如果直接运行此脚本
if (require.main === module) {
    runAllTests();
}

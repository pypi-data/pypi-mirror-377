# MCP Feedback Enhanced 发布流程指南

本文档详细说明了 `mcp-feedback-enhanced` 项目的完整发布流程，包括本地发布和自动化发布两种方式。

## 📋 目录

- [发布前准备](#发布前准备)
- [版本管理策略](#版本管理策略)
- [发布方式](#发布方式)
  - [方式1: GitHub Actions自动发布 (推荐)](#方式1-github-actions自动发布-推荐)
  - [方式2: 本地手动发布](#方式2-本地手动发布)
- [发布后验证](#发布后验证)
- [故障排除](#故障排除)

## 🚀 发布前准备

### 1. 环境检查

确保您的开发环境已正确配置：

```bash
# 检查 Python 版本 (需要 >= 3.11)
python --version

# 检查 uv 工具
uv --version

# 检查项目依赖
uv sync --dev
```

### 2. 代码质量检查

```bash
# 运行代码格式化
uv run ruff format

# 运行代码检查
uv run ruff check

# 运行类型检查
uv run mypy src

# 运行测试
uv run pytest
```

### 3. 更新文档

- 更新 `CHANGELOG.md` 文件，记录新版本的变更
- 更新 `README.md` 中的版本信息（如有需要）
- 确保所有文档与代码同步

### 4. 桌面应用构建（如需要）

如果包含桌面应用功能的更新：

```bash
# 本地测试桌面应用构建
python scripts/build_desktop.py --release

# 检查构建产物
ls -la src/mcp_feedback_enhanced/desktop_release/
```

## 📊 版本管理策略

项目采用语义化版本控制 (Semantic Versioning)：

- **MAJOR.MINOR.PATCH** (如: 2.6.0)
- **日期版本** (如: 2025.0720.01)

### 版本类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| `patch` | Bug修复、文档更新、小改进 | 2.6.0 → 2.6.1 |
| `minor` | 新功能、向后兼容的改进 | 2.6.0 → 2.7.0 |
| `major` | 重大更改、API破坏性变更 | 2.6.0 → 3.0.0 |
| `custom` | 自定义版本号 | 2025.0720.01 |

## 🚀 发布方式

### 方式1: GitHub Actions自动发布 (推荐)

这是最简单、最可靠的发布方式。

#### 步骤1: 配置PyPI Token

1. 访问 [PyPI Account Settings](https://pypi.org/manage/account/token/)
2. 创建新的API Token
3. 在GitHub仓库中添加Secret:
   - 名称: `PYPI_API_TOKEN`
   - 值: 您的PyPI Token

#### 步骤2: 执行自动发布

1. **访问GitHub Actions页面**:
   ```
   https://github.com/jayzqj/mcp-feedback-enhanced/actions/workflows/publish.yml
   ```

2. **点击 "Run workflow" 按钮**

3. **配置发布参数**:
   - **Version Type**: 选择 `patch`/`minor`/`major`
   - **Custom Version**: 可选，如 `2025.0720.01` (会覆盖Version Type)
   - **Include Desktop**: 选择是否包含桌面应用
   - **Desktop Build Run ID**: 可选，指定特定的桌面应用构建

4. **点击 "Run workflow" 开始发布**

#### 自动化流程说明

工作流程将自动执行以下步骤：

1. ✅ **环境准备**: 安装依赖和工具
2. ✅ **版本更新**: 自动更新版本号
3. ✅ **桌面应用检查**: 验证桌面应用二进制文件
4. ✅ **包构建**: 构建Python包
5. ✅ **包验证**: 使用twine检查包
6. ✅ **PyPI发布**: 发布到PyPI
7. ✅ **GitHub Release**: 创建GitHub发布页面
8. ✅ **标签推送**: 推送版本标签

### 方式2: 本地手动发布

适用于需要更多控制的情况。

#### 步骤1: 版本更新

```bash
# 使用项目自带的发布脚本
python scripts/release.py patch   # 2.6.0 -> 2.6.1
python scripts/release.py minor   # 2.6.0 -> 2.7.0
python scripts/release.py major   # 2.6.0 -> 3.0.0

# 或手动编辑版本号
# 编辑 pyproject.toml 中的 version 字段
# 编辑 src/mcp_feedback_enhanced/__init__.py 中的 __version__
```

#### 步骤2: 清理和构建

```bash
# 清理缓存
python scripts/cleanup_cache.py --clean

# 构建包
uv build

# 验证包
uv run twine check dist/*
```

#### 步骤3: 发布到PyPI

```bash
# 方式A: 使用API Token (推荐)
uv publish --token your-pypi-token

# 方式B: 使用用户名密码
uv publish --username your-username --password your-password

# 方式C: 先发布到测试PyPI验证
uv publish --repository testpypi --token your-test-token
```

#### 步骤4: 创建Git标签

```bash
# 获取当前版本
VERSION=$(grep '^version =' pyproject.toml | cut -d'"' -f2)

# 提交更改
git add .
git commit -m "Release v${VERSION}"

# 创建标签
git tag "v${VERSION}"

# 推送到远程
git push origin main
git push origin "v${VERSION}"
```

## ✅ 发布后验证

### 1. PyPI验证

```bash
# 检查PyPI页面
# https://pypi.org/project/ai-interactive-feedback/

# 测试安装
uvx ai-interactive-feedback@latest --help

# 测试特定版本
uvx ai-interactive-feedback@2025.0720.01 --help
```

### 2. 功能测试

```bash
# 测试Web模式
uvx ai-interactive-feedback@latest test --web

# 测试桌面模式 (如果包含)
uvx ai-interactive-feedback@latest test --desktop

# 测试MCP服务器
uvx ai-interactive-feedback@latest server
```

### 3. 配置测试

创建测试配置文件：

```json
{
  "mcpServers": {
    "ai-interactive-feedback": {
      "command": "uvx",
      "args": ["ai-interactive-feedback@latest"],
      "env": {
        "MCP_DESKTOP_MODE": "true",
        "MCP_WEB_PORT": "8765",
        "MCP_DEBUG": "false"
      }
    }
  }
}
```

## 🔧 故障排除

### 常见问题

#### 1. PyPI发布失败

**错误**: `403 Forbidden` 或认证失败

**解决方案**:
```bash
# 检查Token是否正确
# 确保Token有上传权限
# 检查包名是否已被占用
```

#### 2. 版本冲突

**错误**: `File already exists`

**解决方案**:
```bash
# 更新版本号
python scripts/release.py patch

# 或手动修改版本
# 编辑 pyproject.toml 和 __init__.py
```

#### 3. 桌面应用缺失

**错误**: 桌面模式无法启动

**解决方案**:
```bash
# 重新构建桌面应用
python scripts/build_desktop.py --release

# 或在GitHub Actions中设置 include_desktop: false
```

#### 4. 依赖问题

**错误**: 包安装失败

**解决方案**:
```bash
# 检查依赖版本
uv tree

# 更新依赖
uv sync --upgrade

# 检查Python版本兼容性
```

### 调试技巧

```bash
# 启用详细日志
export MCP_DEBUG=true

# 检查包内容
uv run python -c "import ai_interactive_feedback; print(ai_interactive_feedback.__file__)"

# 验证包结构
unzip -l dist/ai_interactive_feedback-*.whl
```

## 🔐 安全注意事项

### PyPI Token管理

1. **Token权限**: 使用最小权限原则
   ```bash
   # 推荐: 项目特定Token
   # 避免: 全局账户Token
   ```

2. **Token轮换**: 定期更新PyPI Token
3. **环境隔离**: 测试和生产使用不同Token

### 敏感信息保护

- ✅ 使用GitHub Secrets存储Token
- ✅ 避免在日志中暴露敏感信息
- ✅ 定期审查访问权限

## 📊 发布统计和监控

### 发布指标

```bash
# 检查包下载统计
# https://pypistats.org/packages/ai-interactive-feedback

# 监控包大小
ls -lh dist/

# 检查依赖树
uv tree
```

### 版本兼容性矩阵

| Python版本 | 支持状态 | 测试状态 |
|------------|----------|----------|
| 3.11       | ✅ 支持  | ✅ 测试  |
| 3.12       | ✅ 支持  | ✅ 测试  |
| 3.13       | ✅ 支持  | ⚠️ 部分  |

### 平台支持

| 平台 | Web模式 | 桌面模式 | 状态 |
|------|---------|----------|------|
| Windows x64 | ✅ | ✅ | 完全支持 |
| macOS Intel | ✅ | ✅ | 完全支持 |
| macOS ARM64 | ✅ | ✅ | 完全支持 |
| Linux x64 | ✅ | ✅ | 完全支持 |

## 🚀 高级发布场景

### 热修复发布

紧急修复的快速发布流程：

```bash
# 1. 创建热修复分支
git checkout -b hotfix/critical-fix

# 2. 修复问题
# ... 进行必要的修复

# 3. 快速测试
uv run pytest tests/critical/

# 4. 发布补丁版本
python scripts/release.py patch

# 5. 合并回主分支
git checkout main
git merge hotfix/critical-fix
```

### 预发布版本

发布测试版本：

```bash
# 使用预发布版本号
# 例如: 2.7.0-alpha.1, 2.7.0-beta.1, 2.7.0-rc.1

# 手动设置版本
sed -i 's/version = ".*"/version = "2.7.0-alpha.1"/' pyproject.toml

# 发布到测试PyPI
uv publish --repository testpypi
```

### 回滚策略

如果发布出现问题：

```bash
# 1. 从PyPI撤回版本 (仅限24小时内)
# 访问 PyPI 管理页面手动撤回

# 2. 发布修复版本
python scripts/release.py patch

# 3. 通知用户升级
# 更新文档和通知渠道
```

## 📋 发布检查清单

### 发布前检查 ✅

- [ ] 代码质量检查通过 (`ruff`, `mypy`)
- [ ] 所有测试通过 (`pytest`)
- [ ] 文档已更新 (`CHANGELOG.md`, `README.md`)
- [ ] 版本号已确定
- [ ] 桌面应用构建成功 (如需要)
- [ ] 本地功能测试通过

### 发布过程检查 ✅

- [ ] GitHub Actions工作流程成功
- [ ] PyPI包已发布
- [ ] GitHub Release已创建
- [ ] 版本标签已推送

### 发布后检查 ✅

- [ ] PyPI页面显示正常
- [ ] 包可以正常安装 (`uvx ai-interactive-feedback@latest`)
- [ ] 基本功能测试通过
- [ ] 文档链接正常
- [ ] 社区通知已发送

## 📚 相关文档

- [GitHub Actions工作流程](./WORKFLOWS.md)
- [桌面应用构建指南](./DESKTOP_BUILD.md)
- [项目架构文档](./architecture/README.md)
- [缓存管理指南](./zh-CN/cache-management.md)

## 🎯 最佳实践

1. **发布前测试**: 始终在本地测试所有功能
2. **版本规划**: 遵循语义化版本控制
3. **文档同步**: 确保文档与代码版本一致
4. **自动化优先**: 优先使用GitHub Actions自动发布
5. **备份策略**: 保留重要版本的构建产物
6. **监控发布**: 发布后及时验证功能正常
7. **社区沟通**: 及时通知重要更新
8. **安全第一**: 保护敏感信息和访问权限

## 🆘 紧急联系

如果发布过程中遇到严重问题：

1. **立即停止**: 停止正在进行的发布流程
2. **评估影响**: 确定问题的影响范围
3. **回滚计划**: 准备回滚到上一个稳定版本
4. **修复问题**: 快速修复并重新发布
5. **事后总结**: 分析问题原因并改进流程

---

**文档版本**: v1.0
**最后更新**: 2025-07-20
**维护者**: Minidoracat
**使用模型**: Claude Sonnet 4

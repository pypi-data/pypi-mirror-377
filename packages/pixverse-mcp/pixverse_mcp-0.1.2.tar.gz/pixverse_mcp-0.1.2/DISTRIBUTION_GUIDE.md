# Pixverse MCP 分发指南

让其他人通过 uvx 访问您的 pixverse-mcp 项目有以下几种方式：

## 方案 1: 发布到 PyPI（推荐）

### 1.1 准备发布

```bash
# 构建包
uv build

# 检查构建结果
ls dist/
```

### 1.2 发布到 PyPI

```bash
# 安装发布工具
uv add --dev twine

# 发布到 PyPI（需要 PyPI 账号和 token）
uv run twine upload dist/*

# 或者先发布到测试 PyPI
uv run twine upload --repository testpypi dist/*
```

### 1.3 其他人使用

发布后，其他人可以直接使用：

```bash
# 直接运行
uvx pixverse-mcp --help

# 指定版本
uvx pixverse-mcp==0.1.0 --help

# 使用配置文件
uvx pixverse-mcp --config config.yaml --sse --port 8080
```

## 方案 2: 通过 Git 仓库分发

### 2.1 推送到 Git 仓库

```bash
# 推送到 GitHub/GitLab 等
git add .
git commit -m "Add uvx support"
git push origin main
```

### 2.2 其他人使用

```bash
# 从 Git 仓库运行
uvx --from git+https://github.com/your-username/pixverse-mcp pixverse-mcp

# 指定分支
uvx --from git+https://github.com/your-username/pixverse-mcp@main pixverse-mcp

# 指定标签
uvx --from git+https://github.com/your-username/pixverse-mcp@v0.1.0 pixverse-mcp
```

## 方案 3: 本地文件分发

### 3.1 分发构建的包

将 `dist/` 目录中的文件分享给其他人：

```bash
# 其他人下载后可以这样使用
uvx --from ./pixverse_mcp-0.1.0-py3-none-any.whl pixverse-mcp

# 或者从 tar.gz
uvx --from ./pixverse_mcp-0.1.0.tar.gz pixverse-mcp
```

### 3.2 分发整个项目目录

```bash
# 其他人获得项目目录后
cd pixverse_mcp/
uvx --from . pixverse-mcp --help
```

## 方案 4: 私有 PyPI 服务器

如果您不想公开发布，可以搭建私有 PyPI：

```bash
# 使用 devpi 搭建私有 PyPI
pip install devpi-server devpi-client

# 启动服务器
devpi-server --start

# 上传包
devpi upload dist/*
```

其他人配置私有源后使用：

```bash
uvx --index-url http://your-private-pypi.com/simple pixverse-mcp
```

## 推荐流程

### 对于开源项目：
1. 推送代码到 GitHub
2. 发布到 PyPI
3. 用户使用：`uvx pixverse-mcp`

### 对于私有项目：
1. 推送到私有 Git 仓库
2. 用户使用：`uvx --from git+https://your-private-repo.git pixverse-mcp`

### 对于内部分发：
1. 构建包：`uv build`
2. 分享 wheel 文件
3. 用户使用：`uvx --from ./pixverse_mcp-0.1.0-py3-none-any.whl pixverse-mcp`

## 配置文件分发

不要忘记提供配置文件模板：

```bash
# 创建配置模板
cp test_config.yaml config.template.yaml

# 在模板中移除敏感信息，添加说明
```

## 使用示例

创建一个使用示例文件，方便其他人快速上手：

```bash
# 示例：运行 MCP 服务器
uvx pixverse-mcp --config config.yaml

# 示例：运行 SSE 服务器
uvx pixverse-mcp --config config.yaml --sse --port 8080
```

## 注意事项

1. **API Key 安全**：确保不要在代码中硬编码 API key
2. **版本管理**：使用语义化版本号
3. **文档完整**：提供完整的使用文档
4. **依赖管理**：确保 `uv.lock` 文件包含所有依赖
5. **测试覆盖**：在发布前充分测试所有功能

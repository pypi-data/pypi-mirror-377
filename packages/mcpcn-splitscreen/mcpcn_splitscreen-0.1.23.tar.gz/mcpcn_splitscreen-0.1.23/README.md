# 电脑分屏 MCP

一个高性能、跨平台的模型上下文协议（MCP）服务器，为 Windows 和 macOS 提供可靠的分屏窗口管理。该服务器通过 MCP 协议暴露 16 个窗口操作工具，使 AI 助手和其他 MCP 客户端能够精确控制桌面窗口布局。

## 🚀 功能特性

- **跨平台支持**：Windows 和 macOS，具有原生优化
- **16 个窗口管理工具**：全面的分屏布局和控制
- **高性能**：Windows：15-60ms，macOS：50-150ms 每次操作
- **可靠性优先**：强大的回退机制和错误处理
- **MCP 集成**：通过 stdio 传输的完整模型上下文协议服务器支持
- **智能焦点检测**：具有平台特定优化的高级窗口焦点检测

## 🛠️ 安装

### 前置要求

- **Python**：3.9 或更高版本
- **包管理器**：`uvx`（推荐）或 `pip`

### 通过 uvx 安装（推荐）

```bash
uvx install computer-split-screen-mcp
```

### 通过 pip 安装

```bash
pip install computer-split-screen-mcp
```

## 🔧 MCP 客户端配置

使用以下设置配置您的 MCP 客户端：

```json
{
  "mcpServers": {
    "computer-split-screen": {
      "command": "uvx",
      "args": ["computer-split-screen-mcp"],
      "env": {}
    }
  }
}
```

### 替代配置（如果不使用 uvx）

```json
{
  "mcpServers": {
    "computer-split-screen": {
      "command": "python",
      "args": ["-m", "computer-split-screen-mcp"],
      "env": {}
    }
  }
}
```

## 🎯 可用工具

### 分屏布局

#### 二分屏（2 路分割）
- `left-half-screen` - 将当前窗口贴靠到左半屏
- `right-half-screen` - 将当前窗口贴靠到右半屏
- `top-half-screen` - 将当前窗口贴靠到上半屏
- `bottom-half-screen` - 将当前窗口贴靠到下半屏

#### 四分屏（4 路分割）
- `top-left-screen` - 左上象限（1/4 屏幕）
- `top-right-screen` - 右上象限（1/4 屏幕）
- `bottom-left-screen` - 左下象限（1/4 屏幕）
- `bottom-right-screen` - 右下象限（1/4 屏幕）

#### 三分屏（3 路分割）
- `left-one-third-screen` - 左三分之一（1/3 屏幕）
- `middle-one-third-screen` - 中间三分之一（1/3 屏幕）
- `right-one-third-screen` - 右三分之一（1/3 屏幕）

#### 三分之二（2/3 分割）
- `left-two-thirds-screen` - 左三分之二（2/3 屏幕）
- `right-two-thirds-screen` - 右三分之二（2/3 屏幕）

### 窗口控制
- `maximize-screen` - 操作系统最大化（有边框，任务栏可见）
- `fullscreen-screen` - 全屏模式（平台特定行为）
- `minimize-screen` - 将窗口最小化到任务栏/程序坞

## ⚡ 性能特征

### Windows 性能
- **总时间**：每次操作 15-60ms
- **检测**：2-5ms（直接 Win32 API）
- **操作**：10-47ms（带修正的 SetWindowPos）
- **最佳情况**：简单分割 15-25ms
- **典型情况**：大多数操作 20-35ms

### macOS 性能
- **总时间**：每次操作 50-150ms
- **检测**：20-50ms（AppleScript + 辅助功能 API）
- **操作**：15-55ms（AXUIElement 操作）
- **最佳情况**：简单分割 50-80ms
- **典型情况**：大多数操作 80-120ms

## 🔍 技术架构

### Windows 实现
- 通过 `pywin32` 的**直接 Win32 API 调用**
- **DWM 集成**用于准确的框架边界
- **DPI 感知定位**用于高分辨率显示器
- **双遍定位**用于精确的窗口放置

### macOS 实现
- **AppleScript 焦点检测**用于可靠性
- **辅助功能 API**用于窗口操作
- **回退机制**用于边缘情况
- **屏幕感知定位**尊重菜单栏和程序坞

### 跨平台功能
- **自动平台检测**
- **条件依赖加载**
- **统一 API 接口**
- **错误处理和恢复**

## 📋 平台依赖

### Windows
- **必需**：`pywin32>=306`
- **用途**：Win32 API 访问、DWM 集成、窗口操作

### macOS
- **必需**：`pyobjc-core>=10.1,<11`、`pyobjc-framework-Cocoa>=10.1,<11`、`pyobjc-framework-Quartz>=10.1,<11`、`pyobjc-framework-ApplicationServices>=10.1,<11`
- **用途**：辅助功能 API、AppleScript 集成、窗口管理

## 🚨 故障排除

### 常见问题

#### macOS 焦点检测问题
- **症状**：窗口不移动或选择了错误的窗口
- **解决方案**：确保终端在系统偏好设置 > 安全性与隐私 > 隐私 > 辅助功能中具有辅助功能权限

#### Windows DPI 问题
- **症状**：在高 DPI 显示器上窗口定位不正确
- **解决方案**：服务器自动处理 DPI 感知，但确保安装 `pywin32>=306`

#### MCP 客户端连接问题
- **症状**：直接调用时功能正常，但通过 MCP 失败
- **解决方案**：检查 MCP 客户端日志，确保正确配置，重启 MCP 客户端

### 性能优化
- **首次运行**：可能由于系统预热而较慢
- **后续运行**：应该持续快速
- **复杂应用**：Safari、Chrome 可能由于窗口结构而需要更长时间

## 🔧 开发

### 项目结构
```
computer-split-screen/
├── src/splitscreen_mcp/
│   ├── __init__.py          # 包初始化
│   ├── __main__.py          # MCP 服务器入口点
│   └── window_actions.py    # 核心窗口管理逻辑
├── pyproject.toml           # 项目配置
├── README.md               # 本文件
└── LICENSE                 # MIT 许可证
```

### 从源码构建
```bash
git clone https://github.com/Beta0415/computer-split-screen-mcp.git
cd computer-split-screen-mcp
uvx install -e .
```

### 运行测试
```bash
# 测试窗口检测
python3 -c "from src.splitscreen_mcp.window_actions import left_half_window; left_half_window()"

# 测试 MCP 服务器
uvx run computer-split-screen-mcp
```

### 贡献
- **仓库**：[https://github.com/Beta0415/computer-split-screen-mcp](https://github.com/Beta0415/computer-split-screen-mcp)
- **问题**：[https://github.com/Beta0415/computer-split-screen-mcp/issues](https://github.com/Beta0415/computer-split-screen-mcp/issues)
- **拉取请求**：欢迎！重大更改请先开一个 issue。

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎贡献！请随时提交拉取请求。对于重大更改，请先开一个 issue 来讨论您想要更改的内容。

## 📊 版本历史

- **v1.4.4** - 当前稳定版本
  - 跨平台窗口管理
  - 16 个全面工具
  - 高性能实现
  - 完整 MCP 协议支持

## 🆘 支持

如果您遇到任何问题或有疑问：

1. 检查上面的故障排除部分
2. 查看 MCP 客户端日志中的错误
3. 直接测试功能以隔离问题
4. 在项目仓库上开一个 issue

---

**为 MCP 社区用心构建 ❤️**

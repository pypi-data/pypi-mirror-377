"""
分屏工具 MCP 服务器

提供跨平台（macOS & Windows）的窗口分屏功能，包括：
- 基础分屏：左半屏、右半屏、上半屏、下半屏
- 四象限分屏：左上、右上、左下、右下
- 三分之一分屏：左、中、右三分之一
- 三分之二分屏：左、右三分之二
- 窗口控制：最大化、全屏、最小化

支持的操作系统：macOS、Windows
"""

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .window_actions import (
    left_half_window, right_half_window,
    top_half_window, bottom_half_window,
    top_left_quadrant_window, top_right_quadrant_window,
    bottom_left_quadrant_window, bottom_right_quadrant_window,
    left_third_window, middle_third_window, right_third_window,
    left_two_thirds_window, right_two_thirds_window,
    maximise_window, minimise_window, fullscreen_window,
)

# 创建 MCP 服务器实例
mcp = FastMCP("computer-split-screen")

def ok(msg: str) -> TextContent:
    """返回成功消息的文本内容"""
    return TextContent(type="text", text=msg)

# ===== 基础分屏工具 =====
@mcp.tool("left-half-screen", description="将当前聚焦的窗口移动到屏幕左半部分，适合并排显示两个窗口！")
def left_half() -> TextContent:
    left_half_window()
    return ok("左半屏分屏完成!")

@mcp.tool("right-half-screen", description="将当前聚焦的窗口移动到屏幕右半部分，适合并排显示两个窗口。")
def right_half() -> TextContent:
    right_half_window()
    return ok("右半屏分屏完成!")

@mcp.tool("top-half-screen", description="将当前聚焦的窗口移动到屏幕上半部分，适合上下分屏显示。")
def top_half() -> TextContent:
    top_half_window()
    return ok("上半屏分屏完成!")

@mcp.tool("bottom-half-screen", description="将当前聚焦的窗口移动到屏幕下半部分，适合上下分屏显示。")
def bottom_half() -> TextContent:
    bottom_half_window()
    return ok("下半屏分屏完成!")

# ===== 四象限分屏工具 =====
@mcp.tool("top-left-screen", description="将当前聚焦的窗口移动到屏幕左上角四分之一区域，适合四窗口布局！")
def top_left() -> TextContent:
    top_left_quadrant_window()
    return ok("左上角分屏完成!")

@mcp.tool("top-right-screen", description="将当前聚焦的窗口移动到屏幕右上角四分之一区域，适合四窗口布局！")
def top_right() -> TextContent:
    top_right_quadrant_window()
    return ok("右上角分屏完成!")

@mcp.tool("bottom-left-screen", description="将当前聚焦的窗口移动到屏幕左下角四分之一区域，适合四窗口布局！")
def bottom_left() -> TextContent:
    bottom_left_quadrant_window()
    return ok("左下角分屏完成!")

@mcp.tool("bottom-right-screen", description="将当前聚焦的窗口移动到屏幕右下角四分之一区域，适合四窗口布局！")
def bottom_right() -> TextContent:
    bottom_right_quadrant_window()
    return ok("右下角分屏完成!")

# ===== 三分之一和三分之二分屏工具 =====
@mcp.tool("left-one-third-screen", description="将当前聚焦的窗口移动到屏幕左侧三分之一区域，适合三窗口布局！")
def left_third() -> TextContent:
    left_third_window()
    return ok("左三分之一分屏完成!")

@mcp.tool("middle-one-third-screen", description="将当前聚焦的窗口移动到屏幕中间三分之一区域，适合三窗口布局！")
def middle_third() -> TextContent:
    middle_third_window()
    return ok("中三分之一分屏完成!")

@mcp.tool("right-one-third-screen", description="将当前聚焦的窗口移动到屏幕右侧三分之一区域，适合三窗口布局！")
def right_third() -> TextContent:
    right_third_window()
    return ok("右三分之一分屏完成!")

@mcp.tool("left-two-thirds-screen", description="将当前聚焦的窗口移动到屏幕左侧三分之二区域，适合主窗口+侧边栏布局！")
def left_two_thirds() -> TextContent:
    left_two_thirds_window()
    return ok("左三分之二分屏完成!")

@mcp.tool("right-two-thirds-screen", description="将当前聚焦的窗口移动到屏幕右侧三分之二区域，适合主窗口+侧边栏布局！")
def right_two_thirds() -> TextContent:
    right_two_thirds_window()
    return ok("右三分之二分屏完成!")

# ===== 窗口控制工具 =====
@mcp.tool("maximize-screen", description="最大化当前聚焦的窗口，保持边框和标题栏可见，适合全屏工作")
def maximize() -> TextContent:
    maximise_window()
    return ok("窗口最大化完成。")

@mcp.tool("fullscreen-screen", description="将当前聚焦的窗口设置为全屏模式，在macOS上使用无边框全屏，在Windows上使用标准最大化模式，适合沉浸式工作。")
def fullscreen() -> TextContent:
    fullscreen_window()
    return ok("窗口全屏完成。")

@mcp.tool("minimize-screen", description="最小化当前聚焦的窗口，在Windows上发送到任务栏，在macOS上发送到Dock，适合临时隐藏窗口。")
def minimize() -> TextContent:
    success = minimise_window()
    return ok("窗口最小化完成。" if success else "窗口最小化失败!")

def main():
    """启动 MCP 服务器"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

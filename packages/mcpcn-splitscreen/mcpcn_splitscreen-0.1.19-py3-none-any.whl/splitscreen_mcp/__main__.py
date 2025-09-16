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

from .window_actions import (
    left_half_window, right_half_window,
    top_half_window, bottom_half_window,
    top_left_quadrant_window, top_right_quadrant_window,
    bottom_left_quadrant_window, bottom_right_quadrant_window,
    left_third_window, middle_third_window, right_third_window,
    left_two_thirds_window, right_two_thirds_window,
    maximise_window, minimise_window, fullscreen_window,
)
from .logging_utils import get_logger, log_startup

# 创建 MCP 服务器实例
mcp = FastMCP("computer-split-screen")
logger = get_logger()
log_startup("splitscreen_mcp.__main__")

def run_and_log(action_name: str, func):
    try:
        logger.info(f"Tool start: {action_name}")
        result = func()
        logger.info(f"Tool done: {action_name} -> {result}")
        return result
    except Exception as e:
        logger.exception(f"Tool error: {action_name}: {e}")
        raise

# ===== 基础分屏工具 =====
@mcp.tool("left-half-screen", description="将当前聚焦的窗口移动到屏幕左半部分，适合并排显示两个窗口。")
def left_half() -> None:
    run_and_log("left-half-screen", left_half_window)

@mcp.tool("right-half-screen", description="将当前聚焦的窗口移动到屏幕右半部分，适合并排显示两个窗口。")
def right_half() -> None:
    run_and_log("right-half-screen", right_half_window)

@mcp.tool("top-half-screen", description="将当前聚焦的窗口移动到屏幕上半部分，适合上下分屏显示。")
def top_half() -> None:
    run_and_log("top-half-screen", top_half_window)

@mcp.tool("bottom-half-screen", description="将当前聚焦的窗口移动到屏幕下半部分，适合上下分屏显示。")
def bottom_half() -> None:
    run_and_log("bottom-half-screen", bottom_half_window)

# ===== 四象限分屏工具 =====
@mcp.tool("top-left-screen", description="将当前聚焦的窗口移动到屏幕左上角四分之一区域，适合四窗口布局。")
def top_left() -> None:
    run_and_log("top-left-screen", top_left_quadrant_window)

@mcp.tool("top-right-screen", description="将当前聚焦的窗口移动到屏幕右上角四分之一区域，适合四窗口布局。")
def top_right() -> None:
    run_and_log("top-right-screen", top_right_quadrant_window)

@mcp.tool("bottom-left-screen", description="将当前聚焦的窗口移动到屏幕左下角四分之一区域，适合四窗口布局。")
def bottom_left() -> None:
    run_and_log("bottom-left-screen", bottom_left_quadrant_window)

@mcp.tool("bottom-right-screen", description="将当前聚焦的窗口移动到屏幕右下角四分之一区域，适合四窗口布局。")
def bottom_right() -> None:
    run_and_log("bottom-right-screen", bottom_right_quadrant_window)

# ===== 三分之一和三分之二分屏工具 =====
@mcp.tool("left-one-third-screen", description="将当前聚焦的窗口移动到屏幕左侧三分之一区域，适合三窗口布局。")
def left_third() -> None:
    run_and_log("left-one-third-screen", left_third_window)

@mcp.tool("middle-one-third-screen", description="将当前聚焦的窗口移动到屏幕中间三分之一区域，适合三窗口布局。")
def middle_third() -> None:
    run_and_log("middle-one-third-screen", middle_third_window)

@mcp.tool("right-one-third-screen", description="将当前聚焦的窗口移动到屏幕右侧三分之一区域，适合三窗口布局。")
def right_third() -> None:
    run_and_log("right-one-third-screen", right_third_window)

@mcp.tool("left-two-thirds-screen", description="将当前聚焦的窗口移动到屏幕左侧三分之二区域，适合主窗口+侧边栏布局。")
def left_two_thirds() -> None:
    run_and_log("left-two-thirds-screen", left_two_thirds_window)

@mcp.tool("right-two-thirds-screen", description="将当前聚焦的窗口移动到屏幕右侧三分之二区域，适合主窗口+侧边栏布局。")
def right_two_thirds() -> None:
    run_and_log("right-two-thirds-screen", right_two_thirds_window)

# ===== 窗口控制工具 =====
@mcp.tool("maximize-screen", description="最大化当前聚焦的窗口，保持边框和标题栏可见，适合全屏工作")
def maximize() -> None:
    run_and_log("maximize-screen", maximise_window)

@mcp.tool("fullscreen-screen", description="将当前聚焦的窗口设置为全屏模式，在macOS上使用无边框全屏，在Windows上使用标准最大化模式，适合沉浸式工作。")
def fullscreen() -> None:
    run_and_log("fullscreen-screen", fullscreen_window)

@mcp.tool("minimize-screen", description="最小化当前聚焦的窗口，在Windows上发送到任务栏，在macOS上发送到Dock，适合临时隐藏窗口。")
def minimize() -> None:
    run_and_log("minimize-screen", minimise_window)
    # 无需返回任何内容

def main():
    """启动 MCP 服务器"""
    logger.info("MCP server starting: transport=stdio")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

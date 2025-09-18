
from mcp.server.fastmcp import FastMCP
# 初始化 MCP 服务器
mcp = FastMCP("WeatherServer")


@mcp.tool()
def lucky_star(num: int) -> int:
    """
    返回一个数字 num 的幸运星
    """
    return num * 100

@mcp.tool()
def num_add(a: int, b: int) -> int:
    """
    计算两个数字相加的和并返回结果
    """
    return a + b

@mcp.tool()
def greeting(name: str) -> str:
    """
    返回一个问候语
    """
    return f"Hello, {name}!"

# 添加main函数以支持命令行入口点
def main():
    """\命令行入口点函数"""
    mcp.run(transport="stdio")

if __name__ == '__main__':
    main()



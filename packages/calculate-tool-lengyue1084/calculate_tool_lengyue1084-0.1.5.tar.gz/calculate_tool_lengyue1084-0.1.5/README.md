一个简单的计算工具包，提供基本的数学运算和问候功能。

## 功能特性
- 提供幸运星计算功能
- 支持两个数字的加法运算
- 提供自定义问候功能

## 安装方法
```bash
pip install calculate_tool_lengyue1084
```

## 使用示例
```python
from calculate import lucky_star, num_add, greeting

# 计算幸运星
result1 = lucky_star(5)  # 返回: 500

# 计算两个数字的和
result2 = num_add(10, 20)  # 返回: 30

# 获取问候语
result3 = greeting("World")  # 返回: "Hello, World!"
```

## 服务器运行
```bash
python -m src.main
```

## 依赖项
- fastapi>=0.116.2
- uvicorn>=0.35.0
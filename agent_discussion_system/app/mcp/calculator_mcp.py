#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算器MCP工具

该模块实现了简单的计算器MCP工具，用于执行数学计算。
这是一个低风险的工具，支持基本的算术运算和函数调用。
"""

from typing import Dict, Any
import math
from app.mcp.mcp_base import MCPBase, MCPPermissionLevel
from app.utils.logger import get_logger

logger = get_logger()


class CalculatorMCP(MCPBase):
    """计算器MCP工具
    
    用于执行简单的数学计算，支持以下功能：
    - 基本算术运算（+、-、*、/、%、**）
    - 数学函数调用（sin、cos、tan、log、sqrt等）
    - 常量（pi、e等）
    
    权限级别：LOW
    """
    
    def __init__(self):
        """初始化计算器MCP工具"""
        super().__init__(
            name="calculator",
            description="执行数学计算",
            permission_level=MCPPermissionLevel.LOW
        )
        
        # 允许使用的数学函数和常量
        self.allowed_functions = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "sqrt": math.sqrt,
            "abs": abs,
            "pow": pow,
            "round": round
        }
        
        self.allowed_constants = {
            "pi": math.pi,
            "e": math.e
        }
    
    def execute(self, expression: str, **kwargs) -> Dict[str, Any]:
        """执行数学计算
        
        Args:
            expression (str): 数学表达式
            **kwargs: 其他参数
        
        Returns:
            Dict[str, Any]: 执行结果，包含status、result和message字段
        """
        # 验证表达式
        if not expression:
            return {
                "status": "error",
                "result": None,
                "message": "数学表达式不能为空"
            }
        
        # 清理表达式
        expression = expression.strip()
        
        # 安全执行数学表达式
        try:
            # 构建本地命名空间，只包含允许的函数和常量
            local_namespace = {
                **self.allowed_functions,
                **self.allowed_constants
            }
            
            # 执行表达式
            result = eval(expression, {}, local_namespace)
            
            return {
                "status": "success",
                "result": {
                    "expression": expression,
                    "result": result
                },
                "message": "计算成功"
            }
        except SyntaxError:
            return {
                "status": "error",
                "result": None,
                "message": f"语法错误: {expression}"
            }
        except NameError as e:
            return {
                "status": "error",
                "result": None,
                "message": f"未知函数或常量: {str(e)}"
            }
        except ZeroDivisionError:
            return {
                "status": "error",
                "result": None,
                "message": "除以零错误"
            }
        except OverflowError:
            return {
                "status": "error",
                "result": None,
                "message": "计算结果溢出"
            }
        except Exception as e:
            return {
                "status": "error",
                "result": None,
                "message": f"计算失败: {str(e)}"
            }
    
    def get_allowed_functions(self) -> dict:
        """获取允许使用的数学函数
        
        Returns:
            dict: 允许使用的数学函数字典
        """
        return self.allowed_functions.copy()
    
    def get_allowed_constants(self) -> dict:
        """获取允许使用的数学常量
        
        Returns:
            dict: 允许使用的数学常量字典
        """
        return self.allowed_constants.copy()

"""
PyAdminKit核心模块

包含数据库抽象层、认证授权、API框架等核心功能
"""

from .database import DatabaseManager, BaseModel

__all__ = ["DatabaseManager", "BaseModel"]

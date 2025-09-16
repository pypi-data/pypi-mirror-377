"""
PyAdminKit - Python管理系统中间件

一个轻量级、高度可扩展的Python管理系统中间件，
让开发者能够在几分钟内搭建起功能完整的后台管理系统。
"""

__version__ = "0.1.0"
__author__ = "PyAdminKit Team"
__email__ = "admin@pyadminkit.com"
__description__ = "A lightweight and highly extensible Python admin system middleware"

from .core.database import DatabaseManager, db, BaseModel, Model
from .core.database.connection import ConnectionManager, connection_manager, DatabaseConfig
from .core.database.query import QueryBuilder, QuerySet
from .core.database.migrations import MigrationManager, migration_manager

__all__ = [
    "DatabaseManager",
    "db",
    "BaseModel", 
    "Model",
    "ConnectionManager",
    "connection_manager",
    "DatabaseConfig",
    "QueryBuilder",
    "QuerySet",
    "MigrationManager",
    "migration_manager",
]

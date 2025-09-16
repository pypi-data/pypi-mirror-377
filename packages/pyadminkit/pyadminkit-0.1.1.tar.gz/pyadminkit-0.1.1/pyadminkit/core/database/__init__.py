"""
数据库抽象层

提供统一的数据库操作接口，支持多种数据库类型和ORM框架
"""

from .manager import DatabaseManager, db
from .models import BaseModel, Model
from .connection import ConnectionManager, connection_manager, DatabaseConfig
from .query import QueryBuilder, QuerySet
from .migrations import MigrationManager, migration_manager, Migration

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
    "Migration",
]

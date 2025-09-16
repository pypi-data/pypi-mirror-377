"""
数据库管理器

统一管理数据库连接、模型注册和迁移
"""

from typing import Dict, List, Optional, Type, Any
import asyncio

from .connection import ConnectionManager, DatabaseConfig, connection_manager
from .models import BaseModel
from .migrations import MigrationManager, migration_manager
from .query import QuerySet


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.connection_manager = connection_manager
        self.migration_manager = migration_manager
        self._models: Dict[str, Type[BaseModel]] = {}
        self._initialized = False
    
    async def add_database(self, name: str, url: str, **kwargs):
        """添加数据库连接"""
        config = DatabaseConfig(url=url, **kwargs)
        await self.connection_manager.add_database(name, config, is_default=(name == 'default'))
    
    async def set_default_database(self, url: str, **kwargs):
        """设置默认数据库"""
        await self.add_database('default', url, **kwargs)
    
    def register_model(self, model_class: Type[BaseModel], database: Optional[str] = None):
        """注册模型"""
        model_name = model_class.__name__
        self._models[model_name] = model_class
        
        # 设置模型的默认数据库
        if database:
            model_class.__database__ = database
        
        # 自动创建表迁移
        self.migration_manager.create_table_migration(model_class)
    
    def get_model(self, name: str) -> Optional[Type[BaseModel]]:
        """获取模型类"""
        return self._models.get(name)
    
    def get_models(self) -> Dict[str, Type[BaseModel]]:
        """获取所有模型"""
        return self._models.copy()
    
    async def create_tables(self, database: Optional[str] = None):
        """创建所有表"""
        for model_class in self._models.values():
            db_name = database or model_class.__database__
            try:
                # 获取数据库类型
                pool = self.connection_manager.get_pool(db_name)
                db_type = 'mysql'  # 默认使用mysql
                
                # 根据连接池类型确定数据库类型
                from .connection import MySQLPool, PostgreSQLPool, SQLitePool
                if isinstance(pool, MySQLPool):
                    db_type = 'mysql'
                elif isinstance(pool, PostgreSQLPool):
                    db_type = 'postgresql'
                elif isinstance(pool, SQLitePool):
                    db_type = 'sqlite'
                
                sql = model_class.get_create_table_sql(db_type)
                await self.connection_manager.execute(sql, database=db_name)
                print(f"Created table for {model_class.__name__}")
            except Exception as e:
                print(f"Failed to create table for {model_class.__name__}: {e}")
    
    async def drop_tables(self, database: Optional[str] = None):
        """删除所有表"""
        for model_class in reversed(list(self._models.values())):
            db_name = database or model_class.__database__
            try:
                sql = f"DROP TABLE IF EXISTS {model_class.__tablename__}"
                await self.connection_manager.execute(sql, database=db_name)
                print(f"Dropped table for {model_class.__name__}")
            except Exception as e:
                print(f"Failed to drop table for {model_class.__name__}: {e}")
    
    async def migrate(self, database: Optional[str] = None):
        """执行数据库迁移"""
        return await self.migration_manager.migrate(database)
    
    async def rollback(self, steps: int = 1, database: Optional[str] = None):
        """回滚迁移"""
        return await self.migration_manager.rollback(steps, database)
    
    async def migration_status(self, database: Optional[str] = None):
        """获取迁移状态"""
        return await self.migration_manager.status(database)
    
    def query(self, model_class: Type[BaseModel], database: Optional[str] = None) -> QuerySet:
        """创建查询集合"""
        return QuerySet(model_class, database or model_class.__database__)
    
    async def raw_query(self, sql: str, params: List[Any] = None, database: Optional[str] = None):
        """执行原生SQL查询"""
        return await self.connection_manager.fetch_all(sql, *(params or []), database=database)
    
    async def raw_execute(self, sql: str, params: List[Any] = None, database: Optional[str] = None):
        """执行原生SQL命令"""
        return await self.connection_manager.execute(sql, *(params or []), database=database)
    
    async def transaction(self, database: Optional[str] = None):
        """获取事务上下文管理器"""
        return self.connection_manager.transaction(database)
    
    async def close(self):
        """关闭所有数据库连接"""
        await self.connection_manager.close_all()
        self._initialized = False
    
    async def initialize(self):
        """初始化数据库管理器"""
        if self._initialized:
            return
        
        # 初始化迁移管理器
        await self.migration_manager.initialize()
        self._initialized = True
    
    async def health_check(self, database: Optional[str] = None) -> Dict[str, Any]:
        """数据库健康检查"""
        try:
            # 简单的查询测试
            result = await self.connection_manager.fetch_one("SELECT 1 as test", database=database)
            return {
                'status': 'healthy',
                'database': database or 'default',
                'test_query': result is not None
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'database': database or 'default',
                'error': str(e)
            }
    
    def get_table_info(self, model_class: Type[BaseModel]) -> Dict[str, Any]:
        """获取表信息"""
        return {
            'model_name': model_class.__name__,
            'table_name': model_class.__tablename__,
            'fields': {
                name: {
                    'type': field.field_type.value,
                    'nullable': field.nullable,
                    'primary_key': field.primary_key,
                    'unique': field.unique,
                    'default': field.default,
                    'description': field.description
                }
                for name, field in model_class.__fields__.items()
            }
        }
    
    def get_database_schema(self) -> Dict[str, Any]:
        """获取数据库架构信息"""
        schema = {
            'models': {},
            'tables': []
        }
        
        for model_name, model_class in self._models.items():
            table_info = self.get_table_info(model_class)
            schema['models'][model_name] = table_info
            schema['tables'].append(model_class.__tablename__)
        
        return schema
    
    async def backup_data(self, model_class: Type[BaseModel], 
                         database: Optional[str] = None) -> List[Dict[str, Any]]:
        """备份模型数据"""
        queryset = self.query(model_class, database)
        instances = await queryset.all()
        return [instance.to_dict() for instance in instances]
    
    async def restore_data(self, model_class: Type[BaseModel], 
                          data: List[Dict[str, Any]], 
                          database: Optional[str] = None):
        """恢复模型数据"""
        for item in data:
            instance = model_class(**item)
            await instance.save(database)
    
    async def truncate_table(self, model_class: Type[BaseModel], 
                            database: Optional[str] = None):
        """清空表数据"""
        db_name = database or model_class.__database__
        sql = f"DELETE FROM {model_class.__tablename__}"
        await self.connection_manager.execute(sql, database=db_name)
    
    def create_migration(self, migration_id: str, name: str, 
                        up_sql: str, down_sql: str = ""):
        """创建自定义迁移"""
        return self.migration_manager.raw_sql_migration(migration_id, name, up_sql, down_sql)
    
    def save_migrations(self, filename: str = None):
        """保存迁移到文件"""
        self.migration_manager.save_migrations_to_file(filename)
    
    def load_migrations(self, filename: str = None):
        """从文件加载迁移"""
        self.migration_manager.load_migrations_from_file(filename)


# 全局数据库管理器实例
db = DatabaseManager()

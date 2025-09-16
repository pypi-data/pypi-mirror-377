"""
数据库迁移管理

提供版本化的数据库模式管理和迁移功能
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .connection import connection_manager, DatabaseConfig
from .models import BaseModel


@dataclass
class MigrationRecord:
    """迁移记录"""
    id: str
    name: str
    applied_at: datetime
    batch: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'applied_at': self.applied_at.isoformat(),
            'batch': self.batch
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MigrationRecord':
        return cls(
            id=data['id'],
            name=data['name'],
            applied_at=datetime.fromisoformat(data['applied_at']),
            batch=data['batch']
        )


class Migration(ABC):
    """迁移基类"""
    
    def __init__(self):
        self.id = self.get_id()
        self.name = self.get_name()
    
    @abstractmethod
    def get_id(self) -> str:
        """获取迁移ID"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取迁移名称"""
        pass
    
    @abstractmethod
    async def up(self, database: Optional[str] = None):
        """执行迁移"""
        pass
    
    @abstractmethod
    async def down(self, database: Optional[str] = None):
        """回滚迁移"""
        pass


class CreateTableMigration(Migration):
    """创建表迁移"""
    
    def __init__(self, model_class: Type[BaseModel], migration_id: str = None):
        self.model_class = model_class
        self._migration_id = migration_id
        super().__init__()
    
    def get_id(self) -> str:
        if self._migration_id:
            return self._migration_id
        return f"create_{self.model_class.__tablename__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_name(self) -> str:
        return f"Create {self.model_class.__name__} table"
    
    async def up(self, database: Optional[str] = None):
        """创建表"""
        # 获取数据库类型
        pool = connection_manager.get_pool(database)
        db_type = 'mysql'  # 默认使用mysql
        
        # 根据连接池类型确定数据库类型
        from .connection import MySQLPool, PostgreSQLPool, SQLitePool
        if isinstance(pool, MySQLPool):
            db_type = 'mysql'
        elif isinstance(pool, PostgreSQLPool):
            db_type = 'postgresql'
        elif isinstance(pool, SQLitePool):
            db_type = 'sqlite'
        
        sql = self.model_class.get_create_table_sql(db_type)
        await connection_manager.execute(sql, database=database)
    
    async def down(self, database: Optional[str] = None):
        """删除表"""
        sql = f"DROP TABLE IF EXISTS {self.model_class.__tablename__}"
        await connection_manager.execute(sql, database=database)


class AddColumnMigration(Migration):
    """添加列迁移"""
    
    def __init__(self, table: str, column: str, column_type: str, 
                 nullable: bool = True, default: Any = None, migration_id: str = None):
        self.table = table
        self.column = column
        self.column_type = column_type
        self.nullable = nullable
        self.default = default
        self._migration_id = migration_id
        super().__init__()
    
    def get_id(self) -> str:
        if self._migration_id:
            return self._migration_id
        return f"add_{self.column}_to_{self.table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_name(self) -> str:
        return f"Add {self.column} to {self.table}"
    
    async def up(self, database: Optional[str] = None):
        """添加列"""
        sql_parts = [f"ALTER TABLE {self.table} ADD COLUMN {self.column} {self.column_type}"]
        
        if not self.nullable:
            sql_parts.append("NOT NULL")
        
        if self.default is not None:
            if isinstance(self.default, str):
                sql_parts.append(f"DEFAULT '{self.default}'")
            else:
                sql_parts.append(f"DEFAULT {self.default}")
        
        sql = " ".join(sql_parts)
        await connection_manager.execute(sql, database=database)
    
    async def down(self, database: Optional[str] = None):
        """删除列"""
        sql = f"ALTER TABLE {self.table} DROP COLUMN {self.column}"
        await connection_manager.execute(sql, database=database)


class DropColumnMigration(Migration):
    """删除列迁移"""
    
    def __init__(self, table: str, column: str, migration_id: str = None):
        self.table = table
        self.column = column
        self._migration_id = migration_id
        super().__init__()
    
    def get_id(self) -> str:
        if self._migration_id:
            return self._migration_id
        return f"drop_{self.column}_from_{self.table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_name(self) -> str:
        return f"Drop {self.column} from {self.table}"
    
    async def up(self, database: Optional[str] = None):
        """删除列"""
        sql = f"ALTER TABLE {self.table} DROP COLUMN {self.column}"
        await connection_manager.execute(sql, database=database)
    
    async def down(self, database: Optional[str] = None):
        """添加列（需要提供列定义）"""
        # 这里需要保存原始列定义才能正确回滚
        # 简化实现，实际使用时需要更完善的元数据管理
        raise NotImplementedError("Column restoration requires original column definition")


class RawSQLMigration(Migration):
    """原生SQL迁移"""
    
    def __init__(self, migration_id: str, name: str, up_sql: str, down_sql: str = ""):
        self._migration_id = migration_id
        self._name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        super().__init__()
    
    def get_id(self) -> str:
        return self._migration_id
    
    def get_name(self) -> str:
        return self._name
    
    async def up(self, database: Optional[str] = None):
        """执行SQL"""
        if self.up_sql:
            # 支持多条SQL语句
            statements = [stmt.strip() for stmt in self.up_sql.split(';') if stmt.strip()]
            for stmt in statements:
                await connection_manager.execute(stmt, database=database)
    
    async def down(self, database: Optional[str] = None):
        """回滚SQL"""
        if self.down_sql:
            statements = [stmt.strip() for stmt in self.down_sql.split(';') if stmt.strip()]
            for stmt in statements:
                await connection_manager.execute(stmt, database=database)


class MigrationManager:
    """迁移管理器"""
    
    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = migrations_dir
        self.migrations_table = "pyadminkit_migrations"
        self._migrations: List[Migration] = []
    
    async def initialize(self, database: Optional[str] = None):
        """初始化迁移表"""
        # 创建迁移记录表
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.migrations_table} (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP NOT NULL,
            batch INTEGER NOT NULL
        )
        """
        
        await connection_manager.execute(create_table_sql, database=database)
    
    def add_migration(self, migration: Migration):
        """添加迁移"""
        self._migrations.append(migration)
    
    def create_table_migration(self, model_class: Type[BaseModel]) -> CreateTableMigration:
        """创建表迁移"""
        migration = CreateTableMigration(model_class)
        self.add_migration(migration)
        return migration
    
    def add_column_migration(self, table: str, column: str, column_type: str,
                           nullable: bool = True, default: Any = None) -> AddColumnMigration:
        """添加列迁移"""
        migration = AddColumnMigration(table, column, column_type, nullable, default)
        self.add_migration(migration)
        return migration
    
    def drop_column_migration(self, table: str, column: str) -> DropColumnMigration:
        """删除列迁移"""
        migration = DropColumnMigration(table, column)
        self.add_migration(migration)
        return migration
    
    def raw_sql_migration(self, migration_id: str, name: str, 
                         up_sql: str, down_sql: str = "") -> RawSQLMigration:
        """原生SQL迁移"""
        migration = RawSQLMigration(migration_id, name, up_sql, down_sql)
        self.add_migration(migration)
        return migration
    
    async def get_applied_migrations(self, database: Optional[str] = None) -> List[MigrationRecord]:
        """获取已应用的迁移"""
        try:
            query = f"SELECT * FROM {self.migrations_table} ORDER BY applied_at"
            rows = await connection_manager.fetch_all(query, database=database)
            return [MigrationRecord.from_dict(row) for row in rows]
        except:
            # 表不存在，返回空列表
            return []
    
    async def get_pending_migrations(self, database: Optional[str] = None) -> List[Migration]:
        """获取待应用的迁移"""
        applied = await self.get_applied_migrations(database)
        applied_ids = {record.id for record in applied}
        
        pending = []
        for migration in self._migrations:
            if migration.id not in applied_ids:
                pending.append(migration)
        
        # 按ID排序
        pending.sort(key=lambda m: m.id)
        return pending
    
    async def migrate(self, database: Optional[str] = None) -> List[Migration]:
        """执行所有待应用的迁移"""
        await self.initialize(database)
        
        pending = await self.get_pending_migrations(database)
        if not pending:
            return []
        
        # 获取下一个批次号
        applied = await self.get_applied_migrations(database)
        next_batch = max([record.batch for record in applied], default=0) + 1
        
        applied_migrations = []
        
        for migration in pending:
            try:
                # 执行迁移
                await migration.up(database)
                
                # 记录迁移
                record = MigrationRecord(
                    id=migration.id,
                    name=migration.name,
                    applied_at=datetime.now(),
                    batch=next_batch
                )
                
                insert_sql = f"""
                INSERT INTO {self.migrations_table} (id, name, applied_at, batch)
                VALUES (?, ?, ?, ?)
                """
                
                await connection_manager.execute(
                    insert_sql, 
                    record.id, 
                    record.name, 
                    record.applied_at.isoformat(), 
                    record.batch,
                    database=database
                )
                
                applied_migrations.append(migration)
                print(f"Applied migration: {migration.name}")
                
            except Exception as e:
                print(f"Failed to apply migration {migration.name}: {e}")
                break
        
        return applied_migrations
    
    async def rollback(self, steps: int = 1, database: Optional[str] = None) -> List[Migration]:
        """回滚迁移"""
        applied = await self.get_applied_migrations(database)
        if not applied:
            return []
        
        # 按应用时间倒序排列
        applied.sort(key=lambda r: r.applied_at, reverse=True)
        
        # 获取要回滚的迁移
        to_rollback = applied[:steps]
        
        rolled_back = []
        
        for record in to_rollback:
            # 查找对应的迁移对象
            migration = None
            for m in self._migrations:
                if m.id == record.id:
                    migration = m
                    break
            
            if not migration:
                print(f"Migration {record.name} not found, skipping rollback")
                continue
            
            try:
                # 执行回滚
                await migration.down(database)
                
                # 删除迁移记录
                delete_sql = f"DELETE FROM {self.migrations_table} WHERE id = ?"
                await connection_manager.execute(delete_sql, record.id, database=database)
                
                rolled_back.append(migration)
                print(f"Rolled back migration: {migration.name}")
                
            except Exception as e:
                print(f"Failed to rollback migration {migration.name}: {e}")
                break
        
        return rolled_back
    
    async def reset(self, database: Optional[str] = None):
        """重置所有迁移"""
        applied = await self.get_applied_migrations(database)
        if applied:
            await self.rollback(len(applied), database)
    
    async def status(self, database: Optional[str] = None) -> Dict[str, Any]:
        """获取迁移状态"""
        applied = await self.get_applied_migrations(database)
        pending = await self.get_pending_migrations(database)
        
        return {
            'applied': len(applied),
            'pending': len(pending),
            'total': len(self._migrations),
            'last_batch': max([record.batch for record in applied], default=0),
            'applied_migrations': [record.to_dict() for record in applied],
            'pending_migrations': [{'id': m.id, 'name': m.name} for m in pending]
        }
    
    def save_migrations_to_file(self, filename: str = None):
        """保存迁移定义到文件"""
        if not filename:
            filename = os.path.join(self.migrations_dir, "migrations.json")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        migrations_data = []
        for migration in self._migrations:
            migration_data = {
                'id': migration.id,
                'name': migration.name,
                'type': migration.__class__.__name__
            }
            
            # 根据迁移类型保存特定数据
            if isinstance(migration, CreateTableMigration):
                migration_data['model_class'] = migration.model_class.__name__
                migration_data['table_name'] = migration.model_class.__tablename__
            elif isinstance(migration, (AddColumnMigration, DropColumnMigration)):
                migration_data['table'] = migration.table
                migration_data['column'] = migration.column
                if isinstance(migration, AddColumnMigration):
                    migration_data['column_type'] = migration.column_type
                    migration_data['nullable'] = migration.nullable
                    migration_data['default'] = migration.default
            elif isinstance(migration, RawSQLMigration):
                migration_data['up_sql'] = migration.up_sql
                migration_data['down_sql'] = migration.down_sql
            
            migrations_data.append(migration_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(migrations_data, f, indent=2, ensure_ascii=False, default=str)
    
    def load_migrations_from_file(self, filename: str = None):
        """从文件加载迁移定义"""
        if not filename:
            filename = os.path.join(self.migrations_dir, "migrations.json")
        
        if not os.path.exists(filename):
            return
        
        with open(filename, 'r', encoding='utf-8') as f:
            migrations_data = json.load(f)
        
        for data in migrations_data:
            migration_type = data['type']
            
            if migration_type == 'RawSQLMigration':
                migration = RawSQLMigration(
                    data['id'],
                    data['name'],
                    data['up_sql'],
                    data.get('down_sql', '')
                )
                self.add_migration(migration)
            # 其他类型的迁移需要更复杂的重建逻辑
            # 这里简化处理


# 全局迁移管理器实例
migration_manager = MigrationManager()

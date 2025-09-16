"""
数据库模型基类和工具

提供统一的模型定义接口，支持多种数据库类型
"""

import json
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Type, Union, get_type_hints
from dataclasses import dataclass, field, fields
from enum import Enum
from abc import ABC, abstractmethod

from .connection import connection_manager
from .query import QueryBuilder


class FieldType(Enum):
    """字段类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    TEXT = "text"
    JSON = "json"


@dataclass
class FieldDefinition:
    """字段定义"""
    name: str
    field_type: FieldType
    nullable: bool = True
    default: Any = None
    primary_key: bool = False
    unique: bool = False
    index: bool = False
    max_length: Optional[int] = None
    choices: Optional[List[Any]] = None
    foreign_key: Optional[str] = None
    description: Optional[str] = None
    
    def to_sql_type(self, db_type: str) -> str:
        """转换为SQL数据类型"""
        type_mapping = {
            'postgresql': {
                FieldType.STRING: f"VARCHAR({self.max_length or 255})",
                FieldType.INTEGER: "INTEGER",
                FieldType.FLOAT: "REAL",
                FieldType.BOOLEAN: "BOOLEAN",
                FieldType.DATETIME: "TIMESTAMP",
                FieldType.DATE: "DATE",
                FieldType.TEXT: "TEXT",
                FieldType.JSON: "JSONB",
            },
            'mysql': {
                FieldType.STRING: f"VARCHAR({self.max_length or 255})",
                FieldType.INTEGER: "INT",
                FieldType.FLOAT: "FLOAT",
                FieldType.BOOLEAN: "BOOLEAN",
                FieldType.DATETIME: "DATETIME",
                FieldType.DATE: "DATE",
                FieldType.TEXT: "TEXT",
                FieldType.JSON: "JSON",
            },
            'sqlite': {
                FieldType.STRING: "TEXT",
                FieldType.INTEGER: "INTEGER",
                FieldType.FLOAT: "REAL",
                FieldType.BOOLEAN: "INTEGER",
                FieldType.DATETIME: "TEXT",
                FieldType.DATE: "TEXT",
                FieldType.TEXT: "TEXT",
                FieldType.JSON: "TEXT",
            }
        }
        
        return type_mapping.get(db_type, type_mapping['sqlite']).get(
            self.field_type, "TEXT"
        )


class ModelMeta(type):
    """模型元类，用于处理模型定义"""
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        # 收集字段定义
        fields_dict = {}
        annotations = namespace.get('__annotations__', {})
        
        for field_name, field_type in annotations.items():
            if field_name.startswith('_'):
                continue
                
            # 解析字段类型
            python_type = field_type
            if hasattr(field_type, '__origin__'):
                # 处理Optional类型
                if field_type.__origin__ is Union:
                    args = field_type.__args__
                    if len(args) == 2 and type(None) in args:
                        python_type = next(arg for arg in args if arg is not type(None))
            
            # 映射Python类型到FieldType
            type_mapping = {
                str: FieldType.STRING,
                int: FieldType.INTEGER,
                float: FieldType.FLOAT,
                bool: FieldType.BOOLEAN,
                datetime: FieldType.DATETIME,
                date: FieldType.DATE,
                dict: FieldType.JSON,
                list: FieldType.JSON,
            }
            
            # 检查是否为主键字段（通常id字段为主键）
            is_primary_key = field_name == 'id' and python_type == int
            
            field_def = FieldDefinition(
                name=field_name,
                field_type=type_mapping.get(python_type, FieldType.STRING),
                nullable=field_type != python_type,  # Optional类型为nullable
                default=namespace.get(field_name),
                primary_key=is_primary_key
            )
            
            fields_dict[field_name] = field_def
        
        # 设置表名
        table_name = namespace.get('__tablename__')
        if not table_name and name != 'BaseModel':
            # 自动生成表名：驼峰转下划线
            import re
            table_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            table_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', table_name).lower()
        
        namespace['__tablename__'] = table_name
        namespace['__fields__'] = fields_dict
        
        return super().__new__(mcs, name, bases, namespace)


class BaseModel(metaclass=ModelMeta):
    """模型基类"""
    
    __tablename__: Optional[str] = None
    __fields__: Dict[str, FieldDefinition] = {}
    __database__: Optional[str] = None
    
    def __init__(self, **kwargs):
        """初始化模型实例"""
        self._data = {}
        self._original_data = {}
        self._is_new = True
        
        # 设置字段值
        for field_name, field_def in self.__fields__.items():
            value = kwargs.get(field_name, field_def.default)
            self._data[field_name] = value
            self._original_data[field_name] = value
    
    def __getattr__(self, name: str) -> Any:
        """获取字段值"""
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """设置字段值"""
        if name.startswith('_') or name in ('__tablename__', '__fields__', '__database__'):
            super().__setattr__(name, value)
            return
        
        if hasattr(self, '_data') and name in self.__fields__:
            self._data[name] = value
        else:
            super().__setattr__(name, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for field_name in self.__fields__:
            value = self._data.get(field_name)
            if isinstance(value, (datetime, date)):
                result[field_name] = value.isoformat()
            elif isinstance(value, (dict, list)):
                result[field_name] = json.dumps(value) if value else None
            else:
                result[field_name] = value
        return result
    
    def from_dict(self, data: Dict[str, Any]) -> 'BaseModel':
        """从字典创建实例"""
        for field_name, value in data.items():
            if field_name in self.__fields__:
                field_def = self.__fields__[field_name]
                
                # 类型转换
                if value is not None:
                    if field_def.field_type == FieldType.DATETIME and isinstance(value, str):
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    elif field_def.field_type == FieldType.DATE and isinstance(value, str):
                        value = datetime.fromisoformat(value).date()
                    elif field_def.field_type == FieldType.JSON and isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                
                self._data[field_name] = value
                self._original_data[field_name] = value
        
        self._is_new = False
        return self
    
    def get_primary_key(self) -> Optional[str]:
        """获取主键字段名"""
        for field_name, field_def in self.__fields__.items():
            if field_def.primary_key:
                return field_name
        return None
    
    def get_primary_key_value(self) -> Any:
        """获取主键值"""
        pk_field = self.get_primary_key()
        return self._data.get(pk_field) if pk_field else None
    
    def is_dirty(self) -> bool:
        """检查是否有未保存的更改"""
        return self._data != self._original_data
    
    def get_changes(self) -> Dict[str, Any]:
        """获取更改的字段"""
        changes = {}
        for field_name in self.__fields__:
            old_value = self._original_data.get(field_name)
            new_value = self._data.get(field_name)
            if old_value != new_value:
                changes[field_name] = new_value
        return changes
    
    async def save(self, database: Optional[str] = None) -> 'BaseModel':
        """保存模型到数据库"""
        db_name = database or self.__database__
        
        if self._is_new:
            # 插入新记录
            query_builder = QueryBuilder(self.__tablename__)
            query, params = query_builder.insert(self.to_dict()).build()
            
            result = await connection_manager.execute(query, *params, database=db_name)
            
            # 如果有自增主键，更新主键值
            pk_field = self.get_primary_key()
            if pk_field and self._data.get(pk_field) is None:
                # 这里需要根据不同数据库获取插入ID的方式
                # 暂时简化处理
                pass
            
            self._is_new = False
        else:
            # 更新现有记录
            changes = self.get_changes()
            if changes:
                pk_field = self.get_primary_key()
                pk_value = self.get_primary_key_value()
                
                if not pk_field or pk_value is None:
                    raise ValueError("Cannot update record without primary key")
                
                query_builder = QueryBuilder(self.__tablename__)
                query, params = query_builder.update(changes).where(pk_field, pk_value).build()
                
                await connection_manager.execute(query, *params, database=db_name)
        
        # 更新原始数据
        self._original_data = self._data.copy()
        return self
    
    async def delete(self, database: Optional[str] = None) -> bool:
        """从数据库删除模型"""
        if self._is_new:
            return False
        
        pk_field = self.get_primary_key()
        pk_value = self.get_primary_key_value()
        
        if not pk_field or pk_value is None:
            raise ValueError("Cannot delete record without primary key")
        
        db_name = database or self.__database__
        
        query_builder = QueryBuilder(self.__tablename__)
        query, params = query_builder.delete().where(pk_field, pk_value).build()
        
        result = await connection_manager.execute(query, *params, database=db_name)
        return result > 0
    
    async def refresh(self, database: Optional[str] = None) -> 'BaseModel':
        """从数据库刷新模型数据"""
        if self._is_new:
            raise ValueError("Cannot refresh unsaved record")
        
        pk_field = self.get_primary_key()
        pk_value = self.get_primary_key_value()
        
        if not pk_field or pk_value is None:
            raise ValueError("Cannot refresh record without primary key")
        
        db_name = database or self.__database__
        
        query_builder = QueryBuilder(self.__tablename__)
        query, params = query_builder.select().where(pk_field, pk_value).build()
        
        data = await connection_manager.fetch_one(query, *params, database=db_name)
        if data:
            self.from_dict(data)
        
        return self
    
    @classmethod
    async def find_by_id(cls, pk_value: Any, database: Optional[str] = None) -> Optional['BaseModel']:
        """根据主键查找记录"""
        instance = cls()
        pk_field = instance.get_primary_key()
        
        if not pk_field:
            raise ValueError(f"Model {cls.__name__} has no primary key")
        
        db_name = database or cls.__database__
        
        query_builder = QueryBuilder(cls.__tablename__)
        query, params = query_builder.select().where(pk_field, pk_value).build()
        
        data = await connection_manager.fetch_one(query, *params, database=db_name)
        if data:
            return cls().from_dict(data)
        
        return None
    
    @classmethod
    async def find_all(cls, database: Optional[str] = None, limit: Optional[int] = None, 
                      offset: Optional[int] = None, **filters) -> List['BaseModel']:
        """查找所有记录"""
        db_name = database or cls.__database__
        
        query_builder = QueryBuilder(cls.__tablename__).select()
        
        # 添加过滤条件
        for field_name, value in filters.items():
            query_builder = query_builder.where(field_name, value)
        
        # 添加分页
        if limit:
            query_builder = query_builder.limit(limit)
        if offset:
            query_builder = query_builder.offset(offset)
        
        query, params = query_builder.build()
        
        rows = await connection_manager.fetch_all(query, *params, database=db_name)
        return [cls().from_dict(row) for row in rows]
    
    @classmethod
    async def find_one(cls, database: Optional[str] = None, **filters) -> Optional['BaseModel']:
        """查找单条记录"""
        results = await cls.find_all(database=database, limit=1, **filters)
        return results[0] if results else None
    
    @classmethod
    async def count(cls, database: Optional[str] = None, **filters) -> int:
        """统计记录数量"""
        db_name = database or cls.__database__
        
        query_builder = QueryBuilder(cls.__tablename__).select("COUNT(*)")
        
        # 添加过滤条件
        for field_name, value in filters.items():
            query_builder = query_builder.where(field_name, value)
        
        query, params = query_builder.build()
        
        result = await connection_manager.fetch_one(query, *params, database=db_name)
        return list(result.values())[0] if result else 0
    
    @classmethod
    def get_create_table_sql(cls, db_type: str = 'postgresql') -> str:
        """生成创建表的SQL"""
        if not cls.__tablename__:
            raise ValueError(f"Model {cls.__name__} has no table name")
        
        columns = []
        constraints = []
        
        for field_name, field_def in cls.__fields__.items():
            column_parts = [field_name, field_def.to_sql_type(db_type)]
            
            if not field_def.nullable:
                column_parts.append("NOT NULL")
            
            if field_def.default is not None:
                if isinstance(field_def.default, str):
                    column_parts.append(f"DEFAULT '{field_def.default}'")
                else:
                    column_parts.append(f"DEFAULT {field_def.default}")
            
            if field_def.primary_key:
                if db_type in ('postgresql', 'mysql'):
                    column_parts.append("PRIMARY KEY")
                    if field_def.field_type == FieldType.INTEGER:
                        if db_type == 'postgresql':
                            column_parts[1] = "SERIAL"
                        else:  # mysql
                            column_parts.append("AUTO_INCREMENT")
                else:  # sqlite
                    column_parts.append("PRIMARY KEY AUTOINCREMENT")
            
            if field_def.unique and not field_def.primary_key:
                column_parts.append("UNIQUE")
            
            columns.append(" ".join(column_parts))
            
            # 外键约束
            if field_def.foreign_key:
                fk_table, fk_column = field_def.foreign_key.split('.')
                constraints.append(
                    f"FOREIGN KEY ({field_name}) REFERENCES {fk_table}({fk_column})"
                )
        
        # 组装SQL
        sql_parts = [f"CREATE TABLE {cls.__tablename__} ("]
        sql_parts.append("    " + ",\n    ".join(columns))
        
        if constraints:
            sql_parts.append(",\n    " + ",\n    ".join(constraints))
        
        sql_parts.append(")")
        
        return "\n".join(sql_parts)


# 为了向后兼容
Model = BaseModel

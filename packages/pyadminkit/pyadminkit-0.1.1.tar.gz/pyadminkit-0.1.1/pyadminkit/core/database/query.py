"""
查询构建器

提供链式调用的SQL查询构建功能
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from enum import Enum


class JoinType(Enum):
    """连接类型"""
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL JOIN"


class OrderDirection(Enum):
    """排序方向"""
    ASC = "ASC"
    DESC = "DESC"


class QueryBuilder:
    """SQL查询构建器"""
    
    def __init__(self, table: str):
        self.table = table
        self._select_fields: List[str] = []
        self._where_conditions: List[Tuple[str, str, Any]] = []
        self._joins: List[Tuple[JoinType, str, str]] = []
        self._group_by_fields: List[str] = []
        self._having_conditions: List[Tuple[str, str, Any]] = []
        self._order_by_fields: List[Tuple[str, OrderDirection]] = []
        self._limit_count: Optional[int] = None
        self._offset_count: Optional[int] = None
        self._insert_data: Optional[Dict[str, Any]] = None
        self._update_data: Optional[Dict[str, Any]] = None
        self._is_delete: bool = False
        self._distinct: bool = False
    
    def select(self, *fields: str) -> 'QueryBuilder':
        """设置SELECT字段"""
        if fields:
            self._select_fields.extend(fields)
        else:
            self._select_fields = ["*"]
        return self
    
    def distinct(self) -> 'QueryBuilder':
        """设置DISTINCT"""
        self._distinct = True
        return self
    
    def where(self, field: str, value: Any, operator: str = "=") -> 'QueryBuilder':
        """添加WHERE条件"""
        self._where_conditions.append((field, operator, value))
        return self
    
    def where_in(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """添加WHERE IN条件"""
        self._where_conditions.append((field, "IN", values))
        return self
    
    def where_not_in(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """添加WHERE NOT IN条件"""
        self._where_conditions.append((field, "NOT IN", values))
        return self
    
    def where_null(self, field: str) -> 'QueryBuilder':
        """添加WHERE IS NULL条件"""
        self._where_conditions.append((field, "IS", None))
        return self
    
    def where_not_null(self, field: str) -> 'QueryBuilder':
        """添加WHERE IS NOT NULL条件"""
        self._where_conditions.append((field, "IS NOT", None))
        return self
    
    def where_like(self, field: str, pattern: str) -> 'QueryBuilder':
        """添加WHERE LIKE条件"""
        self._where_conditions.append((field, "LIKE", pattern))
        return self
    
    def where_between(self, field: str, start: Any, end: Any) -> 'QueryBuilder':
        """添加WHERE BETWEEN条件"""
        self._where_conditions.append((field, "BETWEEN", (start, end)))
        return self
    
    def where_gt(self, field: str, value: Any) -> 'QueryBuilder':
        """添加WHERE >条件"""
        return self.where(field, value, ">")
    
    def where_gte(self, field: str, value: Any) -> 'QueryBuilder':
        """添加WHERE >=条件"""
        return self.where(field, value, ">=")
    
    def where_lt(self, field: str, value: Any) -> 'QueryBuilder':
        """添加WHERE <条件"""
        return self.where(field, value, "<")
    
    def where_lte(self, field: str, value: Any) -> 'QueryBuilder':
        """添加WHERE <=条件"""
        return self.where(field, value, "<=")
    
    def where_ne(self, field: str, value: Any) -> 'QueryBuilder':
        """添加WHERE !=条件"""
        return self.where(field, value, "!=")
    
    def join(self, table: str, on_condition: str, join_type: JoinType = JoinType.INNER) -> 'QueryBuilder':
        """添加JOIN"""
        self._joins.append((join_type, table, on_condition))
        return self
    
    def inner_join(self, table: str, on_condition: str) -> 'QueryBuilder':
        """添加INNER JOIN"""
        return self.join(table, on_condition, JoinType.INNER)
    
    def left_join(self, table: str, on_condition: str) -> 'QueryBuilder':
        """添加LEFT JOIN"""
        return self.join(table, on_condition, JoinType.LEFT)
    
    def right_join(self, table: str, on_condition: str) -> 'QueryBuilder':
        """添加RIGHT JOIN"""
        return self.join(table, on_condition, JoinType.RIGHT)
    
    def full_join(self, table: str, on_condition: str) -> 'QueryBuilder':
        """添加FULL JOIN"""
        return self.join(table, on_condition, JoinType.FULL)
    
    def group_by(self, *fields: str) -> 'QueryBuilder':
        """添加GROUP BY"""
        self._group_by_fields.extend(fields)
        return self
    
    def having(self, field: str, value: Any, operator: str = "=") -> 'QueryBuilder':
        """添加HAVING条件"""
        self._having_conditions.append((field, operator, value))
        return self
    
    def order_by(self, field: str, direction: Union[OrderDirection, str] = OrderDirection.ASC) -> 'QueryBuilder':
        """添加ORDER BY"""
        if isinstance(direction, str):
            direction = OrderDirection.ASC if direction.upper() == "ASC" else OrderDirection.DESC
        self._order_by_fields.append((field, direction))
        return self
    
    def order_by_asc(self, field: str) -> 'QueryBuilder':
        """添加ORDER BY ASC"""
        return self.order_by(field, OrderDirection.ASC)
    
    def order_by_desc(self, field: str) -> 'QueryBuilder':
        """添加ORDER BY DESC"""
        return self.order_by(field, OrderDirection.DESC)
    
    def limit(self, count: int) -> 'QueryBuilder':
        """设置LIMIT"""
        self._limit_count = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """设置OFFSET"""
        self._offset_count = count
        return self
    
    def paginate(self, page: int, per_page: int) -> 'QueryBuilder':
        """分页"""
        self._limit_count = per_page
        self._offset_count = (page - 1) * per_page
        return self
    
    def insert(self, data: Dict[str, Any]) -> 'QueryBuilder':
        """设置INSERT数据"""
        self._insert_data = data
        return self
    
    def update(self, data: Dict[str, Any]) -> 'QueryBuilder':
        """设置UPDATE数据"""
        self._update_data = data
        return self
    
    def delete(self) -> 'QueryBuilder':
        """设置DELETE操作"""
        self._is_delete = True
        return self
    
    def build(self) -> Tuple[str, List[Any]]:
        """构建SQL查询和参数"""
        if self._insert_data:
            return self._build_insert()
        elif self._update_data:
            return self._build_update()
        elif self._is_delete:
            return self._build_delete()
        else:
            return self._build_select()
    
    def _build_select(self) -> Tuple[str, List[Any]]:
        """构建SELECT查询"""
        params = []
        
        # SELECT子句
        fields = self._select_fields if self._select_fields else ["*"]
        distinct_keyword = "DISTINCT " if self._distinct else ""
        select_clause = f"SELECT {distinct_keyword}{', '.join(fields)}"
        
        # FROM子句
        from_clause = f"FROM {self.table}"
        
        # JOIN子句
        join_clauses = []
        for join_type, table, condition in self._joins:
            join_clauses.append(f"{join_type.value} {table} ON {condition}")
        
        # WHERE子句
        where_clause, where_params = self._build_where_clause()
        params.extend(where_params)
        
        # GROUP BY子句
        group_by_clause = ""
        if self._group_by_fields:
            group_by_clause = f"GROUP BY {', '.join(self._group_by_fields)}"
        
        # HAVING子句
        having_clause = ""
        if self._having_conditions:
            having_parts = []
            for field, operator, value in self._having_conditions:
                if operator == "IN" or operator == "NOT IN":
                    placeholders = ", ".join(["?" for _ in value])
                    having_parts.append(f"{field} {operator} ({placeholders})")
                    params.extend(value)
                elif operator == "BETWEEN":
                    having_parts.append(f"{field} BETWEEN ? AND ?")
                    params.extend(value)
                elif value is None:
                    having_parts.append(f"{field} {operator} NULL")
                else:
                    having_parts.append(f"{field} {operator} ?")
                    params.append(value)
            having_clause = f"HAVING {' AND '.join(having_parts)}"
        
        # ORDER BY子句
        order_by_clause = ""
        if self._order_by_fields:
            order_parts = [f"{field} {direction.value}" for field, direction in self._order_by_fields]
            order_by_clause = f"ORDER BY {', '.join(order_parts)}"
        
        # LIMIT和OFFSET子句
        limit_clause = ""
        if self._limit_count is not None:
            limit_clause = f"LIMIT {self._limit_count}"
            if self._offset_count is not None:
                limit_clause += f" OFFSET {self._offset_count}"
        
        # 组装完整查询
        query_parts = [select_clause, from_clause]
        query_parts.extend(join_clauses)
        if where_clause:
            query_parts.append(where_clause)
        if group_by_clause:
            query_parts.append(group_by_clause)
        if having_clause:
            query_parts.append(having_clause)
        if order_by_clause:
            query_parts.append(order_by_clause)
        if limit_clause:
            query_parts.append(limit_clause)
        
        return " ".join(query_parts), params
    
    def _build_insert(self) -> Tuple[str, List[Any]]:
        """构建INSERT查询"""
        if not self._insert_data:
            raise ValueError("No data provided for INSERT")
        
        fields = list(self._insert_data.keys())
        values = list(self._insert_data.values())
        placeholders = ", ".join(["?" for _ in fields])
        
        query = f"INSERT INTO {self.table} ({', '.join(fields)}) VALUES ({placeholders})"
        return query, values
    
    def _build_update(self) -> Tuple[str, List[Any]]:
        """构建UPDATE查询"""
        if not self._update_data:
            raise ValueError("No data provided for UPDATE")
        
        params = []
        
        # SET子句
        set_parts = []
        for field, value in self._update_data.items():
            set_parts.append(f"{field} = ?")
            params.append(value)
        set_clause = f"SET {', '.join(set_parts)}"
        
        # WHERE子句
        where_clause, where_params = self._build_where_clause()
        params.extend(where_params)
        
        query_parts = [f"UPDATE {self.table}", set_clause]
        if where_clause:
            query_parts.append(where_clause)
        
        return " ".join(query_parts), params
    
    def _build_delete(self) -> Tuple[str, List[Any]]:
        """构建DELETE查询"""
        params = []
        
        # WHERE子句
        where_clause, where_params = self._build_where_clause()
        params.extend(where_params)
        
        query_parts = [f"DELETE FROM {self.table}"]
        if where_clause:
            query_parts.append(where_clause)
        
        return " ".join(query_parts), params
    
    def _build_where_clause(self) -> Tuple[str, List[Any]]:
        """构建WHERE子句"""
        if not self._where_conditions:
            return "", []
        
        where_parts = []
        params = []
        
        for field, operator, value in self._where_conditions:
            if operator == "IN" or operator == "NOT IN":
                if not value:  # 空列表
                    where_parts.append("1=0" if operator == "IN" else "1=1")
                else:
                    placeholders = ", ".join(["?" for _ in value])
                    where_parts.append(f"{field} {operator} ({placeholders})")
                    params.extend(value)
            elif operator == "BETWEEN":
                where_parts.append(f"{field} BETWEEN ? AND ?")
                params.extend(value)
            elif value is None:
                where_parts.append(f"{field} {operator} NULL")
            else:
                where_parts.append(f"{field} {operator} ?")
                params.append(value)
        
        where_clause = f"WHERE {' AND '.join(where_parts)}"
        return where_clause, params
    
    def clone(self) -> 'QueryBuilder':
        """克隆查询构建器"""
        new_builder = QueryBuilder(self.table)
        new_builder._select_fields = self._select_fields.copy()
        new_builder._where_conditions = self._where_conditions.copy()
        new_builder._joins = self._joins.copy()
        new_builder._group_by_fields = self._group_by_fields.copy()
        new_builder._having_conditions = self._having_conditions.copy()
        new_builder._order_by_fields = self._order_by_fields.copy()
        new_builder._limit_count = self._limit_count
        new_builder._offset_count = self._offset_count
        new_builder._insert_data = self._insert_data.copy() if self._insert_data else None
        new_builder._update_data = self._update_data.copy() if self._update_data else None
        new_builder._is_delete = self._is_delete
        new_builder._distinct = self._distinct
        return new_builder
    
    def to_sql(self) -> str:
        """转换为SQL字符串（用于调试）"""
        query, params = self.build()
        
        # 简单的参数替换（仅用于调试）
        for param in params:
            if isinstance(param, str):
                query = query.replace("?", f"'{param}'", 1)
            elif param is None:
                query = query.replace("?", "NULL", 1)
            else:
                query = query.replace("?", str(param), 1)
        
        return query


class RawQuery:
    """原生SQL查询"""
    
    def __init__(self, sql: str, params: Optional[List[Any]] = None):
        self.sql = sql
        self.params = params or []
    
    def build(self) -> Tuple[str, List[Any]]:
        """构建查询"""
        return self.sql, self.params


class QuerySet:
    """查询集合，提供更高级的查询接口"""
    
    def __init__(self, model_class, database: Optional[str] = None):
        self.model_class = model_class
        self.database = database
        self._query_builder = QueryBuilder(model_class.__tablename__)
        self._prefetch_related = []
        self._select_related = []
    
    def filter(self, **kwargs) -> 'QuerySet':
        """过滤条件"""
        new_qs = self._clone()
        for field, value in kwargs.items():
            # 支持字段查找
            if '__' in field:
                field_name, lookup = field.split('__', 1)
                if lookup == 'in':
                    new_qs._query_builder.where_in(field_name, value)
                elif lookup == 'gt':
                    new_qs._query_builder.where_gt(field_name, value)
                elif lookup == 'gte':
                    new_qs._query_builder.where_gte(field_name, value)
                elif lookup == 'lt':
                    new_qs._query_builder.where_lt(field_name, value)
                elif lookup == 'lte':
                    new_qs._query_builder.where_lte(field_name, value)
                elif lookup == 'like':
                    new_qs._query_builder.where_like(field_name, value)
                elif lookup == 'isnull':
                    if value:
                        new_qs._query_builder.where_null(field_name)
                    else:
                        new_qs._query_builder.where_not_null(field_name)
                else:
                    new_qs._query_builder.where(field_name, value)
            else:
                new_qs._query_builder.where(field, value)
        return new_qs
    
    def exclude(self, **kwargs) -> 'QuerySet':
        """排除条件"""
        new_qs = self._clone()
        for field, value in kwargs.items():
            new_qs._query_builder.where(field, value, "!=")
        return new_qs
    
    def order_by(self, *fields) -> 'QuerySet':
        """排序"""
        new_qs = self._clone()
        for field in fields:
            if field.startswith('-'):
                new_qs._query_builder.order_by_desc(field[1:])
            else:
                new_qs._query_builder.order_by_asc(field)
        return new_qs
    
    def limit(self, count: int) -> 'QuerySet':
        """限制数量"""
        new_qs = self._clone()
        new_qs._query_builder.limit(count)
        return new_qs
    
    def offset(self, count: int) -> 'QuerySet':
        """偏移量"""
        new_qs = self._clone()
        new_qs._query_builder.offset(count)
        return new_qs
    
    def distinct(self) -> 'QuerySet':
        """去重"""
        new_qs = self._clone()
        new_qs._query_builder.distinct()
        return new_qs
    
    def select_related(self, *fields) -> 'QuerySet':
        """预加载关联对象"""
        new_qs = self._clone()
        new_qs._select_related.extend(fields)
        return new_qs
    
    def prefetch_related(self, *fields) -> 'QuerySet':
        """预获取关联对象"""
        new_qs = self._clone()
        new_qs._prefetch_related.extend(fields)
        return new_qs
    
    async def all(self) -> List:
        """获取所有结果"""
        from .connection import connection_manager
        
        self._query_builder.select()
        query, params = self._query_builder.build()
        
        rows = await connection_manager.fetch_all(query, *params, database=self.database)
        return [self.model_class().from_dict(row) for row in rows]
    
    async def first(self):
        """获取第一个结果"""
        results = await self.limit(1).all()
        return results[0] if results else None
    
    async def last(self):
        """获取最后一个结果"""
        # 需要反转排序
        new_qs = self._clone()
        # 简化实现，实际需要处理排序反转
        results = await new_qs.limit(1).all()
        return results[0] if results else None
    
    async def get(self, **kwargs):
        """获取单个对象"""
        results = await self.filter(**kwargs).limit(2).all()
        if not results:
            raise ValueError("Object not found")
        if len(results) > 1:
            raise ValueError("Multiple objects returned")
        return results[0]
    
    async def count(self) -> int:
        """统计数量"""
        from .connection import connection_manager
        
        query_builder = QueryBuilder(self.model_class.__tablename__).select("COUNT(*)")
        
        # 复制WHERE条件
        for condition in self._query_builder._where_conditions:
            query_builder._where_conditions.append(condition)
        
        query, params = query_builder.build()
        result = await connection_manager.fetch_one(query, *params, database=self.database)
        return list(result.values())[0] if result else 0
    
    async def exists(self) -> bool:
        """检查是否存在"""
        count = await self.limit(1).count()
        return count > 0
    
    async def delete(self) -> int:
        """删除记录"""
        from .connection import connection_manager
        
        query_builder = QueryBuilder(self.model_class.__tablename__).delete()
        
        # 复制WHERE条件
        for condition in self._query_builder._where_conditions:
            query_builder._where_conditions.append(condition)
        
        query, params = query_builder.build()
        return await connection_manager.execute(query, *params, database=self.database)
    
    async def update(self, **kwargs) -> int:
        """批量更新"""
        from .connection import connection_manager
        
        query_builder = QueryBuilder(self.model_class.__tablename__).update(kwargs)
        
        # 复制WHERE条件
        for condition in self._query_builder._where_conditions:
            query_builder._where_conditions.append(condition)
        
        query, params = query_builder.build()
        return await connection_manager.execute(query, *params, database=self.database)
    
    def _clone(self) -> 'QuerySet':
        """克隆查询集合"""
        new_qs = QuerySet(self.model_class, self.database)
        new_qs._query_builder = self._query_builder.clone()
        new_qs._prefetch_related = self._prefetch_related.copy()
        new_qs._select_related = self._select_related.copy()
        return new_qs

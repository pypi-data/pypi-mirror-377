"""
数据库连接管理器

提供统一的数据库连接管理，支持多种数据库类型和连接池
"""

import asyncio
from typing import Dict, Any, Optional, Union, Type
from urllib.parse import urlparse
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

try:
    import aiomysql
    AIOMYSQL_AVAILABLE = True
except ImportError:
    AIOMYSQL_AVAILABLE = False

try:
    import aiosqlite
    AIOSQLITE_AVAILABLE = True
except ImportError:
    AIOSQLITE_AVAILABLE = False

try:
    import motor.motor_asyncio
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False


class DatabaseType(Enum):
    """支持的数据库类型"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"


@dataclass
class DatabaseConfig:
    """数据库配置"""
    url: str
    min_connections: int = 1
    max_connections: int = 10
    timeout: int = 30
    retry_attempts: int = 3
    pool_recycle: int = 3600
    echo: bool = False
    
    def __post_init__(self):
        """解析数据库URL"""
        parsed = urlparse(self.url)
        self.scheme = parsed.scheme
        self.host = parsed.hostname
        self.port = parsed.port
        self.database = parsed.path.lstrip('/')
        self.username = parsed.username
        self.password = parsed.password
        
        # 确定数据库类型
        if self.scheme in ('postgresql', 'postgres'):
            self.db_type = DatabaseType.POSTGRESQL
        elif self.scheme == 'mysql':
            self.db_type = DatabaseType.MYSQL
        elif self.scheme == 'sqlite':
            self.db_type = DatabaseType.SQLITE
        elif self.scheme == 'mongodb':
            self.db_type = DatabaseType.MONGODB
        else:
            raise ValueError(f"Unsupported database scheme: {self.scheme}")


class ConnectionPool:
    """数据库连接池基类"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool = None
        self._closed = False
    
    async def initialize(self):
        """初始化连接池"""
        raise NotImplementedError
    
    async def close(self):
        """关闭连接池"""
        if self._pool and not self._closed:
            if hasattr(self._pool, 'close'):
                await self._pool.close()
            self._closed = True
    
    @asynccontextmanager
    async def acquire(self):
        """获取数据库连接"""
        raise NotImplementedError
    
    async def execute(self, query: str, *args) -> Any:
        """执行SQL查询"""
        raise NotImplementedError
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        """查询单条记录"""
        raise NotImplementedError
    
    async def fetch_all(self, query: str, *args) -> list:
        """查询多条记录"""
        raise NotImplementedError


class PostgreSQLPool(ConnectionPool):
    """PostgreSQL连接池"""
    
    async def initialize(self):
        """初始化PostgreSQL连接池"""
        if not ASYNCPG_AVAILABLE:
            raise ImportError("asyncpg is required for PostgreSQL support")
        
        self._pool = await asyncpg.create_pool(
            host=self.config.host,
            port=self.config.port or 5432,
            user=self.config.username,
            password=self.config.password,
            database=self.config.database,
            min_size=self.config.min_connections,
            max_size=self.config.max_connections,
            command_timeout=self.config.timeout
        )
    
    async def close(self):
        """关闭PostgreSQL连接池"""
        if self._pool and not self._closed:
            await self._pool.close()
            self._closed = True
    
    @asynccontextmanager
    async def acquire(self):
        """获取PostgreSQL连接"""
        async with self._pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args) -> Any:
        """执行PostgreSQL查询"""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        """查询单条PostgreSQL记录"""
        async with self.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, *args) -> list:
        """查询多条PostgreSQL记录"""
        async with self.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]


class MySQLPool(ConnectionPool):
    """MySQL连接池"""
    
    async def initialize(self):
        """初始化MySQL连接池"""
        if not AIOMYSQL_AVAILABLE:
            raise ImportError("aiomysql is required for MySQL support")
        
        self._pool = await aiomysql.create_pool(
            host=self.config.host,
            port=self.config.port or 3306,
            user=self.config.username,
            password=self.config.password,
            db=self.config.database,
            minsize=self.config.min_connections,
            maxsize=self.config.max_connections,
            echo=self.config.echo
        )
    
    async def close(self):
        """关闭MySQL连接池"""
        if self._pool and not self._closed:
            self._pool.close()
            await self._pool.wait_closed()
            self._closed = True
    
    @asynccontextmanager
    async def acquire(self):
        """获取MySQL连接"""
        async with self._pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args) -> Any:
        """执行MySQL查询"""
        # MySQL使用%s占位符，需要转换查询
        mysql_query = query.replace('?', '%s')
        async with self.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(mysql_query, args)
                await conn.commit()
                return cursor.rowcount
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        """查询单条MySQL记录"""
        # MySQL使用%s占位符，需要转换查询
        mysql_query = query.replace('?', '%s')
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(mysql_query, args)
                return await cursor.fetchone()
    
    async def fetch_all(self, query: str, *args) -> list:
        """查询多条MySQL记录"""
        # MySQL使用%s占位符，需要转换查询
        mysql_query = query.replace('?', '%s')
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(mysql_query, args)
                return await cursor.fetchall()


class SQLitePool(ConnectionPool):
    """SQLite连接池"""
    
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self._connection = None
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """初始化SQLite连接"""
        if not AIOSQLITE_AVAILABLE:
            raise ImportError("aiosqlite is required for SQLite support")
        
        self._connection = await aiosqlite.connect(
            self.config.database,
            timeout=self.config.timeout
        )
        self._connection.row_factory = aiosqlite.Row
    
    async def close(self):
        """关闭SQLite连接"""
        if self._connection and not self._closed:
            await self._connection.close()
            self._closed = True
    
    @asynccontextmanager
    async def acquire(self):
        """获取SQLite连接"""
        async with self._lock:
            yield self._connection
    
    async def execute(self, query: str, *args) -> Any:
        """执行SQLite查询"""
        async with self.acquire() as conn:
            cursor = await conn.execute(query, args)
            await conn.commit()
            return cursor.rowcount
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        """查询单条SQLite记录"""
        async with self.acquire() as conn:
            cursor = await conn.execute(query, args)
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, *args) -> list:
        """查询多条SQLite记录"""
        async with self.acquire() as conn:
            cursor = await conn.execute(query, args)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


class MongoDBPool(ConnectionPool):
    """MongoDB连接池"""
    
    async def initialize(self):
        """初始化MongoDB连接"""
        if not MOTOR_AVAILABLE:
            raise ImportError("motor is required for MongoDB support")
        
        self._client = motor.motor_asyncio.AsyncIOMotorClient(
            self.config.url,
            maxPoolSize=self.config.max_connections,
            minPoolSize=self.config.min_connections,
            serverSelectionTimeoutMS=self.config.timeout * 1000
        )
        self._db = self._client[self.config.database]
    
    async def close(self):
        """关闭MongoDB连接"""
        if hasattr(self, '_client') and not self._closed:
            self._client.close()
            self._closed = True
    
    @asynccontextmanager
    async def acquire(self):
        """获取MongoDB数据库对象"""
        yield self._db
    
    async def execute(self, collection: str, operation: str, *args, **kwargs) -> Any:
        """执行MongoDB操作"""
        async with self.acquire() as db:
            coll = db[collection]
            method = getattr(coll, operation)
            return await method(*args, **kwargs)


class ConnectionManager:
    """数据库连接管理器"""
    
    def __init__(self):
        self._pools: Dict[str, ConnectionPool] = {}
        self._default_pool: Optional[ConnectionPool] = None
    
    async def add_database(self, name: str, config: DatabaseConfig, is_default: bool = False):
        """添加数据库连接"""
        pool = self._create_pool(config)
        await pool.initialize()
        
        self._pools[name] = pool
        if is_default or not self._default_pool:
            self._default_pool = pool
    
    def _create_pool(self, config: DatabaseConfig) -> ConnectionPool:
        """根据配置创建连接池"""
        if config.db_type == DatabaseType.POSTGRESQL:
            return PostgreSQLPool(config)
        elif config.db_type == DatabaseType.MYSQL:
            return MySQLPool(config)
        elif config.db_type == DatabaseType.SQLITE:
            return SQLitePool(config)
        elif config.db_type == DatabaseType.MONGODB:
            return MongoDBPool(config)
        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")
    
    def get_pool(self, name: Optional[str] = None) -> ConnectionPool:
        """获取连接池"""
        if name is None:
            if self._default_pool is None:
                raise RuntimeError("No default database configured")
            return self._default_pool
        
        if name not in self._pools:
            raise ValueError(f"Database '{name}' not found")
        
        return self._pools[name]
    
    async def close_all(self):
        """关闭所有连接池"""
        for pool in self._pools.values():
            await pool.close()
        self._pools.clear()
        self._default_pool = None
    
    async def execute(self, query: str, *args, database: Optional[str] = None) -> Any:
        """执行查询"""
        pool = self.get_pool(database)
        return await pool.execute(query, *args)
    
    async def fetch_one(self, query: str, *args, database: Optional[str] = None) -> Optional[Dict]:
        """查询单条记录"""
        pool = self.get_pool(database)
        return await pool.fetch_one(query, *args)
    
    async def fetch_all(self, query: str, *args, database: Optional[str] = None) -> list:
        """查询多条记录"""
        pool = self.get_pool(database)
        return await pool.fetch_all(query, *args)
    
    @asynccontextmanager
    async def transaction(self, database: Optional[str] = None):
        """事务上下文管理器"""
        pool = self.get_pool(database)
        
        if isinstance(pool, PostgreSQLPool):
            async with pool.acquire() as conn:
                # PostgreSQL
                async with conn.transaction():
                    yield conn
        elif isinstance(pool, MySQLPool):
            async with pool.acquire() as conn:
                # MySQL
                await conn.begin()
                try:
                    yield conn
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise
        elif isinstance(pool, SQLitePool):
            async with pool.acquire() as conn:
                try:
                    yield conn
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise
        else:
            # MongoDB不支持传统事务，直接返回连接
            async with pool.acquire() as db:
                yield db


# 全局连接管理器实例
connection_manager = ConnectionManager()

# PyAdminKit

一个轻量级、高度可扩展的Python管理系统中间件，让开发者能够在几分钟内搭建起功能完整的后台管理系统。

## 🎯 特性

- **开箱即用** - 5分钟内搭建完整管理系统
- **多数据库支持** - PostgreSQL、MySQL、SQLite、MongoDB
- **异步支持** - 基于现代异步编程，高性能处理
- **类型安全** - 完整的类型提示支持
- **灵活查询** - 链式查询构建器和QuerySet
- **自动迁移** - 版本化数据库迁移管理
- **事务支持** - 完整的数据库事务功能

## 🚀 快速开始

### 安装

```bash
pip install pyadminkit
```

### 基本使用

```python
import asyncio
from datetime import datetime
from pyadminkit import db, BaseModel

# 定义模型
class User(BaseModel):
    __tablename__ = "users"
    
    id: int = None
    username: str
    email: str
    is_active: bool = True
    created_at: datetime = None

# 设置数据库并运行
async def main():
    # 连接数据库
    await db.set_default_database("sqlite:///app.db")
    
    # 注册模型
    db.register_model(User)
    
    # 运行迁移
    await db.migrate()
    
    # 创建用户
    user = User(username="alice", email="alice@example.com")
    await user.save()
    
    # 查询用户
    users = await User.find_all()
    print(f"找到 {len(users)} 个用户")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 核心功能

### 1. 模型定义

```python
from pyadminkit import BaseModel
from datetime import datetime
from typing import Optional

class Product(BaseModel):
    __tablename__ = "products"
    
    id: Optional[int] = None
    name: str
    price: float
    category: str
    description: Optional[str] = None
    is_available: bool = True
    created_at: Optional[datetime] = None
```

### 2. 数据库操作

```python
# 创建记录
product = Product(name="笔记本", price=5999.99, category="电子产品")
await product.save()

# 查询记录
products = await Product.find_all()
product = await Product.find_by_id(1)
expensive_products = await Product.find_all(price__gt=1000)

# 更新记录
product.price = 4999.99
await product.save()

# 删除记录
await product.delete()
```

### 3. 复杂查询

```python
from pyadminkit import db

# 使用QuerySet进行复杂查询
products = await db.query(Product)\\
    .filter(category="电子产品")\\
    .filter(price__gt=1000)\\
    .order_by("-price")\\
    .limit(10)\\
    .all()

# 聚合查询
total_count = await db.query(Product).count()
avg_price = await db.raw_query("SELECT AVG(price) FROM products")
```

### 4. 事务支持

```python
async with db.transaction():
    user = User(username="bob", email="bob@example.com")
    await user.save()
    
    product = Product(name="新产品", price=99.99, category="测试")
    await product.save()
    
    # 如果任何操作失败，所有更改都会回滚
```

### 5. 数据库迁移

```python
# 自动生成迁移
db.register_model(User)  # 自动创建表迁移

# 自定义迁移
migration = db.create_migration(
    "add_user_phone_20241215",
    "Add phone field to users",
    "ALTER TABLE users ADD COLUMN phone VARCHAR(20)",
    "ALTER TABLE users DROP COLUMN phone"
)

# 执行迁移
await db.migrate()

# 回滚迁移
await db.rollback(steps=1)
```

## 🔧 高级功能

### 多数据库支持

```python
# 添加多个数据库连接
await db.add_database("main", "postgresql://user:pass@localhost/main")
await db.add_database("cache", "redis://localhost:6379")
await db.add_database("logs", "mongodb://localhost:27017/logs")

# 在特定数据库上操作
await user.save(database="main")
users = await User.find_all(database="main")
```

### 原生SQL查询

```python
# 执行原生查询
results = await db.raw_query("""
    SELECT category, COUNT(*) as count, AVG(price) as avg_price
    FROM products 
    WHERE is_available = ?
    GROUP BY category
""", [True])

# 执行原生命令
await db.raw_execute("CREATE INDEX idx_product_category ON products(category)")
```

### 数据备份和恢复

```python
# 备份数据
data = await db.backup_data(Product)

# 清空表
await db.truncate_table(Product)

# 恢复数据
await db.restore_data(Product, data)
```

## 📖 完整示例

查看 `examples/database_example.py` 文件获取完整的使用示例，包括：

- 模型定义和关系
- 复杂查询操作
- 事务管理
- 迁移管理
- 性能优化技巧

## 🛠️ 开发

### 安装开发依赖

```bash
pip install -e .
pip install -r requirements.txt
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black pyadminkit/
isort pyadminkit/
```

## 📋 系统要求

- Python 3.8+
- 支持的数据库:
  - PostgreSQL 10+
  - MySQL 5.7+
  - SQLite 3.x
  - MongoDB 4.0+

## 🤝 贡献

欢迎提交Issue和Pull Request！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详细信息。

## 🔗 相关链接

- [文档](https://pyadminkit.readthedocs.io/)
- [PyPI](https://pypi.org/project/pyadminkit/)
- [GitHub](https://github.com/pyadminkit/pyadminkit)
- [问题反馈](https://github.com/pyadminkit/pyadminkit/issues)

---

**PyAdminKit** - 让Python后台管理系统开发变得简单而高效！

"""
PyAdminKit Command Line Interface

Provides command-line tools for PyAdminKit operations
"""

import argparse
import asyncio
import sys
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        prog="pyadminkit",
        description="PyAdminKit - Python Admin System Middleware",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pyadminkit version                    Show version information
  pyadminkit init myproject             Initialize a new project
  pyadminkit migrate                    Run database migrations
  pyadminkit migrate --rollback 1       Rollback 1 migration
  pyadminkit test-connection mysql://   Test database connection
  
For more information, visit: https://pyadminkit.readthedocs.io/
        """,
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"PyAdminKit {get_version()}",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("name", help="Project name")
    init_parser.add_argument("--template", default="basic", help="Project template")
    
    # Migration commands
    migrate_parser = subparsers.add_parser("migrate", help="Database migration commands")
    migrate_parser.add_argument("--rollback", type=int, metavar="N", help="Rollback N migrations")
    migrate_parser.add_argument("--status", action="store_true", help="Show migration status")
    migrate_parser.add_argument("--database", help="Database connection URL")
    
    # Test connection command
    test_parser = subparsers.add_parser("test-connection", help="Test database connection")
    test_parser.add_argument("url", help="Database connection URL")
    
    return parser


def get_version() -> str:
    """Get PyAdminKit version"""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "unknown"


async def test_connection(url: str) -> bool:
    """Test database connection"""
    try:
        from .core.database import db
        
        print(f"Testing connection to: {url}")
        await db.set_default_database(url)
        
        # Simple connection test
        health = await db.health_check()
        if health["status"] == "healthy":
            print("✅ Connection successful!")
            return True
        else:
            print(f"❌ Connection failed: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    finally:
        try:
            await db.close()
        except:
            pass


def init_project(name: str, template: str = "basic"):
    """Initialize a new PyAdminKit project"""
    import os
    
    if os.path.exists(name):
        print(f"❌ Directory '{name}' already exists")
        return False
    
    try:
        os.makedirs(name)
        
        # Create basic project structure
        dirs = [
            f"{name}/models",
            f"{name}/api", 
            f"{name}/config",
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            # Create __init__.py files
            with open(f"{dir_path}/__init__.py", "w") as f:
                f.write("")
        
        # Create main.py
        main_content = '''"""
{name} - PyAdminKit Application
"""

import asyncio
from datetime import datetime
from typing import Optional

from pyadminkit import db, BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    id: Optional[int] = None
    username: str
    email: str
    is_active: bool = True
    created_at: Optional[datetime] = None


async def main():
    """Main application function"""
    # Setup database connection
    await db.set_default_database("sqlite:///app.db")
    
    # Register models
    db.register_model(User)
    
    # Run migrations
    await db.migrate()
    
    print("✅ {name} application initialized!")
    
    # Example usage
    user = User(
        username="admin",
        email="admin@example.com",
        created_at=datetime.now()
    )
    await user.save()
    print(f"Created user: {{user.username}}")
    
    # Cleanup
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
'''.format(name=name)
        
        with open(f"{name}/main.py", "w") as f:
            f.write(main_content)
        
        # Create requirements.txt
        requirements_content = """pyadminkit>=0.1.0
# Add your additional dependencies here
"""
        
        with open(f"{name}/requirements.txt", "w") as f:
            f.write(requirements_content)
        
        # Create README.md
        readme_content = f"""# {name}

A PyAdminKit application.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

## Development

This project uses PyAdminKit for database management and admin functionality.

For more information, visit: https://pyadminkit.readthedocs.io/
"""
        
        with open(f"{name}/README.md", "w") as f:
            f.write(readme_content)
        
        print(f"✅ Project '{name}' created successfully!")
        print(f"📁 Created in: {os.path.abspath(name)}")
        print("\nNext steps:")
        print(f"  cd {name}")
        print("  pip install -r requirements.txt")
        print("  python main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create project: {e}")
        return False


async def handle_migrate_command(args):
    """Handle migration commands"""
    try:
        from .core.database import db
        
        # Setup database connection
        if args.database:
            await db.set_default_database(args.database)
        else:
            print("❌ Database URL required. Use --database or set environment variable")
            return False
        
        if args.status:
            # Show migration status
            status = await db.migration_status()
            print(f"Migration Status:")
            print(f"  Applied: {status['applied']}")
            print(f"  Pending: {status['pending']}")
            print(f"  Total: {status['total']}")
            
        elif args.rollback:
            # Rollback migrations
            print(f"Rolling back {args.rollback} migration(s)...")
            rolled_back = await db.rollback(args.rollback)
            print(f"✅ Rolled back {len(rolled_back)} migration(s)")
            
        else:
            # Apply migrations
            print("Applying migrations...")
            applied = await db.migrate()
            if applied:
                print(f"✅ Applied {len(applied)} migration(s)")
                for migration in applied:
                    print(f"  - {migration.name}")
            else:
                print("✅ All migrations are up to date")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        try:
            await db.close()
        except:
            pass


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "version":
            print(f"PyAdminKit {get_version()}")
            
        elif args.command == "init":
            success = init_project(args.name, getattr(args, "template", "basic"))
            sys.exit(0 if success else 1)
            
        elif args.command == "test-connection":
            success = asyncio.run(test_connection(args.url))
            sys.exit(0 if success else 1)
            
        elif args.command == "migrate":
            success = asyncio.run(handle_migrate_command(args))
            sys.exit(0 if success else 1)
            
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

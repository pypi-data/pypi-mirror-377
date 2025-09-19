#!/usr/bin/env python3
"""
Database management script for multi-market trading bot.
Handles migrations, backups, and database maintenance tasks.
"""

import os
import sys
import argparse
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import sqlite3

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.database.connection import DatabaseConnection


class MultiMarketDBManager:
    """Database manager for multi-market trading bot"""
    
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or "sqlite:///trading_bot.db"
        self.logger = self._setup_logging()
        self.backup_dir = Path("backups/database")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for database manager"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create database backup"""
        try:
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            backup_path = self.backup_dir / f"{backup_name}.db"
            
            if self.db_url.startswith("sqlite:///"):
                # SQLite backup
                source_path = self.db_url.replace("sqlite:///", "")
                if Path(source_path).exists():
                    shutil.copy2(source_path, backup_path)
                    self.logger.info(f"Database backup created: {backup_path}")
                    return str(backup_path)
                else:
                    raise FileNotFoundError(f"Source database not found: {source_path}")
            else:
                # For other databases, would need pg_dump, mysqldump, etc.
                raise NotImplementedError("Backup not implemented for non-SQLite databases")
                
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            raise
    
    async def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            if self.db_url.startswith("sqlite:///"):
                # SQLite restore
                target_path = self.db_url.replace("sqlite:///", "")
                
                # Create backup of current database
                if Path(target_path).exists():
                    current_backup = await self.create_backup("pre_restore")
                    self.logger.info(f"Current database backed up to: {current_backup}")
                
                # Restore from backup
                shutil.copy2(backup_file, target_path)
                self.logger.info(f"Database restored from: {backup_path}")
                return True
            else:
                raise NotImplementedError("Restore not implemented for non-SQLite databases")
                
        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.db"):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.stem,
                'path': str(backup_file),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime)
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    async def vacuum_database(self) -> bool:
        """Vacuum database to reclaim space"""
        try:
            if self.db_url.startswith("sqlite:///"):
                db_path = self.db_url.replace("sqlite:///", "")
                
                # Get size before vacuum
                size_before = Path(db_path).stat().st_size if Path(db_path).exists() else 0
                
                # Perform vacuum
                conn = sqlite3.connect(db_path)
                conn.execute("VACUUM")
                conn.close()
                
                # Get size after vacuum
                size_after = Path(db_path).stat().st_size
                space_saved = size_before - size_after
                
                self.logger.info(f"Database vacuumed. Space saved: {space_saved} bytes")
                return True
            else:
                raise NotImplementedError("Vacuum not implemented for non-SQLite databases")
                
        except Exception as e:
            self.logger.error(f"Vacuum failed: {str(e)}")
            return False
    
    async def analyze_database(self) -> Dict[str, Any]:
        """Analyze database statistics"""
        try:
            if self.db_url.startswith("sqlite:///"):
                db_path = self.db_url.replace("sqlite:///", "")
                
                if not Path(db_path).exists():
                    return {'error': 'Database file not found'}
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get database size
                db_size = Path(db_path).stat().st_size
                
                # Get table information
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                table_stats = {}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]
                    table_stats[table] = {'rows': row_count}
                
                # Get index information
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
                indexes = [row[0] for row in cursor.fetchall()]
                
                conn.close()
                
                return {
                    'database_size': db_size,
                    'table_count': len(tables),
                    'tables': table_stats,
                    'index_count': len(indexes),
                    'indexes': indexes
                }
            else:
                raise NotImplementedError("Analysis not implemented for non-SQLite databases")
                
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, int]:
        """Cleanup old data from database"""
        try:
            if self.db_url.startswith("sqlite:///"):
                db_path = self.db_url.replace("sqlite:///", "")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                cutoff_timestamp = cutoff_date.isoformat()
                
                cleanup_stats = {}
                
                # Cleanup old market data
                cursor.execute(
                    "DELETE FROM market_data WHERE timestamp < ?", 
                    (cutoff_timestamp,)
                )
                cleanup_stats['market_data'] = cursor.rowcount
                
                # Cleanup old trades
                cursor.execute(
                    "DELETE FROM trades WHERE timestamp < ?", 
                    (cutoff_timestamp,)
                )
                cleanup_stats['trades'] = cursor.rowcount
                
                # Cleanup old risk events
                cursor.execute(
                    "DELETE FROM risk_events WHERE timestamp < ?", 
                    (cutoff_timestamp,)
                )
                cleanup_stats['risk_events'] = cursor.rowcount
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Cleaned up data older than {days_to_keep} days")
                return cleanup_stats
            else:
                raise NotImplementedError("Cleanup not implemented for non-SQLite databases")
                
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
            return {}
    
    async def migrate_to_multi_market(self) -> bool:
        """Migrate existing single-market database to multi-market schema"""
        try:
            self.logger.info("Starting migration to multi-market schema...")
            
            # Create backup before migration
            backup_path = await self.create_backup("pre_multi_market_migration")
            self.logger.info(f"Pre-migration backup created: {backup_path}")
            
            if self.db_url.startswith("sqlite:///"):
                db_path = self.db_url.replace("sqlite:///", "")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Add market_type column to existing tables
                migration_queries = [
                    # Add market_type to market_data table
                    "ALTER TABLE market_data ADD COLUMN market_type TEXT DEFAULT 'crypto'",
                    
                    # Add market_type to orders table
                    "ALTER TABLE orders ADD COLUMN market_type TEXT DEFAULT 'crypto'",
                    
                    # Add market_type to positions table
                    "ALTER TABLE positions ADD COLUMN market_type TEXT DEFAULT 'crypto'",
                    
                    # Add market_type to trades table
                    "ALTER TABLE trades ADD COLUMN market_type TEXT DEFAULT 'crypto'",
                    
                    # Create new multi-market tables
                    """
                    CREATE TABLE IF NOT EXISTS cross_market_correlations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol1 TEXT NOT NULL,
                        symbol2 TEXT NOT NULL,
                        market_type1 TEXT NOT NULL,
                        market_type2 TEXT NOT NULL,
                        correlation REAL NOT NULL,
                        timestamp DATETIME NOT NULL,
                        period_days INTEGER NOT NULL
                    )
                    """,
                    
                    """
                    CREATE TABLE IF NOT EXISTS forex_economic_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        currency TEXT NOT NULL,
                        event TEXT NOT NULL,
                        importance TEXT NOT NULL,
                        actual REAL,
                        forecast REAL,
                        previous REAL
                    )
                    """,
                    
                    """
                    CREATE TABLE IF NOT EXISTS market_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        market_type TEXT NOT NULL,
                        session_name TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        timezone TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT FALSE
                    )
                    """,
                    
                    """
                    CREATE TABLE IF NOT EXISTS regulatory_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        report_type TEXT NOT NULL,
                        market_type TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        data TEXT NOT NULL,
                        status TEXT DEFAULT 'pending'
                    )
                    """,
                    
                    """
                    CREATE TABLE IF NOT EXISTS market_holidays (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        market_type TEXT NOT NULL,
                        date DATE NOT NULL,
                        name TEXT NOT NULL,
                        country TEXT
                    )
                    """
                ]
                
                for query in migration_queries:
                    try:
                        cursor.execute(query)
                        self.logger.debug(f"Executed migration query: {query[:50]}...")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e).lower():
                            self.logger.debug(f"Column already exists, skipping: {str(e)}")
                        else:
                            raise
                
                # Create indexes for better performance
                index_queries = [
                    "CREATE INDEX IF NOT EXISTS idx_market_data_market_type ON market_data(market_type)",
                    "CREATE INDEX IF NOT EXISTS idx_orders_market_type ON orders(market_type)",
                    "CREATE INDEX IF NOT EXISTS idx_positions_market_type ON positions(market_type)",
                    "CREATE INDEX IF NOT EXISTS idx_trades_market_type ON trades(market_type)",
                    "CREATE INDEX IF NOT EXISTS idx_correlations_symbols ON cross_market_correlations(symbol1, symbol2)",
                    "CREATE INDEX IF NOT EXISTS idx_economic_events_currency ON forex_economic_events(currency)",
                    "CREATE INDEX IF NOT EXISTS idx_sessions_market_type ON market_sessions(market_type)"
                ]
                
                for query in index_queries:
                    cursor.execute(query)
                
                conn.commit()
                conn.close()
                
                self.logger.info("Migration to multi-market schema completed successfully")
                return True
            else:
                raise NotImplementedError("Migration not implemented for non-SQLite databases")
                
        except Exception as e:
            self.logger.error(f"Migration failed: {str(e)}")
            return False
    
    def generate_maintenance_report(self) -> str:
        """Generate database maintenance report"""
        report_lines = ["# Database Maintenance Report\n"]
        report_lines.append(f"Generated: {datetime.now().isoformat()}\n")
        
        # Database analysis
        analysis = asyncio.run(self.analyze_database())
        if 'error' not in analysis:
            report_lines.append("## Database Statistics")
            report_lines.append(f"- Database size: {analysis['database_size']:,} bytes")
            report_lines.append(f"- Number of tables: {analysis['table_count']}")
            report_lines.append(f"- Number of indexes: {analysis['index_count']}\n")
            
            report_lines.append("## Table Statistics")
            for table, stats in analysis['tables'].items():
                report_lines.append(f"- {table}: {stats['rows']:,} rows")
            report_lines.append("")
        
        # Backup information
        backups = self.list_backups()
        report_lines.append("## Available Backups")
        if backups:
            for backup in backups[:5]:  # Show last 5 backups
                size_mb = backup['size'] / (1024 * 1024)
                report_lines.append(
                    f"- {backup['name']}: {size_mb:.2f} MB "
                    f"(created: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')})"
                )
        else:
            report_lines.append("- No backups found")
        
        report_lines.append("")
        
        # Recommendations
        report_lines.append("## Maintenance Recommendations")
        if analysis.get('database_size', 0) > 100 * 1024 * 1024:  # > 100MB
            report_lines.append("- Consider running VACUUM to reclaim space")
        
        if len(backups) > 10:
            report_lines.append("- Consider cleaning up old backups")
        
        if len(backups) == 0:
            report_lines.append("- Create a backup before making changes")
        
        return "\n".join(report_lines)


async def main():
    """Main entry point for database manager"""
    parser = argparse.ArgumentParser(description='Multi-Market Trading Bot Database Manager')
    parser.add_argument('--db-url', help='Database URL')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create database backup')
    backup_parser.add_argument('--name', help='Backup name')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_path', help='Path to backup file')
    
    # List backups command
    subparsers.add_parser('list-backups', help='List available backups')
    
    # Vacuum command
    subparsers.add_parser('vacuum', help='Vacuum database')
    
    # Analyze command
    subparsers.add_parser('analyze', help='Analyze database')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Cleanup old data')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Days to keep')
    
    # Migrate command
    subparsers.add_parser('migrate', help='Migrate to multi-market schema')
    
    # Report command
    subparsers.add_parser('report', help='Generate maintenance report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = MultiMarketDBManager(args.db_url)
    
    try:
        if args.command == 'backup':
            backup_path = await manager.create_backup(args.name)
            print(f"✅ Backup created: {backup_path}")
        
        elif args.command == 'restore':
            success = await manager.restore_backup(args.backup_path)
            if success:
                print("✅ Database restored successfully")
            else:
                print("❌ Restore failed")
                sys.exit(1)
        
        elif args.command == 'list-backups':
            backups = manager.list_backups()
            if backups:
                print("Available backups:")
                for backup in backups:
                    size_mb = backup['size'] / (1024 * 1024)
                    print(f"  {backup['name']}: {size_mb:.2f} MB "
                          f"(created: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                print("No backups found")
        
        elif args.command == 'vacuum':
            success = await manager.vacuum_database()
            if success:
                print("✅ Database vacuumed successfully")
            else:
                print("❌ Vacuum failed")
                sys.exit(1)
        
        elif args.command == 'analyze':
            analysis = await manager.analyze_database()
            if 'error' in analysis:
                print(f"❌ Analysis failed: {analysis['error']}")
                sys.exit(1)
            else:
                print("Database Analysis:")
                print(f"  Size: {analysis['database_size']:,} bytes")
                print(f"  Tables: {analysis['table_count']}")
                print(f"  Indexes: {analysis['index_count']}")
                print("  Table rows:")
                for table, stats in analysis['tables'].items():
                    print(f"    {table}: {stats['rows']:,}")
        
        elif args.command == 'cleanup':
            stats = await manager.cleanup_old_data(args.days)
            if stats:
                print(f"✅ Cleanup completed (keeping last {args.days} days):")
                for table, count in stats.items():
                    print(f"  {table}: {count} rows deleted")
            else:
                print("❌ Cleanup failed")
                sys.exit(1)
        
        elif args.command == 'migrate':
            success = await manager.migrate_to_multi_market()
            if success:
                print("✅ Migration to multi-market schema completed")
            else:
                print("❌ Migration failed")
                sys.exit(1)
        
        elif args.command == 'report':
            report = manager.generate_maintenance_report()
            print(report)
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Operation failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
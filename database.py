import sqlite3
import os
from datetime import datetime
from urllib.parse import urlparse

class Database:
    def __init__(self, db_name="bot_database.db"):
        self.db_name = db_name
        self.db_type = "sqlite"
        self.connection = None
        
        # Check if DATABASE_URL exists (Railway PostgreSQL)
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            self.setup_postgresql(database_url)
        else:
            self.setup_sqlite()
        
        self.init_database()
    
    def setup_postgresql(self, database_url):
        """Setup PostgreSQL connection for Railway"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # Parse DATABASE_URL
            parsed = urlparse(database_url)
            self.db_config = {
                'host': parsed.hostname,
                'port': parsed.port,
                'database': parsed.path[1:],  # Remove leading slash
                'user': parsed.username,
                'password': parsed.password,
                'sslmode': 'require'
            }
            self.db_type = "postgresql"
            print("✅ PostgreSQL configuration loaded for Railway")
        except ImportError:
            print("❌ psycopg2 not available, falling back to SQLite")
            self.setup_sqlite()
    
    def setup_sqlite(self):
        """Setup SQLite connection for local development"""
        self.db_type = "sqlite"
        print("✅ SQLite configuration loaded for local development")
    
    def get_connection(self):
        """Get database connection"""
        if self.db_type == "postgresql":
            import psycopg2
            from psycopg2.extras import RealDictCursor
            return psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
        else:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            return conn
    
    def init_database(self):
        """Initialize database tables"""
        if self.db_type == "postgresql":
            self.init_postgresql_tables()
        else:
            self.init_sqlite_tables()
    
    def init_sqlite_tables(self):
        """Initialize SQLite tables"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    points INTEGER DEFAULT 0,
                    referral_code TEXT,
                    referred_by INTEGER,
                    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_banned BOOLEAN DEFAULT FALSE,
                    total_orders INTEGER DEFAULT 0,
                    total_spent_points INTEGER DEFAULT 0
                )
            ''')
            
            # Orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    service_type TEXT,
                    target_url TEXT,
                    quantity INTEGER,
                    points_cost INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Channels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT PRIMARY KEY,
                    channel_name TEXT,
                    channel_username TEXT,
                    points_reward INTEGER DEFAULT 10,
                    is_active BOOLEAN DEFAULT TRUE,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User channel subscriptions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    user_id INTEGER,
                    channel_id TEXT,
                    subscribed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    points_earned INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, channel_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
                )
            ''')
            
            # Points transactions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS points_transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    points_change INTEGER,
                    transaction_type TEXT,
                    description TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            print("✅ SQLite database initialized successfully")
    
    def init_postgresql_tables(self):
        """Initialize PostgreSQL tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(100),
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    points INTEGER DEFAULT 0,
                    referral_code VARCHAR(20),
                    referred_by BIGINT,
                    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_banned BOOLEAN DEFAULT FALSE,
                    total_orders INTEGER DEFAULT 0,
                    total_spent_points INTEGER DEFAULT 0
                )
            ''')
            
            # Orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    service_type VARCHAR(50),
                    target_url TEXT,
                    quantity INTEGER,
                    points_cost INTEGER,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Channels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id VARCHAR(100) PRIMARY KEY,
                    channel_name VARCHAR(200),
                    channel_username VARCHAR(100),
                    points_reward INTEGER DEFAULT 10,
                    is_active BOOLEAN DEFAULT TRUE,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User channel subscriptions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    user_id BIGINT,
                    channel_id VARCHAR(100),
                    subscribed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    points_earned INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, channel_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
                )
            ''')
            
            # Points transactions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS points_transactions (
                    transaction_id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    points_change INTEGER,
                    transaction_type VARCHAR(50),
                    description TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            print("✅ PostgreSQL database initialized successfully")
    
    def add_user(self, user_id, username, first_name, last_name=None):
        """Add new user to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if self.db_type == "postgresql":
                cursor.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    last_activity = CURRENT_TIMESTAMP
                ''', (user_id, username, first_name, last_name))
            else:
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
            
            conn.commit()
            return True
    
    def get_user(self, user_id):
        """Get user information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if self.db_type == "postgresql":
                cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            else:
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            
            return cursor.fetchone()
    
    def update_user_points(self, user_id, points_change, transaction_type="manual", description=""):
        """Update user points"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if self.db_type == "postgresql":
                cursor.execute('''
                    UPDATE users SET points = points + %s, last_activity = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                ''', (points_change, user_id))
                
                cursor.execute('''
                    INSERT INTO points_transactions (user_id, points_change, transaction_type, description)
                    VALUES (%s, %s, %s, %s)
                ''', (user_id, points_change, transaction_type, description))
            else:
                cursor.execute('''
                    UPDATE users SET points = points + ?, last_activity = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (points_change, user_id))
                
                cursor.execute('''
                    INSERT INTO points_transactions (user_id, points_change, transaction_type, description)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, points_change, transaction_type, description))
            
            conn.commit()
            return True
    
    def add_order(self, user_id, service_type, target_url, quantity, points_cost):
        """Add new order"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if self.db_type == "postgresql":
                cursor.execute('''
                    INSERT INTO orders (user_id, service_type, target_url, quantity, points_cost)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING order_id
                ''', (user_id, service_type, target_url, quantity, points_cost))
                order_id = cursor.fetchone()['order_id']
            else:
                cursor.execute('''
                    INSERT INTO orders (user_id, service_type, target_url, quantity, points_cost)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, service_type, target_url, quantity, points_cost))
                order_id = cursor.lastrowid
            
            conn.commit()
            return order_id
    
    def get_user_orders(self, user_id, limit=10):
        """Get user orders"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if self.db_type == "postgresql":
                cursor.execute('''
                    SELECT * FROM orders WHERE user_id = %s
                    ORDER BY created_date DESC LIMIT %s
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM orders WHERE user_id = ?
                    ORDER BY created_date DESC LIMIT ?
                ''', (user_id, limit))
            
            return cursor.fetchall()
    
    def add_channel(self, channel_id, channel_name, channel_username, points_reward=10):
        """Add new channel"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if self.db_type == "postgresql":
                cursor.execute('''
                    INSERT INTO channels (channel_id, channel_name, channel_username, points_reward)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (channel_id) DO UPDATE SET
                    channel_name = EXCLUDED.channel_name,
                    channel_username = EXCLUDED.channel_username,
                    points_reward = EXCLUDED.points_reward
                ''', (channel_id, channel_name, channel_username, points_reward))
            else:
                cursor.execute('''
                    INSERT OR REPLACE INTO channels (channel_id, channel_name, channel_username, points_reward)
                    VALUES (?, ?, ?, ?)
                ''', (channel_id, channel_name, channel_username, points_reward))
            
            conn.commit()
            return True
    
    def get_all_channels(self):
        """Get all active channels"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM channels WHERE is_active = TRUE ORDER BY added_date')
            return cursor.fetchall()
    
    def remove_channel(self, channel_id):
        """Remove channel"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if self.db_type == "postgresql":
                cursor.execute('DELETE FROM channels WHERE channel_id = %s', (channel_id,))
            else:
                cursor.execute('DELETE FROM channels WHERE channel_id = ?', (channel_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_stats(self):
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total users
            cursor.execute('SELECT COUNT(*) as count FROM users')
            stats['total_users'] = cursor.fetchone()['count']
            
            # Total orders
            cursor.execute('SELECT COUNT(*) as count FROM orders')
            stats['total_orders'] = cursor.fetchone()['count']
            
            # Total channels
            cursor.execute('SELECT COUNT(*) as count FROM channels WHERE is_active = TRUE')
            stats['total_channels'] = cursor.fetchone()['count']
            
            # Total points in circulation
            cursor.execute('SELECT COALESCE(SUM(points), 0) as total FROM users')
            stats['total_points'] = cursor.fetchone()['total']
            
            return stats
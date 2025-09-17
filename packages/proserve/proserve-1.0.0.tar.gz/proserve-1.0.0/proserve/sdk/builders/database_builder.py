"""
ProServe Database Builder - Database Configuration Builder
Fluent API for building database configurations with support for multiple database types
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class DatabaseBuilder:
    """Builder for database configuration with fluent API"""
    db_type: str
    url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 10
    pool_timeout: int = 30
    migrations: List[str] = field(default_factory=list)
    ssl: bool = False
    options: Dict[str, Any] = field(default_factory=dict)
    
    def with_url(self, url: str) -> 'DatabaseBuilder':
        """Set database URL (overrides individual connection parameters)"""
        self.url = url
        return self
        
    def with_host(self, host: str, port: int = None) -> 'DatabaseBuilder':
        """Set host and optionally port"""
        self.host = host
        if port:
            self.port = port
        return self
        
    def with_port(self, port: int) -> 'DatabaseBuilder':
        """Set database port"""
        self.port = port
        return self
        
    def with_credentials(self, username: str, password: str) -> 'DatabaseBuilder':
        """Set database credentials"""
        self.username = username
        self.password = password
        return self
        
    def with_database(self, database: str) -> 'DatabaseBuilder':
        """Set database name"""
        self.database = database
        return self
        
    def with_pool(self, size: int = 10, timeout: int = 30) -> 'DatabaseBuilder':
        """Configure connection pool settings"""
        self.pool_size = size
        self.pool_timeout = timeout
        return self
        
    def with_migrations(self, *migrations: str) -> 'DatabaseBuilder':
        """Add migration files or directories"""
        self.migrations.extend(migrations)
        return self
        
    def with_ssl(self, enabled: bool = True, **ssl_options) -> 'DatabaseBuilder':
        """Enable SSL and optionally configure SSL options"""
        self.ssl = enabled
        if ssl_options:
            self.options.update({f'ssl_{k}': v for k, v in ssl_options.items()})
        return self
        
    def with_option(self, key: str, value: Any) -> 'DatabaseBuilder':
        """Add custom database option"""
        self.options[key] = value
        return self
        
    def with_read_replica(self, url: str = None, host: str = None, 
                         port: int = None) -> 'DatabaseBuilder':
        """Add read replica configuration"""
        replica_config = {}
        if url:
            replica_config['url'] = url
        if host:
            replica_config['host'] = host
        if port:
            replica_config['port'] = port
        
        self.options['read_replica'] = replica_config
        return self
        
    def with_sharding(self, strategy: str = 'hash', 
                     shards: List[Dict[str, Any]] = None) -> 'DatabaseBuilder':
        """Configure database sharding"""
        self.options['sharding'] = {
            'strategy': strategy,
            'shards': shards or []
        }
        return self
        
    def with_backup(self, enabled: bool = True, schedule: str = None,
                   retention: str = '30d') -> 'DatabaseBuilder':
        """Configure database backup settings"""
        self.options['backup'] = {
            'enabled': enabled,
            'schedule': schedule,
            'retention': retention
        }
        return self
        
    def with_monitoring(self, slow_query_log: bool = True,
                       performance_insights: bool = False) -> 'DatabaseBuilder':
        """Configure database monitoring"""
        self.options['monitoring'] = {
            'slow_query_log': slow_query_log,
            'performance_insights': performance_insights
        }
        return self
        
    def build(self) -> Dict[str, Any]:
        """Build database configuration dictionary"""
        config = {
            'type': self.db_type,
            'pool_size': self.pool_size,
            'pool_timeout': self.pool_timeout,
            'ssl': self.ssl
        }
        
        # Connection information
        if self.url:
            config['url'] = self.url
        else:
            if self.host:
                config['host'] = self.host
            if self.port:
                config['port'] = self.port
            if self.database:
                config['database'] = self.database
            if self.username:
                config['username'] = self.username
            if self.password:
                config['password'] = self.password
        
        # Optional configurations
        if self.migrations:
            config['migrations'] = self.migrations
        if self.options:
            config['options'] = self.options
            
        return config


# Convenience functions for common database types
def postgresql(database: str = None) -> DatabaseBuilder:
    """Create PostgreSQL database builder"""
    builder = DatabaseBuilder(db_type='postgresql')
    if database:
        builder.with_database(database)
    return builder.with_port(5432)


def mysql(database: str = None) -> DatabaseBuilder:
    """Create MySQL database builder"""
    builder = DatabaseBuilder(db_type='mysql')
    if database:
        builder.with_database(database)
    return builder.with_port(3306)


def sqlite(database: str = None) -> DatabaseBuilder:
    """Create SQLite database builder"""
    builder = DatabaseBuilder(db_type='sqlite')
    if database:
        builder.with_database(database)
    return builder


def mongodb(database: str = None) -> DatabaseBuilder:
    """Create MongoDB database builder"""
    builder = DatabaseBuilder(db_type='mongodb')
    if database:
        builder.with_database(database)
    return builder.with_port(27017)


def redis(database: int = 0) -> DatabaseBuilder:
    """Create Redis database builder"""
    builder = DatabaseBuilder(db_type='redis')
    if database:
        builder.with_option('database', database)
    return builder.with_port(6379)


def cassandra(keyspace: str = None) -> DatabaseBuilder:
    """Create Cassandra database builder"""
    builder = DatabaseBuilder(db_type='cassandra')
    if keyspace:
        builder.with_database(keyspace)
    return builder.with_port(9042)


def elasticsearch(index: str = None) -> DatabaseBuilder:
    """Create Elasticsearch database builder"""
    builder = DatabaseBuilder(db_type='elasticsearch')
    if index:
        builder.with_database(index)
    return builder.with_port(9200)


# Database cluster configurations
def postgresql_cluster(primary_host: str, replica_hosts: List[str] = None) -> DatabaseBuilder:
    """Create PostgreSQL cluster configuration"""
    builder = postgresql()
    builder.with_host(primary_host)
    
    if replica_hosts:
        for i, replica_host in enumerate(replica_hosts):
            builder.with_option(f'replica_{i}', {'host': replica_host, 'port': 5432})
    
    return builder


def mysql_cluster(primary_host: str, replica_hosts: List[str] = None) -> DatabaseBuilder:
    """Create MySQL cluster configuration"""
    builder = mysql()
    builder.with_host(primary_host)
    
    if replica_hosts:
        for i, replica_host in enumerate(replica_hosts):
            builder.with_option(f'replica_{i}', {'host': replica_host, 'port': 3306})
    
    return builder


def mongodb_replica_set(hosts: List[str], replica_set: str) -> DatabaseBuilder:
    """Create MongoDB replica set configuration"""
    builder = mongodb()
    builder.with_option('replica_set', replica_set)
    builder.with_option('hosts', hosts)
    return builder


# Database configuration validation
def validate_database_config(config: Dict[str, Any]) -> List[str]:
    """Validate database configuration and return list of errors"""
    errors = []
    
    if 'type' not in config:
        errors.append("Database type is required")
        return errors
    
    db_type = config['type']
    
    # Check for connection information
    if not config.get('url'):
        if not config.get('host') and db_type != 'sqlite':
            errors.append(f"Host is required for {db_type} database")
        if not config.get('database') and db_type not in ['redis']:
            errors.append(f"Database name is required for {db_type}")
    
    # Type-specific validation
    if db_type == 'postgresql':
        if config.get('port') and not (1 <= config['port'] <= 65535):
            errors.append("Invalid PostgreSQL port number")
    
    elif db_type == 'mysql':
        if config.get('port') and not (1 <= config['port'] <= 65535):
            errors.append("Invalid MySQL port number")
    
    elif db_type == 'sqlite':
        if not config.get('database') and not config.get('url'):
            errors.append("SQLite requires database file path")
    
    elif db_type == 'mongodb':
        if config.get('port') and not (1 <= config['port'] <= 65535):
            errors.append("Invalid MongoDB port number")
    
    elif db_type not in ['postgresql', 'mysql', 'sqlite', 'mongodb', 'redis', 'cassandra', 'elasticsearch']:
        errors.append(f"Unsupported database type: {db_type}")
    
    # Pool configuration validation
    if config.get('pool_size', 0) <= 0:
        errors.append("Pool size must be positive")
    
    if config.get('pool_timeout', 0) <= 0:
        errors.append("Pool timeout must be positive")
    
    return errors

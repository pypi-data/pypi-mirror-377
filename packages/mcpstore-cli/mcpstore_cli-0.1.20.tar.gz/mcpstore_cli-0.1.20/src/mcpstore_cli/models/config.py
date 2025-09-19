"""Configuration models for Mcpstore-cli."""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, HttpUrl, validator
from pydantic_settings import BaseSettings


class ClientType(str, Enum):
    """Supported MCP client types."""
    
    CURSOR = "cursor"
    CLAUDE_DESKTOP = "claude"
    VSCODE = "vscode"
    CLINE = "cline"
    WINDSURF = "windsurf"
    TRAE = "trae"
    CHERRYSTUDIO = "cherrystudio"
    CUSTOM = "custom"


# Client installation URLs
CLIENT_URLS = {
    "cursor": "https://cursor.sh",
    "claude": "https://claude.ai/download",
    "vscode": "https://code.visualstudio.com",
    "cline": "https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev",
    "windsurf": "https://codeium.com/windsurf",
    "trae": "https://trae.ai",
    "cherrystudio": "https://github.com/kangfenmao/cherry-studio"
}


class TransportType(str, Enum):
    """MCP transport types."""
    
    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


class LogLevel(str, Enum):
    """Logging levels."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ClientConfig(BaseModel):
    """Configuration for a specific MCP client."""
    
    type: ClientType = Field(..., description="Client type")
    config_path: Path = Field(..., description="Path to client config file")
    transport: TransportType = Field(default=TransportType.STDIO, description="Transport type")
    
    # Client-specific settings
    supports_env_vars: bool = Field(default=True, description="Supports environment variables")
    config_format: str = Field(default="json", description="Config file format (json/toml)")
    server_key: str = Field(default="mcpServers", description="Key for servers in config")
    
    @validator('config_path')
    def expand_path(cls, v: Path) -> Path:
        """Expand user home directory in path."""
        return Path(v).expanduser().resolve()


class RegistryConfig(BaseModel):
    """Registry configuration."""
    
    url: HttpUrl = Field(default="https://registry.agentrix.dev", description="Registry URL")
    api_key: Optional[str] = Field(None, description="Registry API key")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    
    # Local registry settings
    local_cache_dir: Path = Field(
        default=Path.home() / "cache",
        description="Local cache directory"
    )
    
    @validator('local_cache_dir')
    def expand_cache_dir(cls, v: Path) -> Path:
        """Expand cache directory path."""
        return Path(v).expanduser().resolve()


class ProxyConfig(BaseModel):
    """Proxy server configuration."""
    
    host: str = Field(default="127.0.0.1", description="Proxy host")
    port: int = Field(default=8080, description="Proxy port")
    path: str = Field(default="/mcp", description="Proxy endpoint path")
    
    # Security settings
    enable_auth: bool = Field(default=False, description="Enable authentication")
    api_keys: List[str] = Field(default_factory=list, description="Valid API keys")
    cors_origins: List[str] = Field(default_factory=list, description="CORS origins")
    
    # Performance settings
    max_connections: int = Field(default=100, description="Max concurrent connections")
    timeout: int = Field(default=300, description="Connection timeout")
    
    @validator('port')
    def validate_port(cls, v: int) -> int:
        """Validate port number."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # File logging
    log_file: Optional[Path] = Field(None, description="Log file path")
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Max log file size")
    backup_count: int = Field(default=5, description="Number of backup files")
    
    # Console logging
    console_enabled: bool = Field(default=True, description="Enable console logging")
    colorize: bool = Field(default=True, description="Colorize console output")


class McpstoreConfig(BaseSettings):
    """Main Mcpstore-cli configuration."""
    
    # Core settings
    registry: RegistryConfig = Field(default_factory=RegistryConfig)
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Data directories
    data_dir: Path = Field(
        default=Path.home() / ".mcpstore",
        description="Data directory"
    )
    servers_dir: Path = Field(
        default=Path.home() / ".mcpstore" / "servers",
        description="Servers directory"
    )
    
    # Client configurations
    clients: Dict[str, ClientConfig] = Field(
        default_factory=dict,
        description="Client configurations"
    )
    
    # Development settings
    dev_mode: bool = Field(default=False, description="Development mode")
    debug: bool = Field(default=False, description="Debug mode")
    
    model_config = {
        "env_prefix": "MCPSTORE_",
        "env_file": ".env",
        "env_nested_delimiter": "__",
        "extra": "ignore",  # 忽略额外的环境变量
        "env_ignore_extra": True  # 忽略额外的环境变量
    }
    
    def __init__(self, **kwargs):
        """Initialize configuration and load custom client configs."""
        super().__init__(**kwargs)
        self._load_custom_clients()
    
    @validator('data_dir', 'servers_dir')
    def expand_directories(cls, v: Path) -> Path:
        """Expand directory paths."""
        return Path(v).expanduser().resolve()
    
    def get_client_config(self, client_type: str) -> Optional[ClientConfig]:
        """Get configuration for a specific client."""
        return self.clients.get(client_type)
    
    def set_client_config(self, client_type: str, config: ClientConfig) -> None:
        """Set configuration for a specific client."""
        self.clients[client_type] = config
    
    @classmethod
    def get_default_client_configs(cls) -> Dict[str, ClientConfig]:
        """Get default client configurations."""
        import platform
        system = platform.system()
        
        configs = {
            "cursor": ClientConfig(
                type=ClientType.CURSOR,
                config_path=cls._get_cursor_config_path(system),
                transport=TransportType.STDIO,
                config_format="json",
                server_key="mcpServers"
            ),
            "claude": ClientConfig(
                type=ClientType.CLAUDE_DESKTOP,
                config_path=cls._get_claude_config_path(system),
                transport=TransportType.STDIO,
                config_format="json", 
                server_key="mcpServers"
            ),
            "vscode": ClientConfig(
                type=ClientType.VSCODE,
                config_path=cls._get_vscode_config_path(system),
                transport=TransportType.STDIO,
                config_format="json",
                server_key="mcp.servers"
            ),
            "trae": ClientConfig(
                type=ClientType.TRAE,
                config_path=cls._get_trae_config_path(system),
                transport=TransportType.STDIO,
                config_format="json",
                server_key="mcpServers"
            ),
            "windsurf": ClientConfig(
                type=ClientType.WINDSURF,
                config_path=cls._get_windsurf_config_path(system),
                transport=TransportType.STDIO,
                config_format="json",
                server_key="mcpServers"
            ),
            "cherrystudio": ClientConfig(
                type=ClientType.CHERRYSTUDIO,
                config_path=cls._get_cherrystudio_config_path(system),
                transport=TransportType.STDIO,
                config_format="json",
                server_key="mcpServers"
            )
        }
        
        return configs
    
    @classmethod
    def _get_cursor_config_path(cls, system: str) -> Path:
        """Get Cursor config path based on OS."""
        # Cursor 在所有平台上都使用 .cursor 目录
        return Path.home() / ".cursor" / "mcp.json"
    
    @classmethod
    def _get_claude_config_path(cls, system: str) -> Path:
        """Get Claude Desktop config path based on OS."""
        if system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        elif system == "Windows":
            return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
        else:  # Linux
            return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    
    @classmethod
    def _get_vscode_config_path(cls, system: str) -> Path:
        """Get VS Code config path based on OS."""
        if system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"
        elif system == "Windows":
            return Path.home() / "AppData" / "Roaming" / "Code" / "User" / "settings.json"
        else:  # Linux
            return Path.home() / ".config" / "Code" / "User" / "settings.json"
    
    @classmethod
    def _get_trae_config_path(cls, system: str) -> Path:
        """Get Trae config path based on OS."""
        if system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Trae" / "User" / "mcp.json"
        elif system == "Windows":
            return Path.home() / "AppData" / "Roaming" / "Trae" / "User" / "mcp.json"
        else:  # Linux
            return Path.home() / ".config" / "Trae" / "User" / "mcp.json"
    
    @classmethod
    def _get_windsurf_config_path(cls, system: str) -> Path:
        """Get Windsurf config path based on OS.
        Windsurf uses Codeium's configuration structure."""
        # Windsurf 使用 Codeium 的配置目录
        return Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
    
    @classmethod
    def _get_cherrystudio_config_path(cls, system: str) -> Path:
        """Get CherryStudio config path based on OS.
        CherryStudio 是一个桌面应用，配置路径遵循平台标准。"""
        if system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "CherryStudio" / "mcp.json"
        elif system == "Windows":
            return Path.home() / "AppData" / "Roaming" / "CherryStudio" / "mcp.json"
        else:  # Linux
            return Path.home() / ".config" / "CherryStudio" / "mcp.json"
    
    def _load_custom_clients(self) -> None:
        """Load custom client configurations from config file."""
        config_file = Path.home() / ".mcpstore" / "config.toml"
        if not config_file.exists():
            return
        
        try:
            import tomlkit
            with open(config_file, 'r') as f:
                config_data = tomlkit.load(f)
            
            if "clients" in config_data:
                for client_name, client_data in config_data["clients"].items():
                    # Convert dict to ClientConfig
                    if client_name not in self.clients:
                        client_type = ClientType.CUSTOM
                        for ct in ClientType:
                            if ct.value == client_data.get("type", ""):
                                client_type = ct
                                break
                        
                        transport_type = TransportType.STDIO
                        for tt in TransportType:
                            if tt.value == client_data.get("transport", "stdio"):
                                transport_type = tt
                                break
                        
                        self.clients[client_name] = ClientConfig(
                            type=client_type,
                            config_path=Path(client_data.get("config_path", "")),
                            transport=transport_type,
                            config_format=client_data.get("config_format", "json"),
                            server_key=client_data.get("server_key", "mcpServers")
                        )
        except Exception:
            # Silently ignore errors loading custom configs
            pass
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        for dir_path in [self.data_dir, self.servers_dir, self.registry.local_cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)


class ClientInstallConfig(BaseModel):
    """Configuration for installing to a specific client."""
    
    client: str = Field(..., description="Client name")
    server_name: str = Field(..., description="Server name in client config")
    server_id: str = Field(..., description="Server identifier or URL")
    
    # Installation options
    api_key: Optional[str] = Field(None, description="API key for server")
    custom_args: List[str] = Field(default_factory=list, description="Custom arguments")
    env_vars: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    
    # Advanced options
    auto_start: bool = Field(default=True, description="Auto-start server")
    restart_on_fail: bool = Field(default=True, description="Restart on failure")
    is_url: bool = Field(default=False, description="Whether server_id is a URL")
    
    class Config:
        frozen = True 
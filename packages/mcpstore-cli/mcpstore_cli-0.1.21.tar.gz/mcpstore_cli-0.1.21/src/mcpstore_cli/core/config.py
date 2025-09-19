"""Configuration management for MCP clients."""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import tomlkit
from rich.console import Console

from ..models.config import McpstoreConfig, ClientConfig, ClientInstallConfig
from ..models.server import ServerConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


class ConfigManager:
    """Manages configuration for various MCP clients."""
    
    def __init__(self, config: McpstoreConfig):
        self.config = config
        self._load_default_clients()
    
    def _load_default_clients(self) -> None:
        """Load default client configurations."""
        defaults = McpstoreConfig.get_default_client_configs()
        for name, client_config in defaults.items():
            if name not in self.config.clients:
                self.config.clients[name] = client_config
    
    def list_clients(self) -> List[str]:
        """List available client configurations."""
        return list(self.config.clients.keys())
    
    def get_client_config(self, client_name: str) -> Optional[ClientConfig]:
        """Get configuration for a specific client."""
        return self.config.clients.get(client_name)
    
    def validate_client(self, client_name: str, auto_create_config: bool = False) -> bool:
        """Validate that a client is configured and accessible."""
        from ..models.config import CLIENT_URLS
        
        client_config = self.get_client_config(client_name)
        if not client_config:
            logger.error(f"Client '{client_name}' not found")
            console.print(f"❌ Client '{client_name}' is not supported", style="red")
            console.print(f"   Supported clients: {', '.join(self.list_clients())}")
            return False
        
        if not client_config.config_path.exists():
            if auto_create_config:
                # Auto-create empty config file
                logger.info(f"Creating config file for {client_name}: {client_config.config_path}")
                console.print(f"📁 Creating MCP config file for {client_name}...", style="yellow")
                
                try:
                    # Create directory if it doesn't exist
                    client_config.config_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Create empty config with basic structure
                    if client_config.config_format == "json":
                        empty_config = {client_config.server_key: {}}
                        self._write_json_config(client_config.config_path, empty_config)
                    elif client_config.config_format == "toml":
                        empty_config = {client_config.server_key: {}}
                        self._write_toml_config(client_config.config_path, empty_config)
                    
                    console.print(f"✅ Created config file: {client_config.config_path}", style="green")
                    return True
                    
                except Exception as e:
                    logger.error(f"Failed to create config file: {e}")
                    console.print(f"❌ Failed to create config file: {e}", style="red")
                    return False
            else:
                logger.warning(f"Config file not found: {client_config.config_path}")
                console.print(f"⚠️ {client_name.capitalize()} is not installed or config file not found", style="yellow")
                console.print(f"   Expected config path: {client_config.config_path}")
                
                # Provide installation URL if available
                if client_name in CLIENT_URLS:
                    console.print(f"\n💡 Install {client_name.capitalize()} from: [link]{CLIENT_URLS[client_name]}[/link]")
                    console.print(f"   After installation, the MCP config should be at: {client_config.config_path}")
                
                return False
        
        return True
    
    def read_client_config(self, client_name: str) -> Optional[Dict[str, Any]]:
        """Read configuration from client config file."""
        client_config = self.get_client_config(client_name)
        if not client_config:
            return None
        
        try:
            if client_config.config_format == "json":
                return self._read_json_config(client_config.config_path)
            elif client_config.config_format == "toml":
                return self._read_toml_config(client_config.config_path)
            else:
                logger.error(f"Unsupported config format: {client_config.config_format}")
                return None
        except Exception as e:
            logger.error(f"Failed to read config for {client_name}: {e}")
            return None
    
    def write_client_config(self, client_name: str, config_data: Dict[str, Any]) -> bool:
        """Write configuration to client config file."""
        client_config = self.get_client_config(client_name)
        if not client_config:
            return False
        
        try:
            # Create backup
            self._backup_config(client_config.config_path)
            
            # Write new config
            if client_config.config_format == "json":
                return self._write_json_config(client_config.config_path, config_data)
            elif client_config.config_format == "toml":
                return self._write_toml_config(client_config.config_path, config_data)
            else:
                logger.error(f"Unsupported config format: {client_config.config_format}")
                return False
        except Exception as e:
            logger.error(f"Failed to write config for {client_name}: {e}")
            return False
    
    def install_server_config(self, install_config: ClientInstallConfig) -> bool:
        """Install server configuration to a client."""
        client_name = install_config.client
        server_name = install_config.server_name
        
        # logger.info(f"Installing server '{server_name}' to client '{client_name}'")
        console.print(f"📦 Installing '{server_name}' to {client_name}...")
        
        # Read existing config
        config_data = self.read_client_config(client_name)
        if config_data is None:
            config_data = {}
        
        # Get client configuration
        client_config = self.get_client_config(client_name)
        if not client_config:
            logger.error(f"Client '{client_name}' not configured")
            console.print(f"❌ Client '{client_name}' not configured", style="red")
            return False
        
        # Prepare server configuration
        server_config = self._generate_server_config(install_config)
        
        # Navigate to the correct section in config
        config_section = self._get_config_section(config_data, client_config.server_key)
        config_section[server_name] = server_config
        
        # Write updated config
        success = self.write_client_config(client_name, config_data)
        
        if success:
            # logger.info(f"Successfully installed '{server_name}' to '{client_name}'")
            console.print(f"✅ Successfully configured '{server_name}' in {client_name}", style="green")
        else:
            logger.error(f"Failed to install '{server_name}' to '{client_name}'")
            console.print(f"❌ Failed to install server '{server_name}'", style="red")
        
        return success
    
    def uninstall_server_config(self, client_name: str, server_name: str) -> bool:
        """Uninstall server configuration from a client."""
        logger.info(f"Uninstalling server '{server_name}' from client '{client_name}'")
        
        # Read existing config
        config_data = self.read_client_config(client_name)
        if config_data is None:
            logger.error(f"No config found for client '{client_name}'")
            return False
        
        # Get client configuration
        client_config = self.get_client_config(client_name)
        if not client_config:
            logger.error(f"Client '{client_name}' not configured")
            return False
        
        # Navigate to the correct section in config
        config_section = self._get_config_section(config_data, client_config.server_key)
        
        if server_name not in config_section:
            logger.warning(f"Server '{server_name}' not found in {client_name} config")
            return False
        
        # Remove server configuration
        del config_section[server_name]
        
        # Write updated config
        success = self.write_client_config(client_name, config_data)
        
        if success:
            logger.info(f"Successfully uninstalled '{server_name}' from '{client_name}'")
            console.print(f"✅ Server '{server_name}' uninstalled from {client_name}", style="green")
        else:
            logger.error(f"Failed to uninstall '{server_name}' from '{client_name}'")
            console.print(f"❌ Failed to uninstall server '{server_name}'", style="red")
        
        return success
    
    def list_installed_servers(self, client_name: str) -> List[str]:
        """List servers installed in a client."""
        config_data = self.read_client_config(client_name)
        if not config_data:
            return []
        
        client_config = self.get_client_config(client_name)
        if not client_config:
            return []
        
        config_section = self._get_config_section(config_data, client_config.server_key)
        return list(config_section.keys())
    
    def _generate_server_config(self, install_config: ClientInstallConfig) -> Dict[str, Any]:
        """Generate MCP server configuration for client."""
        
        # Check if this is a URL installation
        if install_config.is_url:
            # Get client config to check client type
            client_config = self.get_client_config(install_config.client)
            
            # For Claude Desktop, we need stdio proxy
            if client_config and client_config.type.value == "claude":
                server_config = {
                    "command": "uvx",
                    "args": [
                        "mcpstore-cli",
                        "run",
                        "--url",
                        install_config.server_id  # The full URL only
                    ]
                }
            else:
                # For other clients (like Cursor), use direct URL format
                server_config = {
                    "url": install_config.server_id
                }
                
                # Add environment variables if provided
                if install_config.env_vars:
                    server_config["env"] = install_config.env_vars
                
                return server_config
        else:
            # Regular package-based configuration (existing logic)
            server_config = {
                "command": "uvx",
                "args": [
                    "mcpstore-cli",
                    "run", 
                    install_config.server_id
                ]
            }
        
        # Add API key if provided (for both URL and package configs)
        if install_config.api_key:
            server_config["args"].extend(["--key", install_config.api_key])
        
        # Add config JSON if env_vars or custom_args are provided
        config_json = {}
        if install_config.env_vars:
            config_json["env"] = install_config.env_vars
        if install_config.custom_args:
            config_json["args"] = install_config.custom_args
        
        if config_json:
            import json
            server_config["args"].extend(["--config", json.dumps(config_json)])
        
        return server_config
    
    def _get_config_section(self, config_data: Dict[str, Any], key_path: str) -> Dict[str, Any]:
        """Navigate to the correct section in config using dot notation."""
        current = config_data
        keys = key_path.split('.')
        
        for key in keys:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        return current
    
    def _read_json_config(self, config_path: Path) -> Dict[str, Any]:
        """Read JSON configuration file."""
        if not config_path.exists():
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _write_json_config(self, config_path: Path, config_data: Dict[str, Any]) -> bool:
        """Write JSON configuration file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def _read_toml_config(self, config_path: Path) -> Dict[str, Any]:
        """Read TOML configuration file."""
        if not config_path.exists():
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return dict(tomlkit.load(f))
    
    def _write_toml_config(self, config_path: Path, config_data: Dict[str, Any]) -> bool:
        """Write TOML configuration file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            tomlkit.dump(config_data, f)
        
        return True
    
    def _backup_config(self, config_path: Path) -> None:
        """Create backup of configuration file."""
        if not config_path.exists():
            return
        
        backup_path = config_path.with_suffix(f"{config_path.suffix}.backup")
        shutil.copy2(config_path, backup_path)
        logger.debug(f"Created backup: {backup_path}")
    
    def restore_config_backup(self, client_name: str) -> bool:
        """Restore configuration from backup."""
        client_config = self.get_client_config(client_name)
        if not client_config:
            return False
        
        backup_path = client_config.config_path.with_suffix(
            f"{client_config.config_path.suffix}.backup"
        )
        
        if not backup_path.exists():
            logger.error(f"No backup found for {client_name}")
            return False
        
        try:
            shutil.copy2(backup_path, client_config.config_path)
            logger.info(f"Restored config for {client_name} from backup")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup for {client_name}: {e}")
            return False 
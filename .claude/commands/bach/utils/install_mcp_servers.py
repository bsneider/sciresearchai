#!/usr/bin/env python3
"""
MCP Server Installation and Setup Script for Bach Research System
Automates installation of existing MCP servers for research operations
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


class MCPServerInstaller:
    """Automated installer for MCP servers"""
    
    def __init__(self):
        self.servers = {
            "arxiv_mcp": {
                "name": "arXiv MCP Server",
                "install_method": "uv",
                "install_command": ["uv", "tool", "install", "arxiv-mcp-server"],
                "test_command": ["uv", "tool", "run", "arxiv-mcp-server", "--help"],
                "required_env": [],
                "optional_env": ["ARXIV_STORAGE_PATH"]
            },
            "brave_search_mcp": {
                "name": "Brave Search MCP Server", 
                "install_method": "npm",
                "install_command": ["npm", "install", "-g", "@modelcontextprotocol/server-brave-search"],
                "test_command": ["npx", "@modelcontextprotocol/server-brave-search", "--help"],
                "required_env": ["BRAVE_API_KEY"],
                "optional_env": []
            },
            "github_mcp": {
                "name": "GitHub MCP Server",
                "install_method": "npm", 
                "install_command": ["npm", "install", "-g", "@modelcontextprotocol/server-github"],
                "test_command": ["npx", "@modelcontextprotocol/server-github", "--help"],
                "required_env": ["GITHUB_TOKEN"],
                "optional_env": []
            },
            "filesystem_mcp": {
                "name": "Filesystem MCP Server",
                "install_method": "npm",
                "install_command": ["npm", "install", "-g", "@modelcontextprotocol/server-filesystem"],
                "test_command": ["npx", "@modelcontextprotocol/server-filesystem", "--help"],
                "required_env": [],
                "optional_env": []
            },
            "postgres_mcp": {
                "name": "PostgreSQL MCP Server",
                "install_method": "npm",
                "install_command": ["npm", "install", "-g", "@modelcontextprotocol/server-postgres"],
                "test_command": ["npx", "@modelcontextprotocol/server-postgres", "--help"],
                "required_env": ["POSTGRES_CONNECTION_STRING"],
                "optional_env": []
            }
        }
        
        self.claude_config_path = self._get_claude_config_path()
    
    def _get_claude_config_path(self) -> Optional[Path]:
        """Get Claude Desktop config path for the current platform"""
        home = Path.home()
        
        if sys.platform == "darwin":  # macOS
            return home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        elif sys.platform == "win32":  # Windows
            return home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
        else:  # Linux
            return home / ".config" / "claude" / "claude_desktop_config.json"
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if required tools are installed"""
        checks = {}
        
        # Check for uv
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
            checks["uv"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            checks["uv"] = False
        
        # Check for npm
        try:
            subprocess.run(["npm", "--version"], capture_output=True, check=True)
            checks["npm"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            checks["npm"] = False
        
        # Check for node
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
            checks["node"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            checks["node"] = False
        
        return checks
    
    def install_server(self, server_id: str, force: bool = False) -> bool:
        """Install a specific MCP server"""
        if server_id not in self.servers:
            print(f"❌ Unknown server: {server_id}")
            return False
        
        server = self.servers[server_id]
        print(f"📦 Installing {server['name']}...")
        
        # Check if already installed (unless force)
        if not force and self._is_server_installed(server_id):
            print(f"✅ {server['name']} already installed")
            return True
        
        try:
            # Run installation command
            result = subprocess.run(
                server["install_command"],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ {server['name']} installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {server['name']}: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"❌ {server['install_method']} not found. Please install {server['install_method']} first.")
            return False
    
    def _is_server_installed(self, server_id: str) -> bool:
        """Check if server is already installed"""
        server = self.servers[server_id]
        
        try:
            subprocess.run(
                server["test_command"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def check_environment_variables(self, server_id: str) -> Dict[str, bool]:
        """Check if required environment variables are set"""
        server = self.servers[server_id]
        env_status = {}
        
        for var in server["required_env"]:
            env_status[var] = var in os.environ and bool(os.environ[var])
        
        for var in server["optional_env"]:
            env_status[f"{var} (optional)"] = var in os.environ and bool(os.environ[var])
        
        return env_status
    
    def generate_claude_config(self, enabled_servers: List[str]) -> Dict[str, any]:
        """Generate Claude Desktop configuration"""
        config = {"mcpServers": {}}
        
        for server_id in enabled_servers:
            if server_id == "arxiv_mcp":
                config["mcpServers"]["arxiv-mcp-server"] = {
                    "command": "uv",
                    "args": [
                        "tool", "run", "arxiv-mcp-server",
                        "--storage-path", os.path.expanduser("~/.arxiv-mcp-server/papers")
                    ]
                }
            elif server_id == "brave_search_mcp":
                config["mcpServers"]["brave-search"] = {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                    "env": {
                        "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")
                    }
                }
            elif server_id == "github_mcp":
                config["mcpServers"]["github"] = {
                    "command": "npx", 
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN", "")
                    }
                }
            elif server_id == "filesystem_mcp":
                config["mcpServers"]["filesystem"] = {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-filesystem",
                        "--allowed-directory", os.getcwd()
                    ]
                }
            elif server_id == "postgres_mcp":
                config["mcpServers"]["postgres"] = {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-postgres"],
                    "env": {
                        "POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_CONNECTION_STRING", "")
                    }
                }
        
        return config
    
    def update_claude_config(self, enabled_servers: List[str]) -> bool:
        """Update Claude Desktop configuration file"""
        if not self.claude_config_path:
            print("❌ Could not determine Claude Desktop config path")
            return False
        
        # Create config directory if it doesn't exist
        self.claude_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing config or create new
        existing_config = {}
        if self.claude_config_path.exists():
            try:
                with open(self.claude_config_path, 'r') as f:
                    existing_config = json.load(f)
            except (json.JSONDecodeError, IOError):
                print("⚠️  Could not read existing Claude config, creating new one")
        
        # Generate new MCP server config
        new_mcp_config = self.generate_claude_config(enabled_servers)
        
        # Merge with existing config
        if "mcpServers" not in existing_config:
            existing_config["mcpServers"] = {}
        
        existing_config["mcpServers"].update(new_mcp_config["mcpServers"])
        
        # Write updated config
        try:
            with open(self.claude_config_path, 'w') as f:
                json.dump(existing_config, f, indent=2)
            
            print(f"✅ Updated Claude Desktop config: {self.claude_config_path}")
            return True
            
        except IOError as e:
            print(f"❌ Failed to write Claude config: {e}")
            return False
    
    def install_all(self, servers: Optional[List[str]] = None, update_claude: bool = True) -> Dict[str, bool]:
        """Install multiple MCP servers"""
        if servers is None:
            # Default to servers that don't require API keys
            servers = ["arxiv_mcp", "filesystem_mcp"]
        
        print("🚀 Bach MCP Server Installation")
        print("=" * 40)
        
        # Check prerequisites
        prereqs = self.check_prerequisites()
        print(f"Prerequisites: {prereqs}")
        
        if not all(prereqs.values()):
            print("❌ Missing prerequisites. Please install:")
            if not prereqs.get("uv"):
                print("  - uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
            if not prereqs.get("npm"):
                print("  - npm: https://nodejs.org/")
            return {}
        
        # Install servers
        results = {}
        for server_id in servers:
            results[server_id] = self.install_server(server_id)
            
            # Check environment variables
            env_status = self.check_environment_variables(server_id)
            if env_status:
                print(f"Environment variables for {server_id}:")
                for var, status in env_status.items():
                    print(f"  {var}: {'✅' if status else '❌'}")
        
        # Update Claude Desktop config
        if update_claude:
            successful_servers = [s for s, success in results.items() if success]
            if successful_servers:
                self.update_claude_config(successful_servers)
        
        print("\n🎉 Installation complete!")
        print("\nNext steps:")
        print("1. Set required environment variables (see MCP_SETUP.md)")
        print("2. Restart Claude Desktop")
        print("3. Test with: /bach:research-search 'your query'")
        
        return results


def main():
    """Main installation script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install MCP servers for Bach research system")
    parser.add_argument("--servers", nargs="+", 
                       choices=["arxiv_mcp", "brave_search_mcp", "github_mcp", "filesystem_mcp", "postgres_mcp"],
                       help="Servers to install")
    parser.add_argument("--no-claude-config", action="store_true",
                       help="Skip updating Claude Desktop config")
    parser.add_argument("--force", action="store_true",
                       help="Force reinstallation")
    
    args = parser.parse_args()
    
    installer = MCPServerInstaller()
    
    # Default servers (no API keys required)
    servers = args.servers or ["arxiv_mcp", "filesystem_mcp"]
    
    results = installer.install_all(
        servers=servers,
        update_claude=not args.no_claude_config
    )
    
    # Print summary
    print(f"\nInstallation Results:")
    for server, success in results.items():
        print(f"  {server}: {'✅' if success else '❌'}")


if __name__ == "__main__":
    main()
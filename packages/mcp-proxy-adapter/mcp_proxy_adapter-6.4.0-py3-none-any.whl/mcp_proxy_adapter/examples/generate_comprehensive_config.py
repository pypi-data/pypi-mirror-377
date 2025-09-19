#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Script for generating comprehensive HTTP configuration for MCP Proxy Adapter.
Generates single comprehensive configuration with all features enabled.
"""
import json
import os
import argparse
import uuid
from typing import Dict, Any


def generate_comprehensive_http_config(
    port: int = 20001,
    roles_file: str = "configs/roles.json",
) -> Dict[str, Any]:
    """Generate comprehensive HTTP configuration with all features."""
    return {
        "uuid": str(uuid.uuid4()),
        "server": {
            "host": "127.0.0.1",
            "port": port,
            "debug": False,
            "log_level": "INFO",
            "workers": 1,
            "reload": False
        },
        "ssl": {
            "enabled": False
        },
        "security": {
            "enabled": True,
            "auth": {
                "enabled": True,
                "methods": [
                    "api_key"
                ],
                "api_keys": {
                    "admin-token-123": "admin",
                    "user-token-456": "user",
                    "readonly-token-789": "readonly",
                    "guest-token-abc": "guest",
                    "proxy-token-def": "proxy"
                }
            },
            "permissions": {
                "enabled": True,
                "roles_file": roles_file
            }
        },
        "registration": {
            "enabled": True,
            "url": "http://127.0.0.1:3004/proxy",
            "name": "comprehensive_http_adapter",
            "capabilities": [
                "http",
                "token_auth",
                "roles",
                "registration",
                "heartbeat"
            ],
            "retry_count": 3,
            "retry_delay": 5,
            "heartbeat": {
                "enabled": True,
                "interval": 30
            }
        },
        "protocols": {
            "enabled": True,
            "allowed_protocols": [
                "http"
            ]
        }
    }


def generate_roles_config() -> Dict[str, Any]:
    """Generate comprehensive roles configuration."""
    return {
        "admin": {
            "description": "Full administrative access",
            "permissions": [
                "read",
                "write",
                "execute",
                "delete",
                "admin"
            ],
            "inherits": []
        },
        "user": {
            "description": "Standard user access",
            "permissions": [
                "read",
                "write",
                "execute"
            ],
            "inherits": []
        },
        "readonly": {
            "description": "Read-only access",
            "permissions": [
                "read"
            ],
            "inherits": []
        },
        "guest": {
            "description": "Limited guest access",
            "permissions": [
                "read"
            ],
            "inherits": []
        },
        "proxy": {
            "description": "Proxy registration access",
            "permissions": [
                "read",
                "register",
                "heartbeat"
            ],
            "inherits": []
        }
    }


def main():
    """Generate comprehensive configuration."""
    parser = argparse.ArgumentParser(description="Generate comprehensive HTTP configuration")
    parser.add_argument(
        "--output-dir",
        default="configs",
        help="Output directory for configuration files"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=20001,
        help="Server port"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate comprehensive HTTP configuration
    config = generate_comprehensive_http_config(port=args.port)
    config_file = os.path.join(args.output_dir, "comprehensive_http.json")
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Generated: {config_file}")
    
    # Generate roles configuration
    roles = generate_roles_config()
    roles_file = os.path.join(args.output_dir, "roles.json")
    
    with open(roles_file, 'w') as f:
        json.dump(roles, f, indent=2)
    
    print(f"Generated: {roles_file}")
    
    print(f"\nGenerated comprehensive configuration in {args.output_dir}/")
    print("Configuration includes:")
    print("- HTTP server with token authentication")
    print("- Role-based permissions")
    print("- Proxy registration")
    print("- Heartbeat monitoring")
    print("- 5 predefined tokens with roles")


if __name__ == "__main__":
    main()

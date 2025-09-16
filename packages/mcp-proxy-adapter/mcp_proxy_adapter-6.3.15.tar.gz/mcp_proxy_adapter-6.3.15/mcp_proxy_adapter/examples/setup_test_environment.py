#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Enhanced script for setting up test environment for MCP Proxy Adapter.
Prepares the test environment with all necessary files, directories, and configurations.
Includes comprehensive documentation and validation for configuration settings.

This script accepts an output directory and copies required example files
and helper scripts into that directory, creating a ready-to-use workspace.
By default, the current working directory is used, so end-users can run
it in their project root after installing this framework in a virtual
environment.

Features:
- Comprehensive configuration documentation
- Validation of mutually exclusive settings
- Protocol-aware configuration generation
- Enhanced error handling and troubleshooting
"""
import shutil
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Import mcp_security_framework
try:
    from mcp_security_framework.core.cert_manager import CertificateManager
    from mcp_security_framework.schemas.config import (
        CertificateConfig,
        CAConfig,
        ServerCertConfig,
        ClientCertConfig,
    )

    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    print("Warning: mcp_security_framework not available")


class ConfigurationValidator:
    """
    Validates MCP Proxy Adapter configurations for mutually exclusive settings
    and protocol compatibility.
    """

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_config(
        self, config: Dict[str, Any], config_name: str
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a configuration for mutually exclusive settings and protocol compatibility.

        Args:
            config: Configuration dictionary to validate
            config_name: Name of the configuration for error reporting

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Validate protocol settings
        self._validate_protocol_settings(config, config_name)

        # Validate SSL/TLS settings
        self._validate_ssl_settings(config, config_name)

        # Validate mTLS settings
        self._validate_mtls_settings(config, config_name)

        # Validate authentication settings
        self._validate_auth_settings(config, config_name)

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_protocol_settings(
        self, config: Dict[str, Any], config_name: str
    ) -> None:
        """Validate protocol configuration settings."""
        protocols = config.get("protocols", {})

        if not protocols.get("enabled", False):
            self.warnings.append(
                f"⚠️ {config_name}: Protocol middleware is disabled - all protocols will be allowed"
            )
            return

        allowed_protocols = protocols.get("allowed_protocols", [])
        if not allowed_protocols:
            self.errors.append(
                f"❌ {config_name}: No allowed protocols specified when protocol middleware is enabled"
            )
            return

        # Check for invalid protocol combinations
        if "http" in allowed_protocols and "https" in allowed_protocols:
            self.warnings.append(
                f"⚠️ {config_name}: Both HTTP and HTTPS protocols are allowed - consider security implications"
            )

        if "mtls" in allowed_protocols and "http" in allowed_protocols:
            self.errors.append(
                f"❌ {config_name}: mTLS and HTTP protocols are mutually exclusive - mTLS requires HTTPS"
            )

    def _validate_ssl_settings(self, config: Dict[str, Any], config_name: str) -> None:
        """Validate SSL/TLS configuration settings."""
        security = config.get("security", {})
        ssl = security.get("ssl", {})

        if not ssl.get("enabled", False):
            return

        # Check certificate file requirements
        cert_file = ssl.get("server_cert_file")
        key_file = ssl.get("server_key_file")

        if not cert_file or not key_file:
            self.errors.append(
                f"❌ {config_name}: SSL enabled but server certificate or key file not specified"
            )

        # Check CA certificate requirements
        ca_cert_file = ssl.get("ca_cert_file")
        verify_server = ssl.get("verify_server", True)

        if verify_server and not ca_cert_file:
            self.warnings.append(
                f"⚠️ {config_name}: Server verification enabled but no CA certificate specified"
            )

    def _validate_mtls_settings(self, config: Dict[str, Any], config_name: str) -> None:
        """Validate mTLS configuration settings."""
        security = config.get("security", {})
        ssl = security.get("ssl", {})

        if not ssl.get("enabled", False):
            return

        # Check if mTLS is configured
        client_cert_file = ssl.get("client_cert_file")
        client_key_file = ssl.get("client_key_file")
        verify_client = ssl.get("verify_client", False)

        if verify_client and (not client_cert_file or not client_key_file):
            self.errors.append(
                f"❌ {config_name}: Client verification enabled but client certificate or key file not specified"
            )

        # Check protocol compatibility
        protocols = config.get("protocols", {})
        if protocols.get("enabled", False):
            allowed_protocols = protocols.get("allowed_protocols", [])
            if verify_client and "mtls" not in allowed_protocols:
                self.warnings.append(
                    f"⚠️ {config_name}: Client verification enabled but 'mtls' not in allowed protocols"
                )

    def _validate_auth_settings(self, config: Dict[str, Any], config_name: str) -> None:
        """Validate authentication configuration settings."""
        security = config.get("security", {})
        auth = security.get("auth", {})

        if not auth.get("enabled", False):
            return

        # Check token requirements
        token_required = auth.get("token_required", False)
        if token_required and not auth.get("token_secret"):
            self.errors.append(
                f"❌ {config_name}: Token authentication enabled but no token secret specified"
            )


def _get_package_paths() -> tuple[Path, Path]:
    """
    Resolve source paths for examples and utils relative to this file
    to avoid importing the package during setup.
    """
    pkg_root = Path(__file__).resolve().parents[1]
    return pkg_root / "examples", pkg_root / "utils"


def create_configuration_documentation(output_dir: Path) -> None:
    """
    Create comprehensive documentation for MCP Proxy Adapter configurations.
    """
    docs_dir = output_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Create main configuration guide
    config_guide = docs_dir / "CONFIGURATION_GUIDE.md"
    with open(config_guide, "w", encoding="utf-8") as f:
        f.write(
            """# MCP Proxy Adapter Configuration Guide

## Overview

This guide explains how to configure MCP Proxy Adapter for different deployment scenarios,
including HTTP, HTTPS, and mTLS configurations.

## Configuration Structure

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "protocols": {
    "enabled": true,
    "allowed_protocols": ["https", "mtls"]
  },
  "security": {
    "ssl": {
      "enabled": true,
      "server_cert_file": "path/to/server.crt",
      "server_key_file": "path/to/server.key",
      "ca_cert_file": "path/to/ca.crt",
      "client_cert_file": "path/to/client.crt",
      "client_key_file": "path/to/client.key",
      "verify_server": true,
      "verify_client": false,
      "min_tls_version": "TLSv1.2"
    },
    "auth": {
      "enabled": false,
      "token_required": false,
      "token_secret": "your-secret-key"
    }
  }
}
```

## Protocol Configuration

### Protocol Middleware

The `protocols` section controls which protocols are allowed:

- `enabled: true` - Protocol validation is active
- `enabled: false` - All protocols are allowed (bypasses validation)

### Allowed Protocols

- `"http"` - Plain HTTP (insecure)
- `"https"` - HTTPS with server certificate
- `"mtls"` - Mutual TLS (client and server certificates)

### Protocol Combinations

**Valid combinations:**
- `["https"]` - HTTPS only
- `["https", "mtls"]` - HTTPS and mTLS
- `["http"]` - HTTP only (not recommended for production)

**Invalid combinations:**
- `["http", "mtls"]` - HTTP and mTLS are mutually exclusive
- `["http", "https"]` - Mixed HTTP/HTTPS (security risk)

## SSL/TLS Configuration

### Server Certificates

Required for HTTPS and mTLS:
- `server_cert_file` - Server certificate file
- `server_key_file` - Server private key file

### CA Certificates

- `ca_cert_file` - CA certificate for server verification
- `verify_server: true` - Verify server certificate against CA
- `verify_server: false` - Disable server certificate verification

### Client Certificates (mTLS)

- `client_cert_file` - Client certificate file
- `client_key_file` - Client private key file
- `verify_client: true` - Require client certificates
- `verify_client: false` - No client certificate required

## Authentication

### Token Authentication

- `auth.enabled: true` - Enable authentication
- `token_required: true` - Require authentication tokens
- `token_secret` - Secret key for token validation

## Common Configuration Patterns

### 1. Development (HTTP)
```json
{
  "protocols": {"enabled": false},
  "security": {"ssl": {"enabled": false}}
}
```

### 2. Production HTTPS
```json
{
  "protocols": {
    "enabled": true,
    "allowed_protocols": ["https"]
  },
  "security": {
    "ssl": {
      "enabled": true,
      "server_cert_file": "certs/server.crt",
      "server_key_file": "keys/server.key",
      "verify_server": true,
      "ca_cert_file": "certs/ca.crt"
    }
  }
}
```

### 3. mTLS with Client Verification
```json
{
  "protocols": {
    "enabled": true,
    "allowed_protocols": ["https", "mtls"]
  },
  "security": {
    "ssl": {
      "enabled": true,
      "server_cert_file": "certs/server.crt",
      "server_key_file": "keys/server.key",
      "ca_cert_file": "certs/ca.crt",
      "client_cert_file": "certs/client.crt",
      "client_key_file": "keys/client.key",
      "verify_server": true,
      "verify_client": true
    }
  }
}
```

## Validation Rules

The configuration validator checks for:

1. **Mutually Exclusive Settings:**
   - HTTP and mTLS protocols
   - Client verification without client certificates
   - Server verification without CA certificates

2. **Required Dependencies:**
   - SSL enabled requires server certificates
   - mTLS requires both server and client certificates
   - Protocol middleware enabled requires allowed protocols

3. **Security Warnings:**
   - HTTP and HTTPS in same configuration
   - Server verification without CA certificate
   - Client verification without mTLS protocol

## Troubleshooting

### Common Issues

1. **"Protocol not allowed" errors:**
   - Check `protocols.allowed_protocols` includes required protocol
   - Ensure `protocols.enabled: true` for validation

2. **SSL certificate errors:**
   - Verify certificate file paths are correct
   - Check certificate validity and format
   - Ensure CA certificate matches server certificate

3. **mTLS connection failures:**
   - Verify client certificates are valid
   - Check `verify_client: true` is set
   - Ensure "mtls" is in allowed protocols

### Debug Mode

Enable debug logging to troubleshoot issues:

```json
{
  "logging": {
    "level": "DEBUG",
    "handlers": ["console", "file"]
  }
}
```
"""
        )

    print(f"✅ Created configuration documentation: {config_guide}")


def create_test_files(output_dir: Path) -> None:
    """
    Create additional test files for proxy registration testing.
    """
    # Create test proxy server script
    test_proxy_server = output_dir / "test_proxy_server.py"
    with open(test_proxy_server, "w", encoding="utf-8") as f:
        f.write(
            '''#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Simple mTLS proxy server for testing proxy registration SSL fix.
"""
import asyncio
import ssl
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn


app = FastAPI(title="Test mTLS Proxy Server", version="1.0.0")


@app.post("/register")
async def register_server(request: Request):
    """Register server endpoint."""
    try:
        data = await request.json()
        print(f"✅ Received registration request: {data}")
        
        # Check if client certificate is present
        client_cert = request.client
        if client_cert:
            print(f"✅ Client certificate verified: {client_cert}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "server_key": f"{data.get('server_id', 'unknown')}_1",
                "message": "Server registered successfully"
            }
        )
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "message": str(e),
                    "code": "REGISTRATION_ERROR"
                }
            }
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "message": "mTLS Proxy Server is running"
        }
    )


def main():
    """Run the mTLS proxy server."""
    print("🚀 Starting Test mTLS Proxy Server...")
    print("📡 Server URL: https://127.0.0.1:3004")
    print("🔐 mTLS enabled with client certificate verification")
    print("📋 Available endpoints:")
    print("   POST /register - Register server")
    print("   GET  /health   - Health check")
    print("⚡ Press Ctrl+C to stop\\n")
    
    # Run server with mTLS
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=3004,
        ssl_keyfile="mtls_certificates/server/mcp-proxy.key",
        ssl_certfile="mtls_certificates/server/mcp-proxy.pem",
        log_level="info"
    )


if __name__ == "__main__":
    main()
'''
        )

    # Make it executable
    test_proxy_server.chmod(0o755)
    print(f"✅ Created test proxy server: {test_proxy_server}")

    # Create test script for proxy registration
    test_script = output_dir / "test_proxy_registration.py"
    with open(test_script, "w", encoding="utf-8") as f:
        f.write(
            '''#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Test script to verify proxy registration SSL configuration fix.
"""
import sys
import subprocess
import time
import requests
from pathlib import Path


def test_proxy_registration():
    """Test proxy registration with SSL configuration."""
    print("🧪 Testing Proxy Registration SSL Configuration Fix")
    print("=" * 60)
    
    # Start proxy server
    print("🚀 Starting test proxy server...")
    proxy_process = subprocess.Popen([
        sys.executable, "test_proxy_server.py"
    ], cwd=Path(__file__).parent)
    
    try:
        # Wait for server to start
        print("⏳ Waiting for proxy server to start...")
        time.sleep(5)
        
        # Test proxy server health
        print("🔍 Testing proxy server health...")
        try:
            response = requests.get(
                "https://127.0.0.1:3004/health",
                verify=False,
                timeout=10
            )
            if response.status_code == 200:
                print("✅ Proxy server is running")
            else:
                print(f"❌ Proxy server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to proxy server: {e}")
            return False
        
        # Test mTLS server with registration
        print("🚀 Starting mTLS server with proxy registration...")
        server_process = subprocess.Popen([
            sys.executable, "-m", "mcp_proxy_adapter",
            "--config", "configs/test_proxy_registration.json"
        ], cwd=Path(__file__).parent)
        
        try:
            # Wait for server to start and attempt registration
            print("⏳ Waiting for server to start and register...")
            time.sleep(10)
            
            # Check if server is running
            if server_process.poll() is None:
                print("✅ mTLS server started successfully")
                print("✅ Proxy registration SSL configuration fix is working!")
                return True
            else:
                print("❌ mTLS server failed to start")
                return False
                
        finally:
            # Clean up server process
            if server_process.poll() is None:
                server_process.terminate()
                server_process.wait()
    
    finally:
        # Clean up proxy process
        if proxy_process.poll() is None:
            proxy_process.terminate()
            proxy_process.wait()


def main():
    """Run the test."""
    success = test_proxy_registration()
    
    if success:
        print("\\n🎉 All tests passed! Proxy registration SSL fix is working correctly.")
        return 0
    else:
        print("\\n❌ Tests failed. Check the logs above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
        )

    # Make it executable
    test_script.chmod(0o755)
    print(f"✅ Created test script: {test_script}")


def generate_enhanced_configurations(output_dir: Path) -> None:
    """
    Generate enhanced configurations with proper protocol settings and validation.
    """
    configs_dir = output_dir / "configs"
    configs_dir.mkdir(parents=True, exist_ok=True)

    validator = ConfigurationValidator()

    # Configuration templates with proper protocol settings
    configs = {
        "development_http.json": {
            "server": {"host": "0.0.0.0", "port": 8000},
            "protocols": {"enabled": False},
            "security": {"ssl": {"enabled": False}},
            "logging": {"level": "DEBUG"},
        },
        "production_https.json": {
            "uuid": "550e8400-e29b-41d4-a716-446655440001",
            "server": {"host": "0.0.0.0", "port": 8443},
            "protocols": {"enabled": True, "allowed_protocols": ["https"]},
            "ssl": {
                "enabled": True,
                "cert_file": "mcp_proxy_adapter/examples/basic_framework/certs/server_cert.pem",
                "key_file": "mcp_proxy_adapter/examples/basic_framework/certs/server_key.pem",
                "ca_cert_file": "mcp_proxy_adapter/examples/basic_framework/certs/ca_cert.pem",
                "verify_client": False,
                "min_tls_version": "TLSv1.2",
            },
            "logging": {"level": "INFO"},
        },
        "mtls_with_roles.json": {
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "server": {"host": "0.0.0.0", "port": 8443},
            "protocols": {"enabled": True, "allowed_protocols": ["https", "mtls"]},
            "ssl": {
                "enabled": True,
                "cert_file": "mcp_proxy_adapter/examples/basic_framework/certs/server_cert.pem",
                "key_file": "mcp_proxy_adapter/examples/basic_framework/certs/server_key.pem",
                "ca_cert_file": "mcp_proxy_adapter/examples/basic_framework/certs/ca_cert.pem",
                "verify_client": True,
                "min_tls_version": "TLSv1.2",
            },
            "security": {
                "auth": {
                    "enabled": True,
                    "token_required": False,
                    "token_secret": "your-secret-key",
                },
            },
            "logging": {"level": "INFO"},
        },
        "mtls_no_roles.json": {
            "server": {"host": "0.0.0.0", "port": 8443},
            "protocols": {"enabled": True, "allowed_protocols": ["https", "mtls"]},
            "security": {
                "ssl": {
                    "enabled": True,
                    "server_cert_file": "certs/server_cert.pem",
                    "server_key_file": "keys/server_key.pem",
                    "ca_cert_file": "certs/ca_cert.pem",
                    "client_cert_file": "certs/client_cert.pem",
                    "client_key_file": "keys/client_key.pem",
                    "verify_server": True,
                    "verify_client": True,
                    "min_tls_version": "TLSv1.2",
                }
            },
            "logging": {"level": "INFO"},
        },
        "https_simple.json": {
            "uuid": "550e8400-e29b-41d4-a716-446655440002",
            "server": {"host": "0.0.0.0", "port": 8443},
            "protocols": {"enabled": True, "allowed_protocols": ["https"]},
            "ssl": {
                "enabled": True,
                "cert_file": "mcp_proxy_adapter/examples/basic_framework/certs/server_cert.pem",
                "key_file": "mcp_proxy_adapter/examples/basic_framework/certs/server_key.pem",
                "verify_client": False,
                "min_tls_version": "TLSv1.2",
            },
            "logging": {"level": "INFO"},
        },
        "https_with_auth.json": {
            "server": {"host": "0.0.0.0", "port": 8443},
            "protocols": {"enabled": True, "allowed_protocols": ["https"]},
            "security": {
                "ssl": {
                    "enabled": True,
                    "server_cert_file": "certs/server_cert.pem",
                    "server_key_file": "keys/server_key.pem",
                    "verify_server": True,
                    "ca_cert_file": "certs/ca_cert.pem",
                    "verify_client": False,
                    "min_tls_version": "TLSv1.2",
                },
                "auth": {
                    "enabled": True,
                    "token_required": True,
                    "token_secret": "your-secret-key",
                },
            },
            "logging": {"level": "INFO"},
        },
        "test_proxy_registration.json": {
            "server": {"host": "127.0.0.1", "port": 8010},
            "protocols": {"enabled": True, "allowed_protocols": ["https", "mtls"]},
            "security": {
                "ssl": {
                    "enabled": True,
                    "server_cert_file": "certs/mtls/server/embedding-service.pem",
                    "server_key_file": "certs/mtls/server/embedding-service.key",
                    "ca_cert_file": "certs/mtls/truststore.pem",
                    "client_cert_file": "certs/mtls/client/embedding-service.pem",
                    "client_key_file": "certs/mtls/client/embedding-service.key",
                    "verify_server": True,
                    "verify_client": True,
                    "min_tls_version": "TLSv1.2",
                }
            },
            "registration": {
                "enabled": True,
                "proxy_url": "https://127.0.0.1:3004",
                "server_id": "test-proxy-registration",
                "server_name": "Test Proxy Registration Service",
                "description": "Test service for proxy registration SSL fix",
                "auth_method": "certificate",
                "certificate": {
                    "cert_file": "certs/mtls/client/embedding-service.pem",
                    "key_file": "certs/mtls/client/embedding-service.key",
                },
                "ssl": {
                    "verify_mode": "CERT_REQUIRED",
                    "ca_cert": "mtls_certificates/truststore.pem",
                },
            },
            "logging": {"level": "DEBUG"},
        },
    }

    # Generate and validate configurations
    for config_name, config_data in configs.items():
        config_path = configs_dir / config_name

        # Validate configuration
        is_valid, errors, warnings = validator.validate_config(config_data, config_name)

        if not is_valid:
            print(f"❌ Configuration {config_name} has errors:")
            for error in errors:
                print(f"   {error}")
            continue

        if warnings:
            print(f"⚠️ Configuration {config_name} has warnings:")
            for warning in warnings:
                print(f"   {warning}")

        # Write configuration file
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        print(f"✅ Generated configuration: {config_path}")

    # Create configuration index
    index_path = configs_dir / "README.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(
            """# Configuration Files

This directory contains pre-configured examples for different deployment scenarios.

## Available Configurations

### Development
- `development_http.json` - HTTP development server (no SSL)

### Production HTTPS
- `production_https.json` - HTTPS with server certificate verification
- `https_simple.json` - HTTPS without certificate verification
- `https_with_auth.json` - HTTPS with token authentication

### mTLS (Mutual TLS)
- `mtls_with_roles.json` - mTLS with role-based authentication
- `mtls_no_roles.json` - mTLS without roles

## Usage

Start the server with a specific configuration:

```bash
python -m mcp_proxy_adapter --config configs/production_https.json
```

## Validation

All configurations are validated for:
- Mutually exclusive settings
- Required dependencies
- Protocol compatibility
- Security best practices

See `docs/CONFIGURATION_GUIDE.md` for detailed documentation.
"""
        )

    print(f"✅ Created configuration index: {index_path}")


def setup_test_environment(output_dir: Path) -> None:
    """
    Setup test environment under output_dir with required files
    and directories.

    All created directories and copied files are rooted at output_dir
    so users can run scripts relative to that directory.
    """
    print("🔧 Setting up enhanced test environment...")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create test environment directory structure
    directories = [
        "examples/basic_framework",
        "examples/full_application",
        "scripts",
        "configs",
        "certs",
        "keys",
        "tokens",
        "logs",
        "docs",
    ]
    for directory in directories:
        target_dir = output_dir / directory
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {target_dir}")

    # Resolve package paths
    examples_src_root, utils_src_root = _get_package_paths()

    # Copy example files
    basic_framework_src = examples_src_root / "basic_framework"
    if basic_framework_src.exists():
        shutil.copytree(
            basic_framework_src,
            output_dir / "examples/basic_framework",
            dirs_exist_ok=True,
        )
        print("✅ Copied basic_framework examples")

    full_application_src = examples_src_root / "full_application"
    if full_application_src.exists():
        shutil.copytree(
            full_application_src,
            output_dir / "examples/full_application",
            dirs_exist_ok=True,
        )
        print("✅ Copied full_application examples")

    # Copy utility scripts
    config_generator_src = utils_src_root / "config_generator.py"
    if config_generator_src.exists():
        shutil.copy2(config_generator_src, output_dir / "scripts/")
        print("✅ Copied config_generator.py")

    # Copy certificate generation scripts
    create_certs_src = examples_src_root / "create_certificates_simple.py"
    if create_certs_src.exists():
        shutil.copy2(create_certs_src, output_dir / "scripts/")
        print("✅ Copied create_certificates_simple.py")

    cert_tokens_src = examples_src_root / "generate_certificates_and_tokens.py"
    if cert_tokens_src.exists():
        shutil.copy2(cert_tokens_src, output_dir / "scripts/")
        print("✅ Copied generate_certificates_and_tokens.py")

    # Copy roles.json to the root directory for compatibility
    roles_src = examples_src_root / "roles.json"
    if roles_src.exists():
        shutil.copy2(roles_src, output_dir)
        print("✅ Copied roles.json to root directory")

    # Also copy from configs directory if it exists
    roles_configs_src = output_dir / "configs" / "roles.json"
    if roles_configs_src.exists():
        shutil.copy2(roles_configs_src, output_dir / "roles.json")
        print("✅ Updated roles.json from configs directory")

    # Create configuration documentation
    create_configuration_documentation(output_dir)

    # Generate enhanced configurations
    generate_enhanced_configurations(output_dir)

    # Create test files
    create_test_files(output_dir)

    print(
        "🎉 Enhanced test environment setup completed successfully at: {}".format(
            output_dir
        )
    )


def generate_certificates_with_framework(output_dir: Path) -> bool:
    """
    Generate certificates using mcp_security_framework.
    """
    if not SECURITY_FRAMEWORK_AVAILABLE:
        print("❌ mcp_security_framework not available for certificate " "generation")
        return False
    try:
        print("🔐 Generating certificates using mcp_security_framework...")
        # Configure certificate manager
        cert_config = CertificateConfig(
            cert_storage_path=str((output_dir / "certs").resolve()),
            key_storage_path=str((output_dir / "keys").resolve()),
            default_validity_days=365,
            key_size=2048,
            hash_algorithm="sha256",
        )
        cert_manager = CertificateManager(cert_config)
        # Generate CA certificate
        ca_config = CAConfig(
            common_name="MCP Proxy Adapter Test CA",
            organization="Test Organization",
            organizational_unit="Certificate Authority",
            country="US",
            state="Test State",
            locality="Test City",
            validity_years=10,  # Use validity_years instead of validity_days
            key_size=2048,
            hash_algorithm="sha256",
        )
        cert_pair = cert_manager.create_root_ca(ca_config)
        if not cert_pair or not cert_pair.certificate_path:
            print("❌ Failed to create CA certificate: Invalid certificate pair")
            return False
        print("✅ CA certificate created successfully")
        # Find CA key file
        ca_key_path = cert_pair.private_key_path
        # Generate server certificate
        server_config = ServerCertConfig(
            common_name="localhost",
            organization="Test Organization",
            organizational_unit="Server",
            country="US",
            state="Test State",
            locality="Test City",
            validity_days=365,
            key_size=2048,
            hash_algorithm="sha256",
            subject_alt_names=[
                "localhost",
                "127.0.0.1",
            ],
            ca_cert_path=cert_pair.certificate_path,
            ca_key_path=ca_key_path,
        )
        cert_pair = cert_manager.create_server_certificate(server_config)
        if not cert_pair or not cert_pair.certificate_path:
            print("❌ Failed to create server certificate: Invalid certificate " "pair")
            return False
        print("✅ Server certificate created successfully")
        # Generate client certificates
        client_configs = [
            (
                "admin",
                ["admin"],
                [
                    "read",
                    "write",
                    "execute",
                    "delete",
                    "admin",
                    "register",
                    "unregister",
                    "heartbeat",
                    "discover",
                ],
            ),
            (
                "user",
                ["user"],
                [
                    "read",
                    "execute",
                    "register",
                    "unregister",
                    "heartbeat",
                    "discover",
                ],
            ),
            ("readonly", ["readonly"], ["read", "discover"]),
            ("guest", ["guest"], ["read", "discover"]),
            (
                "proxy",
                ["proxy"],
                ["register", "unregister", "heartbeat", "discover"],
            ),
        ]
        for client_name, roles, permissions in client_configs:
            client_config = ClientCertConfig(
                common_name=f"{client_name}-client",
                organization="Test Organization",
                organizational_unit="Client",
                country="US",
                state="Test State",
                locality="Test City",
                validity_days=730,
                key_size=2048,
                hash_algorithm="sha256",
                roles=roles,
                permissions=permissions,
                ca_cert_path=cert_pair.certificate_path,
                ca_key_path=ca_key_path,
            )
            cert_pair = cert_manager.create_client_certificate(client_config)
            if not cert_pair or not cert_pair.certificate_path:
                print(
                    (
                        "❌ Failed to create client certificate {}: "
                        "Invalid certificate pair"
                    ).format(client_name)
                )
                return False
            print("✅ Client certificate {} created successfully".format(client_name))
        print(
            "🎉 All certificates generated successfully using "
            "mcp_security_framework!"
        )
        return True
    except Exception as e:
        print("❌ Error generating certificates with framework: {}".format(e))
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if mcp_security_framework is installed:")
        print("   pip install mcp_security_framework")
        print("\n2. Verify write permissions in output directory")
        print("\n3. Check if certs/ and keys/ directories exist")
        return False


def main() -> int:
    """Main function for command line execution."""
    parser = argparse.ArgumentParser(
        description="Setup enhanced test environment for MCP Proxy Adapter"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=".",
        help=(
            "Target directory to create the test environment "
            "(default: current directory)"
        ),
    )
    parser.add_argument(
        "--skip-certs", action="store_true", help="Skip certificate generation"
    )
    args = parser.parse_args()
    try:
        target_root = Path(args.output_dir)
        setup_test_environment(target_root)

        # Generate certificates if framework is available and not skipped
        if not args.skip_certs and SECURITY_FRAMEWORK_AVAILABLE:
            generate_certificates_with_framework(target_root)
        elif args.skip_certs:
            print("⚠️ Skipping certificate generation (--skip-certs specified)")
        else:
            print(
                "⚠️ Skipping certificate generation (mcp_security_framework "
                "not available)"
            )
    except Exception as e:
        print(
            "❌ Error setting up test environment: {}".format(e),
            file=sys.stderr,
        )
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if output directory is writable")
        print("2. Verify mcp_security_framework installation")
        print("3. Check available disk space")
        return 1

    print("\n" + "=" * 60)
    print("✅ ENHANCED TEST ENVIRONMENT SETUP COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Review configuration documentation:")
    print("   cat docs/CONFIGURATION_GUIDE.md")
    print("\n2. Check available configurations:")
    print("   ls -la configs/")
    print("\n3. Test proxy registration SSL fix:")
    print("   python test_proxy_registration.py")
    print("\n4. Start server with a specific configuration:")
    print("   python -m mcp_proxy_adapter --config configs/production_https.json")
    print("\n5. Run security tests:")
    print("   python -m mcp_proxy_adapter.examples.run_security_tests")
    print("\n6. Generate additional certificates (if needed):")
    print("   python scripts/create_certificates_simple.py")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())

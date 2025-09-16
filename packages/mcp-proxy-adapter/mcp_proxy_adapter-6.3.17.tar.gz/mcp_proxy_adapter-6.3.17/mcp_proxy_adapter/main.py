#!/usr/bin/env python3
"""
MCP Proxy Adapter - Main Entry Point

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import sys
import ssl
import hypercorn.asyncio
import hypercorn.config
import asyncio
import argparse
from pathlib import Path

# Add the project root to the path only if running from source
# This allows the installed package to be used when installed via pip
if not str(Path(__file__).parent.parent) in sys.path:
    sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.config import Config
from mcp_proxy_adapter.core.config_validator import ConfigValidator


def main():
    """Main entry point for the MCP Proxy Adapter."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP Proxy Adapter Server")
    parser.add_argument("--config", "-c", type=str, help="Path to configuration file")
    args = parser.parse_args()

    # Load configuration
    if args.config:
        config = Config(config_path=args.config)
    else:
        config = Config()

    # Validate UUID configuration (mandatory)
    validator = ConfigValidator(config.get_all())
    if not validator.validate_all():
        print("❌ Configuration validation failed:")
        for error in validator.get_errors():
            print(f"   - {error}")
        sys.exit(1)
    print("✅ Configuration validation passed")

    # Create application
    app = create_app(app_config=config)

    # Get server configuration
    host = config.get("server.host", "0.0.0.0")
    port = config.get("server.port", 8000)

    # Get SSL configuration
    ssl_enabled = config.get("ssl.enabled", False)
    ssl_cert_file = config.get("ssl.cert_file")
    ssl_key_file = config.get("ssl.key_file")
    ssl_ca_cert = config.get("ssl.ca_cert")
    verify_client = config.get("ssl.verify_client", False)

    print(f"🚀 Starting MCP Proxy Adapter")
    print(f"🌐 Server: {host}:{port}")
    if ssl_enabled:
        print(f"🔐 SSL: Enabled")
        print(f"   Certificate: {ssl_cert_file}")
        print(f"   Key: {ssl_key_file}")
        if ssl_ca_cert:
            print(f"   CA: {ssl_ca_cert}")
        print(f"   Client verification: {verify_client}")
    print("=" * 50)

    # Configure hypercorn
    config_hypercorn = hypercorn.config.Config()
    config_hypercorn.bind = [f"{host}:{port}"]

    if ssl_enabled and ssl_cert_file and ssl_key_file:
        config_hypercorn.certfile = ssl_cert_file
        config_hypercorn.keyfile = ssl_key_file

        if ssl_ca_cert:
            config_hypercorn.ca_certs = ssl_ca_cert

        if verify_client:
            # For mTLS, require client certificates
            config_hypercorn.set_cert_reqs(ssl.CERT_REQUIRED)
            config_hypercorn.verify_mode = ssl.CERT_REQUIRED
            print("🔐 mTLS: Client certificate verification enabled")
        else:
            # For regular HTTPS without client verification
            # Don't set verify_mode for regular HTTPS - let hypercorn handle it
            print("🔐 HTTPS: Regular HTTPS without client certificate verification")

        print(f"🔐 Starting HTTPS server with hypercorn...")
    else:
        print(f"🌐 Starting HTTP server with hypercorn...")

    # Run the server
    asyncio.run(hypercorn.asyncio.serve(app, config_hypercorn))


if __name__ == "__main__":
    main()

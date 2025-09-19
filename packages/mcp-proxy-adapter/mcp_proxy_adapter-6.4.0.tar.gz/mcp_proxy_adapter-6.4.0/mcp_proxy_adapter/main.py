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
    parser = argparse.ArgumentParser(
        description="MCP Proxy Adapter Server",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to configuration file",
    )
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

    # Create application (pass config_path so reload uses same file)
    app = create_app(app_config=config.get_all(), config_path=args.config)

    # Get server configuration
    host = config.get("server.host", "0.0.0.0")
    port = config.get("server.port", 8000)

    # Get SSL configuration strictly from config (no hardcode)
    ssl_enabled = config.get("ssl.enabled", False)
    ssl_cert_file = config.get("ssl.cert_file")
    ssl_key_file = config.get("ssl.key_file")
    # Support both keys: ssl.ca_cert_file (security framework style) and ssl.ca_cert (legacy)
    ssl_ca_cert = config.get("ssl.ca_cert_file", config.get("ssl.ca_cert"))
    verify_client = config.get("ssl.verify_client", False)

    print("🔍 Debug SSL config:")
    print(f"   ssl_enabled: {ssl_enabled}")
    print(f"   ssl_cert_file: {ssl_cert_file}")
    print(f"   ssl_key_file: {ssl_key_file}")
    print(f"   ssl_ca_cert: {ssl_ca_cert}")
    print(f"   verify_client: {verify_client}")
    print("🔍 Source: configuration (hardcode disabled)")

    print("🚀 Starting MCP Proxy Adapter")
    print(f"🌐 Server: {host}:{port}")
    if ssl_enabled:
        print("🔐 SSL: Enabled")
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
            config_hypercorn.verify_mode = ssl.CERT_REQUIRED
            print("🔐 mTLS: Client certificate verification enabled")
        else:
            print(
                "🔐 HTTPS: Regular HTTPS without client certificate",
            )
            print("verification")

        # Prefer modern protocols
        try:
            config_hypercorn.alpn_protocols = ["h2", "http/1.1"]
        except Exception:
            pass

    # Log hypercorn configuration
    print("=" * 50)
    print("🔍 HYPERCORN CONFIGURATION:")
    print(
        "🔍 certfile="
        f"{getattr(config_hypercorn, 'certfile', None)}",
    )
    print(
        "🔍 keyfile="
        f"{getattr(config_hypercorn, 'keyfile', None)}",
    )
    print(
        "🔍 ca_certs="
        f"{getattr(config_hypercorn, 'ca_certs', None)}",
    )
    print(
        "🔍 verify_mode="
        f"{getattr(config_hypercorn, 'verify_mode', None)}",
    )
    print(
        "🔍 alpn_protocols="
        f"{getattr(config_hypercorn, 'alpn_protocols', None)}",
    )
    print("=" * 50)

    if ssl_enabled:
        print("🔐 Starting HTTPS server with hypercorn...")
    else:
        print("🌐 Starting HTTP server with hypercorn...")

    # Run the server
    asyncio.run(hypercorn.asyncio.serve(app, config_hypercorn))


if __name__ == "__main__":
    main()

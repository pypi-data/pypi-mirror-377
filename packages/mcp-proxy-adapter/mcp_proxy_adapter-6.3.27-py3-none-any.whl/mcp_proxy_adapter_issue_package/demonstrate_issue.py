#!/usr/bin/env python3
"""
Demonstration script showing the mcp_proxy_adapter SSL verification issue.
This script reproduces the problem where verify_server: false is ignored.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import ssl
import asyncio
import aiohttp
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MockSSLConfig:
    """Mock SSL configuration to demonstrate the issue."""

    def __init__(self, verify_server=True):
        self.verify_server = verify_server
        self.ca_cert_file = "certs/mtls/truststore.pem"
        self.client_cert_file = "certs/mtls/client/embedding-service.pem"
        self.client_key_file = "certs/mtls/client/embedding-service.key"


def create_client_ssl_context_broken(ssl_config: MockSSLConfig) -> ssl.SSLContext:
    """
    BROKEN: This is how mcp_proxy_adapter currently works.
    It hardcodes CERT_REQUIRED, ignoring the verify_server setting.
    """
    logger.info("🔴 Creating SSL context (BROKEN - current mcp_proxy_adapter behavior)")
    logger.info(f"   Configuration: verify_server={ssl_config.verify_server}")

    try:
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

        # Load CA certificate if provided
        if ssl_config.ca_cert_file and Path(ssl_config.ca_cert_file).exists():
            ssl_context.load_verify_locations(ssl_config.ca_cert_file)
            logger.info(f"   ✅ Loaded CA certificate: {ssl_config.ca_cert_file}")

        # Load client certificate if provided
        if (
            ssl_config.client_cert_file
            and ssl_config.client_key_file
            and Path(ssl_config.client_cert_file).exists()
            and Path(ssl_config.client_key_file).exists()
        ):
            ssl_context.load_cert_chain(
                ssl_config.client_cert_file, ssl_config.client_key_file
            )
            logger.info(
                f"   ✅ Loaded client certificate: {ssl_config.client_cert_file}"
            )

        # PROBLEM: This line hardcodes CERT_REQUIRED, ignoring configuration
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        logger.info("   ❌ HARDCODED: ssl_context.verify_mode = ssl.CERT_REQUIRED")
        logger.info("   ❌ IGNORES: verify_server=False configuration!")

        return ssl_context
    except Exception as e:
        logger.error(f"   ❌ Failed to create SSL context: {e}")
        return ssl.create_default_context()


def create_client_ssl_context_fixed(ssl_config: MockSSLConfig) -> ssl.SSLContext:
    """
    FIXED: This is how mcp_proxy_adapter should work.
    It respects the verify_server configuration setting.
    """
    logger.info("🟢 Creating SSL context (FIXED - proposed solution)")
    logger.info(f"   Configuration: verify_server={ssl_config.verify_server}")

    try:
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

        # Load CA certificate if provided
        if ssl_config.ca_cert_file and Path(ssl_config.ca_cert_file).exists():
            ssl_context.load_verify_locations(ssl_config.ca_cert_file)
            logger.info(f"   ✅ Loaded CA certificate: {ssl_config.ca_cert_file}")

        # Load client certificate if provided
        if (
            ssl_config.client_cert_file
            and ssl_config.client_key_file
            and Path(ssl_config.client_cert_file).exists()
            and Path(ssl_config.client_key_file).exists()
        ):
            ssl_context.load_cert_chain(
                ssl_config.client_cert_file, ssl_config.client_key_file
            )
            logger.info(
                f"   ✅ Loaded client certificate: {ssl_config.client_cert_file}"
            )

        # FIX: Respect the verify_server configuration
        if not ssl_config.verify_server:
            ssl_context.check_hostname = False  # Must be set BEFORE verify_mode
            ssl_context.verify_mode = ssl.CERT_NONE
            logger.info("   ✅ RESPECTS: ssl_context.check_hostname = False")
            logger.info(
                "   ✅ RESPECTS: ssl_context.verify_mode = ssl.CERT_NONE (verify_server=False)"
            )
        else:
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            logger.info(
                "   ✅ RESPECTS: ssl_context.verify_mode = ssl.CERT_REQUIRED (verify_server=True)"
            )

        return ssl_context
    except Exception as e:
        logger.error(f"   ❌ Failed to create SSL context: {e}")
        return ssl.create_default_context()


async def test_connection(ssl_context: ssl.SSLContext, url: str, description: str):
    """Test connection with the given SSL context."""
    logger.info(f"\n🧪 Testing connection: {description}")
    logger.info(f"   URL: {url}")

    try:
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                logger.info(f"   ✅ SUCCESS: HTTP {response.status}")
                return True
    except ssl.SSLCertVerificationError as e:
        logger.error(f"   ❌ SSL VERIFICATION ERROR: {e}")
        return False
    except Exception as e:
        logger.error(f"   ❌ CONNECTION ERROR: {e}")
        return False


async def main():
    """Main demonstration function."""
    logger.info("🚀 mcp_proxy_adapter SSL Verification Issue Demonstration")
    logger.info("=" * 70)

    # Test URL with self-signed certificate
    test_url = "https://127.0.0.1:3004/health"

    # Configuration with verify_server=False (should be respected)
    config = MockSSLConfig(verify_server=False)

    logger.info(f"\n📋 Test Configuration:")
    logger.info(f"   URL: {test_url}")
    logger.info(f"   verify_server: {config.verify_server}")
    logger.info(f"   CA cert: {config.ca_cert_file}")
    logger.info(f"   Client cert: {config.client_cert_file}")

    # Test 1: Current broken behavior
    logger.info(f"\n" + "=" * 50)
    logger.info("TEST 1: Current mcp_proxy_adapter behavior (BROKEN)")
    logger.info("=" * 50)

    broken_ssl_context = create_client_ssl_context_broken(config)
    broken_result = await test_connection(
        broken_ssl_context, test_url, "BROKEN - ignores verify_server=False"
    )

    # Test 2: Proposed fixed behavior
    logger.info(f"\n" + "=" * 50)
    logger.info("TEST 2: Proposed fixed behavior")
    logger.info("=" * 50)

    fixed_ssl_context = create_client_ssl_context_fixed(config)
    fixed_result = await test_connection(
        fixed_ssl_context, test_url, "FIXED - respects verify_server=False"
    )

    # Summary
    logger.info(f"\n" + "=" * 50)
    logger.info("SUMMARY")
    logger.info("=" * 50)
    logger.info(
        f"🔴 Current behavior (broken): {'FAILED' if not broken_result else 'SUCCESS'}"
    )
    logger.info(f"🟢 Proposed fix: {'SUCCESS' if fixed_result else 'FAILED'}")

    if not broken_result and fixed_result:
        logger.info("\n✅ DEMONSTRATION SUCCESSFUL!")
        logger.info("   The issue is confirmed: verify_server=False is ignored")
        logger.info("   The proposed fix works: verify_server=False is respected")
    elif broken_result and not fixed_result:
        logger.info("\n❓ UNEXPECTED RESULT")
        logger.info("   Both approaches failed - may be a different issue")
    else:
        logger.info("\n❓ INCONCLUSIVE")
        logger.info("   Results don't clearly demonstrate the issue")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Demonstration interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Demonstration error: {e}")

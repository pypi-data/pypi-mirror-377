#!/usr/bin/env python3
"""
One-Command Test Runner for MCP Proxy Adapter
This script creates a fresh test environment and runs all tests.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Usage:
    python test_mcp_adapter.py
"""
import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description, cwd=None, timeout=300):
    """Run a command and return success status."""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"🔍 Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def main():
    """Main function to run complete test suite."""
    print("=" * 80)
    print("🎯 MCP PROXY ADAPTER - ONE-COMMAND TEST SUITE")
    print("=" * 80)
    print("This script will create a fresh test environment and run all tests.")
    print("=" * 80)
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"📁 Working directory: {current_dir}")
    
    # Clean up any existing test environment
    test_env_dir = current_dir / "test_environment"
    if test_env_dir.exists():
        print("🧹 Cleaning up existing test environment...")
        import shutil
        shutil.rmtree(test_env_dir)
        print("✅ Cleaned up existing test environment")
    
    # Step 1: Setup test environment
    print("\n" + "=" * 60)
    print("STEP 1: SETTING UP TEST ENVIRONMENT")
    print("=" * 60)
    
    setup_cmd = "python -m mcp_proxy_adapter.examples.setup_test_environment --output-dir test_environment"
    if not run_command(setup_cmd, "Setting up test environment"):
        print("❌ Failed to setup test environment. Aborting.")
        return False
    
    # Step 2: Generate test configurations
    print("\n" + "=" * 60)
    print("STEP 2: GENERATING TEST CONFIGURATIONS")
    print("=" * 60)
    
    config_cmd = "python -m mcp_proxy_adapter.examples.generate_test_configs --output-dir test_environment/configs"
    if not run_command(config_cmd, "Generating test configurations"):
        print("❌ Failed to generate configurations. Aborting.")
        return False
    
    # Step 3: Fix mTLS configurations and certificates
    print("\n" + "=" * 60)
    print("STEP 3: FIXING mTLS CONFIGURATIONS AND CERTIFICATES")
    print("=" * 60)
    
    # Fix certificate naming
    cert_fixes = [
        "ln -sf mcp_proxy_adapter_test_ca_ca.crt certs/mcp_proxy_adapter_ca_ca.crt",
        "ln -sf admin-client_client.crt certs/admin_cert.pem",
        "ln -sf admin-client_client.key certs/admin_key.pem",
        "ln -sf admin-client_client.crt certs/user_cert.pem",
        "ln -sf admin-client_client.key certs/user_key.pem"
    ]
    
    for fix_cmd in cert_fixes:
        run_command(fix_cmd, f"Fixing certificate: {fix_cmd.split()[-1]}", cwd=test_env_dir)
    
    # Fix mTLS configurations
    print("🔧 Fixing mTLS configurations...")
    
    # Read and fix mtls_with_roles.json
    mtls_with_roles_path = test_env_dir / "configs" / "mtls_with_roles.json"
    if mtls_with_roles_path.exists():
        try:
            import json
            with open(mtls_with_roles_path, 'r') as f:
                config = json.load(f)
            
            # Add default_protocol if missing
            if "protocols" in config and "default_protocol" not in config["protocols"]:
                config["protocols"]["default_protocol"] = "mtls"
            
            # Add client certificate paths if missing
            if "ssl" in config:
                if "client_cert_file" not in config["ssl"]:
                    config["ssl"]["client_cert_file"] = "certs/admin_cert.pem"
                if "client_key_file" not in config["ssl"]:
                    config["ssl"]["client_key_file"] = "certs/admin_key.pem"
            
            with open(mtls_with_roles_path, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Fixed mtls_with_roles.json")
        except Exception as e:
            print(f"⚠️ Warning: Failed to fix mtls_with_roles.json: {e}")
    
    # Read and fix mtls_no_roles.json
    mtls_no_roles_path = test_env_dir / "configs" / "mtls_no_roles.json"
    if mtls_no_roles_path.exists():
        try:
            import json
            with open(mtls_no_roles_path, 'r') as f:
                config = json.load(f)
            
            # Add UUID if missing
            if "uuid" not in config:
                import uuid
                config["uuid"] = str(uuid.uuid4())
            
            # Add default_protocol if missing
            if "protocols" in config and "default_protocol" not in config["protocols"]:
                config["protocols"]["default_protocol"] = "mtls"
            
            # Fix certificate paths in security.ssl section
            if "security" in config and "ssl" in config["security"]:
                ssl_config = config["security"]["ssl"]
                ssl_config["server_cert_file"] = "certs/localhost_server.crt"
                ssl_config["server_key_file"] = "keys/localhost_server.key"
                ssl_config["ca_cert_file"] = "certs/mcp_proxy_adapter_test_ca_ca.crt"
                ssl_config["client_cert_file"] = "certs/admin_cert.pem"
                ssl_config["client_key_file"] = "certs/admin_key.pem"
            
            with open(mtls_no_roles_path, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Fixed mtls_no_roles.json")
        except Exception as e:
            print(f"⚠️ Warning: Failed to fix mtls_no_roles.json: {e}")
    
    # Step 4: Run security tests
    print("\n" + "=" * 60)
    print("STEP 4: RUNNING SECURITY TESTS")
    print("=" * 60)
    
    test_cmd = "python -m mcp_proxy_adapter.examples.run_security_tests"
    test_success = run_command(test_cmd, "Running security tests", cwd=test_env_dir, timeout=600)
    
    # Step 5: Show final results
    print("\n" + "=" * 80)
    print("🎉 ONE-COMMAND TEST SUITE FINISHED")
    print("=" * 80)
    print("📋 SUMMARY:")
    print("✅ Test environment created successfully")
    print("✅ Configurations generated successfully")
    print("✅ Certificates generated and fixed")
    print("✅ Security tests executed")
    print(f"📁 Test environment location: {test_env_dir}")
    print("\n🔧 Available configurations:")
    print("   - HTTP: test_environment/configs/http_simple.json")
    print("   - HTTP + Token: test_environment/configs/http_token.json")
    print("   - HTTPS: test_environment/configs/https_simple.json")
    print("   - HTTPS + Token: test_environment/configs/https_token.json")
    print("   - mTLS: test_environment/configs/mtls_with_roles.json")
    print("\n📊 Test Results:")
    if test_success:
        print("✅ All tests completed successfully")
    else:
        print("⚠️ Some tests failed (check output above for details)")
    print("=" * 80)
    
    return test_success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

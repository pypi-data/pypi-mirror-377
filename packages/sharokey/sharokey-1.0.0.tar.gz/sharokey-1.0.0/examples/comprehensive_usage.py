#!/usr/bin/env python3
"""
Sharokey Python SDK - Comprehensive Usage Examples

This example demonstrates all the features of the Sharokey Python SDK,
including secret management, requests, attachments, and diagnostics.
All methods now return JSON data - no more parsed objects.

Usage:
    python comprehensive_usage.py
"""

import asyncio
import json
import os
from pathlib import Path

# Import Sharokey SDK
from sharokey import (
    SharokeyClient, 
    SharokeyError, 
    AuthenticationError, 
    ValidationError,
    NotFoundError,
    AttachmentError
)


async def main():
    """Main example function demonstrating all SDK features."""
    
    # Initialize client (requires API token)
    token = os.getenv('SHAROKEY_TOKEN')
    if not token:
        print("❌ Please set SHAROKEY_TOKEN environment variable")
        print("   Example: export SHAROKEY_TOKEN=your_api_token_here")
        return
    
    client = SharokeyClient(token=token)
    
    print("🚀 Sharokey Python SDK - Comprehensive Examples (JSON Only)")
    print("=" * 50)
    
    # =============================================================================
    # 1. SDK INFORMATION AND DIAGNOSTICS
    # =============================================================================
    
    print("\n📋 SDK Information")
    info = client.get_info()
    print(f"   Name: {info['name']} v{info['version']}")
    print(f"   Language: {info['language']}")
    print(f"   Features: {len(info['features'])} available")
    
    print("\n🔧 Configuration")
    config = client.get_config()
    print(f"   API URL: {config['api_url']}")
    print(f"   Timeout: {config['timeout']}s")
    print(f"   Has Token: {config['has_token']}")
    
    print("\n🏥 Health Check")
    try:
        health = await client.health()
        print(f"   Status: {health.get('status', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
    
    print("\n🧪 Comprehensive Diagnostics")
    test_results = await client.test()
    print(f"   Tests Passed: {test_results['passed']}/{test_results['total']}")
    for detail in test_results['details']:
        status = "✅" if detail['success'] else "❌"
        print(f"   {status} {detail['name']}: {detail['message']}")
    
    # =============================================================================
    # 2. BASIC SECRET OPERATIONS (JSON RESPONSES)
    # =============================================================================
    
    print("\n" + "=" * 50)
    print("📝 Basic Secret Operations (JSON)")
    print("=" * 50)
    
    try:
        # Create a simple secret - returns JSON
        print("\n📝 Creating simple secret...")
        secret1_response = await client.create(
            "This is my secret password: admin123",
            hours=24,
            views=3,
            description="Database credentials"
        )
        
        # Extract data from JSON response
        secret1_data = secret1_response['data']
        secret1_slug = secret1_data['slug']
        
        print(f"   ✅ Secret created: {secret1_slug}")
        print(f"   📋 Description: {secret1_data.get('description')}")
        print(f"   🔗 Share URL: {secret1_data.get('share_url')}")
        print(f"   👁️ Views: {secret1_data.get('current_views', 0)}/{secret1_data.get('maximum_views', 1)}")
        print(f"   📊 Response type: {type(secret1_response)}")
        
        # List all secrets - returns JSON
        print("\n📋 Listing all secrets...")
        secrets_response = await client.list(limit=10)
        
        # Extract secrets from JSON response
        secrets_data = secrets_response['data']
        secrets_list = secrets_data.get('items', [])
        
        print(f"   Found {len(secrets_list)} secrets:")
        print(f"   📊 Response type: {type(secrets_response)}")
        
        for secret in secrets_list[:3]:  # Show first 3
            is_expired = secret.get('is_expired', False)
            status = "🔴" if is_expired else "🟢"
            print(f"     {status} {secret['slug']} - {secret.get('description', 'No description')}")
        
        # Get specific secret details - returns JSON
        print(f"\n🔍 Getting details for {secret1_slug}...")
        detailed_response = await client.get(secret1_slug)
        detailed_data = detailed_response['data']
        
        print(f"   📅 Created: {detailed_data.get('created_at', 'N/A')}")
        print(f"   ⏰ Expires: {detailed_data.get('expiration', 'N/A')}")
        print(f"   🔒 Has password: {detailed_data.get('has_password', False)}")
        print(f"   📊 Response type: {type(detailed_response)}")
        
    except ValidationError as e:
        print(f"❌ Validation Error: {e}")
    except SharokeyError as e:
        print(f"❌ Sharokey Error: {e}")
    
    # =============================================================================
    # 3. ADVANCED SECRET FEATURES (JSON RESPONSES)
    # =============================================================================
    
    print("\n" + "=" * 50)
    print("🔐 Advanced Secret Features (JSON)")
    print("=" * 50)
    
    try:
        # Create secret with security features - returns JSON
        print("\n🔐 Creating secure secret with OTP and restrictions...")
        secure_response = await client.create(
            "Ultra-secret project details: Project Phoenix",
            hours=48,
            views=2,
            description="Project Phoenix confidential",
            message="This contains sensitive project information",
            password="SecurePass123",
            otp_email="admin@company.com",
            ip_whitelist="192.168.1.0/24,10.0.0.1",
            geolocation="FR,US,CA"
        )
        
        secure_data = secure_response['data']
        secure_slug = secure_data['slug']
        
        print(f"   ✅ Secure secret created: {secure_slug}")
        print(f"   🔐 Security features enabled:")
        print(f"     - Password protection: {secure_data.get('has_password', False)}")
        print(f"     - OTP type: {secure_data.get('otp_type', 'None')}")
        print(f"     - IP restrictions: {secure_data.get('ip_whitelist', 'None')}")
        print(f"     - Geo restrictions: {secure_data.get('geolocation', 'None')}")
        print(f"   📊 Response type: {type(secure_response)}")
        
        # Create secret with file attachments (simulated)
        print("\n📎 Creating secret with attachments...")
        try:
            # Note: This would require actual files. For demo, we'll show the syntax
            # Create some test files first
            test_file1 = Path("test_document.txt")
            test_file2 = Path("test_image.png") 
            
            # Create test files if they don't exist
            if not test_file1.exists():
                test_file1.write_text("This is a test document for Sharokey attachment demo.")
            if not test_file2.exists():
                test_file2.write_bytes(b"PNG fake data for demo")
            
            file_response = await client.create(
                "Documents for review",
                hours=72,
                views=5,
                description="Contract documents",
                attachments=[str(test_file1), str(test_file2)]
            )
            
            file_data = file_response['data']
            file_slug = file_data['slug']
            
            print(f"   ✅ Secret with files created: {file_slug}")
            print(f"   📎 Attachments: {file_data.get('attachments_count', 0)} files")
            print(f"   📄 Has attachments: {file_data.get('has_attachments', False)}")
            print(f"   📊 Response type: {type(file_response)}")
            
            # Cleanup test files
            test_file1.unlink(missing_ok=True)
            test_file2.unlink(missing_ok=True)
            
        except AttachmentError as e:
            print(f"   ⚠️ Attachment demo skipped: {e}")
            
    except Exception as e:
        print(f"❌ Error in advanced features: {e}")
    
    # =============================================================================
    # 4. SEARCH AND FILTERING (JSON RESPONSES)
    # =============================================================================
    
    print("\n" + "=" * 50)
    print("🔍 Search and Filtering (JSON)")
    print("=" * 50)
    
    try:
        # Search for specific secrets - returns JSON
        print("\n🔍 Searching for 'database' secrets...")
        search_response = await client.search("database", limit=10, status="active")
        search_data = search_response['data']
        search_items = search_data.get('items', [])
        
        print(f"   Found {len(search_items)} results:")
        print(f"   📊 Response type: {type(search_response)}")
        
        for secret in search_items:
            print(f"     🔍 {secret['slug']} - {secret.get('description', 'No description')}")
        
        # Get only active secrets - returns JSON
        print("\n🟢 Getting active secrets only...")
        active_response = await client.get_active_secrets(limit=20)
        active_data = active_response['data']
        active_items = active_data.get('items', [])
        
        print(f"   Found {len(active_items)} active secrets")
        print(f"   📊 Response type: {type(active_response)}")
        
        # Filter by creator - returns JSON
        print("\n👤 Filtering secrets by creator...")
        user_response = await client.list(creator="admin@company.com", limit=10)
        user_data = user_response['data']
        user_items = user_data.get('items', [])
        
        print(f"   Found {len(user_items)} secrets by admin@company.com")
        print(f"   📊 Response type: {type(user_response)}")
        
    except Exception as e:
        print(f"❌ Error in search/filtering: {e}")
    
    # =============================================================================
    # 5. SECRET REQUESTS (JSON RESPONSES)
    # =============================================================================
    
    print("\n" + "=" * 50)
    print("📨 Secret Requests (JSON)")
    print("=" * 50)
    
    try:
        # Create a secret request - returns JSON
        print("\n📨 Creating secret request...")
        request_response = await client.create_request(
            message="Please share the API credentials for the new environment",
            description="Production API credentials request",
            secret_expiration_hours=24,
            request_expiration_hours=72,
            maximum_views=1,
            email_to="developer@company.com",
            email_reply="admin@company.com"
        )
        
        request_data = request_response['data']
        request_info = request_data.get('request', request_data)  # Handle different response structures
        request_token = request_info['token']
        
        print(f"   ✅ Request created: {request_token}")
        print(f"   📧 Sent to: {request_info.get('email_to', 'N/A')}")
        print(f"   🔗 Request URL: {request_info.get('url', 'N/A')}")
        print(f"   ⏰ Valid until: {request_info.get('request_expiration', 'N/A')}")
        print(f"   📊 Response type: {type(request_response)}")
        
        # List all requests - returns JSON
        print("\n📋 Listing secret requests...")
        requests_response = await client.list_requests(limit=10)
        requests_data = requests_response['data']
        requests_list = requests_data.get('requests', requests_data.get('items', []))
        
        print(f"   Found {len(requests_list)} requests:")
        print(f"   📊 Response type: {type(requests_response)}")
        
        for req in requests_list:
            is_active = req.get('status', 'unknown') == 'active'
            status_icon = "🟢" if is_active else "🔴"
            token_short = req.get('token', 'Unknown')[:12]
            print(f"     {status_icon} {token_short}... - {req.get('description', 'No description')}")
        
        # Get request details - returns JSON
        print(f"\n🔍 Getting details for request {request_token[:12]}...")
        request_details_response = await client.get_request(request_token)
        request_details_data = request_details_response['data']
        request_details = request_details_data.get('request', request_details_data)
        
        print(f"   📄 Description: {request_details.get('description', 'N/A')}")
        print(f"   📧 Email to: {request_details.get('email_to', 'N/A')}")
        print(f"   🔄 Status: {request_details.get('status', 'N/A')}")
        print(f"   👁️ Max views: {request_details.get('maximum_views', 1)}")
        print(f"   📊 Response type: {type(request_details_response)}")
        
        # Get request statistics - returns JSON
        print("\n📊 Request statistics...")
        request_stats_response = await client.request_stats()
        
        print(f"   📊 Response type: {type(request_stats_response)}")
        if 'data' in request_stats_response:
            stats_data = request_stats_response['data']
            print(f"   Total requests: {stats_data.get('total_requests', 0)}")
            print(f"   Active requests: {stats_data.get('active_requests', 0)}")
        else:
            print(f"   Raw stats: {json.dumps(request_stats_response, indent=2)}")
        
        # Clean up - delete the test request - returns JSON
        print(f"\n🗑️ Cleaning up test request...")
        delete_response = await client.delete_request(request_token)
        print(f"   ✅ Request {request_token[:12]}... deleted")
        print(f"   📊 Delete response type: {type(delete_response)}")
        
    except Exception as e:
        print(f"❌ Error in secret requests: {e}")
    
    # =============================================================================
    # 6. STATISTICS AND MONITORING (JSON RESPONSES)
    # =============================================================================
    
    print("\n" + "=" * 50)
    print("📊 Statistics and Monitoring (JSON)")
    print("=" * 50)
    
    try:
        # Get usage statistics - returns JSON
        print("\n📊 Getting usage statistics...")
        stats_response = await client.stats()
        stats_data = stats_response['data']
        
        print(f"   📊 Response type: {type(stats_response)}")
        print(f"   📈 Total secrets: {stats_data.get('total_secrets', 0)}")
        print(f"   🟢 Active secrets: {stats_data.get('active_secrets', 0)}")
        print(f"   🔴 Expired secrets: {stats_data.get('expired_secrets', 0)}")
        print(f"   👁️ Total views: {stats_data.get('total_views', 0)}")
        print(f"   🔐 Secrets with password: {stats_data.get('secrets_with_password', 0)}")
        print(f"   📅 Created today: {stats_data.get('secrets_created_today', 0)}")
        print(f"   📅 Created this week: {stats_data.get('secrets_created_this_week', 0)}")
        print(f"   📅 Created this month: {stats_data.get('secrets_created_this_month', 0)}")
        
        # Test connection
        print("\n🔌 Testing connection...")
        is_connected = await client.test_connection()
        print(f"   Connection status: {'✅ Connected' if is_connected else '❌ Disconnected'}")
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    
    # =============================================================================
    # 7. ERROR HANDLING EXAMPLES
    # =============================================================================
    
    print("\n" + "=" * 50)
    print("⚠️ Error Handling Examples")
    print("=" * 50)
    
    # Demonstrate validation errors
    print("\n⚠️ Demonstrating validation errors...")
    try:
        await client.create("", 24, 1)  # Empty content
    except ValidationError as e:
        print(f"   ✅ Caught validation error: {e}")
    
    try:
        await client.create("test", 0, 1)  # Invalid hours
    except ValidationError as e:
        print(f"   ✅ Caught validation error: {e}")
    
    try:
        await client.create("test", 24, 0)  # Invalid views
    except ValidationError as e:
        print(f"   ✅ Caught validation error: {e}")
    
    # Demonstrate not found error
    print("\n🔍 Demonstrating not found error...")
    try:
        await client.get("NONEXISTENT")
    except NotFoundError as e:
        print(f"   ✅ Caught not found error: {e}")
    
    # Demonstrate authentication error (if using invalid token)
    print("\n🔐 Authentication is working (no error to demonstrate)")
    
    # =============================================================================
    # 8. JSON STRUCTURE EXAMPLES
    # =============================================================================
    
    print("\n" + "=" * 50)
    print("📄 JSON Response Structure Examples")
    print("=" * 50)
    
    try:
        print("\n📝 Example: Create secret JSON response structure:")
        example_secret = await client.create(
            "Example for JSON structure demo",
            hours=1,
            views=1,
            description="JSON demo secret"
        )
        
        print("   Raw JSON response:")
        print(json.dumps(example_secret, indent=4))
        
        print("\n📊 Example: Stats JSON response structure:")
        example_stats = await client.stats()
        print("   Raw JSON response:")
        print(json.dumps(example_stats, indent=4))
        
        # Clean up
        example_slug = example_secret['data']['slug']
        await client.delete(example_slug)
        print(f"\n🗑️ Cleaned up example secret: {example_slug}")
        
    except Exception as e:
        print(f"❌ Error in JSON examples: {e}")
    
    print("\n" + "=" * 50)
    print("✅ All examples completed successfully!")
    print("🔐 Sharokey Python SDK (JSON-only mode) is ready for production use.")
    print("📊 All responses are now JSON dictionaries - no more parsed objects.")
    print("=" * 50)


def print_usage_guide():
    """Print usage guide for JSON-only mode."""
    print("=" * 60)
    print("SHAROKEY PYTHON SDK - JSON-ONLY MODE USAGE GUIDE")
    print("=" * 60)
    print()
    print("All methods now return JSON dictionaries instead of parsed objects.")
    print()
    print("BEFORE (with parsed objects):")
    print("  secret = await client.create('test')")
    print("  print(secret.slug)  # Object property")
    print()
    print("NOW (JSON only):")
    print("  response = await client.create('test')")
    print("  print(response['data']['slug'])  # JSON access")
    print()
    print("COMMON JSON STRUCTURES:")
    print("  Create: response['data']['slug']")
    print("  List: response['data']['items'][0]['slug']")
    print("  Stats: response['data']['total_secrets']")
    print("  Requests: response['data']['request']['token']")
    print()
    print("=" * 60)


if __name__ == "__main__":
    print_usage_guide()
    print()
    
    # Run the comprehensive examples
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Examples interrupted by user")
    except Exception as e:
        print(f"❌ Examples failed: {e}")
        print("Make sure to set SHAROKEY_TOKEN environment variable.")
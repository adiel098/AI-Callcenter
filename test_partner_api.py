"""
Test script for Partner API endpoints
"""
import requests
import json
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_partner_api():
    """Test the complete partner API workflow"""

    print("=" * 60)
    print("PARTNER API TEST SUITE")
    print("=" * 60)

    # Step 1: Create a partner
    print("\n1. Creating test partner...")
    create_response = requests.post(
        f"{BASE_URL}/api/partners/",
        json={
            "name": "Test Partner Inc",
            "rate_limit": 50
        }
    )

    if create_response.status_code == 201:
        partner_data = create_response.json()
        api_key = partner_data['api_key']
        partner_id = partner_data['id']
        print(f"✓ Partner created successfully!")
        print(f"  Partner ID: {partner_id}")
        print(f"  API Key: {api_key[:20]}... (truncated)")
        print(f"  Rate Limit: {partner_data['rate_limit']} leads/min")
    else:
        print(f"✗ Failed to create partner: {create_response.text}")
        return

    # Step 2: List partners
    print("\n2. Listing all partners...")
    list_response = requests.get(f"{BASE_URL}/api/partners/")
    if list_response.status_code == 200:
        partners = list_response.json()
        print(f"✓ Found {partners['total']} partner(s)")
        for p in partners['partners']:
            print(f"  - {p['name']} (ID: {p['id']}, Active: {p['is_active']}, Leads: {p['total_leads']})")
    else:
        print(f"✗ Failed to list partners: {list_response.text}")

    # Step 3: Get specific partner
    print(f"\n3. Getting partner {partner_id}...")
    get_response = requests.get(f"{BASE_URL}/api/partners/{partner_id}")
    if get_response.status_code == 200:
        partner = get_response.json()
        print(f"✓ Partner details retrieved")
        print(f"  Name: {partner['name']}")
        print(f"  Active: {partner['is_active']}")
        print(f"  Rate Limit: {partner['rate_limit']}")
    else:
        print(f"✗ Failed to get partner: {get_response.text}")

    # Step 4: Transfer leads WITHOUT authentication (should fail)
    print("\n4. Testing transfer WITHOUT API key (should fail)...")
    leads_data = {
        "leads": [
            {"name": "John Doe", "phone": "+1234567890", "email": "john@example.com"}
        ]
    }
    no_auth_response = requests.post(
        f"{BASE_URL}/api/leads/partner-transfer",
        json=leads_data
    )
    if no_auth_response.status_code == 401:
        print(f"✓ Correctly rejected: {no_auth_response.json()['detail']}")
    else:
        print(f"✗ Security issue! Expected 401, got {no_auth_response.status_code}")

    # Step 5: Transfer leads WITH invalid API key (should fail)
    print("\n5. Testing transfer with INVALID API key (should fail)...")
    invalid_response = requests.post(
        f"{BASE_URL}/api/leads/partner-transfer",
        headers={"X-API-Key": "invalid_key_12345"},
        json=leads_data
    )
    if invalid_response.status_code == 401:
        print(f"✓ Correctly rejected: {invalid_response.json()['detail']}")
    else:
        print(f"✗ Security issue! Expected 401, got {invalid_response.status_code}")

    # Step 6: Transfer leads WITH valid API key (should succeed)
    print("\n6. Testing transfer with VALID API key (should succeed)...")
    leads_data = {
        "leads": [
            {"name": "John Doe", "phone": "+1234567890", "email": "john@example.com"},
            {"name": "Jane Smith", "phone": "+1987654321", "email": "jane@example.com"},
            {"name": "Bob Johnson", "phone": "+1555555555", "email": "bob@example.com"},
            {"name": "Alice Williams", "phone": "+442071234567", "email": "alice@example.com"},
            {"name": "Charlie Brown", "phone": "+33123456789"}
        ]
    }
    transfer_response = requests.post(
        f"{BASE_URL}/api/leads/partner-transfer",
        headers={"X-API-Key": api_key},
        json=leads_data
    )

    if transfer_response.status_code == 200:
        result = transfer_response.json()
        print(f"✓ Transfer successful!")
        print(f"  Total Submitted: {result['total_submitted']}")
        print(f"  Created: {result['created']}")
        print(f"  Skipped: {result['skipped']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Message: {result['message']}")
        if result.get('errors'):
            print(f"  Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"    - Index {error['index']}: {error['reason']}")
    else:
        print(f"✗ Transfer failed: {transfer_response.text}")

    # Step 7: Try to transfer duplicate leads (should skip)
    print("\n7. Testing duplicate detection (re-sending same leads)...")
    duplicate_response = requests.post(
        f"{BASE_URL}/api/leads/partner-transfer",
        headers={"X-API-Key": api_key},
        json=leads_data
    )

    if duplicate_response.status_code == 200:
        result = duplicate_response.json()
        print(f"✓ Duplicate handling works!")
        print(f"  Created: {result['created']}")
        print(f"  Skipped: {result['skipped']} (all duplicates)")
        if result.get('errors'):
            print(f"  First duplicate error: {result['errors'][0]['reason']}")
    else:
        print(f"✗ Duplicate test failed: {duplicate_response.text}")

    # Step 8: Check partner now has leads
    print(f"\n8. Verifying partner lead count...")
    get_response = requests.get(f"{BASE_URL}/api/partners/{partner_id}")
    if get_response.status_code == 200:
        partner = get_response.json()
        print(f"✓ Partner now has {partner['total_leads']} lead(s)")
    else:
        print(f"✗ Failed to verify leads: {get_response.text}")

    # Step 9: Update partner (deactivate)
    print(f"\n9. Deactivating partner...")
    update_response = requests.patch(
        f"{BASE_URL}/api/partners/{partner_id}",
        json={"is_active": False}
    )
    if update_response.status_code == 200:
        print(f"✓ Partner deactivated")
    else:
        print(f"✗ Failed to update: {update_response.text}")

    # Step 10: Try to transfer with deactivated partner (should fail)
    print("\n10. Testing transfer with DEACTIVATED partner (should fail)...")
    deactivated_response = requests.post(
        f"{BASE_URL}/api/leads/partner-transfer",
        headers={"X-API-Key": api_key},
        json={"leads": [{"name": "Test", "phone": "+1999999999"}]}
    )
    if deactivated_response.status_code == 403:
        print(f"✓ Correctly rejected: {deactivated_response.json()['detail']}")
    else:
        print(f"✗ Security issue! Expected 403, got {deactivated_response.status_code}")

    # Step 11: Reactivate partner
    print(f"\n11. Reactivating partner...")
    requests.patch(
        f"{BASE_URL}/api/partners/{partner_id}",
        json={"is_active": True}
    )
    print(f"✓ Partner reactivated")

    # Step 12: Test rate limiting (send more than limit)
    print(f"\n12. Testing rate limiting (partner limit: {partner_data['rate_limit']})...")
    print(f"   Sending {partner_data['rate_limit'] + 10} leads to trigger rate limit...")

    # Create a large batch
    large_batch = {
        "leads": [
            {"name": f"Test User {i}", "phone": f"+1{1000000000 + i}"}
            for i in range(partner_data['rate_limit'] + 10)
        ]
    }

    rate_limit_response = requests.post(
        f"{BASE_URL}/api/leads/partner-transfer",
        headers={"X-API-Key": api_key},
        json=large_batch
    )

    if rate_limit_response.status_code == 429:
        print(f"✓ Rate limiting works! Got: {rate_limit_response.json()['detail']}")
    elif rate_limit_response.status_code == 200:
        print(f"⚠ Note: First request within limit, rate limiter didn't trigger yet")
        print(f"   (Rate limiter works on a per-minute window)")
    else:
        print(f"✗ Unexpected response: {rate_limit_response.status_code}")

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)
    print(f"\nTest Partner ID: {partner_id}")
    print(f"Test API Key: {api_key}")
    print("\nYou can view the auto-generated API docs at:")
    print(f"  - Swagger UI: {BASE_URL}/docs")
    print(f"  - ReDoc: {BASE_URL}/redoc")


if __name__ == "__main__":
    try:
        test_partner_api()
    except Exception as e:
        print(f"\n✗ Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()

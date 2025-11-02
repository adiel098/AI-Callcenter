"""
Test script for email calendar invite functionality.

This script tests:
1. EmailService initialization
2. .ics file generation
3. Email sending (if SMTP configured)
"""

import sys
from datetime import datetime, timedelta
from services.email_service import EmailService


def test_email_service():
    """Test email service with calendar invite"""
    print("=" * 60)
    print("Testing Email Calendar Invite Service")
    print("=" * 60)

    try:
        # Initialize email service
        print("\n1. Initializing email service...")
        email_service = EmailService()
        print("   ✅ Email service initialized successfully")
        print(f"   SMTP Host: {email_service.smtp_host}")
        print(f"   SMTP Port: {email_service.smtp_port}")
        print(f"   From Email: {email_service.from_email}")
        print(f"   Company Name: {email_service.from_name}")

    except Exception as e:
        print(f"   ❌ Failed to initialize email service: {e}")
        print("\n💡 Make sure SMTP credentials are configured in .env file:")
        print("   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD")
        return False

    # Test .ics generation (no SMTP needed)
    print("\n2. Testing .ics calendar file generation...")
    try:
        meeting_datetime = datetime.now() + timedelta(days=1)
        meeting_datetime = meeting_datetime.replace(hour=14, minute=0, second=0, microsecond=0)

        ics_content = email_service._create_ics_file(
            attendee_email="test@example.com",
            attendee_name="Test User",
            meeting_datetime=meeting_datetime,
            duration_minutes=30,
            meeting_title="Test Meeting - AI Scheduler",
            meeting_description="This is a test meeting to verify calendar invite functionality",
            location="Google Meet",
            google_meet_link="https://meet.google.com/xxx-yyyy-zzz"
        )

        print("   ✅ .ics file generated successfully")
        print(f"   File size: {len(ics_content)} bytes")

        # Save to file for inspection
        with open("test_invite.ics", "wb") as f:
            f.write(ics_content)
        print("   📄 Saved to: test_invite.ics (you can open this in your calendar app)")

    except Exception as e:
        print(f"   ❌ Failed to generate .ics file: {e}")
        return False

    # Test email sending (requires SMTP configuration)
    print("\n3. Testing email sending...")
    test_email = input("   Enter email address to test (or press Enter to skip): ").strip()

    if not test_email:
        print("   ⏭️  Skipping email send test")
        print("\n✅ .ics generation test passed!")
        print("\nTo test email sending:")
        print("1. Configure SMTP in .env file")
        print("2. Run this script again and provide test email address")
        return True

    try:
        meeting_datetime = datetime.now() + timedelta(days=1)
        meeting_datetime = meeting_datetime.replace(hour=14, minute=0, second=0, microsecond=0)

        print(f"   Sending test invite to {test_email}...")

        success = email_service.send_calendar_invite(
            attendee_email=test_email,
            attendee_name="Test Recipient",
            meeting_datetime=meeting_datetime,
            duration_minutes=30,
            meeting_title="Test Meeting - AI Scheduler",
            meeting_description="This is a test calendar invite from the AI Meeting Scheduler.\n\nIf you receive this, the email service is working correctly!",
            google_meet_link="https://meet.google.com/abc-defg-hij"
        )

        if success:
            print("   ✅ Email sent successfully!")
            print(f"\n   📧 Check {test_email} for the calendar invite")
            print("   The email should contain:")
            print("      - Meeting details in HTML format")
            print("      - .ics attachment for easy calendar import")
            print("      - Google Meet link")
            return True
        else:
            print("   ❌ Email sending failed")
            print("\n💡 Troubleshooting:")
            print("   1. Check SMTP credentials in .env")
            print("   2. For Gmail: Use App Password, not regular password")
            print("   3. Check logs for detailed error message")
            return False

    except Exception as e:
        print(f"   ❌ Email sending error: {e}")
        print("\n💡 Common issues:")
        print("   - Gmail: Need to enable 2FA and create App Password")
        print("   - Wrong SMTP host/port")
        print("   - Firewall blocking SMTP port 587")
        return False


def main():
    """Main test function"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        AI Scheduler - Email Calendar Invite Tester        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    success = test_email_service()

    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED")
        print("\nThe email invite system is ready to use!")
        print("\nNext steps:")
        print("1. Make a test call using your AI system")
        print("2. Book a meeting during the call")
        print("3. Verify the guest receives the calendar invite")
    else:
        print("❌ TEST FAILED")
        print("\nPlease fix the issues above and try again")
    print("=" * 60)
    print()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

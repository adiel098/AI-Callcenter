"""
Script to add sample data to the database for testing the frontend
Run this from the backend directory: cd backend && python add_sample_data.py
"""
from datetime import datetime, timedelta
from database import get_db
from models.lead import Lead
from models.call import Call
from models.meeting import Meeting

def add_sample_data():
    db = next(get_db())

    try:
        # Check if data already exists
        existing_leads = db.query(Lead).count()
        if existing_leads > 0:
            print(f"⚠️  Database already has {existing_leads} leads. Skipping...")
            return

        # Add sample leads
        leads_data = [
            {"name": "John Doe", "phone": "+1234567890", "email": "john@example.com", "company": "Acme Corp", "status": "contacted"},
            {"name": "Jane Smith", "phone": "+1234567891", "email": "jane@example.com", "company": "Tech Inc", "status": "meeting_scheduled"},
            {"name": "Bob Johnson", "phone": "+1234567892", "email": "bob@example.com", "company": "StartupXYZ", "status": "pending"},
            {"name": "Alice Williams", "phone": "+1234567893", "email": "alice@example.com", "company": "BigCo", "status": "contacted"},
            {"name": "Charlie Brown", "phone": "+1234567894", "email": "charlie@example.com", "company": "SmallBiz", "status": "not_interested"},
            {"name": "David Lee", "phone": "+1234567895", "email": "david@example.com", "company": "DataCorp", "status": "contacted"},
            {"name": "Emma Davis", "phone": "+1234567896", "email": "emma@example.com", "company": "CloudSoft", "status": "pending"},
            {"name": "Frank Miller", "phone": "+1234567897", "email": "frank@example.com", "company": "AI Solutions", "status": "contacted"},
        ]

        leads = []
        for lead_data in leads_data:
            lead = Lead(**lead_data)
            db.add(lead)
            leads.append(lead)

        db.commit()

        # Refresh to get IDs
        for lead in leads:
            db.refresh(lead)

        # Add sample calls
        calls_data = [
            {
                "lead_id": leads[0].id,
                "status": "completed",
                "outcome": "interested",
                "duration": 180,
                "transcript": "AI: Hello, this is calling from AI Scheduler. May I speak with John?\nUser: Yes, this is John.\nAI: Great! I'm calling to discuss scheduling a meeting. Are you available next week?\nUser: Sure, that works for me.\nAI: Excellent! I'll send you some time slots to choose from.",
                "started_at": datetime.now() - timedelta(hours=2),
                "ended_at": datetime.now() - timedelta(hours=2) + timedelta(minutes=3)
            },
            {
                "lead_id": leads[1].id,
                "status": "completed",
                "outcome": "meeting_scheduled",
                "duration": 240,
                "transcript": "AI: Hello Jane, this is from AI Scheduler.\nUser: Hi there!\nAI: I'd like to schedule a meeting with you. When would be convenient?\nUser: Tuesday at 2pm works great.\nAI: Perfect, I'll send you a calendar invite. Looking forward to speaking with you!",
                "started_at": datetime.now() - timedelta(hours=5),
                "ended_at": datetime.now() - timedelta(hours=5) + timedelta(minutes=4)
            },
            {
                "lead_id": leads[3].id,
                "status": "completed",
                "outcome": "callback",
                "duration": 120,
                "transcript": "AI: Hello Alice!\nUser: Hi, can you call me back tomorrow? I'm in a meeting.\nAI: Of course, I'll call you tomorrow at this same time. Have a great day!",
                "started_at": datetime.now() - timedelta(days=1),
                "ended_at": datetime.now() - timedelta(days=1) + timedelta(minutes=2)
            },
            {
                "lead_id": leads[4].id,
                "status": "completed",
                "outcome": "not_interested",
                "duration": 60,
                "transcript": "AI: Hello Charlie, this is from AI Scheduler.\nUser: I'm not interested, please remove me from your list.\nAI: I understand. I'll remove you from our contact list. Thank you for your time.",
                "started_at": datetime.now() - timedelta(hours=8),
                "ended_at": datetime.now() - timedelta(hours=8) + timedelta(minutes=1)
            },
            {
                "lead_id": leads[5].id,
                "status": "completed",
                "outcome": "interested",
                "duration": 200,
                "transcript": "AI: Hello David!\nUser: Hi there, what's this about?\nAI: I'm reaching out to schedule a demo of our new product. Would you be interested?\nUser: Yes, I'd like to learn more.\nAI: Great! Let me find some available times for you.",
                "started_at": datetime.now() - timedelta(hours=12),
                "ended_at": datetime.now() - timedelta(hours=12) + timedelta(minutes=3, seconds=20)
            },
        ]

        for call_data in calls_data:
            call = Call(**call_data)
            db.add(call)

        db.commit()

        # Add sample meetings
        meetings_data = [
            {
                "lead_id": leads[1].id,
                "scheduled_at": datetime.now() + timedelta(days=2, hours=14),
                "duration": 30,
                "status": "confirmed",
                "meeting_type": "video",
                "email": leads[1].email,
                "meeting_link": "https://meet.google.com/abc-defg-hij"
            },
            {
                "lead_id": leads[0].id,
                "scheduled_at": datetime.now() + timedelta(days=5, hours=10),
                "duration": 45,
                "status": "scheduled",
                "meeting_type": "phone",
                "email": leads[0].email
            },
            {
                "lead_id": leads[5].id,
                "scheduled_at": datetime.now() + timedelta(days=3, hours=15, minutes=30),
                "duration": 60,
                "status": "scheduled",
                "meeting_type": "video",
                "email": leads[5].email,
                "meeting_link": "https://zoom.us/j/123456789"
            },
        ]

        for meeting_data in meetings_data:
            meeting = Meeting(**meeting_data)
            db.add(meeting)

        db.commit()

        print("✅ Sample data added successfully!")
        print(f"   - {len(leads)} leads")
        print(f"   - {len(calls_data)} calls")
        print(f"   - {len(meetings_data)} meetings")
        print("\n🌐 Now refresh your browser at http://localhost:5175 to see the data!")

    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data()

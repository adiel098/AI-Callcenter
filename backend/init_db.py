"""Initialize database and add sample data"""
from datetime import datetime, timedelta
from database import engine, Base, get_db
from models.lead import Lead
from models.call import Call
from models.meeting import Meeting

# Create all tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created!")

# Add sample data
print("Adding sample data...")
db = next(get_db())

try:
    # Check if data already exists
    existing_leads = db.query(Lead).count()
    if existing_leads > 0:
        print(f"Database already has {existing_leads} leads. Skipping...")
    else:
        # Add sample leads
        leads_data = [
            {"name": "John Doe", "phone": "+1234567890", "email": "john@example.com", "status": "contacted"},
            {"name": "Jane Smith", "phone": "+1234567891", "email": "jane@example.com", "status": "meeting_scheduled"},
            {"name": "Bob Johnson", "phone": "+1234567892", "email": "bob@example.com", "status": "pending"},
            {"name": "Alice Williams", "phone": "+1234567893", "email": "alice@example.com", "status": "contacted"},
            {"name": "Charlie Brown", "phone": "+1234567894", "email": "charlie@example.com", "status": "not_interested"},
            {"name": "David Lee", "phone": "+1234567895", "email": "david@example.com", "status": "contacted"},
            {"name": "Emma Davis", "phone": "+1234567896", "email": "emma@example.com", "status": "pending"},
            {"name": "Frank Miller", "phone": "+1234567897", "email": "frank@example.com", "status": "contacted"},
        ]

        leads = []
        for lead_data in leads_data:
            lead = Lead(**lead_data)
            db.add(lead)
            leads.append(lead)

        db.commit()
        for lead in leads:
            db.refresh(lead)

        # Add sample calls
        calls_data = [
            {
                "lead_id": leads[0].id,
                "outcome": "completed",
                "duration": 180,
                "transcript": "AI: Hello, this is calling from AI Scheduler. May I speak with John?\\nUser: Yes, this is John.\\nAI: Great! I'm calling to discuss scheduling a meeting. Are you available next week?\\nUser: Sure, that works for me.",
                "started_at": datetime.now() - timedelta(hours=2),
                "ended_at": datetime.now() - timedelta(hours=2) + timedelta(minutes=3)
            },
            {
                "lead_id": leads[1].id,
                "outcome": "meeting_scheduled",
                "duration": 240,
                "transcript": "AI: Hello Jane, this is from AI Scheduler.\\nUser: Hi there!\\nAI: I'd like to schedule a meeting with you. When would be convenient?\\nUser: Tuesday at 2pm works great.\\nAI: Perfect, I'll send you a calendar invite.",
                "started_at": datetime.now() - timedelta(hours=5),
                "ended_at": datetime.now() - timedelta(hours=5) + timedelta(minutes=4)
            },
            {
                "lead_id": leads[3].id,
                "outcome": "no_answer",
                "duration": 120,
                "transcript": "AI: Hello Alice!\\nUser: Hi, can you call me back tomorrow? I'm in a meeting.\\nAI: Of course, I'll call you tomorrow. Have a great day!",
                "started_at": datetime.now() - timedelta(days=1),
                "ended_at": datetime.now() - timedelta(days=1) + timedelta(minutes=2)
            },
            {
                "lead_id": leads[4].id,
                "outcome": "not_interested",
                "duration": 60,
                "transcript": "AI: Hello Charlie.\\nUser: I'm not interested.\\nAI: I understand. Thank you for your time.",
                "started_at": datetime.now() - timedelta(hours=8),
                "ended_at": datetime.now() - timedelta(hours=8) + timedelta(minutes=1)
            },
            {
                "lead_id": leads[5].id,
                "outcome": "completed",
                "duration": 200,
                "transcript": "AI: Hello David!\\nUser: Hi there, what's this about?\\nAI: I'm reaching out to schedule a demo. Would you be interested?\\nUser: Yes, I'd like to learn more.",
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
                "scheduled_time": datetime.now() + timedelta(days=2, hours=14),
                "status": "confirmed",
                "guest_email": leads[1].email
            },
            {
                "lead_id": leads[0].id,
                "scheduled_time": datetime.now() + timedelta(days=5, hours=10),
                "status": "scheduled",
                "guest_email": leads[0].email
            },
            {
                "lead_id": leads[5].id,
                "scheduled_time": datetime.now() + timedelta(days=3, hours=15, minutes=30),
                "status": "scheduled",
                "guest_email": leads[5].email
            },
        ]

        for meeting_data in meetings_data:
            meeting = Meeting(**meeting_data)
            db.add(meeting)
        db.commit()

        print(f"Sample data added: {len(leads)} leads, {len(calls_data)} calls, {len(meetings_data)} meetings")
        print("Now refresh your browser at http://localhost:5175!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

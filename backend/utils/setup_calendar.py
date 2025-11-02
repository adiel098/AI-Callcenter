from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']

def setup_calendar_auth():
    """
    Authenticates with Google Calendar API and generates token.json

    This script will:
    1. Check if token.json exists and is valid
    2. If not, open browser for Google login
    3. Request calendar permissions
    4. Save credentials to token.json
    """
    # Get the project root directory (two levels up from this file)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))

    # Paths for credentials and token files
    credentials_path = os.path.join(project_root, 'backend', 'credentials.json')
    token_path = os.path.join(project_root, 'backend', 'token.json')

    # Also check project root for credentials.json (fallback)
    if not os.path.exists(credentials_path):
        credentials_path = os.path.join(project_root, 'credentials.json')
        token_path = os.path.join(project_root, 'token.json')

    print(f"🔍 Looking for credentials at: {credentials_path}")

    creds = None

    # Check if token.json already exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials
            creds.refresh(Request())
        else:
            # Run OAuth flow to get new credentials
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials to token.json
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    print("✅ Authentication successful! token.json created")
    print(f"📁 Token file location: {token_path}")

if __name__ == '__main__':
    setup_calendar_auth()

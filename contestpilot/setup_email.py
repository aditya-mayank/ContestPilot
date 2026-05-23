import getpass
from .database import set_preference

def run_email_setup():
    print("=========================================")
    print("      ContestPilot Email Setup           ")
    print("=========================================")
    print("ContestPilot uses Gmail to send you summaries.")
    print("-----------------------------------------")
    
    server = "smtp.gmail.com"
    port = "587"
        
    user = input(" 📧 Your Gmail Address: ").strip()
    
    print("\n 🔑 To send emails, Google requires an 'App Password' (not your main password).")
    print("    1. Go to: https://myaccount.google.com/apppasswords")
    print("    2. Create a new App Password named 'ContestPilot'.")
    print("    3. Paste the 16-character password below.")
    password = getpass.getpass(" App Password: ").replace(" ", "").strip()
    
    recipient = input("\n 🎯 Send alerts to this email (Press Enter to send to yourself): ").strip()
    if not recipient:
        recipient = user
    
    if user and password and recipient:
        set_preference('email_enabled', 'true')
        set_preference('smtp_server', server)
        set_preference('smtp_port', port)
        set_preference('smtp_user', user)
        set_preference('smtp_pass', password)
        set_preference('email_recipient', recipient)
        print("\n [Success] Email credentials saved securely to your local database.")
        print(" ContestPilot will now send email alerts for new and updated contests!")
    else:
        print("\n [Error] Missing required fields. Email setup aborted.")
        
if __name__ == '__main__':
    run_email_setup()

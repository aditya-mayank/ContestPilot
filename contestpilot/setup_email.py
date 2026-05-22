import getpass
from .database import set_preference

def run_email_setup():
    print("=========================================")
    print("      ContestPilot Email Setup           ")
    print("=========================================")
    print("This wizard will configure email notifications.")
    print("To disable email later, you can edit the preferences in DB.")
    print("-----------------------------------------")
    
    server = input("SMTP Server (default: smtp.gmail.com): ").strip()
    if not server:
        server = "smtp.gmail.com"
        
    port = input("SMTP Port (default: 587): ").strip()
    if not port:
        port = "587"
        
    user = input("SMTP Username (e.g. your email): ").strip()
    
    print("SMTP Password (for Gmail, use an App Password):")
    password = getpass.getpass("Password: ").strip()
    
    recipient = input("Recipient Email Address: ").strip()
    
    if user and password and recipient:
        set_preference('email_enabled', 'true')
        set_preference('smtp_server', server)
        set_preference('smtp_port', port)
        set_preference('smtp_user', user)
        set_preference('smtp_pass', password)
        set_preference('email_recipient', recipient)
        print("\n[Success] Email credentials saved securely to your local database.")
        print("ContestPilot will now send email alerts for new and updated contests!")
    else:
        print("\n[Error] Missing required fields. Email setup aborted.")
        
if __name__ == '__main__':
    run_email_setup()

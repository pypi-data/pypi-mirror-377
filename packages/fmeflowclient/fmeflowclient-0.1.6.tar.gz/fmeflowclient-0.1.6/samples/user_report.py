from fmeflowclient import FMEFlowClient

from dotenv import load_dotenv
import os

load_dotenv(r"../.env")

base_url = os.getenv("FMEFLOW_BASE_URL")
token = os.getenv("FMEFLOW_TOKEN")
verify_ssl = os.getenv("FMEFLOW_VERIFY_SSL", "true").lower() in ("true", "1", "yes")
client = FMEFlowClient(base_url=base_url, token=token, verify_ssl=verify_ssl)

workspaces = client.workspaces.all()
print(f"Total workspaces: {len(workspaces)}")

automations = client.automations.all()
print(f"Total automations: {len(automations)}")

projects = client.projects.all()
print(f"Total projects: {len(projects)}")

users = client.users.all()
print(f"Total users: {len(users)}")

usernames = [user.name for user in users]
for username in usernames:
    user_workspaces = [ws for ws in workspaces if ws.get('userName') == username]
    user_automations = [a for a in automations if a.get('userName') == username]
    user_projects = [p for p in projects if p.get('userName') == username]
    print(f'{"User": 20} | Workspaces | Automations | Projects')
    print("-" * 60)
    print(f'{username:20} | {len(user_workspaces):10} | {len(user_automations):11} | {len(user_projects):8}')

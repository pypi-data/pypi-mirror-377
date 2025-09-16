# Copyright 2025-present Erioon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Visit www.erioon.com/dev-docs for more information about the python SDK




"""
Erioon CLI - Command Line Interface for Scalable Project Deployment

This CLI tool allows you to manage projects, authenticate with Erioon, 
and deploy Python-based services or AI/ML models.

Features:
- Login via email/password or API key.
- Logout and clear saved credentials.
- Initialize a project by selecting from your Erioon projects.
- Deploy Python services with optional scheduling.
- Support for future AI/ML model deployment.

Commands:
- login    : Authenticate with Erioon using API key or email/password.
- logout   : Logout and remove saved credentials.
- init     : Initialize a project, choose deployment type, and deploy services.

Configuration:
- Credentials are stored in ~/.erioon/credentials.json
- Selected project info is stored in ~/.erioon/project.json

Dependencies:
- requests
- pyfiglet
- InquirerPy

Example Usage:
    $ erioon login
    $ erioon init
    $ erioon logout

"""


import argparse
import requests
import os
import json
from getpass import getpass
import pyfiglet
from InquirerPy import inquirer
import glob


CONFIG_DIR = os.path.expanduser("~/.erioon")
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "credentials.json")

def save_credentials(user_id: str):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({"user_id": user_id}, f)

def load_credentials():
    """Return user_id if already logged in, else None."""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE) as f:
                data = json.load(f)
            return data.get("user_id")
        except Exception:
            pass
    return None

def login():
    existing_user_id = load_credentials()
    if existing_user_id:
        print(f"Already logged in with account {existing_user_id}")
        return

    login_method = inquirer.select(
        message="How do you want to login?",
        choices=[
            {"name": "API Key", "value": "api_key"},
            {"name": "Access credentials", "value": "access_credentials"}
        ],
        pointer=">",
        instruction="Use arrows ↑↓ and Enter to confirm"
    ).execute()

    if login_method == "api_key":
        api_key = getpass("Enter your API Key: ").strip()
        payload = {"api_key": api_key, "email": None, "password": None}
    else:
        email = input("Email: ").strip()
        password = getpass("Password: ")
        payload = {"api_key": None, "email": email, "password": password}

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post("https://sdk.erioon.com/login_sdk", json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            user_id = data.get("_id")
            if user_id:
                print(f"✅ Welcome! You are now logged in as {user_id}.")
                save_credentials(user_id)
            else:
                print(f"❌ Login succeeded but no user_id returned.")
        else:
            error_message = response.text.strip()
            print(f"❌ {error_message}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        

def logout():
    if os.path.exists(CREDENTIALS_FILE):
        try:
            os.remove(CREDENTIALS_FILE)
            print("Successfully logged out of Erioon.")
        except Exception as e:
            print(f"Failed to logout: {e}")
    else:
        print("No account is currently logged in.")

def init():
    user_id = load_credentials()
    if not user_id:
        print("You must be logged in to initialize a project. Run `erioon login` first.")
        return

    headers = {"Content-Type": "application/json"}
    payload = {"user_id": user_id}

    try:
        response = requests.post(
            "https://sdk.erioon.com/get_projects_list",
            json=payload,
            headers=headers
        )
        if response.status_code != 200:
            print(f"Failed to fetch projects: {response.text}")
            return

        projects = response.json().get("projects", [])
        if not projects:
            print("No projects available for your account.")
            return

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return

    ascii_banner = pyfiglet.figlet_format("Erioon", font="slant", width=500)
    print(ascii_banner)
    print("Scalable and fast infra...\n\n")

    choices = [
        {
            "name": f"{proj.get('project_name', 'Unnamed Project')} ({proj.get('_id')})",
            "value": proj
        }
        for proj in projects
    ]

    selected_project = inquirer.select(
        message="Choose a project:",
        choices=choices,
        pointer=">",
        instruction="Use arrows ↑↓ and Enter to confirm"
    ).execute()

    action_choice = inquirer.select(
        message="What would you like to do?",
        choices=[
            {"name": "New Sandbox", "value": "sandbox"},
            {"name": "New Deployment", "value": "deployment"},
        ],
        pointer=">",
        instruction="Use arrows ↑↓ and Enter to confirm"
    ).execute()

    if action_choice == "sandbox":
        print("📦 Creating a new Playbox...")

        playbox_name = inquirer.text(
            message="Enter a name for your Playbox:",
            validate=lambda val: len(val.strip()) > 0
        ).execute()

        description = inquirer.text(
            message="Enter a brief description for your Playbox:",
            validate=lambda val: len(val.strip()) > 0
        ).execute()

        plan = inquirer.select(
            message="Choose a plan for your Playbox:",
            choices=[
                {"name": "Erioon-S", "value": "s"},
                {"name": "Erioon-M", "value": "m"},
                {"name": "Erioon-L", "value": "l"},
            ],
            pointer=">",
            instruction="Use arrows ↑↓ and Enter to confirm"
        ).execute()

        payload = {
            "user_id": user_id,
            "project_id": selected_project["_id"],
            "playbox_name": playbox_name,
            "description": description,
            "plan": plan,
            "provider": "azure",
            "interval": "monthly"
        }

        try:
            response = requests.post(
                "https://backend.erioon.com/create_playbox",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                result = response.json()
                playbox_id = result.get("playbox_id", "N/A")
                print(f"✅ Playbox '{playbox_name}' created successfully! Use this play_id to connect to it: {playbox_id}")
            else:
                print(f"❌ Playbox creation failed: {response.status_code} {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")

        return


    elif action_choice == "deployment":
        deployment_name = inquirer.text(
            message="Enter a name for this deployment:",
            validate=lambda val: len(val.strip()) > 0
        ).execute()

        selected_project["deployment_name"] = deployment_name

        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(os.path.join(CONFIG_DIR, "project.json"), "w") as f:
            json.dump(selected_project, f, indent=2)

        print(f"\nProject '{selected_project.get('project_name')}' ({selected_project.get('_id')}) selected.")
        print(f"Deployment name set to '{deployment_name}'\n")

        deployment_type = inquirer.select(
            message="What is the deployment type?",
            choices=[
                {"name": "🚀 Deploy Service", "value": "service"},
                # {"name": "🤖 Deploy AI/ML Model", "value": "ai_model"},
            ],
            pointer=">",
            instruction="Use arrows ↑↓ and Enter to confirm"
        ).execute()

        selected_project["deployment_type"] = deployment_type
        with open(os.path.join(CONFIG_DIR, "project.json"), "w") as f:
            json.dump(selected_project, f, indent=2)

        print(f"\nDeployment type '{deployment_type}' selected and saved.")

        if deployment_type == "service":
            deploy_service(selected_project, user_id)
        elif deployment_type == "ai_model":
            print("🚀 AI/ML model deployment coming soon...")


def deploy_service(selected_project, user_id):
    current_dir = os.getcwd()

    py_files = glob.glob(os.path.join(current_dir, "*.py"))
    req_files = glob.glob(os.path.join(current_dir, "requirements.txt"))

    if not user_id:
        print("❌ Deploy failed: You must be logged in to initialize a project. Run `erioon login` first.")
        return
    if not py_files:
        print("❌ Deploy failed: No .py files found in the current directory.")
        return
    if len(req_files) != 1:
        print("❌ Deploy failed: One requirements.txt must be present.")
        return

    py_choices = [{"name": os.path.basename(f), "value": f} for f in py_files]
    selected_file = inquirer.select(
        message="Which service would you like to run?",
        choices=py_choices,
        pointer=">",
        instruction="Use arrows ↑↓ and Enter to confirm"
    ).execute()

    print(f"✅ Selected file: {os.path.basename(selected_file)}")

    scheduled = inquirer.select(
        message="Is this a scheduled service?",
        choices=[
            {"name": "Yes", "value": True},
            {"name": "No", "value": False}
        ],
        pointer=">",
        instruction="Use arrows ↑↓ and Enter to confirm"
    ).execute()

    cron_schedule = None
    if scheduled:
        schedule_time = inquirer.text(
            message="Enter the scheduled time (HH:MM):",
            validate=lambda val: len(val.split(":")) == 2 and all(x.isdigit() for x in val.split(":")),
        ).execute()
        hour, minute = schedule_time.split(":")
        cron_schedule = f"{int(minute)} {int(hour)} * * *"  

    print("✅ Validation passed. Preparing deployment...")

    try:
        files = {
            "user_id": (None, user_id),
            "project_id": (None, selected_project["_id"]),
            "deployment_name": (None, selected_project.get("deployment_name", "default_deployment")),
            "requirements": ("requirements.txt", open(req_files[0], "rb"), "text/plain"),
            "source_file": (os.path.basename(selected_file), open(selected_file, "rb"), "text/x-python")
        }

        if cron_schedule:
            files["schedule"] = (None, cron_schedule)

        response = requests.post("https://sdk.erioon.com/service_deployment", files=files)

        if response.status_code == 200:
            print("✅ Service deployed successfully!")
        else:
            print(f"❌ Deployment failed: {response.status_code} {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Deployment request failed: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Erioon CLI")
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('login', help='Login to Erioon')
    subparsers.add_parser('logout', help='Logout from Erioon')
    subparsers.add_parser('init', help='Initialize an Erioon project')

    args = parser.parse_args()

    if args.command == 'login':
        login()
    elif args.command == 'logout':
        logout()
    elif args.command == 'init':
        init()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


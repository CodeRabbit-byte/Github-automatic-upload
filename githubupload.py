import requests
import json
import sys
import os
import base64
from datetime import datetime
from getpass import getpass

class GitHubAutomation:
    def __init__(self, token, username):
        self.token = token
        self.username = username
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def _request(self, method, endpoint, data=None, params=None):
        """Make API request to GitHub"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, 
                                       json=data, params=params)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None
    
    # Repository Operations
    def list_repos(self):
        """List repositories"""
        print(f"\n📚 Listing repositories for {self.username}...\n")
        repos = self._request("GET", "/user/repos", params={"per_page": 100})
        if repos:
            for repo in repos:
                visibility = "🔒 Private" if repo['private'] else "🌍 Public"
                print(f"  {visibility} - {repo['full_name']}")
        return repos
    
    def create_repo(self, name, private=False, description="", add_readme=True, readme_content=None):
        """Create a new repository"""
        print(f"\n🆕 Creating repository '{name}'...")
        data = {
            "name": name,
            "private": private,
            "description": description,
            "auto_init": add_readme
        }
        repo = self._request("POST", "/user/repos", data=data)
        if repo:
            print(f"✅ Created repository: {repo['html_url']}")
            
            # If custom README content provided, update it
            if add_readme and readme_content:
                print(f"📝 Updating README.md with custom content...")
                import time
                time.sleep(2)  # Wait for repo initialization
                
                content_encoded = base64.b64encode(readme_content.encode('utf-8')).decode('utf-8')
                readme_data = {
                    "message": "Update README.md",
                    "content": content_encoded,
                    "branch": "main"
                }
                
                # Get existing README to get its SHA
                existing_readme = self._request("GET", f"/repos/{self.username}/{name}/contents/README.md")
                if existing_readme and 'sha' in existing_readme:
                    readme_data["sha"] = existing_readme["sha"]
                
                update_result = self._request("PUT", f"/repos/{self.username}/{name}/contents/README.md", data=readme_data)
                if update_result:
                    print(f"✅ README.md updated successfully!")
        
        return repo
    
    def delete_repo(self, repo_name):
        """Delete a repository"""
        print(f"\n🗑️  Deleting repository '{repo_name}'...")
        confirm = input(f"⚠️  Are you sure you want to delete {self.username}/{repo_name}? (yes/no): ")
        if confirm.lower() == 'yes':
            result = self._request("DELETE", f"/repos/{self.username}/{repo_name}")
            if result is not None:
                print(f"✅ Deleted repository: {self.username}/{repo_name}")
            return result
        else:
            print("❌ Deletion cancelled")
            return None
    
    def upload_file(self, repo_name, branch="main"):
        """Upload a file to repository"""
        file_path = input("\n📁 Enter the full path of the file to upload: ").strip()
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        destination = input("📝 Enter destination path in repo (e.g., folder/file.txt): ").strip()
        commit_message = input("💬 Enter commit message: ").strip() or f"Upload {os.path.basename(file_path)}"
        
        print(f"\n📤 Uploading {file_path} to {repo_name}...")
        
        try:
            with open(file_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            
            # Check if file exists
            existing = self._request("GET", f"/repos/{self.username}/{repo_name}/contents/{destination}")
            
            data = {
                "message": commit_message,
                "content": content,
                "branch": branch
            }
            
            if existing and 'sha' in existing:
                data["sha"] = existing["sha"]
                print("📝 File exists, updating...")
            
            result = self._request("PUT", f"/repos/{self.username}/{repo_name}/contents/{destination}", data=data)
            
            if result:
                print(f"✅ File uploaded successfully!")
                print(f"🔗 URL: {result['content']['html_url']}")
            return result
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
    
    def download_file(self, repo_name, file_path):
        """Download a file from repository"""
        print(f"\n📥 Downloading {file_path} from {repo_name}...")
        
        result = self._request("GET", f"/repos/{self.username}/{repo_name}/contents/{file_path}")
        
        if result and 'content' in result:
            content = base64.b64decode(result['content']).decode('utf-8')
            
            save_path = input("💾 Enter path to save file (or press Enter for current directory): ").strip()
            if not save_path:
                save_path = os.path.basename(file_path)
            
            try:
                with open(save_path, 'w') as f:
                    f.write(content)
                print(f"✅ File saved to: {save_path}")
            except Exception as e:
                print(f"❌ Error saving file: {e}")
        
        return result
    
    # Workflow Operations
    def list_workflows(self, repo_name):
        """List GitHub Actions workflows"""
        print(f"\n⚙️  Listing workflows for {repo_name}...\n")
        workflows = self._request("GET", f"/repos/{self.username}/{repo_name}/actions/workflows")
        if workflows and 'workflows' in workflows:
            for wf in workflows['workflows']:
                status = "✅" if wf['state'] == 'active' else "⏸️"
                print(f"  {status} {wf['name']} (ID: {wf['id']})")
        return workflows
    
    def trigger_workflow(self, repo_name, workflow_id, ref="main"):
        """Trigger a workflow run"""
        print(f"\n▶️  Triggering workflow {workflow_id}...")
        data = {"ref": ref}
        result = self._request("POST", f"/repos/{self.username}/{repo_name}/actions/workflows/{workflow_id}/dispatches", data=data)
        if result is not None:
            print(f"✅ Workflow triggered successfully")
        return result
    
    # Gist Operations
    def create_gist(self):
        """Create a gist"""
        description = input("\n📝 Enter gist description: ").strip()
        file_path = input("📁 Enter file path to create gist from: ").strip()
        public = input("🌍 Make gist public? (yes/no): ").strip().lower() == 'yes'
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            filename = os.path.basename(file_path)
            files = {filename: {"content": content}}
            
            data = {
                "description": description,
                "public": public,
                "files": files
            }
            
            print(f"\n📤 Creating gist...")
            gist = self._request("POST", "/gists", data=data)
            if gist:
                print(f"✅ Created gist: {gist['html_url']}")
            return gist
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
    
    def list_gists(self):
        """List gists for authenticated user"""
        print(f"\n📋 Listing gists...\n")
        gists = self._request("GET", "/gists")
        if gists:
            for gist in gists:
                visibility = "🌍 Public" if gist['public'] else "🔒 Private"
                print(f"  {visibility} - {gist['description']} ({gist['html_url']})")
        return gists
    
    # User Operations
    def get_user_info(self):
        """Get authenticated user information"""
        print(f"\n👤 Getting user information...\n")
        user = self._request("GET", "/user")
        if user:
            print(f"  Username: {user['login']}")
            print(f"  Name: {user.get('name', 'N/A')}")
            print(f"  Email: {user.get('email', 'N/A')}")
            print(f"  Bio: {user.get('bio', 'N/A')}")
            print(f"  Public Repos: {user['public_repos']}")
            print(f"  Followers: {user['followers']}")
            print(f"  Following: {user['following']}")
        return user
    
    # Notification Operations
    def list_notifications(self):
        """List notifications"""
        print(f"\n🔔 Listing notifications...\n")
        notifications = self._request("GET", "/notifications")
        if notifications:
            for notif in notifications:
                print(f"  📌 {notif['subject']['title']} ({notif['reason']})")
        else:
            print("  ✨ No notifications")
        return notifications
    
    def mark_notifications_read(self):
        """Mark all notifications as read"""
        print(f"\n✅ Marking all notifications as read...")
        result = self._request("PUT", "/notifications")
        if result is not None:
            print("✅ All notifications marked as read")
        return result
    
    # Issue Operations
    def create_issue(self, repo_name):
        """Create an issue"""
        title = input("\n📝 Enter issue title: ").strip()
        body = input("💬 Enter issue body (optional): ").strip()
        
        print(f"\n🐛 Creating issue...")
        data = {"title": title, "body": body}
        issue = self._request("POST", f"/repos/{self.username}/{repo_name}/issues", data=data)
        if issue:
            print(f"✅ Created issue #{issue['number']}: {issue['html_url']}")
        return issue
    
    def list_issues(self, repo_name, state="open"):
        """List issues"""
        print(f"\n📋 Listing {state} issues for {repo_name}...\n")
        issues = self._request("GET", f"/repos/{self.username}/{repo_name}/issues", 
                              params={"state": state})
        if issues:
            for issue in issues:
                print(f"  #{issue['number']}: {issue['title']} ({issue['state']})")
        else:
            print(f"  ✨ No {state} issues")
        return issues


def print_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("🐙 GitHub Automation Tool")
    print("="*60)
    print("\n📦 Repository Operations:")
    print("  1. List repositories")
    print("  2. Create repository")
    print("  3. Delete repository")
    print("  4. Upload file to repository")
    print("  5. Download file from repository")
    print("\n⚙️  Workflow Operations:")
    print("  6. List workflows")
    print("  7. Trigger workflow")
    print("\n📝 Gist Operations:")
    print("  8. Create gist")
    print("  9. List gists")
    print("\n👤 User Operations:")
    print("  10. Get user info")
    print("\n🔔 Notification Operations:")
    print("  11. List notifications")
    print("  12. Mark all notifications as read")
    print("\n🐛 Issue Operations:")
    print("  13. Create issue")
    print("  14. List issues")
    print("\n  0. Exit")
    print("="*60)


def main():
    """Main function"""
    print("\n🐙 GitHub Automation Tool")
    print("="*60)
    
    # Get credentials
    username = input("Enter your GitHub username: ") #Change this and the token if you do not want to key in everytime
    token = input("Enter your GitHub token: ")
    
    if not username or not token:
        print("❌ Username and token are required!")
        sys.exit(1)
    
    gh = GitHubAutomation(token, username)
    
    # Verify credentials
    print("\n🔐 Verifying credentials...")
    user_info = gh._request("GET", "/user")
    if not user_info:
        print("❌ Authentication failed! Please check your token and try again.")
        sys.exit(1)
    
    print(f"✅ Authenticated as {user_info['login']}")
    
    while True:
        print_menu()
        choice = input("\n➡️  Enter your choice: ").strip()
        
        try:
            if choice == "1":
                gh.list_repos()
            
            elif choice == "2":
                name = input("\n📝 Enter repository name: ").strip()
                private = input("🔒 Make private? (yes/no): ").strip().lower() == 'yes'
                description = input("💬 Enter description (optional): ").strip()
                
                # README options
                add_readme = input("📄 Add README.md? (yes/no): ").strip().lower() == 'yes'
                readme_content = None
                
                if add_readme:
                    customize = input("✏️  Customize README content? (yes/no): ").strip().lower() == 'yes'
                    
                    if customize:
                        print("\n📝 Enter README content options:")
                        print("  1. Type content directly")
                        print("  2. Load from file")
                        content_choice = input("➡️  Choose option: ").strip()
                        
                        if content_choice == "1":
                            print("\n✏️  Enter README content (press Enter twice when done):")
                            lines = []
                            while True:
                                line = input()
                                if line == "" and len(lines) > 0 and lines[-1] == "":
                                    lines.pop()  # Remove last empty line
                                    break
                                lines.append(line)
                            readme_content = "\n".join(lines)
                        
                        elif content_choice == "2":
                            readme_path = input("📁 Enter path to README file: ").strip()
                            try:
                                with open(readme_path, 'r') as f:
                                    readme_content = f.read()
                                print("✅ README content loaded from file")
                            except Exception as e:
                                print(f"❌ Error reading file: {e}")
                                readme_content = None
                
                gh.create_repo(name, private, description, add_readme, readme_content)
            
            elif choice == "3":
                repo_name = input("\n📝 Enter repository name to delete: ").strip()
                gh.delete_repo(repo_name)
            
            elif choice == "4":
                repo_name = input("\n📝 Enter repository name: ").strip()
                branch = input("🌿 Enter branch (default: main): ").strip() or "main"
                gh.upload_file(repo_name, branch)
            
            elif choice == "5":
                repo_name = input("\n📝 Enter repository name: ").strip()
                file_path = input("📁 Enter file path in repository: ").strip()
                gh.download_file(repo_name, file_path)
            
            elif choice == "6":
                repo_name = input("\n📝 Enter repository name: ").strip()
                gh.list_workflows(repo_name)
            
            elif choice == "7":
                repo_name = input("\n📝 Enter repository name: ").strip()
                workflow_id = input("🆔 Enter workflow ID: ").strip()
                ref = input("🌿 Enter branch/ref (default: main): ").strip() or "main"
                gh.trigger_workflow(repo_name, workflow_id, ref)
            
            elif choice == "8":
                gh.create_gist()
            
            elif choice == "9":
                gh.list_gists()
            
            elif choice == "10":
                gh.get_user_info()
            
            elif choice == "11":
                gh.list_notifications()
            
            elif choice == "12":
                gh.mark_notifications_read()
            
            elif choice == "13":
                repo_name = input("\n📝 Enter repository name: ").strip()
                gh.create_issue(repo_name)
            
            elif choice == "14":
                repo_name = input("\n📝 Enter repository name: ").strip()
                state = input("📊 Enter state (open/closed/all): ").strip() or "open"
                gh.list_issues(repo_name, state)
            
            elif choice == "0":
                print("\n👋 Goodbye!")
                sys.exit(0)
            
            else:
                print("❌ Invalid choice! Please try again.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")


if __name__ == "__main__":

    main()

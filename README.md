# Github auto-uploaded
This is a program that gives you the ability to control your github account from the terminal, Windows os only.
# How to Use This Project

## 1. Run the Executable (EXE)
- When you run the executable, it will prompt you to enter your **GitHub username** and **personal access token**.  
- **Important:** These credentials are **not stored or shared** in any way. You will need to enter them each time.

## 2. Run via Python Script
- Alternatively, you can **hardcode your credentials** directly into the Python script at the `username` and `token` variables.  
- After adding your credentials, run the script using your preferred Python environment or compiler.

**Note:**  
- This project does **not share or store your GitHub credentials**, so your token is safe.  
- However, it is always a good practice to consider security precautions when handling personal access tokens.







# How to Get a GitHub Personal Access Token (PAT)

Follow these steps to generate a personal access token for GitHub:

## 1. Navigate to Developer Settings
1. Log in to your GitHub account.  
2. In the upper-right corner, click your profile picture, then select **Settings**.  
3. In the left sidebar, click **Developer settings**.  

## 2. Access Personal Access Tokens
1. In the left sidebar under **Personal access tokens**, choose either:  
   - **Tokens (classic)**  
   - **Fine-grained tokens** (recommended for more granular permission control)  

## 3. Generate a New Token
1. Click **Generate new token**.  
2. Depending on your choice:  
   - **Tokens (classic)** → click **Generate new token (classic)**  
   - **Fine-grained tokens** → click **Generate new token**  

## 4. Configure Token Details
- **Note/Token Name**: Provide a descriptive name (e.g., "CLI Access," "CI/CD Token").  
- **Expiration**: Set a reasonable expiration date. Avoid **No expiration** for security.  
- **Scopes/Permissions**: Select only the permissions your task requires.  
  - Example:  
    - Push code → select `repo` scope  
    - Manage GitHub Actions workflows → select `workflow` scope  

## 5. Generate and Copy the Token
1. After configuring details and selecting scopes, click **Generate token** at the bottom.  
2. Immediately **copy the token**. GitHub only shows it once. If lost, you’ll need to generate a new one.  



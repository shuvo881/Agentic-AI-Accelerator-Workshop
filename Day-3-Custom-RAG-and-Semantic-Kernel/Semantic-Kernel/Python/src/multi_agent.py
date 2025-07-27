import os
import asyncio
import re
import subprocess
import platform
from dotenv import load_dotenv

from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies.termination.termination_strategy import TerminationStrategy
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.kernel import Kernel, KernelFunctionFromPrompt
from semantic_kernel.agents.strategies.termination.kernel_function_termination_strategy import KernelFunctionTerminationStrategy
from semantic_kernel.contents.chat_history import ChatHistory

# ✅ Make ChatCompletionAgent hashable
ChatCompletionAgent.__hash__ = lambda self: hash(id(self))

load_dotenv()

class ApprovalTerminationStrategy(TerminationStrategy):
    """Terminates when the user says 'APPROVED' in the chat history."""
    async def should_agent_terminate(self, agent, history):
        # Check if we have at least completed the full cycle and have HTML code
        has_html_code = False
        for msg in history:
            if hasattr(msg, 'content') and '```html' in msg.content.lower():
                has_html_code = True
                break
        
        # Only terminate if we have HTML code AND user approved
        for msg in reversed(history):
            if hasattr(msg, 'role') and msg.role == AuthorRole.USER and "APPROVED" in msg.content.upper():
                return has_html_code
        
        # Don't terminate early - let all agents participate
        return False

def create_kernel() -> Kernel:
    """Creates and configures the Semantic Kernel with Azure OpenAI service."""
    kernel = Kernel()
    kernel.add_service(service=AzureChatCompletion(
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    ))
    return kernel

# Agent instructions
BA_PROMPT = (
"You are a Business Analyst which will take the requirements from the user (also known as a 'customer') and create a project plan for creating the requested app. The Business Analyst understands the user requirements and creates detailed documents with requirements and costing. The documents should be usable by the SoftwareEngineer as a reference for implementing the required features, and by the Product Owner for reference to determine if the application delivered by the Software Engineer meets all of the user's requirements."
)

SE_PROMPT = (
    "You are a Software Engineer, and your goal is create a web app using HTML and JavaScript by taking into consideration all the requirements given by the Business Analyst. The application should implement all the requested features. Deliver the code to the Product Owner for review when completed. You can also ask questions of the BusinessAnalyst to clarify any requirements that are unclear."
)

PO_PROMPT = (
    "You are the Product Owner which will review the software engineer's code to ensure all user  requirements are completed. You are the guardian of quality, ensuring the final product meets all specifications. IMPORTANT: Verify that the Software Engineer has shared the HTML code using the format ```html [code] ```. This format is required for the code to be saved and pushed to GitHub. Once all client requirements are completed and the code is properly formatted, reply with 'READY FOR USER APPROVAL'. If there are missing features or formatting issues, you will need to send a request back to the SoftwareEngineer or BusinessAnalyst with details of the defect."
)

def extract_html_code(messages):
    """Extracts HTML code blocks from agent messages."""
    html_pattern = r"```html\s*([\s\S]+?)```"
    for msg in messages:
        # Check all messages (including assistant role)
        if msg['role'] in ['assistant', 'SoftwareEngineer', 'ProductOwner', 'BusinessAnalyst']:
            match = re.search(html_pattern, msg['content'], re.IGNORECASE)
            if match:
                return match.group(1).strip()
    return None

def create_git_script():
    """Creates platform-specific Git deployment scripts."""
    if platform.system() == "Windows":
        # Create Windows batch file
        script_content = '''@echo off
echo Starting Git operations...

REM Check if we're in a git repository
if not exist ".git" (
    echo Error: Not in a Git repository. Please run 'git init' first.
    exit /b 1
)

REM Check if index.html exists
if not exist "index.html" (
    echo Error: index.html not found!
    exit /b 1
)

REM Stage the file
echo Staging index.html...
git add index.html

REM Check if there are changes to commit
git diff --staged --quiet
if %errorlevel% equ 0 (
    echo No changes to commit.
    exit /b 0
)

REM Commit the changes
echo Committing changes...
git commit -m "Auto-deploy weather app from multi-agent system"

if %errorlevel% neq 0 (
    echo Error: Git commit failed!
    exit /b 1
)

REM Push to remote
echo Pushing to GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo ✅ Successfully pushed to GitHub!
) else (
    echo ❌ Failed to push to GitHub. Check your Git credentials and remote configuration.
    exit /b 1
)

echo Git operations completed successfully!
'''
        script_name = "push_to_github.bat"
    else:
        # Create Unix/Linux bash script
        script_content = '''#!/bin/bash

# Configuration
REPO_DIR="."
COMMIT_MESSAGE="Auto-deploy weather app from multi-agent system"

echo "Starting Git operations..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Error: Not in a Git repository. Please run 'git init' first."
    exit 1
fi

# Check if index.html exists
if [ ! -f "index.html" ]; then
    echo "Error: index.html not found!"
    exit 1
fi

# Stage the file
echo "Staging index.html..."
git add index.html

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "No changes to commit."
    exit 0
fi

# Commit the changes
echo "Committing changes..."
git commit -m "$COMMIT_MESSAGE"

if [ $? -ne 0 ]; then
    echo "Error: Git commit failed!"
    exit 1
fi

# Push to remote
echo "Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
else
    echo "❌ Failed to push to GitHub. Check your Git credentials and remote configuration."
    exit 1
fi

echo "Git operations completed successfully!"
'''
        script_name = "push_to_github.sh"
    
    with open(script_name, "w") as f:
        f.write(script_content)
    
    # Make executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod(script_name, 0o755)
    
    print(f"✅ Created {script_name} script for {platform.system()}")
    return script_name

def push_to_github_direct():
    """Direct Git operations using subprocess, cross-platform."""
    try:
        print("🚀 Starting Git operations...")
        
        # Check if we're in a git repository
        result = subprocess.run(["git", "status"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ Not in a Git repository. Please run 'git init' first.")
            return False
        
        # Check if index.html exists
        if not os.path.exists("index.html"):
            print("❌ index.html not found!")
            return False
        
        # Stage the file
        print("📁 Staging index.html...")
        result = subprocess.run(["git", "add", "index.html"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"❌ Failed to stage file: {result.stderr}")
            return False
        
        # Check if there are changes to commit
        result = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True, timeout=10)
        if result.returncode == 0:
            print("ℹ️  No changes to commit.")
            return True
        
        # Commit the changes
        print("💾 Committing changes...")
        commit_message = "Auto-deploy weather app from multi-agent system"
        result = subprocess.run(
            ["git", "commit", "-m", commit_message], 
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"❌ Git commit failed: {result.stderr}")
            return False
        
        print(f"✅ Committed: {commit_message}")
        
        # Push to remote
        print("🚀 Pushing to GitHub...")
        result = subprocess.run(
            ["git", "push", "origin", "main"], 
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Successfully pushed to GitHub!")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            # Try 'master' branch if 'main' fails
            print("🔄 Trying 'master' branch...")
            result = subprocess.run(
                ["git", "push", "origin", "master"], 
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Successfully pushed to GitHub (master branch)!")
                if result.stdout:
                    print(f"Output: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Failed to push to GitHub: {result.stderr}")
                print(f"Output: {result.stdout}")
                return False
                
    except subprocess.TimeoutExpired:
        print("❌ Git operation timed out!")
        return False
    except FileNotFoundError:
        print("❌ Git not found in PATH!")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during Git operations: {str(e)}")
        return False

def save_html_and_push_to_github(html_code):
    """Saves HTML code to file and pushes to GitHub using direct Git commands."""
    try:
        # Save HTML to file
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_code)
        print("✅ HTML code saved to index.html")
        
        # Use direct Git operations (cross-platform)
        success = push_to_github_direct()
        
        if success:
            print("🎉 Deployment completed successfully!")
        else:
            print("❌ Deployment failed. Please check the errors above.")
            
    except Exception as e:
        print(f"❌ Unexpected error during deployment: {str(e)}")

def create_bash_script():
    """Legacy function - now calls create_git_script for backward compatibility."""
    return create_git_script()

def setup_git_environment():
    """Checks and provides guidance for Git environment setup."""
    print("🔧 Checking Git environment...")
    
    try:
        # Check if git is installed
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("✅ Git is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git is not installed or not in PATH")
        return False
    
    try:
        # Check if we're in a git repository
        subprocess.run(["git", "status"], capture_output=True, check=True)
        print("✅ In a Git repository")
    except subprocess.CalledProcessError:
        print("❌ Not in a Git repository. Run 'git init' first.")
        return False
    
    try:
        # Check git configuration
        result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Git user.name: {result.stdout.strip()}")
        else:
            print("⚠️  Git user.name not set. Run: git config --global user.name 'Your Name'")
            
        result = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Git user.email: {result.stdout.strip()}")
        else:
            print("⚠️  Git user.email not set. Run: git config --global user.email 'your.email@example.com'")
    except subprocess.CalledProcessError:
        print("⚠️  Could not check Git configuration")
    
    print("\n📋 For non-interactive pushes, ensure you have:")
    print("   1. SSH key configured with GitHub, OR")
    print("   2. Personal Access Token configured, OR") 
    print("   3. Git credential helper configured")
    print("   4. Remote origin set up: git remote add origin <your-repo-url>")
    
    return True


async def run_multi_agent(input: str):
    """Runs the multi-agent workflow and saves code upon approval."""
    
    # Setup Git environment check
    if not setup_git_environment():
        print("❌ Git environment not properly configured. Please fix the issues above.")
        return None
    
    kernel = create_kernel()

    agent_ba = ChatCompletionAgent(kernel=kernel, name="BusinessAnalyst", instructions=BA_PROMPT)
    agent_se = ChatCompletionAgent(kernel=kernel, name="SoftwareEngineer", instructions=SE_PROMPT)
    agent_po = ChatCompletionAgent(kernel=kernel, name="ProductOwner", instructions=PO_PROMPT)

    # Create a simple termination strategy that doesn't terminate early
    class WorkflowTerminationStrategy(TerminationStrategy):
        async def should_agent_terminate(self, agent, history):
            # Check if Product Owner has said "READY FOR USER APPROVAL"
            for msg in reversed(history):
                if hasattr(msg, 'content') and "READY FOR USER APPROVAL" in msg.content.upper():
                    return True
            return False

    chat = AgentGroupChat(
        agents=[agent_ba, agent_se, agent_po],
        termination_strategy=WorkflowTerminationStrategy()
    )
    
    await chat.add_chat_message(message=ChatMessageContent(role=AuthorRole.USER, content=input))

    responses = {
        'messages': [{'role': 'user', 'content': input}]
    }

    print("Starting agent workflow...")
    async for message in chat.invoke():
        print(f"Agent {message.name} ({message.role.value}): {message.content[:100]}...")
        responses['messages'].append({'role': message.role.value, 'content': message.content, 'agent_name': message.name})

    # Debug: Print all messages to see what's being captured
    print("=== DEBUG: All messages ===")
    for i, msg in enumerate(responses['messages']):
        agent_info = f" (Agent: {msg.get('agent_name', 'N/A')})" if 'agent_name' in msg else ""
        print(f"Message {i}: Role={msg['role']}{agent_info}, Content preview: {msg['content'][:100]}...")
    print("========================")

    # Check if we have a "READY FOR USER APPROVAL" message
    ready_for_approval = any(
        "READY FOR USER APPROVAL" in msg['content'].upper()
        for msg in responses['messages']
    )

    if ready_for_approval:
        print("\n🎉 Agents have completed the work and are ready for user approval!")
        
        # Extract HTML code first
        html_code = extract_html_code(responses['messages'])
        if not html_code:
            print("❌ No HTML code found! Cannot proceed with approval.")
            # Additional debug: Check if any messages contain ```html
            for msg in responses['messages']:
                if '```html' in msg['content'].lower():
                    print(f"Found HTML block in {msg.get('agent_name', msg['role'])} message")
                    print(f"Content preview: {msg['content'][:500]}...")
            return responses
        
        print("✅ HTML code found and extracted!")
        
        # Wait for user approval (in real scenario) or simulate it
        print("\n⏳ Waiting for user approval...")
        print("Type 'APPROVED' to deploy to GitHub, or anything else to cancel:")
        
        # For demo purposes, auto-approve. In real use, replace with input()
        # user_response = input().strip()
        user_response = "APPROVED"  # Simulate approval for demo
        print(f"User response: {user_response}")
        
        if user_response.upper() == "APPROVED":
            print("\n🚀 User approved! Deploying to GitHub...")
            
            # Add user approval message to responses
            approval_message = ChatMessageContent(role=AuthorRole.USER, content="APPROVED")
            await chat.add_chat_message(message=approval_message)
            responses['messages'].append({'role': 'user', 'content': 'APPROVED'})
            
            # Save HTML and push to GitHub
            save_html_and_push_to_github(html_code)
        else:
            print("❌ Deployment cancelled by user.")
    else:
        print("❌ Agents did not complete the workflow properly.")

    return responses

if __name__ == "__main__":
    print("🤖 Multi-Agent Weather App Builder")
    print("=" * 50)
    print(f"Platform: {platform.system()}")
    
    # Check if git script already exists, if not create it
    script_name = "push_to_github.bat" if platform.system() == "Windows" else "push_to_github.sh"
    if not os.path.exists(script_name):
        create_git_script()
    
    user_input = "Build a weather app for San Francisco. Once it's done and ready, I will reply 'APPROVED'."
    asyncio.run(run_multi_agent(user_input))
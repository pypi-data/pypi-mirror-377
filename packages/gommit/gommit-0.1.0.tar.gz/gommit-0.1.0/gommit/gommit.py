import subprocess
import os
from openai import OpenAI

def get_git_diff():
    """Get the staged git diff from the current directory."""
    try:
        result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True, check=True)
        diff = result.stdout
        if not diff:
            raise ValueError("No staged changes found. Stage your changes with 'git add' first.")
        return diff
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running git diff: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("Git is not installed or not found in PATH.")

def generate_commit_message(diff, api_key, base_url=None, model="gpt-4o-mini", max_tokens=150):
    """Send the staged diff to an OpenAI-compatible API to generate a commit message."""
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    prompt = (
        "You are a helpful assistant that generates concise, informative Git commit messages. "
        "Follow these guidelines:\n"
        "- Start with a short summary (50 characters or less) in imperative mood.\n"
        "- Use present tense (e.g., 'Add feature' not 'Added feature').\n"
        "- Optionally, add a body with more details if needed, separated by a blank line.\n"
        "- Focus on what changed and why, not how.\n"
        "- Keep it professional and clear.\n\n"
        "Generate a commit message for the following git diff:\n\n" + diff
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Error calling API: {str(e)}")

def main():
    """Main function to run the commit message generator."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    try:
        diff = get_git_diff()
        commit_msg = generate_commit_message(diff, api_key, base_url, model)
        print("Generated Commit Message:\n")
        print(commit_msg)
        
        confirm = input("\nDo you want to commit with this message? (y/n): ").strip().lower()
        if confirm == 'y':
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            print("Committed successfully.")
        else:
            print("Commit aborted.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

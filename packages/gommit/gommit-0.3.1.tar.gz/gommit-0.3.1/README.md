Git Commit AI
A Python tool to generate Git commit messages for staged changes using an OpenAI-compatible API.
Installation
From PyPI:
```bash
pip install gommit
```

### Requirements

- Python 3.6
-  Git installed and accessible in PATH
-   OpenAI API key set as an environment variable (OPENAI_API_KEY)

Environment Variables
Set the following environment variables in your ~/.bashrc or ~/.zshrc for persistence:
```bash
export OPENAI_API_KEY=your-api-key-here
export OPENAI_BASE_URL=https://api.openai.com/v1  # Optional, defaults to OpenAI API
export OPENAI_MODEL=gpt-4o-mini                   # Optional, defaults to gpt-4o-mini
```

Add them and reload your shell:
```bash
echo 'export OPENAI_API_KEY=your-api-key-here' >> ~/.bashrc
echo 'export OPENAI_BASE_URL=https://api.openai.com/v1' >> ~/.bashrc
echo 'export OPENAI_MODEL=gpt-4o-mini' >> ~/.bashrc
source ~/.bashrc
```

### Usage

Stage your changes in a Git repository:git add .


Run the `gommit`


Review the generated commit message and choose to commit (y) or abort (n).

### Notes

- The script uses git diff --cached to read only staged changes.
- Customize the API endpoint or model via OPENAI_BASE_URL and OPENAI_MODEL environment variables.
- Ensure your Git repository is properly initialized before running.


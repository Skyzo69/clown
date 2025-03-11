# BOT DIALOG

A simple Discord bot script to automate conversations based on predefined dialogs and templates, with support for manual message cancellation and dynamic replies.

## Prerequisites
- **Python 3.8+**
- Install dependencies:
  ```bash '''cmd
  pip install requests colorama tabulate pyfiglet
  pip install -r requirements.txt

Setup Files

1. token.txt
Purpose: Stores Discord tokens and their settings.
Format: token_name:token:min_interval:max_interval (one per line).
Requirements: At least 2 tokens.
Example:
Token1:your_discord_token1:5:10
Token2:your_discord_token2:5:10


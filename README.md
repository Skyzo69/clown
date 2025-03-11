# BOT DIALOG

A simple Discord bot script to automate conversations based on predefined dialogs and templates, with support for manual message cancellation and dynamic replies.

## Prerequisites
- **Python 3.8+**
- Install dependencies:
  ```bash '''cmd
  pip install -r requirements.txt
  
**Setup Files**

1. token.txt  

- Format: token_name:token:min_interval:max_interval (one per line).



- Example:


      Token1:your_discord_token1:5:10
      Token2:your_discord_token2:5:10


- Notes: Minimum 2 tokens required. Intervals in seconds.


2. template.txt  

- Format: [keyword1|keyword2] followed by response lines.



- Example:


      [halo|hi]
      Halo bro, kabarku baik!
      [apa kabar]
      Kabar baik, kamu gimana?


3. dialog.txt  

- Format: JSON array of dialog objects.



- Fields: 

text: Message content.



sender: Index of token (0-based).



reply_to: Optional, index of previous sender to reply to.



delay: Optional, custom delay in seconds.


- Example:

*json*

    [
       {"text": "Halo semua!", "sender": 0},
       {"text": "Apa kabar?", "sender": 1, "reply_to": 0, "delay": 10}
    ]







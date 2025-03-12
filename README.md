# BOT DIALOG

_A stupid Discord bot to automate conversations with predefined dialogs, dynamic replies, and manual message cancellation support, featuring human-like randomized timing patterns._

---

## Prerequisites
- **Python 3.8+**
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  
## Setup Files

### 1. token.txt

- Format: token_name:token:min_interval:max_interval (one per line).

- Example:

      Token1:your_discord_token1:5:10
      Token2:your_discord_token2:5:10

- Notes: Minimum 2 tokens required. Intervals in seconds.


### 2. template.txt

- Using AI prompts for better results

- Format: [keyword1|keyword2] followed by response lines.

- Example:

      [thanks|thx]  
      Np bro  
      All good  
        

### 3. dialog.txt

- Using AI prompts for better results

- Format: JSON array of dialog objects.

- Fields:

  - text: Message content.

  - sender: Index of token (0-based).

  - reply_to: Optional, index of previous sender to reply to.

  - delay: Optional, custom delay in seconds.


- Example:


    _json_

      [
        {"text": "Yo, wassup?", "sender": 0, "delay": 5},
        {"text": "All good friends, You?", "sender": 1, "reply_to": 0, "delay": 7},
        {"text": "Same, just finished a book", "sender": 0, "reply_to": 1, "delay": 10},
      ]

## Step-by-Step Usage

1. **Prepare Files**  
   - Create `token.txt`, `dialog.txt`, and `template.txt` as described above.

2. **Run the Script**  
   - Execute:
     ```bash
     python main.py
     ```

3. **Follow Prompts**  
   - Enter the channel ID (e.g., `123456789`).  
   - Set the start time in minutes (e.g., `0` for immediate start).  
   - Specify the number of delays (e.g., `1`).  
   - Input delay details (e.g., `2` messages, `30` seconds).  
   - Choose whether to change intervals after delays (e.g., `n`).

4. **Monitor Terminal**  
   - The script runs automated dialogs from `dialog.txt`.  
   - It polls messages and responds based on `template.txt`.  
   - Manual messages cancel pending auto-replies instantly.

## Features

- Automated dialogs with delays and replies.  
- Dynamic responses to mentions/replies using templates.  
- Manual messages stop auto-replies without delay.  
- Logging to `activity.log`.

## Notes

- Ensure tokens are valid Discord bot/user tokens.  
- Manual messages must be sent outside `dialog.txt` to cancel auto-replies.  
- Replies to others follow template rules and don’t cancel subsequent auto-messages.

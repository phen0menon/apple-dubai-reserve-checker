## Apple Store Reservation Checker (UAE)

Real-time monitoring tool that tracks and alerts you about reservation availability at Apple Stores, ensuring you never miss out on the latest products.

## How to install

### Prerequisites

Python >= 3.8. You can download Python here: https://www.python.org/downloads/

### Running application

1. Open project directory and open terminal in this directory.
2. Run the command to create venv: 
    ```
    python -m venv .venv
    ```
3. Activate the venv (MacOS / Linux): 
    ```
    source .venv/bin/activate
    ```
4. Install project dependencies: 
    ```
    pip install -r requirements.txt
    ```
5. <b>IMPORTANT</b>: make sure you configured your `.env` (read section below) according to your prefs. 
6. Run the application: 
    ```
    python main.py
    ``` 

### Configuring `.env` file

1. Copy `.env.example` file contents
2. Enter your telegram bot id and chat id where to post messages:
    - `TELEGRAM_BOT_ID`: You can use [BotFather](https://t.me/BotFather) for creating a bot. Obtain created bot token. You can do that in the BotFather. The bot token usually have the following pattern: `181283218:BBFRF3r-2Q4fSofzv-wDOFXKX6UIsd_GTtl`
    - `TELEGRAM_CHAT_ID`: An ID of Chat to push messages. You can use this bot to get the identifier: https://t.me/GetChatID_IL_BOT


### Automation

You can use crontab to automate this script to run in background.

1. Create a script .sh:
   ```sh
    #!/bin/bash
    cd /path/to/application
    source .venv/bin/activate
    python3 main.py
   ```
2. Make this script executable:
   ```
   chmod +x test-script.sh
   ```
3. Run `crontab -e` and enter the following (to enter the insert mode - press `I`):
   ```
   */5 * * * * /path/to/apple-checker.sh >> /path/to/logs/apple-checker.log
   ```
4. To exit vi, press Escape, then press `:x` and enter.
5. Run `crontab -l` to check if it worked

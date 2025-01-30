import time
import re
import requests
import configparser
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
config = configparser.ConfigParser()
config.read('config.ini')

logs_path = config['settings'].get('logs_path')
webhook_url = config['settings'].get('webhook_url')
ping = config['settings'].get('ping', 'no').lower() == 'yes'

def send(content, is_embed=False):
    if is_embed:
        embed_color = 0xffffff
        footer_text = "2b2t-notifier"
        message = {
            "embeds": [
                {
                    "title": "Queue notify",
                    "description": f"Position in queue: **{content}**",
                    "color": embed_color,
                    "footer": {
                        "text": footer_text,
                    }
                }
            ]
        }
    else:
        message = {
            "content": content
        }
    
    try:
        response = requests.post(webhook_url, json=message)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error sending message via Discord: {e}")

def parse_log_file():
    previous_pos = None

    if not os.path.isfile(logs_path):
        logging.error(f"Log file not found: {logs_path}")
        return

    try:
        with open(logs_path, 'r', encoding='utf-8') as file:
            file.seek(0, 2)
            while True:
                line = file.readline()
                if not line:
                    time.sleep(1) 
                    continue
                
                match = re.search(r'Position in queue: (\d+)', line)
                if match:
                    current_pos = match.group(1)
                    if current_pos != previous_pos:
                        previous_pos = current_pos
                        if ping:
                            send("@everyone")
                        logging.info(f"Current position: {current_pos}")
                        send(current_pos, is_embed=True)
    except Exception as e:
        logging.error(f"An error occurred while reading the log file: {e}")

if __name__ == "__main__":
    if not logs_path or not webhook_url:
        logging.error("Log file path and webhook URL must be configured.")
    else:
        parse_log_file()
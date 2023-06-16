# MassFBAccountCreate
🤖 likhon.py - Facebook Account Creation

This script allows you to create multiple Facebook accounts automatically. It utilizes the mechanize library to simulate browser interactions and the randomuser.me API to generate random account information. The created accounts are then sent to a Telegram channel for notification.

🔧 Features:

Generates random account information using the randomuser.me API. Creates a Facebook account using the generated information. Waits for and retrieves the OTP (One-Time Password) code from the temporary email address. Sends the created account details (name, email, password, and OTP code) to a Telegram channel. Supports proxy configuration for anonymity. ⚙️ Usage:

Replace 'YOUR_BOT_TOKEN' with your Telegram bot token. Replace 'YOUR_CHANNEL_ID' with your Telegram channel username or ID. Specify the number of accounts you want to create using the '-c' flag. Optionally, set a proxy using the '-p' flag for anonymity. Run the script using the command 'python main.py'. 📝 Note:

Make sure to have the required dependencies installed (mechanize, requests, telegram). Enjoy creating multiple Facebook accounts with ease! 🚀

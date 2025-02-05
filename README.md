# Remote 3D Printing Monitoring

Use a webcam to monitor 3D printing. Takes photos every 15 minutes and sends them to a Telegram chat.

## Usage

1. Create a Telegram bot:
  - Message @BotFather with `/newbot`
  - Save the bot token

2. Get your chat ID:
  - Message the bot
  - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
  - Find the `chat` > `id` field in the response

3. Point the webcam and run python

## Environment Variables Example

```env
TELEGRAM_TOKEN=YOUR_TOKEN
TELEGRAM_CHAT_ID=YOUR_ID

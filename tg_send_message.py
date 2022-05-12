import requests


def telegram_bot_sendtext(bot_message):
    
    bot_token = '5391670074:AAFAYmmkvPZhjBuQemh35pI7UHQtcHbniiU'
    bot_chatID = '@TradingSignals_MagicMole'

    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={bot_chatID}&parse_mode=Markdown&text={bot_message}'

    response = requests.get(send_text)

    return response.json()

s = 'some message'
telegram_bot_sendtext(s)
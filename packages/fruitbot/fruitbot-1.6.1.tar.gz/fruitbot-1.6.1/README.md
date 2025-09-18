## fruitbot
This library lets you use the game's API to automate everything in the Fruitcraft game. Basically, it provides the tools you need to write code that acts like a bot—playing the game for you, handling tasks, fighting battles, managing your tribe, upgrading assets, and more. With it, you can create programs that make the gameplay faster and easier, helping you grow in the game without manual effort.

## Quick Start
```python
from fruitbot import Client
from fruitbot.enums import CardPackTypes

bot = Client(session_name="fruit", restore_key="TOUR ACCOUNT RESTORE KEY")

data = bot.loadPlayer(save_session=True)
print(f"name: {data['name']},   amount of gold: {data['gold']},  id: {data['id']}")
print(bot.buyCardPack(CardPackTypes.BROWN_PACK))
```

## Encryption Notice

The `fruitbot` library uses the latest encryption method by default to match the current Fruitcraft game version.

To use the older encryption (e.g. for legacy accounts or testing), set `enc_version=1`:

```python
Client(session_name="fruit", restore_key="TOUR ACCOUNT RESTORE KEY", enc_version=1)
```

## Processing Updates
You can utilize the decorators `on_message_update()`, `on_player_status_update()`, `on_battle_alert()`, `on_battle_update()`, `on_auction_update()` and `on_tribe_membership_update()` to receive and process the updates you need. 

To start receiving updates, call the `comebackToGame()` method and set the `open_socket` argument to `True`.


For example:
```python
from fruitbot import Client
from fruitbot.exceptions import OnlineOnAnotherDevice, PlayingOnAnotherDevice
from colorama import Fore
from time import sleep

bot = Client(session_name="fruit", restore_key="YOUR ACCOUNT RESTORE KEY")

try:
    account_name = bot.loadPlayer(save_session=True)["name"]
except (OnlineOnAnotherDevice, PlayingOnAnotherDevice) as e:
    print(e)
    exit()

@bot.on_message_update()
def answerMessage(message: dict):
    if "سلام" in message["text"] and message["sender"] != account_name:
        bot.sendMessageToTribe(f"Hi {message['sender']}")
        sleep(1)
    print(f"{Fore.GREEN}\u202A{message['sender']}:\u202A{Fore.RESET} {message['text']}")

bot.comebackToGame(open_socket=True)
sleep(60)
bot.stopUpdates()
```
As demonstrated in the previous example, you can use the `stopUpdates()` method to terminate the reception of updates. Without invoking this method, updates will continue to be received forever, unless an issue arises.

If you ever need a specific update for any reason, `@on_special_event()` is here to assist you. The only required argument is `push_message_type`.
```python
@bot.on_special_event("battle_help")
def helpTribemate():
    # your code
    pass
```


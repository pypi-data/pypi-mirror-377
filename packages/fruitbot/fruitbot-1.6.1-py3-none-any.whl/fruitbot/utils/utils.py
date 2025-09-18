from ..configs import mobile_models
from ..data import loadJson
from random import choice
from string import ascii_lowercase, digits
from hashlib import md5
from typing import List, Dict, Union, Tuple
from time import time

class Utils:
    @staticmethod
    def generateRandomPassport():
        return "".join(choice(ascii_lowercase + digits) for _ in range(32))

    @staticmethod
    def generateRandomUdid():
        return "".join(choice(ascii_lowercase + digits) for _ in range(16))

    @staticmethod
    def getRandomMobileModel():
        return choice(mobile_models)

    @staticmethod
    def hashQueueNumber(q: int):
        return md5(str(q).encode()).hexdigest()

    @staticmethod
    def calculateGoldMiningPerHour(cards: List[dict]):
        if not isinstance(cards, (list, tuple)):
            raise TypeError(f"calculateGoldMiningPerHour() expected a list or tuple, not {type(cards).__name__}.")
        elif len(cards) > 4 or len(cards) < 1:
            raise ValueError(
                f"calculateGoldMiningPerHour() expected a list containing between 1 and 4 cards, got {len(cards)}.")
        power = sum(card['power'] for card in cards)
        return int(3 * power ** 0.7)

    @staticmethod
    def getMineOverflowDuration(gold_per_hour: int, storage_limit: int):
        return int(3600 // (gold_per_hour / storage_limit))

    @staticmethod
    def sortCardsByPower(cards: List[dict], return_ids_only: bool = False, limit: int = None,
                            ascending: bool = False) -> Union[List[int], List[Dict]]:
        sorted_cards = sorted(cards, key=lambda card: card['power'], reverse=not ascending)

        if limit is not None:
            sorted_cards = sorted_cards[:limit]

        if return_ids_only:
            return [card['id'] for card in sorted_cards]

        return sorted_cards

    @staticmethod
    def getStrongestCards(cards: List[dict], count: int = 4) -> List[int]:
        return Utils.sortCardsByPower(cards, True, count)

    @staticmethod
    def getWeakestCards(cards: List[dict], count: int = 1) -> List[int]:
        return Utils.sortCardsByPower(cards, True, count, True)

    @staticmethod
    def getReadyAndUnreadyCards(cards: List[dict]) -> Tuple[list, list]:
        all_cards_data = loadJson("cards.json")
        ready_cards, unready_cards = [], []
        now = int(time())
        for card in cards:
            if (now - card['last_used_at']) < all_cards_data[str(card['base_card_id'])]['cooldown']:
                unready_cards.append(card)
            else:
                ready_cards.append(card)

        return ready_cards, unready_cards

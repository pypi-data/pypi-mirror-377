class Genders:
    """
    The constants of this class can be used as an argument for the
    `gender` parameter in the `Client.changePlayerGender` method.
    """
    UNDEFINED = 0
    MALE = 1
    FEMALE = 2

class Moods:
    """
    The constants of this class can be used as an argument for the
    `mood_id` parameter in the `Client.changePlayerMood` method.
    """
    HAPPY = 1
    ANGRY = 2
    ASHAMED = 3
    BORED = 4
    CALM = 5
    CHEERFUL = 6
    COLD = 7
    PROUD = 8
    CONFUSED = 9
    CRANKY = 10
    CRAZY = 11
    CURIOUS = 12
    DEPRESSED = 13
    DISAPPOINTED = 14
    GOOD = 15
    HOPEFUL = 16
    HUNGRY = 17
    INDIFFERENT = 18
    APATHETIC = 19
    ALONE = 20

class AuctionCategories:
    """
    The constants of this class can be used as an argument for the
    `category` parameter in the `Client.searchAuctionCardsByFilters` method.
    """
    COMMON_CARDS = 0
    CHRISTMAS_CARDS = 1
    MONSTER_CARDS = 2

class AuctionPriceFilter:
    """
    The constants of this class can be used as an argument for the
    `price_filter` parameter in the `Client.searchAuctionCardsByFilters` method.
    """
    LOWEST_PRICE = 0
    HIGHEST_PRICE = 1

class BuildingTypes:
    """
    The constants of this class can be used as an argument for the
    `building_type` parameter in the `Client.assignCardsToBuilding` method.
    """
    GOLD_MINE = 1001
    OFFENSE_BUILDING = 1002
    DEFENSE_BUILDING = 1003

class CardPackTypes:
    """
    The constants of this class can be used as an argument for the
    `card_pack_type` parameter in the `Client.buyCardPack` method.

    The contents of each pack are as follows:
    - BROWN_PACK: 2 Level 1 cards.
    - GREEN_PACK: 2 Level 2 cards.
    - YELLOW_PACK: 2 Level 3 cards.
    - RED_PACK: 2 Level 3 or 4 cards.
    - SILVER_PACK: 20 Level 1 cards and 10 Level 2 cards.
    - GOLD_PACK: 2 Level 4 or 5 cards.
    - PLATINUM_PACK: 2 Level 5 or 6 cards.
    - BLACK_PACK: 2 Level 6 or 7 cards.
    - MONSTER_PACK: 1 Super Powerful Monster card.
    - CRYSTAL_PACK: 1 Crystal card.
    - HERO_PACK: 1 Hero card of your choice from `HeroCardPackTypes`.
    """
    BROWN_PACK = 1
    GREEN_PACK = 2
    YELLOW_PACK = 3
    RED_PACK = 4
    SILVER_PACK = 5
    GOLD_PACK = 6
    PLATINUM_PACK = 7
    BLACK_PACK = 8
    MONSTER_PACK = 16
    CRYSTAL_PACK = 25
    HERO_PACK = 32

class HeroCardPackTypes:
    """
    The constants of this class can be used as an argument for the
    `hero_card_pack_type` parameter in the `Client.buyHeroCardPack` method.
    """
    XAKHMI = 415
    XEBELUS = 515
    HUSHIDAR = 615
    SIBILU = 715

class TribeCapabilities:
    """
    The constants of this class can be used as an argument for the
    `hero_card_pack_type` parameter in the `Client.buyHeroCardPack` method.
    """
    ATTACK_BONUS = 1002
    DEFENSE_BONUS = 1003
    RECOVERY_TIME = 1004
    TRIBE_CAPACITY = 1005

class TribeStatuses:
    """
    The constants of this class can be used as an argument for the
    `status` parameter in the `Client.editTribeInfo` and `Client.createTribe` methods.
    """
    OPEN = 1
    INVITE_ONLY = 2
    CLOSED = 3


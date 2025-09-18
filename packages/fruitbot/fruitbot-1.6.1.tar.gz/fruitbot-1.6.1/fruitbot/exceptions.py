class FruitCraftException(Exception):
    """Base class for all FruitCraft exceptions."""

    def __init__(self, message, code=None, params: tuple = ()):
        super().__init__(message)
        self.code = code
        self.params = params


class UnknownError(FruitCraftException):
    def __init__(self):
        super().__init__("An unknown error occurred.")


class GeneralError(FruitCraftException):
    """Raised for general errors."""

    def __init__(self, params: tuple = (), message: str = "An unexpected error occurred, please try again.",
                 code: int = 100):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AccountBlocked(FruitCraftException):
    """Raised when the account is blocked."""

    def __init__(self, params: tuple = (), message: str = "Your account is blocked.", code: int = 101):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardNotFound(FruitCraftException):
    """Raised when a card is not found."""

    def __init__(self, params: tuple = (), message: str = "Card not found.", code: int = 102):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NoCardSelected(FruitCraftException):
    """Raised when no card is selected."""

    def __init__(self, params: tuple = (), message: str = "You should choose at least one card!", code: int = 103):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardAlreadyInAuction(FruitCraftException):
    """Raised when a card is already in auction."""

    def __init__(self, params: tuple = (), message: str = "Card is already in auction.", code: int = 104):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotEnoughCards(FruitCraftException):
    """Raised when there are not enough cards."""

    def __init__(self, params: tuple = (), message: str = "Not enough cards.", code: int = 105):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InconsistencyError(FruitCraftException):
    """Raised for inconsistency errors."""

    def __init__(self, params: tuple = (),
                 message: str = "An inconsistency error occurred about your action, please try again.",
                 code: int = 106):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardNotInAuction(FruitCraftException):
    """Raised when a card is not found in auctions."""

    def __init__(self, params: tuple = (), message: str = "Card not found in auctions.", code: int = 107):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxBidReached(FruitCraftException):
    """Raised when the maximum bid is reached."""

    def __init__(self, params: tuple = (),
                 message: str = "You cannot bid on this item, it's already reached the maximum price.",
                 code: int = 108):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CannotBidOwnCard(FruitCraftException):
    """Raised when a user tries to bid on their own card."""

    def __init__(self, params: tuple = (), message: str = "You cannot bid on your own cards.", code: int = 109):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AlreadyHighestBidder(FruitCraftException):
    """Raised when the user is already the highest bidder."""

    def __init__(self, params: tuple = (), message: str = "You are already the highest bidder.", code: int = 110):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AuctionClosed(FruitCraftException):
    """Raised when the auction is closed."""

    def __init__(self, params: tuple = (), message: str = "Too late! Auction is closed.", code: int = 111):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardTypeQuery(FruitCraftException):
    """Raised when querying for a card type."""

    def __init__(self, params: tuple = (), message: str = "What kind of card should I look for?", code: int = 112):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardTypeNotFound(FruitCraftException):
    """Raised when the selected card type is not found."""

    def __init__(self, params: tuple = (), message: str = "We cannot find the card type selected.", code: int = 113):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardTypeQueryDuplicate(FruitCraftException):
    """Raised when querying for a card type is duplicated."""

    def __init__(self, params: tuple = (), message: str = "What kind of card should I look for?", code: int = 114):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotOwnerError(FruitCraftException):
    """Raised when the user is not the owner of a card."""

    def __init__(self, params: tuple = (), message: str = "You are not the owner. Cannot proceed.", code: int = 115):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AccessDenied(FruitCraftException):
    """Raised when access is denied."""

    def __init__(self, params: tuple = (), message: str = "Access denied.", code: int = 116):
        super().__init__(message % params)
        self.code = code
        self.params = params


class ServerMaintenance(FruitCraftException):
    """Raised when the server is under maintenance."""

    def __init__(self, params: tuple = (), message: str = "Server is in maintenance. We will be available soon.",
                 code: int = 117):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NoCardsSpecified(FruitCraftException):
    """Raised when no cards are specified for an operation."""

    def __init__(self, params: tuple = (), message: str = "You need to specify some cards for this operation.",
                 code: int = 118):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NoOpponentSpecified(FruitCraftException):
    """Raised when no opponent is specified for an operation."""

    def __init__(self, params: tuple = (), message: str = "You need to specify an opponent for this operation.",
                 code: int = 119):
        super().__init__(message % params)
        self.code = code
        self.params = params


class BattleNotAvailable(FruitCraftException):
    """Raised when a battle cannot be started."""

    def __init__(self, params: tuple = (), message: str = "You can't start the battle right now, please try again.",
                 code: int = 120):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CannotAttackSelf(FruitCraftException):
    """Raised when a user tries to attack themselves."""

    def __init__(self, params: tuple = (), message: str = "You cannot attack yourself.", code: int = 121):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PlayerProtected(FruitCraftException):
    """Raised when a player is protected by a shield."""

    def __init__(self, params: tuple = (),
                 message: str = "Player is protected by shield, wait a few hours before attacking them again.",
                 code: int = 122):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CaptchaRequired(FruitCraftException):
    """Raised when a captcha code is required to proceed."""

    def __init__(self, params: tuple = (), message: str = "You have to enter captcha code to proceed.",
                 code: int = 123):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PlayingOnAnotherDevice(FruitCraftException):
    """Raised when the user is playing on another device."""

    def __init__(self, params: tuple = (),
                 message: str = "You are currently playing on another device, please close the game on other devices and try again in a few seconds.",
                 code: int = 124):
        super().__init__(message % params)
        self.code = code
        self.params = params


class OpponentNotFound(FruitCraftException):
    """Raised when the opponent is not found."""

    def __init__(self, params: tuple = (), message: str = "Opponent not found.", code: int = 125):
        super().__init__(message % params)
        self.code = code
        self.params = params


class OpponentOutOfRange(FruitCraftException):
    """Raised when the opponent is out of range."""

    def __init__(self, params: tuple = (), message: str = "Opponent not in your range.", code: int = 126):
        super().__init__(message % params)
        self.code = code
        self.params = params


class OpponentDefenseEmpty(FruitCraftException):
    """Raised when the opponent's defense deck is empty."""

    def __init__(self, params: tuple = (), message: str = "Opponent's defence deck is empty.", code: int = 127):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidCaptcha(FruitCraftException):
    """Raised when the captcha is invalid."""

    def __init__(self, params: tuple = (), message: str = "Captcha is invalid.", code: int = 128):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardInUse(FruitCraftException):
    """Raised when a card is in use and cannot be used in another operation."""

    def __init__(self, params: tuple = (),
                 message: str = "Card is used in one of your buildings and cannot be used here.", code: int = 129):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardMarkedForSacrifice(FruitCraftException):
    """Raised when a card is already marked for sacrifice."""

    def __init__(self, params: tuple = (), message: str = "Card is already marked for sacrifice.", code: int = 130):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxPowerReached(FruitCraftException):
    """Raised when a card has reached its maximum power."""

    def __init__(self, params: tuple = (), message: str = "Card has reached its maximum power.", code: int = 131):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxEvolutionsExceeded(FruitCraftException):
    """Raised when more than two cards are attempted to be evolved."""

    def __init__(self, params: tuple = (), message: str = "Cannot evolve more than two cards.", code: int = 132):
        super().__init__(message % params)
        self.code


class EvolveLimitExceeded(FruitCraftException):
    """Raised when trying to evolve more than two cards."""

    def __init__(self, params: tuple = (), message: str = "Only two cards of the same type can be evolved.",
                 code: int = 133):
        super().__init__(message % params)
        self.code = code
        self.params = params


class BuildingNotFound(FruitCraftException):
    """Raised when a building is not found."""

    def __init__(self, params: tuple = (), message: str = "The specified building was not found.", code: int = 134):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxCardsAssigned(FruitCraftException):
    """Raised when the maximum number of cards has been assigned."""

    def __init__(self, params: tuple = (), message: str = "Maximum number of cards assigned.", code: int = 135):
        super().__init__(message % params)
        self.code = code
        self.params = params


class LiveBattleUnavailable(FruitCraftException):
    """Raised when live battle is not available."""

    def __init__(self, params: tuple = (),
                 message: str = "Live-battle is not available due to some inconsistencies. We will be available soon.",
                 code: int = 136):
        super().__init__(message % params)
        self.code = code
        self.params = params


class OpponentOffline(FruitCraftException):
    """Raised when the opponent is no longer online."""

    def __init__(self, params: tuple = (), message: str = "Opponent is no longer online.", code: int = 137):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AlreadyInLiveBattle(FruitCraftException):
    """Raised when the user is already in a live battle."""

    def __init__(self, params: tuple = (), message: str = "Already in live-battle.", code: int = 138):
        super().__init__(message % params)
        self.code = code
        self.params = params


class OpponentBusy(FruitCraftException):
    """Raised when the opponent is busy."""

    def __init__(self, params: tuple = (), message: str = "Opponent is busy.", code: int = 139):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CannotAttackTribeMate(FruitCraftException):
    """Raised when a user tries to attack their tribemate."""

    def __init__(self, params: tuple = (), message: str = "You cannot attack your tribemate.", code: int = 140):
        super().__init__(message % params)
        self.code = code
        self.params = params


class BattleIdRequired(FruitCraftException):
    """Raised when a battle ID is required."""

    def __init__(self, params: tuple = (), message: str = "Battle ID required.", code: int = 141):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InconsistencyErrorUpdate(FruitCraftException):
    """Raised for inconsistency errors during updates."""

    def __init__(self, params: tuple = (),
                 message: str = "An inconsistency error occurred. Please update your game to the latest version and try again.",
                 code: int = 142):
        super().__init__(message % params)
        self.code = code
        self.params = params


class OperationTimeout(FruitCraftException):
    """Raised when an operation times out."""

    def __init__(self, params: tuple = (), message: str = "The operation is timed out. Please try again.",
                 code: int = 143):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PlayerUnavailable(FruitCraftException):
    """Raised when a player is not available."""

    def __init__(self, params: tuple = (),
                 message: str = "Player is not available right now. Please try again in a moment.", code: int = 144):
        super().__init__(message % params)
        self.code = code
        self.params = params


class BattleNotFound(FruitCraftException):
    """Raised when a battle is not found."""

    def __init__(self, params: tuple = (), message: str = "Battle not found. Please try again.", code: int = 145):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AttackerNotFound(FruitCraftException):
    """Raised when the attacker is not found."""

    def __init__(self, params: tuple = (), message: str = "Attacker not found. Please try again.", code: int = 146):
        super().__init__(message % params)
        self.code = code
        self.params = params


class DefenderNotFound(FruitCraftException):
    """Raised when the defender is not found."""

    def __init__(self, params: tuple = (), message: str = "Defender not found. Please try again.", code: int = 147):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeNotFound(FruitCraftException):
    """Raised when a tribe is not found."""

    def __init__(self, params: tuple = (), message: str = "Tribe not found. Please try again.", code: int = 148):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotInTribe(FruitCraftException):
    """Raised when the user is not in a tribe."""

    def __init__(self, params: tuple = (), message: str = "You are not in a tribe.", code: int = 149):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeHelpLimit(FruitCraftException):
    """Raised when the tribe cannot use help due to limitations."""

    def __init__(self, params: tuple = (),
                 message: str = "Your tribe cannot use help for not conforming to the tribe member limitation rule.",
                 code: int = 150):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MessageSizeExceeded(FruitCraftException):
    """Raised when the message size exceeds the limit."""

    def __init__(self, params: tuple = (), message: str = "Message size exceeded.", code: int = 151):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MessageNotFound(FruitCraftException):
    """Raised when a message is not found."""

    def __init__(self, params: tuple = (), message: str = "Message not found.", code: int = 152):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidInvitationTicket(FruitCraftException):
    """Raised when an invitation ticket is invalid."""

    def __init__(self, params: tuple = (), message: str = "Invalid invitation ticket.", code: int = 153):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidRestoreKey(FruitCraftException):
    """Raised when a restore key is invalid."""

    def __init__(self, params: tuple = (),
                 message: str = "You have entered an invalid restore key. Please contact customer care for more information.",
                 code: int = 154):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AccountChangeLimit(FruitCraftException):
    """Raised when the account cannot be changed more than once a day."""

    def __init__(self, params: tuple = (), message: str = "You cannot change your account more than once a day.",
                 code: int = 155):
        super().__init__(message % params)
        self.code = code
        self.params = params


class IdentificationRequired(FruitCraftException):
    """Raised when identification information is required."""

    def __init__(self, params: tuple = (), message: str = "We need your name or restore key for your identification.",
                 code: int = 156):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PlayerNotFound(FruitCraftException):
    """Raised when a player is not found."""

    def __init__(self, params: tuple = (),
                 message: str = "Player not found, please try again. If problem persists, be sure to let us know.",
                 code: int = 157):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvitationCodeAlreadyRedeemed(FruitCraftException):
    """Raised when an invitation code has already been redeemed."""

    def __init__(self, params: tuple = (), message: str = "You have already redeemed an invitation code.",
                 code: int = 158):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidEmail(FruitCraftException):
    """Raised when an invalid email address is provided."""

    def __init__(self, params: tuple = (), message: str = "Please enter a valid e-Mail address.", code: int = 159):
        super().__init__(message % params)
        self.code = code
        self.params = params


class EmailAlreadyExists(FruitCraftException):
    """Raised when the email address already exists."""

    def __init__(self, params: tuple = (), message: str = "e-Mail already exists.", code: int = 160):
        super().__init__(message % params)
        self.code = code
        self.params = params


class EmailAlreadyRegistered(FruitCraftException):
    """Raised when the email address has already been registered."""

    def __init__(self, params: tuple = (), message: str = "You have already registered a valid e-Mail address.",
                 code: int = 161):
        super().__init__(message % params)
        self.code = code
        self.params = params


class RewardAlreadyReceived(FruitCraftException):
    """Raised when a reward has already been received."""

    def __init__(self, params: tuple = (), message: str = "You have already received this reward.", code: int = 162):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AccountDeactivated(FruitCraftException):
    """Raised when the account is deactivated."""

    def __init__(self, params: tuple = (), message: str = "Your account is deactivated.", code: int = 163):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AccountResetFailed(FruitCraftException):
    """Raised when account reset fails."""

    def __init__(self, params: tuple = (), message: str = "Account reset failed.", code: int = 164):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidActivationCode(FruitCraftException):
    """Raised when the activation code is invalid."""

    def __init__(self,
                 params: tuple = (),
                 message: str = "Your activation code is invalid. Please contact customer care for more information.",
                 code: int = 165):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CashRewardNotFound(FruitCraftException):
    """Raised when the specified cash reward cannot be found."""

    def __init__(self, params: tuple = (), message: str = "The specified cash reward cannot be found.",
                 code: int = 166):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AvatarNotAvailable(FruitCraftException):
    """Raised when the selected avatar is not available."""

    def __init__(self, params: tuple = (), message: str = "Avatar is not available. Please try another one.",
                 code: int = 167):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotInLeague(FruitCraftException):
    """Raised when the user is not in a league."""

    def __init__(self, params: tuple = (), message: str = "You are not in a league.", code: int = 168):
        super().__init__(message % params)
        self.code = code
        self.params = params


class DeviceVerificationError(FruitCraftException):
    """Raised when there is trouble verifying the device."""

    def __init__(self,
                 params: tuple = (),
                 message: str = "We are having trouble to verify your device. Please contact customer care for more information.",
                 code: int = 169):
        super().__init__(message % params)
        self.code = code
        self.params = params


class StoreNotSupported(FruitCraftException):
    """Raised when the selected store is not supported."""

    def __init__(self, params: tuple = (), message: str = "The selected store is not supported yet.", code: int = 170):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PackInconsistencyError(FruitCraftException):
    """Raised for inconsistencies related to the selected pack."""

    def __init__(self,
                 params: tuple = (),
                 message: str = "An inconsistency occurred about your selected pack. Please restart your game and try again.",
                 code: int = 171):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PaymentReceiptNotProvided(FruitCraftException):
    """Raised when the receipt for a payment is not provided."""

    def __init__(self,
                 params: tuple = (),
                 message: str = "The receipt for your payment is not provided. If the problem persists, please contact customer care.",
                 code: int = 172):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardCannotEvolve(FruitCraftException):
    """Raised when a card cannot be evolved further."""

    def __init__(self, params: tuple = (), message: str = "You cannot evolve this card further.", code: int = 173):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InternalError(FruitCraftException):
    """Raised for internal errors."""

    def __init__(self, params: tuple = (), message: str = "An internal error occurred. We are trying to fix it ASAP.",
                 code: int = 174):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InternalErrorWait(FruitCraftException):
    """Raised for internal errors requiring a wait."""

    def __init__(self, params: tuple = (),
                 message: str = "An internal error occurred. Please wait for a moment and try again.",
                 code: int = 175):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PlayerNotParticipated(FruitCraftException):
    """Raised when a player did not participate in a battle."""

    def __init__(self, params: tuple = (), message: str = "Player did not participate in this battle.",
                 code: int = 176):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardCoolingDown(FruitCraftException):
    """Raised when a card is cooling down and unavailable."""

    def __init__(self, params: tuple = (), message: str = "Card is cooling down and unavailable right now.",
                 code: int = 177):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CardCoolEnough(FruitCraftException):
    """Raised when a card is cool enough to be used."""

    def __init__(self, params: tuple = (), message: str = "Card is cool enough.", code: int = 178):
        super().__init__(message % params)
        self.code = code
        self.params = params


class DeviceInconsistency(FruitCraftException):
    """Raised when there is an inconsistency about the device."""

    def __init__(self, params: tuple = (),
                 message: str = "There is an inconsistency about your device. Please contact customer care for more information.",
                 code: int = 179):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NameTooLong(FruitCraftException):
    """Raised when the provided name is too long."""

    def __init__(self, params: tuple = (),
                 message: str = "Name is too long. You can specify %s characters for your name.",
                 code: int = 180):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NameAlreadyTaken(FruitCraftException):
    """Raised when the provided name is already taken."""

    def __init__(self, params: tuple = (), message: str = "Name is already taken.", code: int = 181):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CountryCodeNotSupported(FruitCraftException):
    """Raised when the provided country code is not supported."""

    def __init__(self, params: tuple = (), message: str = "Your selected country code is not supported yet.",
                 code: int = 182):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotEnoughGold(FruitCraftException):
    """Raised when there is not enough gold."""

    def __init__(self, params: tuple = (), message: str = "You need %s more gold.", code: int = 183):
        super().__init__(message % params)
        self.code = code
        self.params = params


class OnlineOnAnotherDevice(FruitCraftException):
    """Raised when the player is online on another device."""

    def __init__(self, params: tuple = (), message: str = "You are currently online on another device.",
                 code: int = 184):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeNameTooLong(FruitCraftException):
    """Raised when the tribe name is too long."""

    def __init__(self, params: tuple = (), message: str = "Tribe name cannot exceed 30 characters.", code: int = 185):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TopTribeEditLimit(FruitCraftException):
    """Raised when the top tribe edit limit is reached."""

    def __init__(self, params: tuple = (), message: str = "Top 25 tribes cannot edit their information.",
                 code: int = 186):
        super().__init__(message % params)
        self.code = code
        self.params = params


class CannotSellCard(FruitCraftException):
    """Raised when a card cannot be sold."""

    def __init__(self, params: tuple = (), message: str = "You cannot sell crystal or hero cards.", code: int = 187):
        super().__init__(message % params)
        self.code = code
        self.params = params


class StatusRequired(FruitCraftException):
    """Raised when a status is required."""

    def __init__(self, params: tuple = (), message: str = "You need to specify a status!", code: int = 188):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeNotFound(FruitCraftException):
    """Raised when a tribe is not found."""

    def __init__(self, params: tuple = (), message: str = "Tribe not found.", code: int = 189):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NameRequired(FruitCraftException):
    """Raised when a name is required."""

    def __init__(self, params: tuple = (), message: str = "Name Required.", code: int = 190):
        super().__init__(message % params)
        self.code = code
        self.params = params


class DescriptionRequired(FruitCraftException):
    """Raised when a description is required."""

    def __init__(self, params: tuple = (), message: str = "Description Required.", code: int = 191):
        super().__init__(message % params)
        self.code = code
        self.params = params


class DescriptionTooLong(FruitCraftException):
    """Raised when the description is too long."""

    def __init__(self, params: tuple = (), message: str = "Description is Too Long.", code: int = 192):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeNameExists(FruitCraftException):
    """Raised when a tribe name already exists."""

    def __init__(self, params: tuple = (), message: str = "A tribe with the same name already exists.",
                 code: int = 193):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidChiefPlayers(FruitCraftException):
    """Raised when invalid chief players are provided."""

    def __init__(self, params: tuple = (), message: str = "Invalid chief players for tribe id %d", code: int = 194):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AlreadyInTribe(FruitCraftException):
    """Raised when a player is already a member of a tribe."""

    def __init__(self, params: tuple = (), message: str = "You are already a member of this tribe.", code: int = 195):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NoTribeBuilding(FruitCraftException):
    """Raised when the player does not have the tribe building yet."""

    def __init__(self, params: tuple = (), message: str = "You do not have the tribe building yet.", code: int = 196):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxTribeChangeLimit(FruitCraftException):
    """Raised when the maximum tribe change limitation is reached."""

    def __init__(self, params: tuple = (), message: str = "You have reached the maximum tribe change limitation.",
                 code: int = 197):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeNoMembers(FruitCraftException):
    """Raised when a tribe has no members."""

    def __init__(self, params: tuple = (), message: str = "Inconsistency exception! Tribe has no members.",
                 code: int = 198):
        super().__init__(message % params)
        self.code = code
        self.params = params


class UndecidedRequest(FruitCraftException):
    """Raised when there is an undecided request."""

    def __init__(self, params: tuple = (), message: str = "You already have an undecided request.", code: int = 199):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidDecisionParameter(FruitCraftException):
    """Raised when an invalid decision parameter is provided."""

    def __init__(self, params: tuple = (), message: str = "Invalid decision parameter. Please try again.",
                 code: int = 200):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotJoinRequest(FruitCraftException):
    """Raised when the request is not a join request."""

    def __init__(self, params: tuple = (),
                 message: str = "This is not a join request. Please contact customer care for more information.",
                 code: int = 201):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InconsistentDataProvided(FruitCraftException):
    """Raised when inconsistent data is provided."""

    def __init__(self,
                 params: tuple = (),
                 message: str = "Inconsistent Data Provided, please try again. If problem persists, be sure to let us know.",
                 code: int = 202):
        super().__init__(message % params)
        self.code = code
        self.params = params


class JoinRequestProcessed(FruitCraftException):
    """Raised when a join request has already been processed."""

    def __init__(self, params: tuple = (), message: str = "Join request has already been processed.", code: int = 203):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeFull(FruitCraftException):
    """Raised when a tribe is full."""

    def __init__(self, params: tuple = (), message: str = "Tribe is full.", code: int = 204):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeAccessDenied(FruitCraftException):
    """Raised when tribe access permission is denied."""

    def __init__(self, params: tuple = (), message: str = "Tribe access permission denied.", code: int = 205):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PlayerAlreadyInTribe(FruitCraftException):
    """Raised when a player is already a member of the tribe."""

    def __init__(self, params: tuple = (), message: str = "Player is already a member of this tribe.", code: int = 206):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotAnInvitation(FruitCraftException):
    """Raised when the request is not an invitation."""

    def __init__(self, params: tuple = (), message: str = "This is not an invitation.", code: int = 207):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvitationProcessed(FruitCraftException):
    """Raised when an invitation has already been processed."""

    def __init__(self, params: tuple = (), message: str = "Invitation has already been processed.", code: int = 208):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NoTribesAvailable(FruitCraftException):
    """Raised when there are no tribes available."""

    def __init__(self, params: tuple = (), message: str = "You do not have any tribes.", code: int = 209):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PlayerNotInYourTribe(FruitCraftException):
    """Raised when a player is not in your tribe."""

    def __init__(self, params: tuple = (), message: str = "Player is not in your tribe.", code: int = 210):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PlayerAlreadyPromoted(FruitCraftException):
    """Raised when a player is already promoted."""

    def __init__(self, params: tuple = (), message: str = "Player is already promoted.", code: int = 211):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PlayerNotElder(FruitCraftException):
    """Raised when a player is not an elder."""

    def __init__(self, params: tuple = (), message: str = "Player is not an elder.", code: int = 212):
        super().__init__(message % params)
        self.code = code
        self.params = params


class SelfPoke(FruitCraftException):
    """Raised when a player tries to poke themselves."""

    def __init__(self, params: tuple = (), message: str = "You can not poke yourself.", code: int = 213):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotAMemberOfTribe(FruitCraftException):
    """Raised when a player is not a member of the tribe."""

    def __init__(self, params: tuple = (), message: str = "You are not a member of this tribe.", code: int = 214):
        super().__init__(message % params)
        self.code = code
        self.params = params


class SelfKick(FruitCraftException):
    """Raised when a player tries to kick themselves."""

    def __init__(self, params: tuple = (), message: str = "You can not kick yourself.", code: int = 215):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InsufficientPermission(FruitCraftException):
    """Raised when a player does not have enough permission to perform an operation."""

    def __init__(self, params: tuple = (), message: str = "You don't have enough permission to do this operation.",
                 code: int = 216):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxLevelCooldownBuilding(FruitCraftException):
    """Raised when the maximum level for the cooldown building is reached."""

    def __init__(self, params: tuple = (), message: str = "Maximum level reached for Cooldown building.",
                 code: int = 217):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxLevelMainHallBuilding(FruitCraftException):
    """Raised when the maximum level for the main hall building is reached."""

    def __init__(self, params: tuple = (), message: str = "Maximum level reached for Main Hall building.",
                 code: int = 218):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxLevelDefenseBuilding(FruitCraftException):
    """Raised when the maximum level for the defense building is reached."""

    def __init__(self, params: tuple = (), message: str = "Maximum level reached for Defense building.",
                 code: int = 219):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxLevelOffenseBuilding(FruitCraftException):
    """Raised when the maximum level for the offense building is reached."""

    def __init__(self, params: tuple = (), message: str = "Maximum level reached for Offense building.",
                 code: int = 220):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxLevelGoldBuilding(FruitCraftException):
    """Raised when the maximum level for the gold building is reached."""

    def __init__(self, params: tuple = (), message: str = "Maximum level reached for Gold building.", code: int = 221):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxLevelBankBuilding(FruitCraftException):
    """Raised when the maximum level for the bank building is reached."""

    def __init__(self, params: tuple = (), message: str = "Maximum level reached for Bank building.", code: int = 222):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidBuildingTypeForUpgrade(FruitCraftException):
    """Raised when an invalid building type is provided for upgrade."""

    def __init__(self, params: tuple = (), message: str = "Invalid building type for upgrade.", code: int = 223):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MinimumDonationAmount(FruitCraftException):
    """Raised when the minimum donation amount is not met."""

    def __init__(self, params: tuple = (), message: str = "Minimum donation amount is %s golds.", code: int = 224):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PlayerNoTribeBuilding(FruitCraftException):
    """Raised when a player does not have the tribe building."""

    def __init__(self, params: tuple = (), message: str = "Player does not have the tribe building yet.",
                 code: int = 225):
        super().__init__(message % params)
        self.code = code
        self.params = params


class UndecidedInvitation(FruitCraftException):
    """Raised when a user has an undecided invitation."""

    def __init__(self, params: tuple = (), message: str = "User has an undecided invitation already.", code: int = 226):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotEnoughTribeMoney(FruitCraftException):
    """Raised when there is not enough tribe money."""

    def __init__(self, params: tuple = (), message: str = "Not enough tribe money.", code: int = 227):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeScoreUpdateFailed(FruitCraftException):
    """Raised when updating the tribe score fails."""

    def __init__(self,
                 params: tuple = (),
                 message: str = "Failed to update tribe score, please try again. If problem persists, be sure to let us know.",
                 code: int = 228):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeNoIdentifier(FruitCraftException):
    """Raised when a tribe has no identifier."""

    def __init__(self,
                 params: tuple = (),
                 message: str = "Tribe has no identifier, please try again. If problem persists, be sure to let us know.",
                 code: int = 229):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidBuildingTypeForCardCapacity(FruitCraftException):
    """Raised when an invalid building type is provided for card capacity."""

    def __init__(self, params: tuple = (), message: str = "Invalid building type for card capacity.", code: int = 230):
        super().__init__(message % params)
        self.code = code
        self.params = params


class OperationFailed(FruitCraftException):
    """Raised when an operation fails."""

    def __init__(self,
                 params: tuple = (),
                 message: str = "Operation failed, please try again. If problem persists, be sure to let us know.",
                 code: int = 231):
        super().__init__(message % params)
        self.code = code
        self.params = params


class GooglePlayVerificationFailed(FruitCraftException):
    """Raised when Google Play verification fails."""

    def __init__(self, params: tuple = (), message: str = "Google Play verification failed.", code: int = 232):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidPurchaseState(FruitCraftException):
    """Raised when the purchase state is invalid."""

    def __init__(self, params: tuple = (), message: str = "purchaseState is invalid. (%s)", code: int = 233):
        super().__init__(message % params)
        self.code = code
        self.params = params


class DataReadingError(FruitCraftException):
    """Raised when there is a problem reading data from the server."""

    def __init__(self, params: tuple = (), message: str = "Problem reading data from server", code: int = 234):
        super().__init__(message % params)
        self.code = code
        self.params = params


class SibcheVerificationFailed(FruitCraftException):
    """Raised when Sibche verification fails."""

    def __init__(self, params: tuple = (), message: str = "Sibche verification failed.", code: int = 235):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxBoostsLimit(FruitCraftException):
    """Raised when the maximum boosts limit is reached."""

    def __init__(self, params: tuple = (), message: str = "You cannot buy more boosts.", code: int = 236):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidCountryCode(FruitCraftException):
    """Raised when an invalid country code is provided."""

    def __init__(self, params: tuple = (), message: str = "Invalid country code.", code: int = 237):
        super().__init__(message % params)
        self.code = code
        self.params = params


class UserNotFound(FruitCraftException):
    """Raised when a user is not found."""

    def __init__(self, params: tuple = (), message: str = "User Not Found", code: int = 238):
        super().__init__(message % params)
        self.code = code
        self.params = params


class UserRecentlyPoked(FruitCraftException):
    """Raised when a user has been recently poked."""

    def __init__(self, params: tuple = (), message: str = "User has been recently poked.", code: int = 239):
        super().__init__(message % params)
        self.code = code
        self.params = params


class LeagueUpdateInProgress(FruitCraftException):
    """Raised when league update is in progress."""

    def __init__(self, params: tuple = (), message: str = "Updating league is in progress. Please wait.",
                 code: int = 240):
        super().__init__(message % params)
        self.code = code
        self.params = params


class FeatureNotImplemented(FruitCraftException):
    """Raised when a feature is not implemented yet."""

    def __init__(self, params: tuple = (), message: str = "This feature is not implemented yet :)", code: int = 241):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidLeagueId(FruitCraftException):
    """Raised when an invalid league ID is provided."""

    def __init__(self,
                 params: tuple = (),
                 message: str = "Operation failed (invalid league ID). Please contact customer care for more information.",
                 code: int = 242):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeHelpAlreadyInProgress(FruitCraftException):
    """Raised when tribe help is already in progress."""

    def __init__(self, params: tuple = (), message: str = "You should be fast! Your tribe mates are already helping",
                 code: int = 243):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NameRequired(FruitCraftException):
    """Raised when a name is required."""

    def __init__(self, params: tuple = (), message: str = "You should write a name", code: int = 244):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TutorialUpdateParameters(FruitCraftException):
    """Raised when tutorial updating requires more parameters."""

    def __init__(self, params: tuple = (), message: str = "Tutorial updating requires more parameters",
                 code: int = 245):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NoTribeAvailableToCoach(FruitCraftException):
    """Raised when there is no tribe available to coach."""

    def __init__(self, params: tuple = (), message: str = "No tribe available to coach, Try later", code: int = 246):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotEnoughNectar(FruitCraftException):
    """Raised when there is not enough nectar."""

    def __init__(self, params: tuple = (), message: str = "You need %s more nectar.", code: int = 247):
        super().__init__(message % params)
        self.code = code
        self.params = params


class HeroItemNotPurchased(FruitCraftException):
    """Raised when a hero item has not been purchased."""

    def __init__(self, params: tuple = (), message: str = "You've not bought this hero item.", code: int = 248):
        super().__init__(message % params)
        self.code = code
        self.params = params


class HeroItemAlreadyPurchased(FruitCraftException):
    """Raised when a hero item has already been purchased."""

    def __init__(self, params: tuple = (), message: str = "You've already bought this hero item.", code: int = 249):
        super().__init__(message % params)
        self.code = code
        self.params = params


class AllHeroesPurchased(FruitCraftException):
    """Raised when all heroes have been purchased."""

    def __init__(self, params: tuple = (), message: str = "You've bought all of the heroes!", code: int = 250):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotEnoughPotion(FruitCraftException):
    """Raised when there is not enough potion."""

    def __init__(self, params: tuple = (), message: str = "You have not enough potion.", code: int = 251):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidGiftCode(FruitCraftException):
    """Raised when an invalid gift code is entered."""

    def __init__(self, params: tuple = (), message: str = "Wrong gift code entered.", code: int = 252):
        super().__init__(message % params)
        self.code = code
        self.params = params


class GiftCodeAlreadyRedeemed(FruitCraftException):
    """Raised when a gift code has already been redeemed."""

    def __init__(self, params: tuple = (), message: str = "You've already redeemed this gift code", code: int = 253):
        super().__init__(message % params)
        self.code = code
        self.params = params


class GiftCodeExpired(FruitCraftException):
    """Raised when a gift code is expired."""

    def __init__(self, params: tuple = (), message: str = "Gift code is expired.", code: int = 254):
        super().__init__(message % params)
        self.code = code
        self.params = params


class HeroLevelRequirement(FruitCraftException):
    """Raised when a hero level requirement is not met."""

    def __init__(self, params: tuple = (), message: str = "You need at least one hero with level %s or above.",
                 code: int = 255):
        super().__init__(message % params)
        self.code = code
        self.params = params


class TribeEntryNotAllowed(FruitCraftException):
    """Raised when a player cannot enter a tribe."""

    def __init__(self, params: tuple = (), message: str = "You can't enter this tribe. Try another one.",
                 code: int = 256):
        super().__init__(message % params)
        self.code = code
        self.params = params


class LevelRequirement(FruitCraftException):
    """Raised when a level requirement is not met."""

    def __init__(self, params: tuple = (), message: str = "You should reach at least level %s !", code: int = 257):
        super().__init__(message % params)
        self.code = code
        self.params = params


class PrizeAlreadyReceived(FruitCraftException):
    """Raised when a prize has already been received."""

    def __init__(self, params: tuple = (), message: str = "You have got enough prize! Wait a little", code: int = 258):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidMobileNumber(FruitCraftException):
    """Raised when an invalid mobile number is entered."""

    def __init__(self, params: tuple = (), message: str = "You should enter a valid mobile number!", code: int = 259):
        super().__init__(message % params)
        self.code = code
        self.params = params


class InvalidVerificationCode(FruitCraftException):
    """Raised when an invalid verification code is entered."""

    def __init__(self, params: tuple = (), message: str = "Not a valid verification code! Try again", code: int = 260):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotSubscribed(FruitCraftException):
    """Raised when a user is not subscribed."""

    def __init__(self, params: tuple = (), message: str = "You are not subscribed! First subscribe then try again",
                 code: int = 261):
        super().__init__(message % params)
        self.code = code
        self.params = params


class NotCharged(FruitCraftException):
    """Raised when a user is not charged."""

    def __init__(self, params: tuple = (), message: str = "You are not charged! First get charged then try again",
                 code: int = 262):
        super().__init__(message % params)
        self.code = code
        self.params = params


class LevelRequirementAgain(FruitCraftException):
    """Raised when a level requirement is not met again."""

    def __init__(self, params: tuple = (), message: str = "You should reach at least level %s !", code: int = 263):
        super().__init__(message % params)
        self.code = code
        self.params = params


class MaxTribeBroadcastReached(FruitCraftException):
    """Raised when the maximum tribe broadcast limit is reached."""

    def __init__(self, params: tuple = (), message: str = "You reached max tribe broadcast! Wait a while and try again",
                 code: int = 264):
        super().__init__(message % params)
        self.code = code
        self.params = params


class BundlePurchaseError(FruitCraftException):
    """Raised when there is an error in purchasing a bundle."""

    def __init__(self, params: tuple = (),
                 message: str = "Error occurred in purchasing bundle. Please contact customer care.",
                 code: int = 265):
        super().__init__(message % params)
        self.code = code
        self.params = params

class TooManyRequests(Exception):
    """Raised when too many requests are made (HTTP 429)."""

    def __init__(self, params: tuple = (),
                 message: str = "You have sent too many requests in a given amount of time.",
                 code: int = 429):
        super().__init__(message % params)
        self.code = code
        self.params = params
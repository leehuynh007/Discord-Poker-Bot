from enum import Enum
from functools import total_ordering
from itertools import combinations
from typing import List, Tuple
import random

SUITS = ('♠', '♥', '♦', '♣')
RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')

# An enumeration for ranking poker hands
@total_ordering
class HandRanking(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_KIND = 8
    STRAIGHT_FLUSH = 9
    # Note that royal flushes aren't here, because they're just a special case
    # of a straight flush

    def __lt__(self, other):
        return self.value < other.value

# A simple class representing a card
@total_ordering
class Card:
    def __init__(self, suit: str, rank: str) -> None:
        self.suit = suit
        self.rank = rank

    # When comparing two cards, suit doesn't matter, just who has the higher rank
    def __lt__(self, other):
        return RANKS.index(self.rank) < RANKS.index(other.rank)

    def __eq__(self, other):
        return self.rank == other.rank

    def __str__(self) -> str:
        return self.suit + self.rank

# A class for representing a 5-card hand, and allowing for the easy comparison
# of hands
@total_ordering
class Hand:
    def __init__(self, cards: Tuple[Card, Card, Card, Card, Card]) -> None:
        # Sort the cards first thing to make hands easier to compare
        self.cards = sorted(cards)

        # Gets a list of the duplicated cards (pairs, three-of-a-kinds, etc)
        dups = self.get_dups()

        # At this point, we determine the ranking of the hand
        if self.is_flush():
            if self.is_straight():
                self.rank = HandRanking.STRAIGHT_FLUSH
            else:
                self.rank = HandRanking.FLUSH
        elif self.is_straight():
            self.rank = HandRanking.STRAIGHT
        elif dups:
            if len(dups) == 2:
                if len(dups[1]) == 3:
                    self.rank = HandRanking.FULL_HOUSE
                else:
                    self.rank = HandRanking.TWO_PAIR
            else:
                if len(dups[0]) == 4:
                    self.rank = HandRanking.FOUR_OF_KIND
                elif len(dups[0]) == 3:
                    self.rank = HandRanking.THREE_OF_KIND
                else:
                    self.rank = HandRanking.PAIR
            self.rearrange_dups(dups)
        else:
            self.rank = HandRanking.HIGH_CARD

    def __lt__(self, other):
        if self.rank < other.rank:
            return True
        if self.rank > other.rank:
            return False
        for self_card, other_card in zip(self.cards[::-1], other.cards[::-1]):
            if self_card < other_card:
                return True
            elif self_card > other_card:
                return False
        return False

    def __eq__(self, other):
        if self.rank != other.rank:
            return False
        for self_card, other_card in zip(self.cards, other.cards):
            if self_card != other_card:
                return False
        return True

    # Rearrange the duplicated cards in the hand so that comparing two hands
    # with the same ranking is easier
    # This moves duplicated cards to the end of the hand
    def rearrange_dups(self, dups: List[List[Card]]) -> None:
        flat_dups = [card for cards in dups for card in cards]
        for dup in flat_dups:
            self.cards.pop(self.cards.index(dup))
        self.cards += flat_dups

    # Returns whether the hand is a straight
    def is_straight(self) -> bool:
        ranks = [RANKS.index(card.rank) for card in self.cards]
        # Check to see if each card is exactly one better than the previous card
        for i in range(1, 5):
            if ranks[i - 1] != ranks[i] - 1:
                break
        else:
            # If we've reached this point, each card was exactly one rank
            # higher than the previous card.
            return True
        # Check for the special case of an ace-low straight
        if ranks == [0, 1, 2, 3, 12]:
            self.cards = [self.cards[-1]] + self.cards[:-1]
            return True
        return False

    # Returns whether a hand is a flush, meaning all the cards are the same suit
    def is_flush(self) -> bool:
        suit = self.cards[0].suit
        for card in self.cards[1:]:
            if card.suit != suit:
                return False
        return True

    # Returns a list of the pairs, three-of-a-kinds and four-of-a-kinds in the hand
    def get_dups(self) -> List[List[Card]]:
        dups: List[List[Card]] = []
        cur_dup: List[Card] = [self.cards[0]]
        for card in self.cards[1:]:
            if cur_dup[0] != card:
                if len(cur_dup) > 1:
                    dups.append(cur_dup)
                cur_dup = [card]
            else:
                cur_dup.append(card)
        if len(cur_dup) > 1:
            dups.append(cur_dup)
        # For full houses, make it so the three-of-a-kind is always second in
        # the list of duplicates
        if len(dups) == 2 and len(dups[0]) > len(dups[1]):
            dups[0], dups[1] = dups[1], dups[0]
        return dups

# Returns the best possible 5-card hand that can be made from the five
# community cards and a player's two hole cards
def best_possible_hand(public: List[Card], private: Tuple[Card, Card]) -> Hand:
    return max(Hand(hand) for hand in combinations(tuple(public) + private, 5))

# A class for representing a simple, randomized deck that can be drawn from
class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in SUITS
                                       for rank in RANKS]
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()
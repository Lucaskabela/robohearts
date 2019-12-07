import torch
import numpy as np
import torch.nn.functional as F
import torch.utils.tensorboard as tb
from os import path

'''
Utilities to be implemented in all agents
'''

suits = ["c", "d", "s", "h"]
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

# List of all valid cards
def create_deck():
    deck = list()
    for suit in suits:
        for rank in ranks:
            deck.append(f'{rank}{suit}')
    return deck

def create_points():
    pts = list()
    for rank in ranks:
        suit = 'h'
        pts.append(f'{rank}{suit}')
    pts.append('Qs')
    return pts

# Reference to get index for each card
def deck_reference():
    deck = create_deck()
    return {card : i for i, card in enumerate(deck)}

# Reference to get index for each point bearing card
def pts_reference():
    pts = create_points()
    return {card : i for i, card in enumerate(pts)}

# Return the number of features associated with each feature group
def feature_length(feature_list):
    count = 0
    if 'in_hand' in feature_list:
        count += 52
    if 'in_play' in feature_list:
        count += 52
    if 'played_cards' in feature_list:
        count += 52
    if 'won_cards' in feature_list:
        count += 4 * 14
    if 'scores' in feature_list:
        count += 4
    return count

# Format cards from Hearts.Card format to pretty format
def pretty_card(card):
    rank = card[0].upper() if card[0] != 'T' else '10'
    suit = card[1]
    suit_lookup = {'c':'♣', 'd':'♦', 's':'♠', 'h':'♥'}
    return f'[{rank}{suit_lookup[suit]}]'

# Return a list of all valid moves in Hearts.Card format
def filter_valid_moves(observation):
    data = observation['data']
    hand = data['hand']
    trick_num = data['trickNum']
    trick_suit = data['trickSuit']
    no_suit = trick_suit == 'Unset'
    hearts_broken = data['IsHeartsBroken']

    suit_in_hand = True
    if not no_suit:
        suit_in_hand = False
        for card in hand:
            if trick_suit in card:
                suit_in_hand = True
                break
    
    valid_cards = []
    # First move, only 2c
    if trick_num == 1 and no_suit:
        if '2c' in hand:
            valid_cards.append('2c')
    # Starting trick, hearts broken, all cards valid
    elif hearts_broken and no_suit:
        valid_cards = hand
    # Starting trick, hearts not broken, all non-heart cards valid
    elif no_suit:
        for card in hand:
            if 'h' not in card:
                valid_cards.append(card)
        # Nothing but cards in hand
        if not valid_cards:
            valid_cards = hand
    # Not starting trick, valid suit in hand, only cards of suit valid
    elif suit_in_hand:
        for card in hand:
            if trick_suit in card:
                valid_cards.append(card)
    # Not starting trick, valid suit not in hand, all cards valid
    else:
        valid_cards = hand
        # Can't play queen of spades or hearts in first trick
        if trick_num == 1 and len(valid_cards) > 1:
            valid_cards = [card for card in valid_cards if card != 'Qs' and 'h' not in card]
    return valid_cards

# Handle specific observations by presenting human friendly prompts
def handle_event(observation):
    event = observation['event_name']
    if event == 'PassCards':
        hand = observation['data']['hand']
        phand = [pretty_card(card) for card in hand]
        retstring = f"\n{observation['data']['playerName']}'s Hand\n{' '.join(phand)}\n"
        return retstring
    elif event == 'PlayTrick':
        hand = observation['data']['hand']
        phand = [pretty_card(card) for card in hand]
        filtered_hand = filter_valid_moves(observation)
        filtered_phand = [pretty_card(card) for card in filtered_hand]
        retstring = f"\n{observation['data']['playerName']}'s Hand\n{' '.join(phand)}\n"
        retstring += f"\nValid Moves\n{' '.join(filtered_phand)}\n"
        return retstring
    else:
        return observation

# --------------FUNCTION APPROX-------------------

class MLPClassifier(torch.nn.Module):
    def __init__(self, input_features, output_features=1, layers=None, log=False, log_dir='./log'):
        super().__init__()
        if not layers:
            layers = [input_features * 2, input_features * 4]

        L = []
        c = input_features
        for l in layers:
            L.append(torch.nn.Linear(c, l))
            L.append(torch.nn.ReLU())
            c = l
        L.append(torch.nn.Linear(c, output_features))

        self.network = torch.nn.Sequential(*L)

        self.global_step = 0

        self.log = log
        if self.log:
            self.logger = tb.SummaryWriter(path.join(log_dir, 'train'), flush_secs=1)


    def forward(self, x):
        return self.network(x)

def update(nn, optimizer, device, G, features):
    nn.train()
    val = nn(features)
    ret = torch.tensor([G]).to(device).float()
    optimizer.zero_grad()
    loss = F.mse_loss(val, ret)
    loss.backward()
    optimizer.step()

    if nn.log and nn.global_step % 1000 == 0:
        nn.logger.add_scalar('loss', loss, nn.global_step)
    nn.global_step += 1


model_factory = {
    'mlp': MLPClassifier,
}


def save_model(model, path=None):
    from torch import save
    from os import path
    for n, m in model_factory.items():
        if isinstance(model, m):
            if path:
                return save(model.state_dict(), path.join(path.dirname(path.abspath(__file__)), '%s.th' % path))
            else:
                return save(model.state_dict(), path.join(path.dirname(path.abspath(__file__)), '%s.th' % n))
    raise ValueError("model type '%s' not supported!" % str(type(model)))


def load_model(model, feature_list):
    from torch import load
    from os import path
    r = model_factory['mlp'](input_features=feature_length(feature_list))
    if model is not '':
        print("loaded from " + str(path.join(path.dirname(path.abspath(__file__)), '%s.th' % model)))
        r.load_state_dict(load(path.join(path.dirname(path.abspath(__file__)), '%s.th' % model), map_location='cpu'))
    return r


#-------------- FEATURE CALCULATIONS --------------
def cards_to_bin_features(cards):
    deck = deck_reference()
    feature_vec = np.zeros(52)
    for card in cards:
        feature_vec[deck[card]] = 1
    return feature_vec 

def in_hand_features(observation):
    return cards_to_bin_features(observation['data']['hand'])

def in_play_features(observation):
    in_play_cards = [entry['card'] for entry in observation['data']['currentTrick']]
    return cards_to_bin_features(in_play_cards)

def played_cards_features(played_cards):
    return cards_to_bin_features(played_cards)

def won_cards_features(won_cards):
    point_cards = pts_reference()
    feature_vec = np.zeros((4, 14))
    for player, won_card in enumerate(won_cards):
        for card in won_card:
            if card in point_cards:
                feature_vec[player][point_cards[card]] = 1
    return feature_vec.flatten()

def scores_features(scores):
    return np.array(scores)

'''
 Need data for feature construction - played cards and won cards can be built from TrickEnd event
 in the primary program driver (note, played_cards could be a list, won_cards could be list of lists
 or a dictionary (lists of lists/2d array seems easier).  Probably cleanest sol is both are np
 arrays we update at the end of tricks in the MC agent (ie MC keeps the state).  Scores just stored
 in a list easily. 
'''
def get_features(observation, feature_list=['in_hand'], played_cards=None, won_cards=None, scores=None):
    features = np.array([])

    if 'in_hand' in feature_list:
        features = np.concatenate([features, in_hand_features(observation)])
    if 'in_play' in feature_list:
        features = np.concatenate([features, in_play_features(observation)])
    if 'played_cards' in feature_list:
        features = np.concatenate([features, played_cards_features(played_cards)])
    if 'won_cards' in feature_list:
        features = np.concatenate([features, won_cards_features(won_cards)])
    if 'scores' in feature_list:
        features = np.concatenate([features, scores_features(scores)])
    return features
from mk2lib import MachiKoroGame

# Initialize game with player ID 1 as owner.
game = MachiKoroGame(1)

# Player with ID 2 joins lobby.
game.join(2)

# Owner (1) starts game with landmark promo pack and random player order.
game.start(1, use_promo=True, randomize_players=True)

# Try to build a Convenience Store as current player.
game.build_card("convenience_store", None)

while not game.events.empty():
    print(game.events.get())

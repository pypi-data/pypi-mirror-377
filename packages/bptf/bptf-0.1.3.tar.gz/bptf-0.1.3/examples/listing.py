from backpack_tf import BackpackTF

bptf = BackpackTF(
    token="token",
    steam_id="76561198253325712",
    user_agent="superbot5000 user agent",
)

# will add the lightning icon and indicate that the user is a bot
bptf.register_user_agent()

listing = bptf.create_listing(
    "5021;6", "buy", {"metal": 62.11}, "buying keys for listed price :)"
)

print(listing)

asset_id = 11543535227
listing = bptf.create_listing(
    "30745;6",
    "sell",
    {"keys": 1, "metal": 2.11},
    "selling my Siberian Sweater as i dont want it anymore",
    asset_id,
)

print(listing)

bptf.delete_listing_by_asset_id(asset_id)
bptf.delete_listing_by_sku("5021;6")
# or
bptf.delete_all_listings()

from backpack_tf import BackpackTFWebsocket


def my_function(data: list[dict]):
    print("got listings")

    for listing in data:
        print("listing", listing)

    # your logic here


socket = BackpackTFWebsocket(my_function, as_solo_entries=False)
# if as_solo_entries is True, you'll get a single dict instead of a list of dicts

socket.listen()

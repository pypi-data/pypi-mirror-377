from src.backpack_tf import get_item_hash


def test_item_hash() -> None:
    assert (
        get_item_hash("Mann Co. Supply Crate Key") == "d9f847ff5dfcf78576a9fca04cbf6c07"
    )
    assert get_item_hash("Team Captain") == "a893c93bf986b65690e9e8b00bfc28e1"
    assert get_item_hash("Ellis' Cap") == "9e89a4a85aae68266ec992c22b0d52e2"

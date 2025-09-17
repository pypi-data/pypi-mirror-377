from src.backpack_tf import Currencies


def test_currencies() -> None:
    assert Currencies().__dict__ == {"keys": 0, "metal": 0.0}
    assert Currencies(1, 1.5).__dict__ == {"keys": 1, "metal": 1.5}
    assert Currencies(**{"metal": 10.55}).__dict__ == {"keys": 0, "metal": 10.55}

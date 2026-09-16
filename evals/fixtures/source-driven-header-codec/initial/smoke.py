"""Focused consumer smoke for HeaderCodec-backed cache keys."""

from service import cache_key


def main() -> None:
    observed = [
        cache_key("  North  Star  "),
        cache_key("A_B / C"),
        cache_key("ＦＯＯ Bar"),
    ]
    expected = ["north-star", "a-b-c", "foo-bar"]
    if observed != expected:
        raise AssertionError(f"expected {expected!r}, observed {observed!r}")
    print("header codec smoke: ok")


if __name__ == "__main__":
    main()

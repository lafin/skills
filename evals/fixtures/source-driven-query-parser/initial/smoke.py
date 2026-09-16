"""Focused consumer smoke for repeated query-filter behavior."""

from filters import values_for


def main() -> None:
    observed = values_for("tag=red&tag=&other=x&tag=blue+sky", "tag")
    expected = ["red", "", "blue sky"]
    if observed != expected:
        raise AssertionError(f"expected {expected!r}, observed {observed!r}")
    flags = values_for("flag&other=y&flag=on", "flag")
    if flags != ["", "on"]:
        raise AssertionError(f"expected blank and on flags, observed {flags!r}")
    print("query parser smoke: ok")


if __name__ == "__main__":
    main()

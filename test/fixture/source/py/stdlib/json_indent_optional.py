from pytra.std import json


if __name__ == "__main__":
    arr = json.loads_arr("[2, 3]")
    if arr is not None:
        indent_value: int | None = 2
        print(json.dumps(arr.raw, ensure_ascii=True, indent=indent_value, separators=None))

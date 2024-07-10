import json
import os
import re


def load_template_dict(item: str = "text_template/prompt/prompt_set.json"):
    try:
        with open(item, "r", encoding="utf-8") as f:
            s = f.read()
    except (TypeError, FileNotFoundError):
        s = item
    else:
        pass
    finally:
        try:
            json_dict = json.loads(s)
        except (TypeError, json.JSONDecodeError) as e:
            return s
        else:
            try:
                return {key: load_template_dict(value) for key, value in json_dict.items()}
            except AttributeError as ae:
                return [load_template_dict(value) for value in json_dict]


if __name__ == "__main__":
    i = load_template_dict("text_template/prompt/prompt_set.json")
    print(type(i))
    print(i)

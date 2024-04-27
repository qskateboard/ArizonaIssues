import json
import re

rules = json.loads(open("PR.bind", "r", encoding="windows-1251").read())


def search_rules(text):
    result = {}
    to_find = text.split(" ", 1)[1].lower()
    for line in rules:
        if to_find in line["text"].lower():
            rls = re.compile("(\d{1,2}\..*)\\n").findall(line["text"])
            for rule in rls:
                if to_find in rule.lower():
                    try:
                        result[line["name"]].append(rule.replace(to_find, "<b>" + to_find + "</b>"))
                    except KeyError:
                        result[line["name"]] = []
                        result[line["name"]].append(rule.replace(to_find, "<b>" + to_find + "</b>"))
    return result


query = "/find ИЗП (Использование Запрещенных Програм"
print(search_rules(query))

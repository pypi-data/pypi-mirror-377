import os
import json
import difflib

KB_FILE = "command_action-kb.json"


def load_kb():
    if not os.path.exists(KB_FILE):
        return []
    with open(KB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_kb(kb_data):
    with open(KB_FILE, "w") as f:
        json.dump(kb_data, f, indent=2)

def add_to_kb(query, plan):
    kb = load_kb()
    kb.append({"query": query, "plan": plan})
    save_kb(kb)

def find_similar_plan(query, threshold=0.6):
    kb = load_kb()
    if not kb:
        return None
    queries = [item["query"] for item in kb]
    match = difflib.get_close_matches(query, queries, n=1, cutoff=threshold)
    if match:
        for item in kb:
            if item["query"] == match[0]:
                return item["plan"]
    return None


def get_multiline_input(prompt="Enter your request (type 'END' to finish):"):
    print(prompt)
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)
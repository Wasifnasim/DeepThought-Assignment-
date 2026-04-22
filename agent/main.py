import json

# Load tree
with open("../tree/decision_tree.json") as f:
    nodes = {node["id"]: node for node in json.load(f)}

current = "start"
state = {}
answers = {}

def add_signal(signal):
    state[signal] = state.get(signal, 0) + 1

def get_value(key):
    return state.get(key, 0)

def get_dominant(axis):
    if axis == "axis1":
        return "internal" if get_value("axis1:internal") >= get_value("axis1:external") else "external"
    if axis == "axis2":
        return "contribution" if get_value("axis2:contribution") >= get_value("axis2:entitlement") else "entitlement"
    if axis == "axis3":
        return "others" if get_value("axis3:others") >= get_value("axis3:self") else "self"

while True:
    node = nodes[current]

    text = node.get("text", "")

    # Replace interpolation
    for key, val in answers.items():
        text = text.replace(f"{{{key}.answer}}", val)

    print("\n" + text)

    if node["type"] == "question":
        for i, opt in enumerate(node["options"], 1):
            print(f"{i}. {opt['text']}")

        choice = int(input("Choose option: ")) - 1
        selected = node["options"][choice]

        answers[node["id"]] = selected["text"]

        if "signal" in selected:
            add_signal(selected["signal"])

        current = node["next"]

    elif node["type"] == "decision":
        moved = False
        for rule in node["rules"]:
            cond = rule.get("condition", "")

            if cond == "default":
                current = rule["next"]
                moved = True
                break

            # Parse condition
            if ">=" in cond:
                left, right = cond.split(">=")
                if get_value(left.strip()) >= get_value(right.strip()):
                    current = rule["next"]
                    moved = True
                    break
            elif ">" in cond:
                left, right = cond.split(">")
                if get_value(left.strip()) > get_value(right.strip()):
                    current = rule["next"]
                    moved = True
                    break

        if not moved:
            print("No condition matched. Check rules.")
            break

    elif node["type"] in ["start", "reflection", "bridge"]:
        input("\nPress Enter to continue...")
        current = node["next"]

    elif node["type"] == "summary":
        text = text.replace("{axis1.dominant}", get_dominant("axis1"))
        text = text.replace("{axis2.dominant}", get_dominant("axis2"))
        text = text.replace("{axis3.dominant}", get_dominant("axis3"))

        print("\n" + text)
        current = node["next"]

    elif node["type"] == "end":
        print("\nSession complete.")
        break
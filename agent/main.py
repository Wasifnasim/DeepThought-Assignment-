import json
import re
import os

def load_tree(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        nodes = json.load(f)
    return {node['id']: node for node in nodes}

def get_dominant(axis, signals):
    axis_signals = {k: v for k, v in signals.items() if k.startswith(f"{axis}:")}
    if not axis_signals:
        return "unknown"
    dominant_key = max(axis_signals, key=axis_signals.get)
    return dominant_key.split(":")[1]

def format_text(text, answers, signals):
    # Replace {node_id.answer}
    def replace_answer(match):
        node_id = match.group(1)
        return answers.get(node_id, f"{{{node_id}.answer}}")
    text = re.sub(r'\{([a-zA-Z0-9_]+)\.answer\}', replace_answer, text)
    
    # Replace {axisX.dominant}
    def replace_dominant(match):
        axis = match.group(1)
        return get_dominant(axis, signals)
    text = re.sub(r'\{([a-zA-Z0-9_]+)\.dominant\}', replace_dominant, text)
    
    return text

def evaluate_condition(condition, signals):
    if condition == "default":
        return True
    parts = condition.split()
    if len(parts) == 3:
        left_key, op, right_key = parts
        left_val = signals.get(left_key, 0)
        right_val = signals.get(right_key, 0)
        if op == ">=": return left_val >= right_val
        if op == ">": return left_val > right_val
        if op == "<=": return left_val <= right_val
        if op == "<": return left_val < right_val
        if op == "==": return left_val == right_val
    return False

def main():
    # Adjust path based on where it's being run from
    filepath = os.path.join(os.path.dirname(__file__), '..', 'tree', 'decision_tree.json')
    tree = load_tree(filepath)
    
    current_node_id = "start"
    signals = {}
    answers = {}
    
    while current_node_id:
        node = tree.get(current_node_id)
        if not node:
            print(f"Error: Node {current_node_id} not found.")
            break
            
        node_type = node.get("type")
        
        if node_type == "start":
            print(format_text(node.get("text", ""), answers, signals))
            print()
            current_node_id = node.get("next")
            
        elif node_type == "question":
            print(format_text(node.get("text", ""), answers, signals))
            options = node.get("options", [])
            for i, opt in enumerate(options):
                print(f"  {i + 1}. {opt['text']}")
            
            while True:
                try:
                    choice_str = input("Select an option: ")
                    choice = int(choice_str) - 1
                    if 0 <= choice < len(options):
                        break
                    print("Invalid choice, please try again.")
                except ValueError:
                    print("Please enter a number.")
                except EOFError:
                    return
            
            selected_option = options[choice]
            answers[current_node_id] = selected_option["text"]
            
            signal = selected_option.get("signal")
            if signal:
                signals[signal] = signals.get(signal, 0) + 1
                
            print()
            current_node_id = node.get("next")
            
        elif node_type in ["bridge", "reflection", "summary"]:
            print(format_text(node.get("text", ""), answers, signals))
            print()
            current_node_id = node.get("next")
            
        elif node_type == "decision":
            rules = node.get("rules", [])
            next_node = None
            for rule in rules:
                if evaluate_condition(rule.get("condition"), signals):
                    next_node = rule.get("next")
                    break
            if next_node:
                current_node_id = next_node
            else:
                print("Error: No valid rule found in decision node.")
                break
                
        elif node_type == "end":
            print(format_text(node.get("text", ""), answers, signals))
            print()
            break
            
        else:
            print(f"Unknown node type: {node_type}")
            break

if __name__ == "__main__":
    main()

import json
import sys
import os

def validate_json(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✅ Success: '{file_path}' is a valid JSON file.")
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error in '{file_path}':")
        print(f"Message: {e.msg}")
        print(f"Line: {e.lineno}, Column: {e.colno}")
        print("-" * 30)
        
        # Show context
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                error_line_idx = e.lineno - 1
                
                # Print a few lines before for context
                start = max(0, error_line_idx - 2)
                end = min(len(lines), error_line_idx + 3)
                
                for i in range(start, end):
                    prefix = ">>> " if i == error_line_idx else "    "
                    line_content = lines[i].rstrip()
                    print(f"{i+1:5} | {prefix}{line_content}")
                    if i == error_line_idx:
                        # Draw a pointer to the column
                        print("      |     " + " " * (e.colno - 1) + "^")
        except Exception as read_err:
            print(f"Could not read file context: {read_err}")

if __name__ == "__main__":
    target_file = "emoji_tags_refined.json"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    validate_json(target_file)

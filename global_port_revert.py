import os

def global_revert_port(root_dir, search_text, replace_text, extensions):
    count = 0
    for root, dirs, files in os.walk(root_dir):
        # Skip virtual environments and git history
        if 'venv' in dirs:
            dirs.remove('venv')
        if '.git' in dirs:
            dirs.remove('.git')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if search_text in content:
                        new_content = content.replace(search_text, replace_text)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Reverted: {file_path}")
                        count += 1
                except Exception as e:
                    print(f"Error in {file_path}: {e}")
    return count

if __name__ == "__main__":
    # Expand the scope to the entire gestao_editais folder to be safe
    root = r"c:\Users\higosantos\Documents\gestao_editais"
    extensions = ['.py', '.bat', '.ps1', '.html', '.txt', '.md', '.env', '.vbs']
    
    print(f"Global Revert: Searching for '5000' and reverting to '5000' in {root}...")
    total = global_revert_port(root, "5000", "5000", extensions)
    print(f"\nFinished! Fixed {total} files.")

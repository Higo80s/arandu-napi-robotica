import os

def check_encoding():
    files_to_check = [
        'app.py',
        'models.py',
        'templates/bolsistas/form.html',
        'templates/bolsistas/index.html',
        'templates/dashboard.html',
        'templates/base.html'
    ]
    
    for fname in files_to_check:
        if os.path.exists(fname):
            try:
                with open(fname, 'rb') as f:
                    start = f.read(4)
                    print(f"{fname}: {start}")
                    if start.startswith(b'\xff\xfe'):
                        print(f"!!! {fname} is UTF-16 LE !!!")
                    elif start.startswith(b'\xfe\xff'):
                        print(f"!!! {fname} is UTF-16 BE !!!")
                    elif start.startswith(b'\xef\xbb\xbf'):
                        print(f"{fname} is UTF-8 BOM")
                    else:
                        print(f"{fname} seems normal (start: {start})")
            except Exception as e:
                print(f"Error checking {fname}: {e}")
        else:
            print(f"{fname} not found.")

if __name__ == "__main__":
    check_encoding()

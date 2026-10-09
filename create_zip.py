import zipfile
import os

def create_zip():
    zip_filename = 'clean-loop.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        root_dir = 'clean-loop'
        for root, dirs, files in os.walk(root_dir):
            # Skip __pycache__ and .git directories
            dirs[:] = [d for d in dirs if not d.startswith('__pycache__') and d != '.git']

            for file in files:
                file_path = os.path.join(root, file)
                # Skip __pycache__ files
                if '__pycache__' not in file_path:
                    arcname = os.path.relpath(file_path, start='.')
                    zipf.write(file_path, arcname)

    print(f"Created {zip_filename}")

if __name__ == "__main__":
    create_zip()
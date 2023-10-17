import argparse
from pathlib import Path
import shutil
import hashlib
from datetime import datetime

WOOL_DIRECTORY = 'wool_data/'

CONFIG_PATH = 'config/xyz.data'

def save(args):
    # Source path
    source_path = Path(CONFIG_PATH)
    if not source_path.exists():
        print(f"Error: Config file at {CONFIG_PATH} does not exist.")
        return

    # Destination path
    dest_path = Path(WOOL_DIRECTORY, args.filename)

    # Check if destination file exists and warn the user
    if dest_path.exists():
        overwrite = input(f"Warning: {dest_path} already exists. Overwrite? (yes/no): ")
        if overwrite.lower() != "yes":
            print("Operation cancelled.")
            return

    # Copy the file
    shutil.copy2(source_path, dest_path)
    print(f"Config saved to {dest_path}.")

def compute_md5(file_path):
    """Compute the MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        # Read the file in chunks
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def config_matches_any_saved_file(config_path):
    """Check if the config matches any file in WOOL_DIRECTORY."""
    if not config_path.exists():
        return False
    config_hash = compute_md5(config_path)
    for wool_file in Path(WOOL_DIRECTORY).iterdir():
        if wool_file.is_file() and compute_md5(wool_file) == config_hash:
            return True
    return False

def load(args):
    # Source path for the file specified to be loaded
    source_path = Path(WOOL_DIRECTORY, args.filename)
    if not source_path.exists():
        print(f"Error: File {args.filename} does not exist in {WOOL_DIRECTORY}.")
        return

    # Destination path
    dest_path = Path(CONFIG_PATH)

    if not config_matches_any_saved_file(dest_path):
        warn = input(f"Warning: The current config file at {CONFIG_PATH} might not have been saved to {WOOL_DIRECTORY}. Continue loading? (yes/no): ")
        if warn.lower() != "yes":
            print("Operation cancelled.")
            return

    # Copy the file
    shutil.copy(source_path, dest_path)
    print(f"{args.filename} loaded to config path.")


def ordinal(number):
    """Return number as an ordinal (e.g., 1st, 2nd, 3rd)."""
    if 10 <= number % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
    return f"{number}{suffix}"

def list_items(args):
    """Implementation for listing items along with their last modified date."""
    print("Listing available recipes...")
    
    for wool_file in Path(WOOL_DIRECTORY).iterdir():
        if wool_file.is_file():
            # Retrieve the last modified timestamp and convert it to the desired format
            modified_timestamp = wool_file.stat().st_mtime
            modified_date = datetime.fromtimestamp(modified_timestamp)
            formatted_date = f"{modified_date.strftime('%B')}, {ordinal(modified_date.day)} {modified_date.year}"
            
            print(f"{wool_file.name} - Last Modified: {formatted_date}")

def main():
    parser = argparse.ArgumentParser(description="Simple CLI using argparse")

    subparsers = parser.add_subparsers()

    # Save subcommand
    save_parser = subparsers.add_parser('save', help='Save recipe')
    save_parser.add_argument('filename', type=str, help='Filename to store recip')
    save_parser.set_defaults(func=save)

    # Load subcommand
    load_parser = subparsers.add_parser('load', help='Load recipe from file')
    load_parser.add_argument('filename', type=str, help='Filename to load recipe from')
    load_parser.set_defaults(func=load)

    # List subcommand
    list_parser = subparsers.add_parser('list', help='List available wool recipes')
    list_parser.set_defaults(func=list_items)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


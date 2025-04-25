import os
import shutil
import sys
import argparse
import logging

# --- Command-line arguments ---
parser = argparse.ArgumentParser(description='Move items to SSD externo com symlinks.')
parser.add_argument('--dry-run', action='store_true', help='Simula operações sem alterar arquivos.')
parser.add_argument('--log-file', type=str, help='Arquivo para gravar logs.')
parser.add_argument('--undo', action='store_true', help='Reverte operações anteriores (experimental).')
args = parser.parse_args()

# Configura logger
if args.log_file:
    logging.basicConfig(filename=args.log_file, level=logging.INFO, format='%(asctime)s %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(message)s')

dry_run = args.dry_run

if args.undo:
    print('Função de undo experimental. Implementação pendente.')
    sys.exit(0)

# --- Configuration ---
# !!! IMPORTANT: Replace "SEU_SSD" with the actual name of your SSD volume !!!
ssd_volume_name = "SSD-EXTERNO"

# --- Items to Move ---

# 1. User Folders (names relative to your home directory ~/)
#    Common examples: "Documents", "Music", "Pictures", "Movies"
#    "Downloads" is handled separately below for backward compatibility, but could be added here.
USER_FOLDERS_TO_MOVE = [
    "Documents",
    "Music",
    "Pictures",
    "Movies",
    # Add other top-level user folders here if needed
]

# 2. Applications (exact .app folder names in /Applications)
APPS_TO_MOVE = [
  
  # Add other large apps here
]

# 3. Cache Subfolders (names relative to ~/Library/Caches)
#    WARNING: Moving caches can sometimes cause issues. Move specific large ones.
#    Examples: "com.apple.dt.Xcode", "pip", "Google"
CACHE_SUBFOLDERS_TO_MOVE = [
    # "com.apple.dt.Xcode", # Example if you have Xcode caches
    # "pip",               # Example pip cache
]

# 4. Application Support Subfolders (names relative to ~/Library/Application Support)
#    WARNING: Moving these requires care. Ensure the app handles symlinks well.
#    Examples: "Steam", "Docker", "MobileSync" (iOS Backups)
APP_SUPPORT_SUBFOLDERS_TO_MOVE = [
    # "Steam",             # Example Steam data
    # "MobileSync",        # Example iOS backups (can be very large)
]

# 5. Other Large Files/Folders (provide *absolute* paths)
#    Use this for VMs, large project folders, etc.
OTHER_PATHS_TO_MOVE = [
    # "/Users/your_username/Virtual Machines", # Example VM folder
    # "/Users/your_username/LargeProjects/MyVideoProject", # Example project
]
# -------------------

home_dir = os.path.expanduser("~")
ssd_base_path = os.path.join("/Volumes", ssd_volume_name)

# --- Base Destination Paths on SSD ---
ssd_user_folders_base = ssd_base_path
ssd_apps_dest_base = os.path.join(ssd_base_path, "Applications")
ssd_caches_dest_base = os.path.join(ssd_base_path, "Library", "Caches")
ssd_app_support_dest_base = os.path.join(ssd_base_path, "Library", "Application Support")
ssd_other_dest_base = os.path.join(ssd_base_path, "OtherMovedItems")

# --- Source Paths ---
# Downloads (kept separate for clarity from original script)
downloads_source_path = os.path.join(home_dir, "Downloads")
downloads_dest_path = os.path.join(ssd_user_folders_base, "Downloads") # Goes to root of SSD now

# Applications source base
apps_source_base = "/Applications"

# Library source bases
library_caches_source_base = os.path.join(home_dir, "Library", "Caches")
library_app_support_source_base = os.path.join(home_dir, "Library", "Application Support")


def ensure_dir_exists(path):
    """Creates a directory if it doesn't exist."""
    if not os.path.exists(path):
        try:
            print(f"Creating directory: {path}")
            os.makedirs(path, exist_ok=True) # exist_ok=True is safer
            print("Directory created successfully.")
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            sys.exit(1)
    elif not os.path.isdir(path):
         print(f"Error: {path} exists but is not a directory.")
         sys.exit(1)


def transfer_and_link_item(item_name, source_path, destination_path, destination_base_dir):
    """Moves an item (file or directory) and creates a symbolic link."""
    logging.info(f"--- Processing: {item_name} ---")
    logging.info(f"Source: {source_path}")
    logging.info(f"Destination: {destination_path}")

    # 0. Ensure destination base directory exists
    ensure_dir_exists(destination_base_dir)

    # 1. Skip if dry-run
    if dry_run:
        logging.info(f"DRY-RUN: would move {item_name} from {source_path} to {destination_path} and create symlink.")
        return 'skipped'

    # 1. Check if source exists and is not a symlink
    if os.path.islink(source_path):
        # Verify if the existing link points to the *correct* destination
        try:
            link_target = os.readlink(source_path)
            if link_target == destination_path:
                print(f"Skipping: {source_path} is already a symbolic link pointing to the correct destination.")
            else:
                print(f"WARNING: {source_path} is a symbolic link, but points to '{link_target}' instead of the expected '{destination_path}'. Skipping.")
        except OSError as e:
            print(f"WARNING: Could not read existing symlink at {source_path}: {e}. Skipping.")
        return "skipped" # Indicate skipped
    if not os.path.exists(source_path):
        print(f"Skipping: Source {source_path} not found.")
        return "skipped" # Indicate skipped
    print(f"Source {item_name} found.")

    # 2. Check if destination already exists (and is not the target of an existing link)
    if os.path.exists(destination_path):
        print(f"Skipping: Destination {destination_path} already exists.")
        # We already checked for the link case above
        return "skipped" # Indicate skipped

    # 3. Move the item
    try:
        logging.info(f"Moving {source_path} to {destination_path}...")
        shutil.move(source_path, destination_path)
        logging.info("Move successful.")
    except Exception as e:
        logging.error(f"Error moving {item_name}: {e}")
        return 'failed'

    # 4. Create the symbolic link
    try:
        logging.info(f"Creating symbolic link from {destination_path} to {source_path}...")
        os.symlink(destination_path, source_path, target_is_directory=os.path.isdir(destination_path))
        logging.info("Symbolic link created successfully.")
        return 'success'
    except Exception as e:
        logging.error(f"Error creating symbolic link for {item_name}: {e}")
        print("Attempting to restore original item...")
        try:
            # Ensure the source path doesn't exist before restoring
            if os.path.exists(source_path):
                 print(f"WARNING: Cannot restore because {source_path} still exists (possibly a broken link). Manual cleanup needed.")
                 print(f"Your {item_name} is at: {destination_path}")
            else:
                shutil.move(destination_path, source_path)
                print(f"Original {item_name} restored at {source_path}.")
        except Exception as restore_e:
            print(f"CRITICAL ERROR: Could not restore {item_name}: {restore_e}")
            print(f"Your {item_name} is now at: {destination_path}")
            print(f"The original path {source_path} might be empty or contain an incomplete link.")
        return 'failed'


def run_transfers():
    """
    Coordinates the transfer of files/folders to an external SSD and creates symbolic links.
    
    This function performs the following operations:
    1. Verifies that the target SSD is mounted and accessible
    2. Processes and transfers the following items to the SSD:
       - Downloads folder
       - User folders (defined in USER_FOLDERS_TO_MOVE)
       - Applications (defined in APPS_TO_MOVE)
       - Cache subfolders (defined in CACHE_SUBFOLDERS_TO_MOVE)
       - Application Support subfolders (defined in APP_SUPPORT_SUBFOLDERS_TO_MOVE)
       - Other specified paths (defined in OTHER_PATHS_TO_MOVE)
    3. Creates symbolic links at the original locations pointing to the new locations on the SSD
    4. Reports a summary of operations (successful, skipped, and failed transfers)
    
    Returns:
        None
        
    Raises:
        SystemExit: If the target SSD is not mounted or accessible
    
    Note:
        This function relies on several global variables that must be defined before calling:
        - ssd_base_path: Path to the mounted SSD
        - ssd_volume_name: Name of the SSD volume
        - Various source and destination paths for different categories of items
        - Lists of items to be transferred in each category
    """
    print(f"Target SSD: {ssd_base_path}")
    results = {"success": 0, "skipped": 0, "failed": 0}

    # 1. Check if SSD is mounted
    if not os.path.exists(ssd_base_path):
        print(f"Error: SSD volume '{ssd_volume_name}' not found at {ssd_base_path}.")
        print("Please ensure the SSD is connected and mounted correctly.")
        sys.exit(1)
    print(f"SSD '{ssd_volume_name}' found.")

    # --- Transfer Downloads (Original Logic) ---
    print("\\n=== Processing Downloads Folder ===")
    # Ensure the base destination exists (root of SSD in this case)
    ensure_dir_exists(ssd_user_folders_base)
    result = transfer_and_link_item("Downloads", downloads_source_path, downloads_dest_path, ssd_user_folders_base)
    results[result] += 1


    # --- Transfer User Folders ---
    print("\\n=== Processing User Folders ===")
    ensure_dir_exists(ssd_user_folders_base) # Base is root of SSD
    for folder_name in USER_FOLDERS_TO_MOVE:
        source = os.path.join(home_dir, folder_name)
        dest = os.path.join(ssd_user_folders_base, folder_name)
        result = transfer_and_link_item(folder_name, source, dest, ssd_user_folders_base)
        results[result] += 1

    # --- Transfer Applications ---
    print("\\n=== Processing Applications ===")
    ensure_dir_exists(ssd_apps_dest_base) # Ensures /Volumes/SSD/Applications exists
    for app_name in APPS_TO_MOVE:
        source = os.path.join(apps_source_base, app_name)
        dest = os.path.join(ssd_apps_dest_base, app_name)
        result = transfer_and_link_item(app_name, source, dest, ssd_apps_dest_base)
        results[result] += 1

    # --- Transfer Cache Subfolders ---
    print("\\n=== Processing Cache Subfolders ===")
    ensure_dir_exists(ssd_caches_dest_base) # Ensures /Volumes/SSD/Library/Caches exists
    for subfolder_name in CACHE_SUBFOLDERS_TO_MOVE:
        source = os.path.join(library_caches_source_base, subfolder_name)
        dest = os.path.join(ssd_caches_dest_base, subfolder_name)
        result = transfer_and_link_item(subfolder_name, source, dest, ssd_caches_dest_base)
        results[result] += 1

    # --- Transfer Application Support Subfolders ---
    print("\\n=== Processing Application Support Subfolders ===")
    ensure_dir_exists(ssd_app_support_dest_base) # Ensures /Volumes/SSD/Library/Application Support exists
    for subfolder_name in APP_SUPPORT_SUBFOLDERS_TO_MOVE:
        source = os.path.join(library_app_support_source_base, subfolder_name)
        dest = os.path.join(ssd_app_support_dest_base, subfolder_name)
        result = transfer_and_link_item(subfolder_name, source, dest, ssd_app_support_dest_base)
        results[result] += 1

    # --- Transfer Other Paths ---
    print("\\n=== Processing Other Specified Paths ===")
    ensure_dir_exists(ssd_other_dest_base) # Ensures /Volumes/SSD/OtherMovedItems exists
    for source_path in OTHER_PATHS_TO_MOVE:
        if not os.path.isabs(source_path):
            print(f"Skipping invalid path in OTHER_PATHS_TO_MOVE: '{source_path}'. Must be absolute.")
            results["skipped"] += 1
            continue
        item_name = os.path.basename(source_path)
        dest_path = os.path.join(ssd_other_dest_base, item_name)
        result = transfer_and_link_item(item_name, source_path, dest_path, ssd_other_dest_base)
        results[result] += 1


    print("\\n--- Summary ---")
    total_processed = sum(results.values())
    print(f"Total items considered: {total_processed}") # Adjust based on actual items attempted
    print(f"  Successfully moved & linked: {results['success']}")
    print(f"  Skipped (e.g., already linked, source missing, dest exists): {results['skipped']}")
    print(f"  Failed: {results['failed']}")
    print("\\nProcess completed.")


if __name__ == "__main__":
    # Add a confirmation step
    print("This script will attempt to move items to your SSD and create symbolic links.")
    print(f"Target SSD Volume: '{ssd_volume_name}' (mounted at '{ssd_base_path}')")

    print("\\nPlanned Operations:")
    print(f"1. Downloads Folder: '{downloads_source_path}' -> '{downloads_dest_path}'")

    if USER_FOLDERS_TO_MOVE:
        print("2. User Folders:")
        for folder in USER_FOLDERS_TO_MOVE:
            print(f"   - ~/{folder} -> {os.path.join(ssd_user_folders_base, folder)}")

    if APPS_TO_MOVE:
        print("3. Applications:")
        for app in APPS_TO_MOVE:
            print(f"   - {os.path.join(apps_source_base, app)} -> {os.path.join(ssd_apps_dest_base, app)}")

    if CACHE_SUBFOLDERS_TO_MOVE:
        print("4. Cache Subfolders (from ~/Library/Caches):")
        print("   WARNING: Moving caches can sometimes cause application issues.")
        for subfolder in CACHE_SUBFOLDERS_TO_MOVE:
            print(f"   - {subfolder} -> {os.path.join(ssd_caches_dest_base, subfolder)}")

    if APP_SUPPORT_SUBFOLDERS_TO_MOVE:
        print("5. Application Support Subfolders (from ~/Library/Application Support):")
        print("   WARNING: Ensure applications function correctly after moving these.")
        for subfolder in APP_SUPPORT_SUBFOLDERS_TO_MOVE:
            print(f"   - {subfolder} -> {os.path.join(ssd_app_support_dest_base, subfolder)}")

    if OTHER_PATHS_TO_MOVE:
        print("6. Other Specified Paths:")
        for path in OTHER_PATHS_TO_MOVE:
             print(f"   - {path} -> {os.path.join(ssd_other_dest_base, os.path.basename(path))}")


    print("\\nEnsure:")
    print(f" - Your SSD name ('{ssd_volume_name}') is correct and the volume is mounted.")
    print(f" - You have necessary permissions (you might need to run with 'sudo python3 {__file__}' for /Applications).")
    print(" - Close any applications listed or those using the folders/caches being moved.")
    print(" - Backup important data before proceeding!")

    confirm = input("\\nProceed with moving items and creating links? (yes/no): ").lower().strip()

    if confirm == 'yes':
        print("\\nStarting transfer process...")
        run_transfers()
    else:
        print("Operation cancelled by user.")

import os
import datetime
import subprocess
import glob
import sys # Import sys for exiting on error

def remove_old_files_from_git(target_dir, days_threshold=5):
    """
    Removes files from the Git index in target_dir if their filename
    starts with a date pattern (YYYYMMDD-) older than days_threshold.
    """
    try:
        current_date = datetime.datetime.now()
        print(f"Current date: {current_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # Calculate the cutoff date (files older than this will be removed)
        cutoff_date = current_date - datetime.timedelta(days=days_threshold)
        print(f"Removing files strictly older than: {cutoff_date.strftime('%Y-%m-%d')}")

        # --- Revised File Finding Logic ---
        # Use glob to find all potentially matching files first
        # '????????-*' matches files starting with 8 digits followed by a hyphen
        pattern = os.path.join(target_dir, "????????-*")
        potential_files = glob.glob(pattern)
        print(f"Found {len(potential_files)} potential files matching pattern '{pattern}'")

        files_to_remove = []
        for file_path in potential_files:
            filename = os.path.basename(file_path)
            date_str = filename[:8] # Extract first 8 characters for date

            try:
                # Attempt to parse the date part of the filename
                file_date = datetime.datetime.strptime(date_str, "%Y%m%d")

                # Check if the file's date is older than the cutoff date
                if file_date < cutoff_date:
                    print(f"  Marking for removal (date {file_date.strftime('%Y-%m-%d')} < {cutoff_date.strftime('%Y-%m-%d')}): {filename}")
                    files_to_remove.append(file_path)
                # else: # Optional: print files that are within the threshold
                #     print(f"  Keeping (date {file_date.strftime('%Y-%m-%d')} >= {cutoff_date.strftime('%Y-%m-%d')}): {filename}")

            except ValueError:
                # Ignore files where the first 8 chars aren't a valid YYYYMMDD date
                print(f"  Skipping (invalid date prefix '{date_str}'): {filename}")
                continue
        # --- End Revised Logic ---

        if not files_to_remove:
            print("No files found older than the threshold.")
            return # Exit the function gracefully

        print(f"\nAttempting to remove {len(files_to_remove)} files from Git index...")
        files_removed_count = 0
        for file_path in files_to_remove:
            # Use git rm --cached to remove from index but keep local file (important for Actions runner)
            result = subprocess.run(
                ["git", "rm", "--ignore-unmatch", "--cached", file_path],
                capture_output=True, text=True, check=False # Allow checking result manually
            )
            if result.returncode == 0:
                print(f"  Removed from index: {os.path.basename(file_path)}")
                files_removed_count += 1
            else:
                # Log error but continue trying other files
                print(f"  Warning: Failed to 'git rm --cached {os.path.basename(file_path)}'")
                print(f"    Stderr: {result.stderr.strip()}")
                print(f"    Stdout: {result.stdout.strip()}")


        # Only commit and push if files were actually removed from the index
        if files_removed_count > 0:
            print(f"\nSuccessfully removed {files_removed_count} files from index.")
            print("Committing changes...")
            commit_message = f"Automated: Remove {files_removed_count} story files older than {cutoff_date.strftime('%Y-%m-%d')}"
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True, text=True, check=False
            )

            if commit_result.returncode == 0:
                print("Commit successful.")
                print("Pushing changes...")
                # Assuming push to default remote 'origin' and current branch
                push_result = subprocess.run(
                    ["git", "push"],
                    capture_output=True, text=True, check=False
                )

                if push_result.returncode == 0:
                    print("Successfully pushed changes to remote.")
                else:
                    print(f"ERROR: Push failed!")
                    print(f"Stderr: {push_result.stderr.strip()}")
                    print(f"Stdout: {push_result.stdout.strip()}")
                    sys.exit(1) # Exit with error code if push fails
            else:
                # Check if commit failed because nothing was staged (e.g., git rm failed silently)
                if "nothing to commit" in commit_result.stdout or "nothing to commit" in commit_result.stderr:
                     print("Commit skipped: No changes were staged for commit.")
                else:
                    print(f"ERROR: Commit failed!")
                    print(f"Stderr: {commit_result.stderr.strip()}")
                    print(f"Stdout: {commit_result.stdout.strip()}")
                    sys.exit(1) # Exit with error code if commit fails unexpectedly
        else:
            print("\nNo files were successfully removed from the index, skipping commit and push.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1) # Exit with error code on unexpected exception

    print("\nCleanup script finished.")


if __name__ == "__main__":
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assume the script is in repo_root/scripts, so repo_root is one level up
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))

    # Construct the path to the stories folder relative to the repo root
    stories_folder = os.path.join(repo_root, "docs", "stories") # Use os.path.join for cross-platform compatibility

    if not os.path.isdir(stories_folder):
        print(f"ERROR: Target directory not found: {stories_folder}")
        sys.exit(1)

    print(f"Target directory: {stories_folder}")
    remove_old_files_from_git(stories_folder, days_threshold=5)

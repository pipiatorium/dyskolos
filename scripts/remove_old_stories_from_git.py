import os
import datetime
import subprocess
import glob

def remove_old_files_from_remote(local_path, days_threshold=5):
    current_date = datetime.datetime.now()
    print(f"Current date: {current_date}")
    
    # Calculate cutoff date
    cutoff_date = current_date - datetime.timedelta(days=days_threshold)
    cutoff_str = cutoff_date.strftime("%Y%m%d")
    print(f"Removing files older than: {cutoff_str}")
    
    # Track if any files were removed
    files_removed = False
    
    # Remove files by date pattern
    for i in range(1, days_threshold + 1):
        date_to_remove = cutoff_date - datetime.timedelta(days=i)
        date_str = date_to_remove.strftime("%Y%m%d")
        
        # Use glob to find matching files first (Python handles wildcards)
        pattern = f"{local_path}/{date_str}-*"
        matching_files = glob.glob(pattern)
        
        if matching_files:
            print(f"Found {len(matching_files)} files with pattern {date_str}-*")
            
            # Remove each file individually from Git index
            for file_path in matching_files:
                result = subprocess.run(
                    ["git", "rm", "--cached", file_path],
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    print(f"Removed from index: {file_path}")
                    files_removed = True
                else:
                    print(f"Failed to remove: {file_path}")
                    print(f"Error: {result.stderr}")
    
    # Only commit and push if files were actually removed
    if files_removed:
        # Check if there are staged changes before committing
        status_result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True, text=True
        )
        
        if status_result.returncode != 0:  # Changes exist
            print("Committing changes...")
            commit_result = subprocess.run(
                ["git", "commit", "-m", f"Remove files older than {cutoff_str}"],
                capture_output=True, text=True
            )
            
            if commit_result.returncode == 0:
                print("Pushing changes...")
                push_result = subprocess.run(
                    ["git", "push"],
                    capture_output=True, text=True
                )
                
                if push_result.returncode == 0:
                    print("Successfully pushed changes")
                else:
                    print(f"Push failed: {push_result.stderr}")
            else:
                print(f"Commit failed: {commit_result.stderr}")
        else:
            print("No changes to commit after removal")
    else:
        print("No matching files found to remove")
    
    print("Completed removal process")

if __name__ == "__main__":
    # Get the repository root directory (one level up from script location)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    # Stories folder is in docs/stories relative to repo root
    stories_folder = os.path.join(repo_root, "docs/stories")
    
    print(f"Using stories folder: {stories_folder}")
    remove_old_files_from_remote(stories_folder)

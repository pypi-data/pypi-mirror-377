#!/usr/bin/env python3
"""
Script to create a public release by:
1. Pulling latest from main in the public_release submodule
2. Creating a release branch with version and commit hash
3. Copying files from this repo to the submodule
4. Committing changes and creating a merge request
"""

import subprocess
import sys
import argparse
from pathlib import Path
import re
import requests
import os
from urllib.parse import quote


def run_command(cmd, cwd=None, capture_output=True):
    """Run a shell command and return the result"""
    try:
        if isinstance(cmd, str):
            cmd = cmd.split()

        result = subprocess.run(
            cmd, cwd=cwd, capture_output=capture_output, text=True, check=True
        )
        return result.stdout.strip() if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"✗ Command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr if e.stderr else e}")
        raise


def get_version_from_init():
    """Extract version from breathe_design/__init__.py"""
    init_file = Path(__file__).parent.parent / "breathe_design" / "__init__.py"

    if not init_file.exists():
        raise FileNotFoundError(f"Could not find __init__.py at {init_file}")

    with open(init_file, "r") as f:
        content = f.read()

    # Look for __version__ = "x.y.z" pattern
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not version_match:
        raise ValueError("Could not find __version__ in __init__.py")

    return version_match.group(1)


def get_current_commit_hash():
    """Get the current commit hash of this repo"""
    return run_command("git rev-parse --short HEAD")


def get_current_branch():
    """Get the current branch name of this repo"""
    return run_command("git rev-parse --abbrev-ref HEAD")


def pull_latest_main(submodule_path):
    """Pull the latest changes from main branch in the submodule"""
    print("Pulling latest changes from main in submodule...")

    # Change to submodule directory and pull latest main
    run_command("git checkout main", cwd=submodule_path)
    run_command("git pull origin main", cwd=submodule_path)

    print("✓ Successfully pulled latest main")


def create_release_branch(submodule_path, version, commit_hash, source_branch):
    """Create a new release branch in the submodule"""
    branch_name = f"release_from_branch_{source_branch}_{version}_{commit_hash}"

    print(f"Creating release branch: {branch_name}")

    # Create and checkout new branch
    run_command(f"git checkout -b {branch_name}", cwd=submodule_path)

    print(f"✓ Created and switched to branch: {branch_name}")
    return branch_name


def run_copy_script(submodule_path):
    """Run the copy script to sync files to the submodule"""
    print("Running copy script to sync files...")

    # Run the copy script with the submodule path as destination
    copy_script = Path(__file__).parent / "copy_to_remote_repo.py"
    run_command(f"python {copy_script} {submodule_path}", capture_output=False)

    print("✓ Files copied successfully")


def commit_changes(submodule_path, version, commit_hash):
    """Add all changes and commit them in the submodule"""
    print("Committing changes in submodule...")

    # Add all changes
    run_command(["git", "add", "."], cwd=submodule_path)

    # Check if there are any changes to commit
    try:
        status = run_command("git status --porcelain", cwd=submodule_path)
        if not status.strip():
            print("⚠ No changes to commit")
            return False
    except subprocess.CalledProcessError:
        pass

    # Commit changes
    commit_message = f"Release {version} from commit {commit_hash}"
    run_command(["git", "commit", "-m", commit_message], cwd=submodule_path)

    print(f"✓ Committed changes: {commit_message}")
    return True


def push_branch(submodule_path, branch_name):
    """Push the release branch to origin"""
    print(f"Pushing branch {branch_name} to origin...")

    run_command(f"git push -u origin {branch_name}", cwd=submodule_path)

    print(f"✓ Pushed branch {branch_name}")


def get_gitlab_token():
    """Get GitLab access token from environment or user input"""
    # Try to get token from environment variable
    token = os.getenv("GITLAB_TOKEN")
    if token:
        return token

    # Try to get token from git config (if set)
    try:
        token = run_command("git config --global gitlab.token")
        if token:
            return token
    except subprocess.CalledProcessError:
        pass

    # Ask user for token
    print("GitLab access token required for creating merge requests.")
    print("You can:")
    print("1. Set GITLAB_TOKEN environment variable")
    print("2. Set git config: git config --global gitlab.token YOUR_TOKEN")
    print("3. Get a token from: https://gitlab.com/-/profile/personal_access_tokens")
    print("   (Needs 'api' scope)")
    print()

    token = input("Enter your GitLab access token (or press Enter to skip): ").strip()
    return token if token else None


def extract_gitlab_project_info(submodule_path):
    """Extract GitLab project info from git remote"""
    try:
        # Get the remote URL
        remote_url = run_command("git remote get-url origin", cwd=submodule_path)

        # Parse GitLab URL to get project path
        # Example: https://gitlab.com/breathebatterytechnologies/breathe-model/test_public_breathe_design.git
        if "gitlab.com" in remote_url:
            # Remove .git suffix and extract path
            project_path = remote_url.replace("https://gitlab.com/", "").replace(
                ".git", ""
            )
            return "gitlab.com", project_path
        else:
            print(f"⚠ Non-GitLab.com URL detected: {remote_url}")
            return None, None

    except subprocess.CalledProcessError:
        print("✗ Could not get git remote URL")
        return None, None


def create_merge_request(submodule_path, branch_name, version, commit_hash):
    """Create a merge request using GitLab REST API"""
    print("Creating merge request...")

    # Get GitLab project info
    gitlab_host, project_path = extract_gitlab_project_info(submodule_path)
    if not gitlab_host or not project_path:
        print("✗ Could not extract GitLab project information")
        return False

    # Get access token
    token = get_gitlab_token()
    if not token:
        print("⚠ No GitLab token provided. Please create merge request manually:")
        print("  1. Go to the GitLab repository")
        print(f"  2. Create a merge request from branch '{branch_name}' to 'main'")
        print(f"  3. Title: 'Release {version} from commit {commit_hash}'")
        print(f"  4. Description: Release of breathe_design version {version}")
        return False

    try:
        # Prepare merge request data
        title = f"Release {version} from commit {commit_hash}"
        description = f"""Release of breathe_design version {version} from source commit {commit_hash}.

This release includes:
- Updated documentation and examples
- Latest version of requirements.txt
- All necessary files for public distribution

Auto-generated by create_public_release.py"""

        # GitLab API endpoint
        api_url = f"https://{gitlab_host}/api/v4/projects/{quote(project_path, safe='')}/merge_requests"

        # Request payload
        payload = {
            "source_branch": branch_name,
            "target_branch": "main",
            "title": title,
            "description": description,
            "remove_source_branch": False,  # Keep the branch after merge
        }

        # Request headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        print(f"Creating MR at: {api_url}")
        print(f"From: {branch_name} → main")

        # Make the API request
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)

        if response.status_code == 201:
            mr_data = response.json()
            mr_url = mr_data.get("web_url", "")
            mr_iid = mr_data.get("iid", "")
            print("✓ Merge request created successfully!")
            print(f"  URL: {mr_url}")
            print(f"  MR !{mr_iid}: {title}")
            return True
        else:
            print(f"✗ Failed to create merge request (HTTP {response.status_code})")
            try:
                error_info = response.json()
                if "message" in error_info:
                    print(f"  Error: {error_info['message']}")
                if "error" in error_info:
                    print(f"  Details: {error_info['error']}")
            except ValueError:
                print(f"  Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Network error creating merge request: {e}")
        return False
    except Exception as e:
        print(f"✗ Error creating merge request: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Create a public release in the submodule repository"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )
    parser.add_argument(
        "--skip-mr",
        action="store_true",
        help="Skip creating the merge request",
    )

    args = parser.parse_args()

    # Get paths
    current_repo = Path(
        __file__
    ).parent.parent  # Go up one level from public_release_scripts
    submodule_path = current_repo / "public_release"

    if not submodule_path.exists():
        print("✗ Error: public_release submodule not found")
        print("Make sure the submodule is properly initialized")
        sys.exit(1)

    try:
        # Get version, commit info, and source branch
        version = get_version_from_init()
        commit_hash = get_current_commit_hash()
        source_branch = get_current_branch()

        print(f"Source repo: {current_repo}")
        print(f"Submodule path: {submodule_path}")
        print(f"Version: {version}")
        print(f"Commit hash: {commit_hash}")
        print(f"Source branch: {source_branch}")
        print()

        if args.dry_run:
            print("DRY RUN - What would happen:")
            print("1. Pull latest main in submodule")
            print(
                f"2. Create branch: release_from_branch_{source_branch}_{version}_{commit_hash}"
            )
            print("3. Run copy script to sync files")
            print("4. Commit all changes")
            print("5. Push branch to origin")
            if not args.skip_mr:
                print("6. Create merge request")
            return

        # Step 1: Pull latest main
        pull_latest_main(submodule_path)
        print()

        # Step 2: Create release branch
        branch_name = create_release_branch(
            submodule_path, version, commit_hash, source_branch
        )
        print()

        # Step 3: Run copy script
        run_copy_script(submodule_path)
        print()

        # Step 4: Commit changes
        has_changes = commit_changes(submodule_path, version, commit_hash)
        if not has_changes:
            print("No changes to release. Exiting.")
            return
        print()

        # Step 5: Push branch
        push_branch(submodule_path, branch_name)
        print()

        # Step 6: Create merge request (if not skipped)
        if not args.skip_mr:
            mr_success = create_merge_request(
                submodule_path, branch_name, version, commit_hash
            )
            if not mr_success:
                print(
                    "⚠ Merge request creation failed, but release branch was created successfully"
                )

        # Summary
        print("=" * 60)
        print("RELEASE SUMMARY")
        print("=" * 60)
        print(f"Version: {version}")
        print(f"Source commit: {commit_hash}")
        print(f"Release branch: {branch_name}")
        print("Branch pushed: ✓")
        print(f"Submodule: {submodule_path}")

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

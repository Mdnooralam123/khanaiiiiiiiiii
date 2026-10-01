import os
import sys
import shutil
import subprocess
import requests
from getpass import getpass

SOURCE_REPO = "https://github.com/Ashwanikumar991713/Zoya-Assistant---Your-Virtual-Ai-partner.git"
SOURCE_OWNER = "Ashwanikumar991713"
SOURCE_REPO_NAME = "Zoya-Assistant---Your-Virtual-Ai-partner"
WORK_DIR = "zoya_temp"


def run(cmd, cwd=None, check=True):
    print(f"\n$ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, text=True,
                            capture_output=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        print(f"❌ Command fail hua: {cmd}")
        sys.exit(1)
    return result


def get_user_info(token):
    r = requests.get("https://api.github.com/user",
                     headers={"Authorization": f"token {token}"})
    if r.status_code != 200:
        print("❌ Token galat hai ya expire ho gaya.")
        sys.exit(1)
    return r.json()


def create_repo(token, repo_name):
    data = {
        "name": repo_name,
        "private": False,
        "auto_init": False,
        "description": "Zoya AI Assistant - copied from original repo"
    }
    r = requests.post("https://api.github.com/user/repos",
                      headers={"Authorization": f"token {token}",
                               "Accept": "application/vnd.github+json"},
                      json=data)
    if r.status_code == 201:
        print(f"✅ Naya repo ban gaya: {r.json()['html_url']}")
        return r.json()
    elif r.status_code == 422:
        print("⚠️ Repo already exists — usi me push karenge.")
        return {"full_name": f"{get_user_info(token)['login']}/{repo_name}"}
    else:
        print(f"❌ Repo create nahi hua: {r.text}")
        sys.exit(1)


def main():
    print("=" * 55)
    print("  ZOYA ASSISTANT — GitHub Repo Copier (Termux)")
    print("=" * 55)

    token = getpass("🔑 Apna GitHub Personal Access Token daalo: ").strip()
    if not token:
        print("Token khali hai.")
        sys.exit(1)

    user = get_user_info(token)
    username = user["login"]
    print(f"✅ Logged in as: {username}")

    new_repo_name = input(
        f"📦 Naye repo ka naam (Enter = same naam): "
    ).strip() or SOURCE_REPO_NAME

    # 1. Clean old temp folder
    if os.path.exists(WORK_DIR):
        shutil.rmtree(WORK_DIR)

    # 2. Clone source repo
    print("\n📥 Original repo clone kar raha hoon...")
    run(f"git clone {SOURCE_REPO} {WORK_DIR}")

    # 3. Remove old .git to start fresh
    git_dir = os.path.join(WORK_DIR, ".git")
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir)
        print("🧹 Purani .git history hata di.")

    # 4. Create new repo on user's account
    print("\n🆕 Tumhare account me naya repo banata hoon...")
    new_repo = create_repo(token, new_repo_name)
    full_name = new_repo.get("full_name", f"{username}/{new_repo_name}")
    remote_url = f"https://{username}:{token}@github.com/{full_name}.git"

    # 5. Init and push
    print("\n🚀 Files push kar raha hoon...")
    run("git init", cwd=WORK_DIR)
    run("git config user.email \"zoya@local\"", cwd=WORK_DIR)
    run("git config user.name \"Zoya Bot\"", cwd=WORK_DIR)
    run("git add .", cwd=WORK_DIR)
    run("git commit -m \"Initial commit - Zoya Assistant files\"", cwd=WORK_DIR, check=False)
    run("git branch -M main", cwd=WORK_DIR)
    run(f"git remote add origin {remote_url}", cwd=WORK_DIR, check=False)
    run(f"git remote set-url origin {remote_url}", cwd=WORK_DIR, check=False)
    run("git push -u origin main --force", cwd=WORK_DIR)

    print("\n" + "=" * 55)
    print(f"✅ HO GAYA BHAI!")
    print(f"🔗 Tumhara repo: https://github.com/{full_name}")
    print("=" * 55)

    # cleanup
    shutil.rmtree(WORK_DIR, ignore_errors=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Cancel kar diya.")
        shutil.rmtree(WORK_DIR, ignore_errors=True)
#!/usr/bin/env python3

import subprocess
import os
import shutil


# Define categories and their related tools
APP_CATEGORIES = {
    "CI/CD & Version Control": ["git", "gh", "glab", "jenkins"],
    "Containers & Orchestration": ["docker", "kubectl", "minikube", "helm"],
    "IaC Tools": ["terraform", "ansible"],
    "Development Tools": ["code", "python3", "node"]
}

# ✅ Check internet conection
def has_internet():
    try:
        subprocess.check_call(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

# ✅ Check if a command exists on the system
def is_installed(app):
    if app == "node":
        # Try regular node detection first
        if shutil.which("node"):
            return True

        # Try detecting node via nvm
        nvm_paths = [
            os.path.expanduser("~/.nvm"),
            "/usr/local/share/nvm",
            "/opt/nvm"
        ]

        for nvm_dir in nvm_paths:
            nvm_sh = os.path.join(nvm_dir, "nvm.sh")
            if os.path.exists(nvm_sh):
                cmd = (
                    f'export NVM_DIR="{nvm_dir}" && '
                    f'[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && '
                    'nvm current'
                )
                result = subprocess.run(
                    cmd,
                    shell=True,
                    executable="/bin/bash",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                # Check if nvm returned a valid node version
                if b"none" not in result.stdout and result.returncode == 0:
                    return True
        return False

    return shutil.which(app) is not None

# ✅ Display which tools are currently installed
def check_installed_apps():
    print("\n🔍 Checking installed applications:")
    for category, apps in APP_CATEGORIES.items():
        print(f"\n📦 {category}")
        for app in apps:
            status = "✅" if is_installed(app) else "❌"
            print(f"   {status} {app}")

# developing...

def prompt_install_apps():
    bulk_choice = input("\n🚀 Install all missing apps without confirmation? [y/n]: ").strip().lower()
    for category, apps in APP_CATEGORIES.items():
        print(f"\n🔧 {category}")
        for app in apps:
            if not is_installed(app):
                if bulk_choice == "y":
                    install_app(app)
                else:
                    choice = input(f"   → Install {app}? [y/n]: ").strip().lower()
                    if choice == "y":
                        install_app(app)

# ✅ Custom install logic for specific apps
def install_app(app):
    print(f"\n📥 Installing {app}...")

    try:
        if app == "terraform":
            # Terraform custom install via HashiCorp APT repo
            subprocess.run("wget -O- https://apt.releases.hashicorp.com/gpg | "
                           "sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg",
                           shell=True, check=True)

            subprocess.run('echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] '
                           'https://apt.releases.hashicorp.com '
                           '$(grep -oP \'(?<=UBUNTU_CODENAME=).*\' /etc/os-release || lsb_release -cs) main" | '
                           'sudo tee /etc/apt/sources.list.d/hashicorp.list',
                           shell=True, check=True)

            subprocess.run("sudo apt update", shell=True, check=True)
            subprocess.run("sudo apt install -y terraform", shell=True, check=True)

            print(f"✅ {app} has been installed successfully.")
            result = subprocess.run([app, "version"], check=True, capture_output=True, text=True)
            print(f"Current {app} version: {result.stdout.strip()}") 

        elif app == "gh":
            # GitHub CLI install (official method)
            subprocess.run("type -p curl >/dev/null || sudo apt install curl -y", shell=True, check=True)
            subprocess.run("curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | "
                           "sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg", shell=True, check=True)
            subprocess.run("sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg", shell=True, check=True)
            subprocess.run('echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] '
                           'https://cli.github.com/packages stable main" | '
                           "sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null", shell=True, check=True)
            subprocess.run("sudo apt update", shell=True, check=True)
            subprocess.run("sudo apt install -y gh", shell=True, check=True)

            print(f"✅ {app} has been installed successfully.")
            result = subprocess.run([app, "--version"], check=True, capture_output=True, text=True)
            print(f"Current {app} version: {result.stdout.strip()}")

        elif app == "glab":
            # Install glab via Homebrew
            if not shutil.which("brew"):
                print("🔍 Homebrew not found. Installing Homebrew first...")
                subprocess.run('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                               shell=True, check=True)
                # Homebrew needs to be added to path (especially for Linux)
                os.environ["PATH"] += os.pathsep + "/home/linuxbrew/.linuxbrew/bin"

            subprocess.run("brew install glab", shell=True, check=True)

        elif app == "jenkins":
            # Jenkins custom install from official repository
            subprocess.run("sudo mkdir -p /etc/apt/keyrings", shell=True, check=True)
            subprocess.run("sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc "
                           "https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key",
                           shell=True, check=True)

            subprocess.run('echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] '
                           'https://pkg.jenkins.io/debian-stable binary/" | '
                           "sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null",
                           shell=True, check=True)

            subprocess.run("sudo apt-get update", shell=True, check=True)
            subprocess.run("sudo apt-get install -y jenkins", shell=True, check=True)
        
            print(f"✅ {app} has been installed successfully.")
            result = subprocess.run([app, "--version"], check=True, capture_output=True, text=True)
            print(f"Current {app} version: {result.stdout.strip()}") 

        elif app == "docker":
            # Docker official install via Docker APT repository
            subprocess.run("sudo apt-get update", shell=True, check=True)
            subprocess.run("sudo apt-get install -y ca-certificates curl", shell=True, check=True)
            subprocess.run("sudo install -m 0755 -d /etc/apt/keyrings", shell=True, check=True)
            subprocess.run("sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg "
                           "-o /etc/apt/keyrings/docker.asc", shell=True, check=True)
            subprocess.run("sudo chmod a+r /etc/apt/keyrings/docker.asc", shell=True, check=True)

            subprocess.run('echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] '
                           'https://download.docker.com/linux/ubuntu '
                           '$(. /etc/os-release && echo ${UBUNTU_CODENAME:-$VERSION_CODENAME}) stable" | '
                           'sudo tee /etc/apt/sources.list.d/docker.list > /dev/null',
                           shell=True, check=True)

            subprocess.run("sudo apt-get update", shell=True, check=True)
            subprocess.run("sudo apt-get install -y docker-ce docker-ce-cli containerd.io "
                           "docker-buildx-plugin docker-compose-plugin", shell=True, check=True)
            
            print(f"✅ {app} has been installed successfully.")
            result = subprocess.run([app, "version"], check=True, capture_output=True, text=True)
            print(f"Current {app} version: {result.stdout.strip()}")

        elif app == "kubectl":
            # Install kubectl from official Kubernetes release
            print("🔍 Downloading latest kubectl release...")

            subprocess.run('curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"',
                           shell=True, check=True)
            subprocess.run('curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"',
                           shell=True, check=True)

            print("🔍 Verifying checksum...")
            result = subprocess.run('echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check',
                                    shell=True)

            if result.returncode != 0:
                print("❌ Checksum verification failed! Aborting install.")
                return

            print("✅ Checksum OK. Installing kubectl...")
            subprocess.run("sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl",
                           shell=True, check=True)

            print(f"✅ {app} has been installed successfully.")
            result = subprocess.run([app, "version"], check=True, capture_output=True, text=True)
            print(f"Current {app} version: {result.stdout.strip()}")

        elif app == "minikube":
            # Install minikube from latest GitHub release
            print("🔍 Downloading Minikube binary...")
            subprocess.run("curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64",
                           shell=True, check=True)

            print("📦 Installing Minikube...")
            subprocess.run("sudo install minikube-linux-amd64 /usr/local/bin/minikube", shell=True, check=True)

            print("🧹 Cleaning up...")
            subprocess.run("rm minikube-linux-amd64", shell=True, check=True)

            print(f"✅ {app} has been installed successfully.")
            result = subprocess.run([app, "version"], check=True, capture_output=True, text=True)
            print(f"Current {app} version: {result.stdout.strip()}")

        elif app == "helm":
            # Install Helm using the official install script
            print("📥 Downloading Helm install script...")
            subprocess.run("curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3",
                           shell=True, check=True)

            print("🔐 Making script executable...")
            subprocess.run("chmod 700 get_helm.sh", shell=True, check=True)

            print("🚀 Running Helm installer...")
            subprocess.run("./get_helm.sh", shell=True, check=True)

            print("🧹 Cleaning up installer...")
            subprocess.run("rm get_helm.sh", shell=True, check=True)

            print(f"✅ {app} has been installed successfully.")
            result = subprocess.run([app, "version"], check=True, capture_output=True, text=True)
            print(f"Current {app} version: {result.stdout.strip()}")

        elif app == "code":
            # Install Visual Studio Code via Microsoft APT repository
            print("📥 Setting up Microsoft APT repo for VS Code...")

            subprocess.run("sudo apt-get install -y wget gpg apt-transport-https", shell=True, check=True)

            subprocess.run("wget -qO- https://packages.microsoft.com/keys/microsoft.asc | "
                           "gpg --dearmor > microsoft.gpg", shell=True, check=True)

            subprocess.run("sudo install -D -o root -g root -m 644 microsoft.gpg "
                           "/usr/share/keyrings/microsoft.gpg", shell=True, check=True)

            subprocess.run("rm -f microsoft.gpg", shell=True, check=True)

            vscode_repo = (
                "Types: deb\n"
                "URIs: https://packages.microsoft.com/repos/code\n"
                "Suites: stable\n"
                "Components: main\n"
                "Architectures: amd64,arm64,armhf\n"
                "Signed-By: /usr/share/keyrings/microsoft.gpg\n"
            )

            with open("/tmp/vscode.sources", "w") as f:
                f.write(vscode_repo)

            subprocess.run("sudo mv /tmp/vscode.sources /etc/apt/sources.list.d/vscode.sources", shell=True, check=True)

            subprocess.run("sudo apt update", shell=True, check=True)
            subprocess.run("sudo apt install -y code", shell=True, check=True)

            print(f"✅ {app} has been installed successfully.")
            result = subprocess.run([app, "--version"], check=True, capture_output=True, text=True)
            print(f"Current {app} version: {result.stdout.strip()}")

        elif app == "node":
            print("📥 Installing NVM (Node Version Manager)...")
            subprocess.run(
            "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash",
            shell=True,
            check=True,
            )

            # 🧩 Add NVM to .bashrc so node is available in future sessions
            with open(os.path.expanduser("~/.bashrc"), "a") as f:
                f.write(r'\nexport NVM_DIR="$HOME/.nvm"\n[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"\n')

            # Detect the correct NVM_DIR
            nvm_paths = [
            os.path.expanduser("~/.nvm"),
            "/usr/local/share/nvm",
            "/opt/nvm"
            ]
            nvm_dir = next((p for p in nvm_paths if os.path.exists(os.path.join(p, "nvm.sh"))), None)

            if not nvm_dir:
                print("❌ Could not find NVM directory after installation.")
                return

            print(f"📍 Detected NVM at: {nvm_dir}")

            node_version = input("⬇️ Enter Node.js version to install (default: 22): ").strip() or "22"
            print("⬇️ Installing Node.js via NVM...")
            subprocess.run(
            f'export NVM_DIR="{nvm_dir}" && '
            f'[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && '
            f'nvm install {node_version} && nvm use {node_version}',
            shell=True,
            executable="/bin/bash",
            check=True,
            )

            print(f"✅ {app} has been installed successfully.")
            result = subprocess.run([app, "--version"], check=True, capture_output=True, text=True)
            print(f"Current {app} version: {result.stdout.strip()}")

        else:
            # Default APT install
            subprocess.run(["sudo", "apt", "install", "-y", app], check=True)

        from datetime import datetime

        with open("install_log.txt", "a") as log_file:
            log_file.write(f"[{datetime.now()}] {app} installed successfully\n")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {app}")
        print(f"   Error: {e}")

# ✅ Setup Git global configuration
def setup_git_config():
    print("\n🛠️ Setting up Git config...")
    name = input("   Git username: ")
    email = input("   Git email: ")
    subprocess.run(["git", "config", "--global", "user.name", name])
    subprocess.run(["git", "config", "--global", "user.email", email])
    print("✅ Git config updated")


# ✅ Generate SSH key and show user how to add it to GitHub
def setup_github_ssh():
    print("\n🔐 Setting up GitHub SSH key...")

    ssh_path = os.path.expanduser("~/.ssh")
    key_path = os.path.join(ssh_path, "id_rsa")

    if not os.path.exists(key_path):
        os.makedirs(ssh_path, exist_ok=True)

        email = input("   Enter your GitHub email for SSH key: ")
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "4096", "-C", email, "-f", key_path, "-N", ""])

        # Start the ssh-agent and add the new key
        agent_output = subprocess.check_output('eval "$(ssh-agent -s)" && echo $SSH_AUTH_SOCK', shell=True, executable='/bin/bash', text=True)
        os.environ["SSH_AUTH_SOCK"] = agent_output.strip()
        subprocess.run(["ssh-add", key_path])

        print("\n📋 Public SSH key:")
        subprocess.run(["cat", f"{key_path}.pub"])
        print("\n🔗 Add this public key to your GitHub account under 'SSH and GPG keys'")
    else:
        print("✅ SSH key already exists at ~/.ssh/id_rsa")

###########

def show_git_url_tip(url: str):
    if url.startswith("https://"):
        print("💡 Tip: HTTPS URLs may prompt for username/password or token.")
    elif url.startswith("git@"):
        print("🔑 Tip: You're using SSH. Make sure your SSH keys are set up.")

def run_git_command(args, check=True, capture_output=False, text=True):
    """Helper to run git commands with error handling."""
    try:
        return subprocess.run(args, check=check, capture_output=capture_output, text=text)
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {' '.join(args)}")
        print(f"   Error: {e}")
        if capture_output and hasattr(e, 'output'):
            print(f"   Output: {e.output}")
        raise

def has_unstaged_or_untracked_changes():
    proc = run_git_command(["git", "status", "--porcelain"], capture_output=True)
    lines = proc.stdout.strip().splitlines()
    for line in lines:
        if not line:
            continue
        # Untracked files start with "??"
        if line.startswith("??") or line[1] != ' ':
            return True
    return False

def has_staged_changes():
    proc = run_git_command(["git", "diff", "--cached", "--name-only"], capture_output=True)
    return bool(proc.stdout.strip())

def confirm_commit_or_stash():
    print("⚠️ You have staged changes that are not committed.")
    while True:
        choice = input("Do you want to [c]ommit, [s]tash, or [a]bort? ").strip().lower()
        if choice == "c":
            msg = input("📝 Commit message: ").strip() or "WIP commit"
            run_git_command(["git", "commit", "-m", msg])
            return True
        elif choice == "s":
            run_git_command(["git", "stash"])
            print("🧹 Changes stashed.")
            return True
        elif choice == "a":
            print("🚫 Operation aborted.")
            return False
        else:
            print("❌ Invalid option, please enter 'c', 's', or 'a'.")

def setup_git_remote():
    print("\n🔗 Git Remote Setup")

    # Step 1: Check if inside a Git repo
    inside_git = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                                capture_output=True, text=True)
    if inside_git.returncode != 0:
        choice = input("📁 No Git repo found. Clone one? [y/n]: ").strip().lower()
        if choice == "y":
            url = input("🔗 Enter remote repo URL: ").strip()
            run_git_command(["git", "clone", url])
            print("✅ Repo cloned. Navigate into it and rerun this function.")
            return
        else:
            init_choice = input("🆕 Initialize a new Git repo here? [y/n]: ").strip().lower()
            if init_choice == "y":
                run_git_command(["git", "init", "--quiet"])
            else:
                print("❌ Skipping remote setup.")
                return

    # Step 2: Check existing remotes
    remotes_proc = run_git_command(["git", "remote"], capture_output=True)
    remotes = remotes_proc.stdout.strip().splitlines()
    action = None

    if "origin" in remotes:
        url_proc = run_git_command(["git", "remote", "get-url", "origin"], capture_output=True)
        url = url_proc.stdout.strip()
        print(f"✅ Remote 'origin' exists: {url}")
        show_git_url_tip(url)

        action = input("🔁 Action: [k]eep / [c]hange / [p]ull / [u]push: ").strip().lower()

        if action == "p":
            branch = input("⬇️ Branch to pull (default: main): ").strip() or "main"

            # SAFETY CHECKS BEFORE PULL
            if has_unstaged_or_untracked_changes():
                print("❌ Unstaged or untracked changes detected. Please commit, stash, or discard them before pulling.")
                return
            if has_staged_changes():
                if not confirm_commit_or_stash():
                    return

            run_git_command(["git", "pull", "--rebase", "origin", branch], check=False)
            return

        elif action == "u":
            # SAFETY CHECKS BEFORE PUSH
            if has_unstaged_or_untracked_changes():
                print("❌ Unstaged or untracked changes detected. Please commit, stash, or discard them before pushing.")
                return
            if has_staged_changes():
                if not confirm_commit_or_stash():
                    return
            # Continue to push after checks

        elif action == "c":
            run_git_command(["git", "remote", "remove", "origin"])

        elif action != "k":
            print("❌ Invalid option.")
            return

    # Step 3: Add remote if needed
    if "origin" not in remotes or action == "c":
        remote_url = input("🔗 Enter new remote URL (SSH or HTTPS): ").strip()
        run_git_command(["git", "remote", "add", "origin", remote_url])
        show_git_url_tip(remote_url)

    # Step 4: Test remote connection
    print("🔍 Testing connection to 'origin'...")
    try:
        run_git_command(["git", "ls-remote", "origin"])
        print("✅ Connection successful.")
    except subprocess.CalledProcessError:
        print("❌ Could not connect to remote. Check your URL or SSH config.")
        return

    # Step 5: Stage all files
    run_git_command(["git", "add", "."], check=False)

    # Step 6: Commit if needed
    has_commits = subprocess.run(["git", "log"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    status_proc = run_git_command(["git", "status", "--porcelain"], capture_output=True)
    if has_commits.returncode != 0 and status_proc.stdout.strip():
        msg = input("📝 Commit message [default: Initial commit]: ").strip() or "Initial commit"
        run_git_command(["git", "commit", "-m", msg])

    # Step 7: Choose branch name
    branch = input("🌿 Branch name to push (default: main): ").strip() or "main"
    run_git_command(["git", "branch", "-M", branch])

    # Step 8: Confirm push
    confirm_push = input(f"📤 Do you want to push to origin/{branch}? [y/n]: ").strip().lower()
    if confirm_push != "y":
        print("🚫 Push cancelled by user.")
        return

    # SAFETY CHECKS BEFORE PULL + PUSH
    if has_unstaged_or_untracked_changes():
        print("❌ Unstaged or untracked changes detected. Please commit, stash, or discard them before pushing.")
        return
    if has_staged_changes():
        if not confirm_commit_or_stash():
            return

    # Step 9: Pull with rebase to avoid push conflicts
    print(f"🔄 Rebasing from origin/{branch}...")
    run_git_command(["git", "pull", "--rebase", "origin", branch], check=False)

    # Step 10: Push
    print(f"🚀 Pushing to origin/{branch}...")
    try:
        run_git_command(["git", "push", "-u", "origin", branch])
        print("✅ Push successful.")
    except subprocess.CalledProcessError as e:
        print("❌ Push failed.")
        if "set upstream" in str(e):
            print("💡 Hint: You may need to set an upstream branch.")
        print(f"   Error: {e}")

    # Step 11: Summary
    print("\n📦 Remote setup complete.")
    print(f"🔗 Remote: origin")
    print(f"🌿 Branch: {branch}")

#########
# ✅ Main menu loop
def main_menu():
    while True:
        print("\n=== DevOps Setup Menu ===")
        print("1. Check installed apps")
        print("2. Install missing apps")
        print("3. Setup Git config")
        print("4. Setup GitHub SSH key")
        print("5. Setup Git Remote")
        print("6. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            check_installed_apps()
        elif choice == "2":
            prompt_install_apps()
        elif choice == "3":
            setup_git_config()
        elif choice == "4":
            setup_github_ssh()
        elif choice == "5":
            setup_git_remote()
        elif choice == "6":
            print("✅ Exiting setup.")
            break
        else:
            print("❌ Invalid option, try again.")


# ✅ Run main menu if executed directly
if __name__ == "__main__":
    main_menu()

# 🧠 Git Commands Cheat Sheet

## Core Git Concepts
- **Repository (repo)**: A folder tracked by Git.  
- **Commit**: A snapshot of your code.  
- **Branch**: A parallel version of your repo.  
- **Remote**: A version stored online (e.g., GitHub).  

---

## 🚀 Setup
```bash
git config --global user.name "Aidan Nelappana"
git config --global user.email "anelappana@gmail.com"
git config --list          # view settings
```

---

## 📁 Starting a Project
```bash
git init                    # start a new repo
git clone <url>             # clone an existing repo
git status                  # check file changes
```

---

## ✏️ Staging and Committing
```bash
git add <file>              # stage one file
git add .                   # stage all changes
git commit -m "message"     # commit with message
git commit -am "message"    # add + commit tracked files
```

---

## 🌿 Branches
```bash
git branch                  # list branches
git branch <name>           # create new branch
git checkout <name>         # switch branch
git switch <name>           # modern switch
git checkout -b <name>      # create + switch
git merge <name>            # merge branch into current
git branch -d <name>        # delete branch
```

---

## ☁️ Remotes
```bash
git remote -v                              # view remotes
git remote add origin <url>                # add remote
git push -u origin main                    # push main branch
git pull origin main                       # pull latest
git fetch origin                           # get updates, no merge
```

---

## 🔄 Updating and Syncing
```bash
git pull                                  # fetch + merge
git fetch && git merge origin/main        # manual merge
git rebase origin/main                    # reapply commits
git stash                                 # save uncommitted work
git stash pop                             # restore stashed work
```

---

## 🧹 Undoing Mistakes
```bash
git restore <file>            # undo unstaged changes
git reset <file>              # unstage file
git reset --hard HEAD         # discard all local changes
git log                       # view commit history
git diff                      # see changes
git reflog                    # view command history
```

---

## 🧩 Working with GitHub
```bash
# Create and connect
git remote add origin https://github.com/<user>/<repo>.git

# Push and Pull
git push origin main
git pull origin main
```

---

## 🔍 Viewing and Inspecting
```bash
git show <commit>           # view details of a commit
git diff HEAD~1 HEAD        # compare commits
git log --oneline --graph   # visualize history
git blame <file>            # see who changed each line
```

---

## ⚙️ Advanced
```bash
git cherry-pick <commit>    # apply commit from another branch
git revert <commit>         # make a new commit that undoes changes
git tag v1.0 -m "Release"   # tag commit
git push origin v1.0        # push tag
```

---

## 🐙 Common Workflows

### 1. Feature Branch
```bash
git checkout -b feature-x
# work and commit
git push origin feature-x
```

### 2. Sync with Main
```bash
git checkout main
git pull origin main
git merge feature-x
```

### 3. Squash Commits Before Push
```bash
git rebase -i HEAD~3
```

---

## 🧭 Shortcuts

| Command | Description |
|----------|-------------|
| `git status -sb` | Compact status |
| `git log --graph --decorate --oneline` | Pretty history |
| `git diff --staged` | See staged changes |
| `git commit --amend` | Edit last commit |

import sys, os, re

def setup():
    """
    Normalise notebook environment:
    - In Colab: clone/checkout correct branch, add repo root to sys.path, cd to notebook folder
    - In local Jupyter: detect notebook path, find repo root, add sys.path, cd to notebook folder
    """
    try:
        import google.colab
        from google.colab import _message
        is_colab = True
    except ImportError:
        is_colab = False

    if is_colab:
        # --- Colab case ---
        nb = _message.blocking_request('get_ipynb')['ipynb']
        org = repo = branch = nb_relpath = None

        for cell in nb['cells']:
            if cell.get('cell_type') == 'markdown':
                text = "".join(cell.get('source', []))
                # Extract the first href link in the markdown cell
                href_match = re.search(r'href="([^"]+)"', text)
                if href_match:
                    href = href_match.group(1)
                    # Now parse out org, repo, branch, and path from the URL
                    m = re.search(
                        r'github/([^/]+)/([^/]+)/blob/([^/]+)/(.*?)(?:\.ipynb|#|$)',
                        href
                    )
                    if m:
                        org, repo, branch, nb_relpath = m.groups()
                        break


        if not repo:
            raise RuntimeError("No Colab badge with repo info found")

        repo_root = f"/content/{repo}"

        # Clone or checkout branch
        if not os.path.exists(repo_root):
            os.system(f"git clone -b {branch} https://github.com/{org}/{repo}.git {repo_root}")
        else:
            os.system(f"cd {repo_root} && git fetch && git checkout {branch}")

        # Add repo root to sys.path
        sys.path.insert(0, repo_root)

        # cd into the notebook’s directory
        target_dir = os.path.join(repo_root, os.path.dirname(nb_relpath))
        os.chdir(target_dir)

        print(f"[Colab] Repo: {repo} | Branch: {branch}")
        print("[Colab] Repo root added to sys.path")
        print(f"[Colab] Working directory set to: {os.path.relpath(target_dir, repo_root)}")

        return repo_root, branch, target_dir

    else:
        # --- Local Jupyter case ---
        import ipynbname
        from pathlib import Path

        nb_path = ipynbname.path()
        nb_dir = nb_path.parent

        # Walk up until we find repo root (by `.git`)
        repo_root = nb_dir
        while not (repo_root / ".git").exists() and repo_root != repo_root.parent:
            repo_root = repo_root.parent

        sys.path.insert(0, str(repo_root))
        os.chdir(nb_dir)

        print("[Local] Repo root added to sys.path")
        print(f"[Local] Working directory set to: {os.path.relpath(nb_dir, repo_root)}")

        return str(repo_root), None, str(nb_dir)

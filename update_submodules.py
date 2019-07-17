"""Tool to mirror relevant CISAGOV infrastructure repositories as submodules.

Usage:
	COMMAND_NAME (amis | ansible-roles | skeletons)...

"""

import json
import os
import subprocess
import urllib.request

import docopt

API_BASE_URL = "https://api.github.com/search/repositories?q=org:cisagov+"
AMI_QUERY = "cyhy_amis+in:name"
ANSIBLE_ROLE_QUERY = "ansible-role-+in:name"
SKELETON_QUERY = "skeleton-+in:name"


def get_repository_list(url):
    response = urllib.request.urlopen(url)
    resp_json = json.loads(
        response.read().decode(response.info().get_param("charset") or "utf-8")
    )
    return resp_json.get("items", [])


def get_missing_list(path, repo_list):
    dir_list = [dI for dI in os.listdir(path) if os.path.isdir(os.path.join(path, dI))]
    return set(repo_list) - set(dir_list)


def get_missing_repos(prefix, path, repo_list):
    valid_repos = [r for r in repo_list if r["name"].startswith(prefix)]
    missing_repos = get_missing_list(path, [r["name"] for r in valid_repos])
    for url in [r["ssh_url"] for r in valid_repos if r["name"] in missing_repos]:
        print(subprocess.run(["git", "submodule", "add", url], cwd=path).stdout)


def get_amis(repo_list):
    get_missing_repos("", ".", repo_list)


def get_ansible_roles(repo_list):
    get_missing_repos("ansible-role-", "ansible-roles", repo_list)


def get_skeletons(repo_list):
    get_missing_repos("skeleton-", "skeletons", repo_list)


def main():
    args = docopt.docopt(__doc__, version="1.0")

    if args["amis"]:
        print("Getting amis")
        get_amis(get_repository_list(API_BASE_URL + AMI_QUERY))
    if args["ansible-roles"]:
        print("Getting ansible roles")
        get_ansible_roles(get_repository_list(API_BASE_URL + ANSIBLE_ROLE_QUERY))
    if args["skeletons"]:
        print("Getting skeletons")
        get_skeletons(get_repository_list(API_BASE_URL + SKELETON_QUERY))


if __name__ == "__main__":
    main()

import errno
import logging
import os
import progressbar
import requests
import sys

from collections import deque

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

git_user = "CSSEGISandData"
git_repo = "COVID-19"
git_base = "https://api.github.com/repos/{}/{}".format(git_user, git_repo)
git_contents_base = "https://api.github.com/repos/{}/{}/contents".format(git_user, git_repo)
repo_subdirectory = "csse_covid_19_data/csse_covid_19_daily_reports"
local_dir = "covid-ingestion-container/output/data"
token = ""

req = requests.Session()
req.headers.update({'Authorization': f'token {token} '})



def request_error_handler(r):
    if r.status_code == 200:
        return r
    else:
        logger.error(f'Request resulted in Status Code {r.status_code}\n{r.url}\n{r.text}')
        sys.exit(1)
def get_repo_sha(author, repo, ref="master"):
    """
    Gets the Whole Repository Tree SHA for latest commit

    Args:
        author (str): Github Repo Author
        repo (str): GitHub Repo
        ref (ref): Repo Branch/Ref

    Returns:
        str: the Tree SHA of the repository's latest commit
    """

    r = req.get(
        f"https://api.github.com/repos/{author}/{repo}/branches/{ref}"
    )

    r = request_error_handler(r)
    return r.json()['commit']['commit']['tree']['sha']
def get_subdir_tree(author, repo, tree_sha):
    """
    Grabs the tree for the given sha:
    Args:
        author (str): Repository Author
        repo (str): Repository Name
        tree_sha (str): a tree SHA

    Returns:
        list: Contents and SHAs of a directory
    """
    r = req.get(
        f"https://api.github.com/repos/{author}/{repo}/git/trees/{tree_sha}"
    )

    r = request_error_handler(r)
    return r.json()['tree']
def get_subdir_sha(subdir_tree, subdir):
    """
    Grabs the SHA of a subdirectory from the subdir_tree
    Args:
        subdir_tree (list): Contents and SHAs of a directory
        subdir (str): Matching Directory to look for to get the corresponding SHA

    Returns:
        str: SHA of a matching directory

    """
    for element in subdir_tree:
        logger.info(element)
        if element['path'] == subdir:
            return element['sha']

    logger.error(f"No Subdirectory \"{subdir}\" found")
    sys.exit(1)
def get_sub_tree(author, repo, subdir = None, tree_sha = None):
    """
    Recursive function for fetching the contents and SHAs of a subfolder of interest
    Args:
        author (str): Repository Author
        repo (str): Repository Name
        subdir (str): subdirectory of interest in repo
        tree_sha (str): a commit's tree SHA

    Returns:
        list: Contents and SHAs of a subdirectory

    """
    # Gets Repo SHA if none is supplied
    if not tree_sha:
        tree_sha = get_repo_sha(
            author,
            repo
        )

    # Gets the subdir SHA


    subdir_tree = get_subdir_tree(
        author,
        repo,
        tree_sha
    )

    subdir_sha = get_subdir_sha(
        subdir_tree,
        subdir.split("/")[0]
    )
    if '/' in subdir:
        return get_sub_tree(
            author,
            repo,
            '/'.join(subdir.split("/")[1:]),
            subdir_sha

        )
    else:
        return get_subdir_tree(
            author,
            repo,
            subdir_sha
        )


def get_download_link(author, repo, blob):

    r = req.get(
        f"https://api.github.com/repos/{author}/{repo}/contents/{repo_subdirectory}/{blob['path']}"
    )
    r = request_error_handler(r)
    return r.json()['download_url']

def download_blob_as_file(local_dir, blob, download_link):
    r = req.get(download_link, stream=True)
    r = request_error_handler(r)
    blob_local_fp = os.path.join(local_dir, blob['path'])

    with open(blob_local_fp, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

def git_sync(local_dir):
    files = get_sub_tree(git_user, git_repo, repo_subdirectory)
    bar = progressbar.ProgressBar(max_value=len(files))
    for idx, file in enumerate(files):
        download_link = get_download_link(git_user, git_repo, file)
        download_blob_as_file(local_dir, file, download_link)
        bar.update(idx)


derp = git_sync(local_dir)
req.close()
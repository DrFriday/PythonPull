"""Defines a git pull"""

# The MIT License (MIT)

# Copyright (c) 2015 Michael Boselowitz

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import datetime
import pygit2

def pull(repo, remote_name='origin', credentials_callback=None):
    """Pulls from remote_name, updates the repo

    Parameters:
        repo - Repository used to keep track
        remote_name - name for the remote will be pulled
        credentials_callback - credentials callback, see comment below

    The credentials_callback should be of the form
    pygit2.RemoteCallbacks(pygit2.UserPass(uname, psswrd)).
    This makes fetching from a repo what needs authentication possible.
    """

    # Get the remote
    remote = repo.remotes[remote_name]

    # Fetch any new changes
    remote.fetch(callbacks=credentials_callback)

    # Lookes up the reference for the master branch
    remote_master_id = repo.lookup_reference('refs/remotes/origin/master').target

    # merge_analysis returns a mixture of the following GIT_MERGE flags
    # GIT_MERGE_ANALYSIS_NONE = 0
    # GIT_MERGE_ANALYSIS_NORMAL = 1
    # GIT_MERGE_ANALYSIS_UP_TO_DATE = 2
    # GIT_MERGE_ANALYSIS_FASTWORWARD = 4
    # GIT_MERGE_ANALYSIS_UNBORN = 8
    merge_result, _ = repo.merge_analysis(remote_master_id)

    # Up to date, do nothing
    if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
        return
    # We can just fastforward
    elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
        print("Changes can be fast-forwarded")

        repo.checkout_tree(repo.get(remote_master_id))
        master_ref = repo.lookup_reference('refs/heads/master')
        master_ref.set_target(remote_master_id)
        repo.head.set_target(remote_master_id)
    elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:

        try:
            repo.merge(remote_master_id)
        except pygit2.GitError as err:
            print(f"Git Error {err}")

        # print(repo.index.conflicts)
        print("Merge detected!")

        # Checks to see if there are any conflicts
        assert repo.index.conflicts is None, 'Conflicts!'

        # Get the user
        user = repo.default_signature

        # Write changes to the current working tree
        tree = repo.index.write_tree()

        # Create the message
        now = datetime.datetime.now().strftime(r"%Y-%m-%d %H:%M")
        message = f"Automatically merging by python script on {now}"

        # Create the commit, with all the updates
        commit = repo.create_commit('HEAD',
                                    user,
                                    user,
                                    message,
                                    tree,
                                    [repo.head.target, remote_master_id])

        # Cleanup
        repo.state_cleanup()
    else:
        raise AssertionError('Unknown merge analysis result')

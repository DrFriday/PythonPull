"""Continuously updates the git repo"""

import time
import getpass
import pygit2

from git_pull import pull

def main():
    """Main entry point to the program"""

    target_dir = input("Please enter target dir > ")
    u_name = input("Please enter github username > ")
    pss_wrd = getpass.getpass(prompt="Please enter github password > ")
    check_interval = input("Please enter desired check interval (seconds)[10] > ")

    if check_interval == "":
        check_interval = 10

    if target_dir == "" or u_name == "" or pss_wrd == "":
        print_help()
        return

    # getting set up for the pull request
    cred = pygit2.UserPass(u_name, pss_wrd)
    callback = pygit2.RemoteCallbacks(credentials=cred)
    repo = pygit2.Repository(target_dir)

    print(f"Watching {target_dir} for updates every {check_interval} seconds.")

    start_time = time.time()
    while True:
        cur_time = time.time()

        if cur_time - start_time >= check_interval:
            print(f"Checking for updates...")

            # initiate the pull
            pull(repo, credentials_callback=callback)

            # reset start time to check new interval
            start_time = time.time()

def print_help():
    """Prints out helps if the user didn't supply enough information"""
    print("""\nPlease enter you target directory (don't include .git in the name),
and a valid github username and password to pull from private repositories.""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting program")

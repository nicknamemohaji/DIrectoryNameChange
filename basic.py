"""
Single search + blocking IO + single task
"""
import os
import sys
import time


def check_input(prompt):
    while True:
        key = input(prompt)
        selection = input("[*] Input was [%s]. Proceed? (Y/n) : " % key)
        if selection == 'y' or selection == 'Y' or selection == '':
            return key
        else:
            continue


def change_file_names(path):
    # TODO Uppercase

    # Change file name
    for filename in os.listdir(path):
        try:
            os.rename(path + filename, path + filename.lower())
        except FileExistsError:
            pass

    # Change directory name
    try:
        os.rename(path,
                  "/".join(path.split('/')[:-2]) + "/" + path.split('/')[-2].lower())
    except FileExistsError:
        pass


def recursive_basic(path):
    directories = [f for f in os.listdir(path) if not os.path.isfile(path + f)]

    if len(directories) != 0:  # There is subdirectory, so do recursive search.
        for dirs in directories:
            recursive_basic(path + dirs + '/')

    else:
        print("[-] Working on %s" % path)
        _file_count = len([f for f in os.listdir(path) if os.path.isfile(path + f)])
        print("[-] Current directory has %d files, %d folders. " % (_file_count,
                                                                    len(os.listdir(path)) - _file_count))
        change_file_names(path)


if __name__ == "__main__":
    # Get path
    PATH = check_input("[*] Enter path : ").replace("\\", "/")
    PATH = PATH + "/" if PATH[-1] != "/" else PATH

    if os.path.isdir(PATH) is False:
        print("[-] DIRECTORY DOES NOT EXISTS. ")
        sys.exit(1)

    file_count = len([f for f in os.listdir(PATH) if os.path.isfile(PATH + f)])
    print("[*] Directory has %d files, %d folders. " % (file_count,
                                                        len(os.listdir(PATH)) - file_count))
    if ["Y", "y", ""].count(input("[*] Continue? [Y/n] : ")) == 0:
        print("[-] Abort.")
        sys.exit(1)

    # TODO Mode selection (lowercase / uppercase)

    # Start task
    start_time = time.time()
    print("[+] Starting task : %s" % time.strftime("%H:%m:%S", time.localtime(start_time)))
    recursive_basic(PATH)
    print("[+] Finished task : %s" % time.strftime("%H:%m:%S", time.localtime(time.time())))
    print("[*] BASIC | %lf seconds." % (time.time() - start_time))

"""
Utility for making test data.
[*] Options
    - Directory to make test data
    - TODO Hierarchy of test data
    - TODO Naming procedures of test data
    - Size of test data
"""

import os
import sys
import time
import random
import string


def check_input(prompt):
    while True:
        key = input(prompt)
        selection = input("[+] Input was [%s]. Proceed? (Y/n) : " % key)
        if selection == 'y' or selection == 'Y' or selection == '':
            return key
        else:
            continue


def make_data(count, naming, size, path):
    for i in range(count):
        name = ""
        if naming == 1:  # UPPER 5 + INT 5 + LOWER 5
            # TODO arbitrary naming prefix
            name += "".join([random.choice(string.ascii_uppercase) for _ in range(5)])
            name += "".join([random.choice(string.digits) for _ in range(5)])
            name += "".join([random.choice(string.ascii_lowercase) for _ in range(5)])

            name += ".testdata"

        with open(path + name, "w") as f:
            f.write("A" * size)


if __name__ == '__main__':
    # Get path
    PATH = check_input("[*] Enter path to make test data : ").replace("\\", "/")
    PATH = PATH + "/" if PATH[-1] != "/" else PATH

    if os.path.isdir(PATH) is False:
        print("[-] DIRECTORY DOES NOT EXISTS. ")
        sys.exit(1)

    # Check write permission
    PATH = PATH + "test_%s/" % (str(int(time.time())))
    try:
        os.mkdir(PATH[:-1])
    except OSError:
        print("[-] CHECK WRITE PERMISSION. ")
        sys.exit(1)

    # Get settings
    SETTINGS = {'count': int(check_input("[*] Enter amount of files per directory : ")),
                'size': int(check_input("[*] Enter size of files : ")),
                'subdirs': int(check_input("[*] Enter amount of sub-directories : "))}

    print("[*] Making with settings")
    print("- naming prefix : %s" % "UPPER(5) + INT(5) + LOWER(5)")
    print("- subdirectories : %d" % SETTINGS['subdirs'])
    print("- size : %dKB" % int(SETTINGS['size'] / 1024))
    print("- count : %d" % SETTINGS['count'])
    if ["Y", "y", ""].count(input("[*] Continue? [Y/n] : ")) == 0:
        os.rmdir(PATH)
        print("[-] Abort.")
        sys.exit(1)

    # Make test data
    for i in range(SETTINGS['subdirs']):
        subdir_name = "".join([random.choice(string.digits + string.ascii_letters) for _ in range(15)]) + '/'
        os.mkdir(PATH + subdir_name)
        for j in range(SETTINGS['subdirs']):
            # TODO Multi-layer hierarchy
            subdir_name_2 = "".join([random.choice(string.digits + string.ascii_letters) for _ in range(15)]) + '/'
            os.mkdir(PATH + subdir_name + subdir_name_2)
            make_data(path=PATH + subdir_name + subdir_name_2, naming=1, size=SETTINGS['size'] , count=SETTINGS['count'])
    print("[+] Task finished. ")
    sys.exit(0)

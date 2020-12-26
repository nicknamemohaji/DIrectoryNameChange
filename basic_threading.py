"""
Single search + non blocking IO emulated with Threading + single task
"""
import os
import sys
import time
import argparse
import threading
from threading import Thread, Lock, Timer

# TODO add logging module

THREAD_PER_FILE = 0  # For dividing files
MAX_THREAD = 0  # Limit resource...
EMERGENCY_KILL = False
dirs = []  # As threads does not finish task sequentially, have to remember directory names separately.


class VariableHolder:  # Might occur in race-condition scenario, so lock resource just in case.
    def __init__(self):
        self.lock = Lock()
        self.file_count_all = 0
        self.file_processing_done = 0
        self.thread_list = []


variables = VariableHolder()


def check_input(prompt):
    while True:
        key = input(prompt)
        selection = input("[*] Input was [%s]. Proceed? (Y/n) : " % key)
        if selection == 'y' or selection == 'Y' or selection == '':
            return key
        else:
            continue


def split(a, n):
    # https://stackoverflow.com/a/2135920
    # For splitting list
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def change_file_names(_path, file_list, mode):
    # mode : True for lowercase, False for uppercase
    global variables

    # Change file name
    for filename in file_list:
        try:
            if not EMERGENCY_KILL:
                os.rename(_path + filename, _path +
                        (filename.lower() if mode else filename.upper()))
        except FileExistsError:
            pass

    # Update work status
    # TODO UPDATE STATUS WHILE WORKING
    with variables.lock:
        variables.file_processing_done += len(file_list)
    return


def recursive_threading(path, mode):
    # Check for subdirectory
    directories = [f for f in os.listdir(path) if not os.path.isfile(path + f)]
    if len(directories) != 0:  # There is subdirectory, so do recursive search on those
        for directory in directories:
            recursive_threading(path + directory + '/', mode)
            dirs.append(path + directory + '/')  # Because threads are working, remind for later

    '''
    # Notify current working status
    logging.info("[-] Working on %s" % path)
    _file_count = len([f for f in os.listdir(path) if os.path.isfile(path + f)])
    logging.info("[-] Current directory has %d files, %d folders. " % (_file_count,
                                                                len(os.listdir(path)) - _file_count))
    '''

    # Make threads to change names
    file_list = [f for f in os.listdir(path) if os.path.isfile(path + f)]
    if len(file_list) > 0:
        # Mark file count
        with variables.lock:
            variables.file_count_all += len(file_list)

        global THREAD_PER_FILE
        for files in split(file_list, int(len(file_list) / THREAD_PER_FILE) + 1):
            with variables.lock:
                variables.thread_list.append(Thread(target=change_file_names,
                                                    args=(path, files, mode)
                                                    ))

    return


def print_status():
    try:
        ratio = variables.file_processing_done / variables.file_count_all
    except ZeroDivisionError:
        return

    if ratio < 1:
        print(f"[-] {time.strftime('%H:%M:%S', time.localtime(time.time()))}  : "
              f"{variables.file_processing_done} / {variables.file_count_all} " +
              "(%.2f%%)" % (ratio * 100))
        Timer(3, print_status).start()
    else:
        return


if __name__ == "__main__":
    """
    1. Parse arguments
    """
    # Use `argparse` to parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Absolute path of directory.", type=str)
    parser.add_argument("--case", help="[L/U] Change file name to Lowercase or Uppercase. (Default L)", type=str)
    parser.add_argument("--thread", help="Thread per files. Default 200", type=int)
    parser.add_argument("--max-thread", help="Maximum thread limit. Default 20", type=int)
    args = parser.parse_args()

    # Get path
    PATH = args.path.replace("\\", "/")
    PATH = PATH + "/" if PATH[-1] != "/" else PATH
    if os.path.isdir(PATH) is False:
        parser.error("[-] DIRECTORY DOES NOT EXISTS. ")
        sys.exit(1)

    # Select mode (True = Lower / False = Upper)
    if args.case is None:
        MODE = True
    elif ["L", "l", ""].count(args.case) != 0:
        MODE = True
    elif ["U", "u"].count(args.case) != 0:
        MODE = False
    else:
        parser.error("Invalid choice in --case (choose from 'L', 'l', 'U', 'u')")
        sys.exit(1)

    # THREAD_PER_FILE
    THREAD_PER_FILE = int(args.thread) if args.thread is not None else 200

    # MAX_THREAD
    MAX_THREAD = int(args.max_thread) if args.max_thread is not None else 20

    # Final confirmation
    file_count = len([f for f in os.listdir(PATH) if os.path.isfile(PATH + f)])
    print("[*] Working in [%s]" % PATH)
    print("[*] %d threads per file" % THREAD_PER_FILE)
    print("[*] Max %d threads" % MAX_THREAD)
    print("[*] Directory has %d files, %d folders. " % (file_count, len(os.listdir(PATH)) - file_count))
    print("[*] Changing file names to %s." % ("Lowercase" if MODE else "Uppercase"))
    if ["Y", "y", ""].count(input("[*] Continue? [Y/n] : ")) == 0:
        print("[-] Abort.")
        sys.exit(1)

    """
    2. Start job
    """
    # Start task
    start_time = time.time()
    print("[+] Starting task : %s" % time.strftime("%H:%M:%S", time.localtime(time.time())))

    print("[-] Listing directory. Please wait... ")
    recursive_threading(PATH, MODE)
    print("[-] Directory listing done : %d directories in %.2f seconds" % (len(dirs), time.time() - start_time))
    print_status()

    # Start threads
    try:
        for thread in variables.thread_list:
            while threading.active_count() > MAX_THREAD and not EMERGENCY_KILL:
                continue
            thread.start()
    except KeyboardInterrupt:
        EMERGENCY_KILL = True

    # Wait for threads to finish
    for thread in variables.thread_list:
        try:
            thread.join()
        except RuntimeError:    # If thread is not started
            pass

    if EMERGENCY_KILL:
        print("[-] Abort.")
        variables.file_count_all = 0    # For quitting log function
        sys.exit(1)

    # Change directory names when threads are all finished.
    for __path in dirs:
        try:
            os.rename(__path,
                      "/".join(__path.split('/')[:-2]) + "/" +
                      ((__path.split('/')[-2].lower()) if MODE else __path.split('/')[-2].upper())
                      )
        except FileExistsError:  # Renamed File / Folder name is as original.
            pass
        except PermissionError:  # TODO CATCH THIS BUG
            print("!!!!!!!!!!!!!!!")
            print("[-] BUG FROM FILE : %s" % __path)
            print("!!!!!!!!!!!!!!!")

    """
    3. End task
    """
    print("[+] Finished task : %s" % time.strftime("%H:%M:%S", time.localtime(time.time())))
    print("[*] %d FILES, %d DIRECTORIES IN %lf seconds." %
          (variables.file_count_all, len(dirs), time.time() - start_time))

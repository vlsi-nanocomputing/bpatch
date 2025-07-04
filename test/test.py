import os
import re
import sys


# path to testin and testout folders
TESTIN_FOLDER = "testin"
TESTOUT_FOLDER = "testout"

# set verbosity level
"""
with VERBOSE = 0, only errors and final result is printed
with VERBOSE = 1, also test start and end for each folder is printed
with VERBOSE = 2, also a message for each patch is printed
"""
VERBOSE = 1
# set option for bpatch
OPTIONS = "-d"


def extract_last_decimal(s):
    """
    Extract the last decimal number from a string.

    :param s: string to extract the last decimal number from
    :type s: str
    :return: the last decimal number found in the string, or None if no number is found
    :rtype: int
    """

    # find all numbers in the string
    numbers = re.findall(r'\d+', s)
    # restur last number if exists
    return numbers[-1]if numbers else None

def test_bpatch():
    """
    run the bpatch test on all directories in TESTIN_FOLDER.

    :return: error count
    :rtype: int
    """

    error_count = 0
    tested_patches = 0

    # check if testin and testout folders exist, otherwise create them
    if not os.path.exists(TESTIN_FOLDER):
        os.makedirs(TESTIN_FOLDER)
    if not os.path.exists(TESTOUT_FOLDER):
        os.makedirs(TESTOUT_FOLDER)

    # iterate over all directories in TESTIN_FOLDER
    for d in os.listdir(TESTIN_FOLDER):
        if VERBOSE >= 1:
            print(f'### Start test folder {d} ###')

        # create output directory if not exists or clean previous results
        if not os.path.exists(f"{TESTOUT_FOLDER}/{d}"):
            os.makedirs(f"{TESTOUT_FOLDER}/{d}")
        else:
            for file in os.listdir(f"{TESTOUT_FOLDER}/{d}"):
                os.remove(os.path.join(f"{TESTOUT_FOLDER}/{d}", file))

        # create firmware dict with fw name and version
        f = {}
        for fw in os.listdir(f"{TESTIN_FOLDER}/{d}"):
            # extract the version from the firmware name
            version = extract_last_decimal(fw)
            # check if the version is not None and not in the dict
            if version is None:
                print(f'Error: cannot find version in {fw}', file=sys.stderr)
                exit(-1)
            if version in f:
                print(f'Error: duplicate version {version} in {fw}', file=sys.stderr)
                exit(-1)
            # add fw in dict
            f[version] = fw

        # sort the versions
        versions = sorted(f.keys())

        for i in range(len(versions) - 1):
            if VERBOSE >= 2:
                print(f'Start test bpatch for {d}/{f[versions[i]]} and {d}/{f[versions[i+1]]}')
            # run bpatch
            if os.system(f'python3 ../bpatch.py encode {TESTIN_FOLDER}/{d}/{f[versions[i]]} {TESTIN_FOLDER}/{d}/{f[versions[i+1]]} {TESTOUT_FOLDER}/{d}/p_{versions[i+1]}.bin {OPTIONS} -v > /dev/null') != 0:
                print(f'Error while running bpatch for {d}/{f[versions[i]]} and {d}/{f[versions[i+1]]}', file=sys.stderr)
                error_count += 1
            else:
                if VERBOSE >= 2:
                    print('Test OK')
            tested_patches += 1

        if VERBOSE >= 1:
            print(f'### End test folder {d} ###\n\n')

    print(f"Test finished\nTotal patches tested: {tested_patches}\nErrors found: {error_count}\n")

    return error_count


if __name__ == '__main__':
    exit(test_bpatch())
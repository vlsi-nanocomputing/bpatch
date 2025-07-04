import matplotlib.pyplot as plt
import os

from test import extract_last_decimal, TESTOUT_FOLDER, TESTIN_FOLDER

# exit if TESTOUT_FOLDER does not exist
if not os.path.exists(TESTOUT_FOLDER):
    exit(0)

# iterate over all directories in TESTOUT_FOLDER
for d in os.listdir(TESTOUT_FOLDER):
    # create patch dict with patch name and version
    p = {}

    for patch in os.listdir(f"{TESTOUT_FOLDER}/{d}"):
        # extract the version from the firmware name
        version = extract_last_decimal(patch)
        # add patch in dict
        p[version] = os.path.getsize(f"{TESTOUT_FOLDER}/{d}/{patch}") / 1024

    # create firmware dict with fw name and version
    fw = {}

    for f in os.listdir(f"{TESTIN_FOLDER}/{d}"):
        # extract the version from the firmware name
        version = extract_last_decimal(f)
        # add patch in dict
        fw[version] = os.path.getsize(f"{TESTIN_FOLDER}/{d}/{f}") / 1024

    # sort the patch and firmware dicts by version
    versions = sorted(p.keys())
    p_sizes = [p[v] for v in versions]
    f_sizes = [fw[v] for v in versions]

    # plot the firmwares and patch sizes
    plt.figure()
    plt.title(f"{d}")
    plt.xlabel('Firmware Version')
    plt.ylabel('KBytes')
    plt.grid()
    plt.plot(versions, p_sizes, 'o-', label='Patch Size')
    plt.plot(versions, f_sizes, 'o-', label='Firmware Size')
    plt.legend()
    plt.show()
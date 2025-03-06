import os
import subprocess
import re
import sys

def extract_last_decimal(s):
    # find all numbers in the string
    numbers = re.findall(r'\d+', s)
    # restur last number if exists
    return numbers[-1]if numbers else None

def test_bpatch():
    error_count = 0

    for d in os.listdir():
        if d.startswith('f'):
            print(f'### Start test folder {d} ###')
            # create output directory if not exists
            if not os.path.exists(d + '/testout'):
                os.makedirs(d + '/testout')
            # create firmware dict with fw name and version
            f = {}
            for el in os.listdir(d):
                # check if the file is a binary file
                if el.endswith('.bin'):
                    version = extract_last_decimal(el)
                    # check if the version is not None and not in the dict
                    if version is None:
                        print(f'Error: cannot find version in {el}', file=sys.stderr)
                        exit(-1)
                    if version in f:
                        print(f'Error: duplicate version {version} in {el}', file=sys.stderr)
                        exit(-1)
                    # add fw in dict
                    f[version] = el

            for version in sorted(f.keys())[:-1]:
                print(f'Start test bpatch for {d}/{f[version]} and {d}/{f[str(int(version) + 1)]}')
                # run bpatch
                if os.system(f'python3 ../bpatch.py encode {d}/{f[version]} {d}/{f[str(int(version) + 1)]} {d}/testout/patch_{int(version) + 1}.bin -v -R {d}/testout/report_{int(version) + 1}.csv> /dev/null') != 0:
                    print(f'Error while running bpatch for {d}/{f[version]} and {d}/{f[str(int(version) + 1)]}', file=sys.stderr)
                    error_count += 1
                else:
                    print('Test OK')

            print(f'### End test folder {d} ###\n\n')

    return error_count


if __name__ == '__main__':
    exit(test_bpatch())
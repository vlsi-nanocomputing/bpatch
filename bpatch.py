#!/usr/bin/python3

"""bpatch.py - Bit Patch Firmware Tool"""

__author__ = "Andrea De Simone and Fabrizio Riente"
__copyright__ = "Copyright 2025, Politecnico di Torino"
__license__ = "Apache-2.0"
__version__ = "1.0.1"
__maintainer__ = "Andrea De Simone"
__email__ = "andrea.desimone@polito.it, fabrizio.riente@polito.it"


import binascii
import re
from math import log, ceil
import sys
import os
from path_bpatch import path_patch_exec

# enable custom header
header_custom = False
# from custom_header.header_sbsfu import header_fw_size, header_patch_size, header_lines, write_header_custom

""" Custom Header definition start """
if not header_custom:
    header_fw_size    = 0   # size of the custom header in the firmware in bytes
    header_patch_size = 0   # size of the custom header in the patch in bits
    header_lines      = 0   # number of lines of the custom header in the patch

    write_header_custom = None  # custom header disabled
"""
# function to build header for txt patch
def write_header_custom(bin_txt):
    """"""Read the header from "new_fw_header.tmp" and write the custom header in the patch in binary
    
    :param bin_txt: string with the binary patch
    :return: string with the binary patch with the header added
    """"""
    pass
"""

""" Custom Header definition end """

def decode_diff(diff_str):
    """
    private function to decode "diff" instruction

    :param diff_str: string to decode
    :return: left and right part of the string
    """
    left, rigth = re.split('[acd]', diff_str)
    if ',' in left:
        l = left.split(',')
    else:
        l = [left]

    if ',' in rigth:
        r = rigth.split(',')
    else:
        r = [rigth]

    return l, r


def copy(start, end, patch, max_nbd, max_nbc, nc):
    """
    private function to handle COPY instruction

    :param start: nbd
    :param end: nbc
    :param patch: string with the patch
    :param max_nbd: max number of bits for nbd
    :param max_nbc: max number of bits for nbc
    :param nc: number of copy
    :return: updated values of patch, max_nbd, max_nbc, nc
    """
    patch += '0'
    patch += ','
    patch += str(start)
    patch += ','
    patch += str(end)
    patch += '\n'

    if start > 0:
        nbd = ceil(log(start + 1, 2))
        if nbd > max_nbd:
            max_nbd = nbd

    nbc = ceil(log(end + 1, 2))
    if nbc > max_nbc:
        max_nbc = nbc

    nc += 1

    return patch, max_nbd, max_nbc, nc


def add(nba, f_add, patch, max_nba, na, b_to_a):
    """
    private function to handle ADD instruction

    :param nba: number of bytes to add
    :param f_add: file with the bytes to add
    :param patch: string with the patch
    :param max_nba: max number of bits for nba
    :param na: number of add
    :param b_to_a: number of bytes to add
    :return: updated values of patch, max_nba, na, b_to_a
    """
    patch += '1'
    patch += ','
    patch += str(nba)
    for i in range(nba):
        patch += ','
        patch += f_add.readline()[:-1]

    patch += '\n'

    nbta = ceil(log(nba + 1, 2))
    if nbta > max_nba:
        max_nba = nbta

    b_to_a += nba
    na += 1

    return patch, max_nba, na, b_to_a

def encode_fw(path_change, path_add, endfile, fw_size, custom_header_size=0, path_report_txt='', path_report_csv=''):
    """
    Function to encode the firmware and generate the patch

    :param path_change: path to the diff log with the changes
    :param path_add: path to the diff log with the added bytes
    :param endfile: size of the old firmware in bytes (if present a custom header, the size is the firmware size - header size)
    :param fw_size: size of the new firmware in bytes
    :param custom_header_size: size of the custom header in the patch in bits
    :param path_report_txt: path to the report in txt format (if empty the report is not generated)
    :param path_report_csv: path to the report in csv format (if empty the report is not generated)
    :return: WNBD, WNBC, WNBA, b (size of the patch in bits), new_patch (patch in txt format)
    """
    # number of bits in the file
    b_to_a = 0
    # position in the old firmware
    oldpos = 1
    # position in the new firmware
    pos = 1

    # max value
    max_nbd = 0
    max_nbc = 0
    max_nba = 0
    # number of copy
    nc = 0
    # number of add
    na = 0

    # patch txt
    patch = ''
    # header txt
    # header = ''

    # apply header function if it is present
    # if write_header:
    #     header = write_header(path_header, patch)

    # generate patch
    with open(path_change, "r") as f:
        with open(path_add, "r") as f_add:
            for line in f:
                # decode line
                l, r = decode_diff(line[:-1])

                # copy until the next change
                if (int(l[0]) - oldpos) > 0 or 'a' in line:
                    if 'a' in line:
                        patch, max_nbd, max_nbc, nc = copy(oldpos - pos, int(l[0]) - oldpos + 1, patch, max_nbd,
                                                           max_nbc, nc)
                        pos = int(l[0]) + 1
                    else:
                        patch, max_nbd, max_nbc, nc = copy(oldpos - pos, int(l[0]) - oldpos, patch, max_nbd, max_nbc,
                                                           nc)
                        pos = int(l[0])

                if ('a' in line) or ('c' in line):
                    # add the new data
                    if len(r) == 2:
                        patch, max_nba, na, b_to_a = add(int(r[1]) - int(r[0]) + 1, f_add, patch, max_nba, na, b_to_a)
                    else:
                        patch, max_nba, na, b_to_a = add(1, f_add, patch, max_nba, na, b_to_a)

                oldpos = int(l[-1]) + 1

    patch, max_nbd, max_nbc, nc = copy(oldpos - pos, endfile - oldpos + 1, patch, max_nbd, max_nbc, nc)

    WNBD = ceil(log(max_nbd + 1, 2))
    WNBC = ceil(log(max_nbc + 1, 2))
    WNBA = ceil(log(max_nba + 1, 2))

    # check double CPY and add empty ADD and count bits
    prev_op = ''
    double_op = 0
    new_patch = ''
    nbc = 0
    nbd = 0
    nba = 0
    for i, p in enumerate(patch.split('\n')):
        # check if the row is an operation
        if p:
            f = p.split(',')
            # count operations
            if f[0] == '0':
                if int(f[1]) > 0:
                    nbd += ceil(log(int(f[1]) + 1, 2))

                nbc += ceil(log(int(f[2]) + 1, 2))

            elif f[0] == '1':
                nba += ceil(log(int(f[1]) + 1, 2))
            # check double CPY
            if p[0] == prev_op:
                double_op += 1
                new_patch += '1,0\n'
                # print(f"Double {p[0]} at line {i + 1}")
                na += 1
            prev_op = p[0]
        new_patch += p + '\n'

    b = (nbd + nbc + nba) + nc * (WNBD + WNBC) + na * WNBA + b_to_a * 8
    # header size
    b += 48
    if custom_header_size:
        # header fw size
        b += custom_header_size

    # patch size
    patch_size = ceil(b / 8)
    # overhead
    if b_to_a:
        over_nbd = (nc * WNBD + nbd) / (b_to_a * 8) * 100
        over_nbc = (nc * WNBC + nbc) / (b_to_a * 8) * 100
        over_nba = (na * WNBA + nba) / (b_to_a * 8) * 100
        over_tot = ((nbd + nbc + nba) + nc * (WNBD + WNBD) + na * WNBA) / (b_to_a * 8) * 100
    else:
        over_nbd = 0
        over_nbc = 0
        over_nba = 0
        over_tot = 0

    # write report
    if path_report_txt:
        with open(path_report_txt, "w") as f_r:
            f_r.write(f"Firmware size: {fw_size}\n")

            f_r.write(f"\nNumber of CPY: {nc}\n")
            f_r.write(f"Number of ADD: {na}\n")
            f_r.write(f"Number of new bytes: {b_to_a}\n")
            # f_r.write(f"Double CPY instructions: {double_op}\n")

            f_r.write(f"\nNumber of bits Patch: {b}\n")
            f_r.write(f"Number of bytes Patch: {patch_size}\n")

            f_r.write(f"NBD overhead {nc * WNBD + nbd} bits, {over_nbd: .2f} %\n")
            f_r.write(f"NBC overhead {nc * WNBC + nbc} bits, {over_nbc: .2f} %\n")
            f_r.write(f"NBA overhead {na * WNBA + nba} bits, {over_nba: .2f} %\n")
            f_r.write(f"TOT overhead {(nbd + nbc + nba) + nc * (WNBD + WNBC) + na * WNBA} bits, {over_tot: .2f} %\n")

            f_r.write(f"\nNumber of Patch fragments: {ceil(patch_size / 112)}\n")
            f_r.write(f"Number of Firmware fragments: {ceil(fw_size / 112)}\n")

            f_r.write(f"\nMax nbd: {max_nbd}\n")
            f_r.write(f"MNBD: {WNBD}\n")
            f_r.write(f"Mean bit nbd: {nbd / nc + WNBC: .2f}\n")

            f_r.write(f"\nMax nbc: {max_nbc}\n")
            f_r.write(f"MNBC: {WNBC}\n")
            f_r.write(f"Mean bit nbc: {nbc / nc + WNBC: .2f}\n")

            f_r.write(f"\nMax nba: {max_nba}\n")
            f_r.write(f"MNBA: {WNBA}\n")
            f_r.write(f"Mean bit nba: {nba / nc + WNBA: .2f}\n")

    # write csv report
    if path_report_csv:
        with open(path_report_csv, "w") as f_r:
            f_r.write('fw_size, patch_sz, CPY, ADD, NB, OVER_NBD, OVER_NBC, OVER_NBA, OVER_TOT\n')

            f_r.write(f'{fw_size},')
            f_r.write(f'{patch_size},')
            f_r.write(f'{nc},')
            f_r.write(f'{na},')
            f_r.write(f'{b_to_a},')
            f_r.write(f'{over_nbd},')
            f_r.write(f'{over_nbc},')
            f_r.write(f'{over_nba},')
            f_r.write(f'{over_tot},')

    return WNBD, WNBC, WNBA, b, new_patch


def decode_py(fin_path, fp_path, fout_path):
    """
    Function to apply the txt patch to the firmware converted in hex

    :param fin_path: path to the firmware (in hex format)
    :param fp_path: path to the patch (in txt format)
    :param fout_path: path to the patched firmware (in hex format)
    """
    fin = open(fin_path, "r")
    fp = open(fp_path, "r")
    fout = open(fout_path, "w")

    for line in fp:
        f = line[:-1].split(',')
        if f[0] == '0':
            # jump to the position
            if int(f[1]) > 0:
                fin.read(int(f[1]) * 3)
            # copy the bytes
            b = fin.read(int(f[2]) * 3)
            fout.write(str(b))

        else:
            # add the bytes
            if int(f[1]) > 0:
                for i in range(int(f[1])):
                    fout.write(format(int(f[2 + i], 16), '02X') + '\n')

    fin.close()
    fp.close()
    fout.close()


def write_binary_patch(patch_txt, path_patch_bin, WNBD, WNBC, WNBA, endpatch, write_header=None, path_patch_bin_txt=""):
    """
    Function to write the patch in binary format

    :param patch_txt: patch in txt format
    :param path_patch_bin: path to write the binary patch in binary file
    :param WNBD: width required for NBD
    :param WNBC: width required for NBC
    :param WNBA: width required for NBA
    :param endpatch: size of the patch in bits
    :param write_header: function to write the header in the patch
    :param path_patch_bin_txt: path to write the binary patch in txt format

    """
    bin_txt = ""

    # write the size of the patch
    bin_txt += format(endpatch & 0xFF, f'08b')
    bin_txt += format((endpatch >> 8) & 0xFF, f'08b')
    bin_txt += format((endpatch >> 16) & 0xFF, f'08b')
    bin_txt += '\n'
    # write WNBD, WNBC, WNBA
    bin_txt += format(WNBD, f'08b')
    bin_txt += '\n'
    bin_txt += format(WNBC, f'08b')
    bin_txt += '\n'
    bin_txt += format(WNBA, f'08b')
    bin_txt += '\n'
    bin_txt += '\n'
    # write header
    if write_header:
        bin_txt = write_header(bin_txt)

    cnt_cmd = 0
    cnt_nbd = 0
    cnt_nbc = 0
    cnt_nba = 0
    cnt_b_to_a = 0
    # write patch
    for line in patch_txt.split('\n'):
        f = line.split(',')
        if f[0] == '0':
            bin_txt += '0,'
            cnt_cmd += 1

            if int(f[1]) == 0:
                bin_txt += '0' * WNBD + ','
                cnt_nbd += WNBD

            else:
                nbd = ceil(log(int(f[1]) + 1, 2))

                bin_txt += format(nbd, f'0{WNBD}b') + ' '
                cnt_nbd += WNBD

                bin_txt += format(int(f[1]), f'0{nbd}b') + ','
                cnt_nbd += nbd

            nbc = ceil(log(int(f[2]) + 1, 2))

            bin_txt += format(nbc, f'0{WNBC}b') + ' '
            cnt_nbc += WNBC

            bin_txt += format(int(f[2]), f'0{nbc}b') + '\n'
            cnt_nbc += nbc

        elif f[0] == '1':
            bin_txt += '1,'
            cnt_cmd += 1

            if int(f[1]) == 0:
                bin_txt += '0' * WNBA
                cnt_nbd += WNBA

            else:
                nba = ceil(log(int(f[1]) + 1, 2))

                bin_txt += format(nba, f'0{WNBA}b') + ' '
                cnt_nba += WNBA

                bin_txt += format(int(f[1]), f'0{nba}b')
                cnt_nba += nba

                for i in range(int(f[1])):
                    bin_txt += ',' + format(int(f[2 + i], 16), f'08b')
                    cnt_b_to_a += 8

            bin_txt += '\n'

    # write binary patch in txt format
    if path_patch_bin_txt:
        f_bin_txt = open(path_patch_bin_txt, "w")
        f_bin_txt.write(bin_txt)
        f_bin_txt.close()

    f_bin = open(path_patch_bin, "wb")

    # eliminate cmd bits
    lines = bin_txt.split('\n')
    # copy header
    bin_txt = '\n'.join(lines[:4 + header_lines])
    # copy the rest
    for line in lines[5 + header_lines:]:
        bin_txt += line[2:] + '\n'


    bin_txt = bin_txt.replace('\n', '').replace(' ', '').replace(',', '')
    if len(bin_txt) % 8 != 0:
        bin_txt += '0' * (8 - len(bin_txt) % 8)
    f_bin.write(bytes([int(bin_txt[i:i+8], 2) for i in range(0, len(bin_txt), 8)]))

    f_bin.close()


def read_binary_patch(path_patch_txt, path_patch_txt_new, header_lines = 0):
    """
    Read the binary patch in txt format and re-write the patch in txt format

    :param path_patch_txt: path to the binary patch in txt format
    :param path_patch_txt_new: path to write the new txt patch in txt format
    :param header_lines: number of lines of the custom header in the patch
    """

    f_bin_txt = open(path_patch_txt, "r")
    f_txt = open(path_patch_txt_new, "w")

    size = int(f_bin_txt.readline()[:-1], 2)
    WNBD = int(f_bin_txt.readline()[:-1], 2)
    WNBC = int(f_bin_txt.readline()[:-1], 2)
    WNBA = int(f_bin_txt.readline()[:-1], 2)

    f_bin_txt.readline()

    for i in range(header_lines):
        f_bin_txt.readline()

    for line in f_bin_txt:
        f = line[:-1].split(',')
        # print(f)
        if f[0] == '0':
            f_txt.write('0,')

            ff = f[1].split(' ')
            if len(ff[0]) != WNBD:
                print('error wnbd')

            if int(ff[0], 2) == 0:
                f_txt.write(f'0,')
            else:
                nbd = int(ff[0], 2)

                if len(ff[1]) != nbd:
                    print('error nbd')

                f_txt.write(f"{int(ff[1], 2)},")

            ff = f[2].split(' ')
            if len(ff[0]) != WNBC:
                print('error wnbc')

            nbc = int(ff[0], 2)

            if len(ff[1]) != nbc:
                print('error nbc')

            f_txt.write(f"{int(ff[1], 2)}\n")

        elif f[0] == '1':
            f_txt.write('1,')

            ff = f[1].split(' ')
            if len(ff[0]) != WNBA:
                print('error wnba')

            nba = int(ff[0], 2)

            if nba > 0:
                if len(ff[1]) != nba:
                    print('error nba')

                b_to_a = int(ff[1], 2)
                f_txt.write(f"{b_to_a}")

                for i in range(b_to_a):
                    if len(f[2 + i]) != 8:
                        print('error b to a')

                    f_txt.write(f",{int(f[2 + i], 2):02X}")
            else:
                f_txt.write('0')

            f_txt.write('\n')


def generate_hex_fw(filename, fw_path, fw_header_path, header_fw_size):
    """
    private function to read the binary file and write the firmware in hex format

    :param filename: path to read the binary file
    :param fw_path: path to write the firmware in hex format
    :param fw_header_path: path to write the header in hex format
    :param header_fw_size: size of the custom header in the firmware in bytes
    """
    # Read the binary file
    frags = []
    try:
        with open(filename, "rb") as f:
            while bytes_str := f.read(1):
                frags.extend([binascii.hexlify(bytes_str).decode()])
    except FileNotFoundError as e:
        print("File not found, error: ", e)
        exit(1)

    # CSV new fw file writting --------------------------------------------------------------------------------------------------------
    if header_fw_size:
        with open(fw_header_path, "w", newline='') as f:
            f.write("\n".join(frags[:header_fw_size]).upper() + '\n')

    with open(fw_path, "w", newline='') as f:
        f.write("\n".join(frags[header_fw_size:]).upper() + '\n')


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ['encode', 'decode', 'help']:
        print("Usage: python3 patch.py [OPTION]")
        print("Options:"
              "\n\t-encode: generate the patch"
              "\n\t-decode: apply the patch")
        exit()

    # encode function
    if sys.argv[1] == 'encode':
        # check the number of arguments
        if len(sys.argv) < 5:
            print("Usage: python3 patch.py encode OLD_FW NEW_FW PATCH [OPTIONS]")
            print("Options:"
                  "\n\t-d         : use diff with option minimal to reduce the patch size"
                  "\n\t-v         : verify che correctness of the patch"
                  "\n\t-V         : verify che correctness of the txt patch"
                  "\n\t-t FILENAME: write the patch in txt format"
                  "\n\t-b FILENAME: write the patch in binary format"
                  "\n\t-r FILENAME: write the report in txt format"
                  "\n\t-R FILENAME: write the report in csv format")
            exit()

        # decode arguments
        old_fw = sys.argv[2]
        new_fw = sys.argv[3]
        p = sys.argv[4]

        # default values
        verify = False
        verify_py = False
        minimal = False
        path_patch_txt = ""
        path_patch_bin_txt = ""
        path_report_txt = ""
        path_report_csv = ""
        # check the optional arguments
        try:
            for i in range(5, len(sys.argv)):
                # verify the correctness of the patch
                if sys.argv[i] == '-v':
                    verify = True
                # verify the flow of the patch generation
                elif sys.argv[i] == '-V':
                    verify_py = True
                # write the patch in txt format
                elif sys.argv[i] == '-t':
                    path_patch_txt = sys.argv[i + 1]
                # write the patch in binary format
                elif sys.argv[i] == '-b':
                    path_patch_bin_txt = sys.argv[i + 1]
                elif sys.argv[i] == '-r':
                    path_report_txt = sys.argv[i + 1]
                elif sys.argv[i] == '-R':
                    path_report_csv = sys.argv[i + 1]
                elif sys.argv[i] == '-d':
                    minimal = True


        except IndexError:
            print("Error during parsing arguments")

        to_remove = []

        if verify_py:
            if not path_report_txt:
                path_patch_txt = "patch_txt.tmp"
                to_remove.append(path_patch_txt)
            if not path_patch_bin_txt:
                path_patch_bin_txt = "patch_bin_txt.tmp"
                to_remove.append(path_patch_bin_txt)

        # read the binary files
        generate_hex_fw(old_fw, "old_fw.tmp", "old_fw_header.tmp", header_fw_size)
        generate_hex_fw(new_fw, "new_fw.tmp", "new_fw_header.tmp", header_fw_size)
        to_remove.extend(["old_fw.tmp", "new_fw.tmp"])
        if header_custom:
            to_remove.extend(["old_fw_header.tmp", "new_fw_header.tmp"])
        # compute diff
        if minimal:
            os.system("diff -d old_fw.tmp new_fw.tmp > diff.tmp")
        else:
            os.system("diff old_fw.tmp new_fw.tmp > diff.tmp")
        os.system("grep -E '^[0-9,]+[acd][0-9,]+$' diff.tmp > diff_c.tmp")
        os.system("grep '^>' diff.tmp | sed 's/^> //' > diff_a.tmp")

        to_remove.extend(["diff.tmp", "diff_c.tmp", "diff_a.tmp"])

        # patch generation
        size_old_fw = os.path.getsize(old_fw)
        size_new_fw = os.path.getsize(new_fw)

        # encode function
        wnbd, wnbc, wnba, patch_size, patch = encode_fw("diff_c.tmp", "diff_a.tmp", size_old_fw - header_fw_size, size_new_fw, custom_header_size=header_patch_size, path_report_txt=path_report_txt, path_report_csv=path_report_csv)

        # write the txt patch
        if path_patch_txt:
            with open(path_patch_txt, "w") as f:
                f.write(patch[:-1])

        # write binary patch
        write_binary_patch(patch, p, wnbd, wnbc, wnba, patch_size, write_header_custom, path_patch_bin_txt)

        if verify_py:
            # verify the correctness of the txt patch
            decode_py("old_fw.tmp", path_patch_txt, "patched_fw.tmp")

            # check if the patched firmware is equal to the new firmware
            if os.system(f"diff patched_fw.tmp new_fw.tmp"):
                print("The txt patch is not correct")
                exit(2)
            else:
                print("The txt patch is correct")

            # verify the correctness of the binary patch
            read_binary_patch(path_patch_bin_txt, "patch_txt_new.tmp", header_lines)
            to_remove.append("patch_txt_new.tmp")

            # check if the patched firmware is equal to the new firmware
            if os.system(f"diff {path_patch_txt} patch_txt_new.tmp"):
                print("The bin patch is not correct")
                exit(3)
            else:
                print("The bin patch is correct")

        # check the correctness of the patch
        if verify or verify_py:
            # generate the patched firmware
            os.system(f"{path_patch_exec} {old_fw} {p} patched_fw.tmp {1016} {1024} > /dev/null")
            to_remove.append("patched_fw.tmp")
            # check if the patched firmware is equal to the new firmware
            if os.system(f"diff patched_fw.tmp {new_fw}"):
                print("The patch is not correct")
                exit(1)
            else:
                print("The patch is correct")

        # remove temporary files
        for tmp in to_remove:
            os.remove(tmp)

        exit(0)

    # decode function
    elif sys.argv[1] == 'decode':
        # check the number of arguments
        if len(sys.argv) < 5:
            print("Usage: python3 patch.py decode OLD_FW PATCH NEW_FW [OPTIONS]")
            print("Options:"
                  "\n\t-v     : enable verbose mode"
                  "\n\t-r SIZE: set the read buffer size"
                  "\n\t-p SIZE: set the patch buffer size")
            exit()

        old_fw = sys.argv[2]
        p = sys.argv[3]
        new_fw = sys.argv[4]

        # default values
        verbose =  '> /dev/null'
        read_buffer = 1016
        patch_buffer = 1024
        # check the optional arguments
        try:
            for i in range(5, len(sys.argv)):
                # enable verbose mode
                if sys.argv[i] == '-v':
                    verbose = ''
                # set the read buffer size
                elif sys.argv[i] == '-r':
                    read_buffer = int(sys.argv[i + 1])
                # set the patch buffer size
                elif sys.argv[i] == '-p':
                    patch_buffer = int(sys.argv[i + 1])

        except IndexError:
            print("Error during parsing arguments")

        # apply the patch
        exit(os.system(f"{path_patch_exec} {old_fw} {p} {new_fw} {read_buffer} {patch_buffer} {verbose}"))

    # help function
    elif sys.argv[1] == 'help':
        print("Usage: python3 patch.py [OPTION]")
        print("\n\tOptions:"
              "\n\t-encode: generate the patch"
              "\n\t\t Usage: python3 patch.py encode OLD_FW NEW_FW PATCH [OPTIONS]")
        print("\n\t\tOptions:"
              "\n\t\t-v         : verify che correctness of the patch"
              "\n\t\t-V         : verify che correctness of the txt patch"
              "\n\t\t-t FILENAME: write the patch in txt format"
              "\n\t\t-b FILENAME: write the patch in binary format"
              "\n\t\t-r FILENAME: write the report in txt format"
              "\n\t\t-R FILENAME: write the report in csv format")

        print("\n\t-decode: apply the patch"
              "\n\t\t Usage: python3 patch.py decode OLD_FW PATCH NEW_FW [OPTIONS]")
        print("\n\t\tOptions:"
              "\n\t\t-v     : enable verbose mode"
              "\n\t\t-r SIZE: set the read buffer size"
              "\n\t\t-p SIZE: set the patch buffer size")

        print("\n\t-help")
        exit()

    else:
        print("Usage: python3 patch.py [OPTION]")
        print("Options:"
              "\n\t-encode: generate the patch"
              "\n\t-decode: apply the patch"
              "\n\t-help: help")
        exit()

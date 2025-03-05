# custom header size
header_fw_size    = 512 # size of the custom header in the firmware in bytes
header_patch_size = 800 # size of the custom header in the patch in bits
header_lines      = 4   # number of lines of the custom header in the patch

# function to build header for txt patch
def write_header_custom(bin_txt):
    """
    Read the header from "new_fw_header.tmp" and write the custom header in the patch in binary

    :param bin_txt: string with the binary patch
    :return: string with the binary patch with the header added
    """
    with open("new_fw_header.tmp", "r") as f_header:
        # read header
        header = f_header.read().split('\n')
        # add FWsize
        FWsize = "".join(header[8:12]) + '\n'
        # add TAG
        TAG = "".join(header[20:52]) + '\n'
        # add SIGN
        SIGN = "".join(header[128:192]) + '\n'

        bin_txt += format(int(FWsize, 16), f'032b') + '\n'
        bin_txt += format(int(TAG, 16), f'0256b') + '\n'
        bin_txt += format(int(SIGN, 16), f'0512b') + '\n\n'

    return bin_txt

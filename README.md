# bpatch 
[![DOI](https://zenodo.org/badge/978161231.svg)](https://doi.org/10.5281/zenodo.15348169)
[![arXiv](https://img.shields.io/static/v1?label=arXiv&message=1905.02477&color=informational&style=flat-square)](https://arxiv.org/abs/2505.13764)


## Overview
Application to generate a patch between two binary files without compression. The differential algorithm is based on the bash command DIFF.
It is available a Python application to encode (generate the patch) and decode (rebuild the new firmware) options. The decode is based on a C code.

## Prerequisite
The application works only on Linux operating system

## How to configure
It is available a script to build and configure the Python script

    sh configure.sh

## How to use
- encode
    
        python3 patch.py encode OLD_FW NEW_FW PATCH [OPTIONS]
    
    options:

        -d         : use diff with option minimal to reduce the patch size"
		-v         : verify che correctness of the patch
		-V         : verify che correctness of the txt patch
		-t FILENAME: write the patch in txt format
		-b FILENAME: write the patch in binary format
		-r FILENAME: write the report in txt format
		-R FILENAME: write the report in csv format

- decode

        python3 patch.py decode OLD_FW PATCH NEW_FW [OPTIONS]

    options:

        -v     : enable verbose mode
		-r SIZE: set the read buffer size
		-p SIZE: set the patch buffer size


## bpatch structure
Are present two instructions: **CPY** to copy bytes from the old firmware, **ADD** to add new bytes. To save the bit to indicate the command in final patch it is assumed that the first instruction is a **CPY** then there is an alternance between **ADD** and **CPY**

- **Patch txt**
    
    Textual patch generated in Python, it is a temporary patch 
    
    CPY format:
            
            0, <nbd>, <nbc>
    - 0: indicate CPY instruction
    - nbd: number of bytes to jump in old firmware
    - nbc: number of bytes to copy from old firmware in new firmware

    ADD format:
            
            1, <nba>, <hex[B1]>, <hex[B2]>, ... <hex[Bnba]>
    - 1: indicate ADD instruction
    - nba: number of bytes to add in new firmware
    - Bn: new bytes in hex format

    example of **Patch txt**

        0,0,8
        1,2,30,2C​
        0,2,6
        1,2,30,2C​
        0,2,2​
        1,13,BA,11,61,AD,9A,AD,58,2B,65,61,...​
        0,17,1​
        1,3,19,14,38
        [...]

- **Patch bin txt**

    It is the previous patch converted in binary and saved in textual format

    Header format:

        <bin[endpatch]>
        <bin[WNBD]>
        <bin[WNBC]>
        <bin[WNBA]>

    - endpatch: number of bits of the patch
    - WNBD: define the number of bit reserved to \<wnbd\> field
    - WNBC: define the number of bit reserved to \<wnbc\> field
    - WNBA: define the number of bit reserved to \<wnba\> field
    
    [Optional custum fw header]

    *It is possible to define a methodology to built the firmware header*
    
    CPY format:

        0, <bin[wnbd]> <bin[nbd]>, <bin[wnbc]> <bin[nbc]>

    - 0: indicate CPY instruction
    - wnbd: number of bit reserved to next \<nbd\> field
    - nbd: number of bytes to jump in old firmware (if 0 this field is not present)
    - wnbc: number of bit reserved to next \<nbc\> field
    - nbc: number of bytes to copy from old firmware in new firmware
    
    ADD format:
            
            1, <bin[wnba]> <bin[nba]>, <bin[B1]>, <bin[B2]>, ... <bin[Bnba]>
    
    - 1: indicate ADD instruction
    - wnba: number of bit reserved to next \<nba\> field
    - nba: number of bytes to add in new firmware (if 0 this field is not present)
    - Bn: new bytes in bin format
    
    example of **Patch bin txt**:

        100000111100010000001101
        00000011
        00000100
        00000100
        
        [Custom fw header]

        0,000,0100 1000
        1,0010 10,00110000,00101100
        0,010 10,0011 110​
        1,0010 10,00110000,00101100​
        0,010 10,0010 10​
        1,0100 1101,10111010,00010001,01100001,10101101,10011010,...​
        0,101 10001,0001 1​
        1,0010 11,00011001,00010100,00111000
        [...]

- **Final patch**

    The final patch is generated by the previous patch with the first bit of each instruction line eliminated (instruction bit). The patch is written in binary format



## Custom header

It is possible to define a methodology to generate an header for the firmware.

In *bpatch.py*:

- set *header_fw_size*: size of the custom header in the firmware in bytes
- set *header_patch_size*: size of the custom header in the patch in bits
- set *header_lines*: number of lines of the custom header in the patch
- define *write_header_custom*: function that read the header of the firmware and produce the lines required to re-built the header in **Patch bin txt**

In *bpatch.h*

- enable MACRO *HEADER_PATCH*

In *bpatch.c*

- define *write_header*: function to re-built header for correspondent bytes from the patch

In the repository is present as example a custum header for SBSFU expansion for STM32, detailed [here](https://www.st.com/en/embedded-software/x-cube-sbsfu.html)


## CSV report format

Fields of CSV report:

- **fw_size**: size of new firmware in bytes
- **patch_sz**: size of patch in bytes
- **CPY**: number of CPY instructions
- **ADD**: number of ADD instructions
- **NB**: number of new bytes added
- **OVER_NBD**: number of bit necessary to NBD field compared to the total number new bytes in percentage
- **OVER_NBC**: number of bit necessary to NBC field compared to the total number new bytes in percentage
- **OVER_NBA**: number of bit necessary to NBA field compared to the total number new bytes in percentage
- **OVER_TOT**: number of bit necessary to NBD, NBC, NBA fields compared to the total number new bytes in percentage


## Test environment

It is present a **test** folder when the application can be tested and assessed on firmwares

## Reference

Since **bpatch** is the result of an academic effort, we kindly ask that you acknowledge it by citing the following publication:
```bibtex
@misc{bpatch,
      title={Incremental Firmware Update Over-the-Air for Low-Power IoT Devices over LoRaWAN}, 
      author={Andrea De Simone and Giovanna Turvani and Fabrizio Riente},
      year={2025},
      eprint={2505.13764},
      archivePrefix={arXiv},
      primaryClass={eess.SY},
      url={https://arxiv.org/abs/2505.13764}, 
}
```

## Versioning
We use M.m.p as a verdioning system.

- M = Major
- m = minor
- p = patch

There is always back compatibility among minor version and patches only fix possible bugs
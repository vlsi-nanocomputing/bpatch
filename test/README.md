# Test Environment

This section describes the environment used to test patch generation and application.  
It includes two scripts:

- `test.py`: Automatically generates and verifies binary patches.  
- `plot.py`: Visualizes patch sizes over firmware versions.

## How to Use

### 1. Patch Generation and Verification (`test.py`)

Place one or more folders inside the `testin` directory. Each folder should contain the binaries to be tested.  
Binaries must include the firmware version in their filename, e.g., `f_v1.bin`, `f_v2.bin`, etc.  
The script extracts the version number from the last numeric part of the filename.

For each folder in `testin`:

- Patches will be generated and verified.
- Output will be saved in a corresponding folder in `testout`.
- Patches will be named `p_n.bin`, where `n` indicates the version number of the new firmware.

### 2. Patch Size Plotting (`plot.py`)

This script generates a plot showing the size of each patch relative to its firmware version.

**Requirements**:

- Patches must be generated using `test.py`.
- The `matplotlib` Python library is required.

For each folder in `testout`, a separate plot will be generated.

import matplotlib.pyplot as plt
import numpy as np
from math import ceil
import os

from test import extract_last_decimal

for d in os.listdir():
    if d.startswith('f'):
        r = {}

        fw_size = np.array([])
        patch_size = np.array([])
        n_frag_patch = np.array([])
        n_frag_fw = np.array([])
        ovh_nbd = np.array([])
        ovh_nbc = np.array([])
        ovh_nba = np.array([])
        ovh_tot = np.array([])
        n_nba = np.array([])

        if os.path.exists(d + '/testout'):
            for report in os.listdir(d + '/testout'):
                if report.startswith('report'):
                    # extract version
                    version = extract_last_decimal(report)
                    # add to dictionary
                    r[version] = report

        # check if there are report in the folder
        if r:
            fw_versions = sorted(r.keys())
            for v in fw_versions:
                with open(d + '/testout/' + r[v], 'r') as f:
                    f.readline()
                    fields = f.readline().split(',')

                    fw_size         = np.append(fw_size, int(fields[0]))
                    patch_size      = np.append(patch_size, int(fields[1]))
                    n_frag_patch    = np.append(n_frag_patch, ceil(int(fields[1])/112))
                    n_frag_fw       = np.append(n_frag_fw, ceil(int(fields[0])/112))
                    n_nba           = np.append(n_nba, int(fields[4]))
                    ovh_nbd         = np.append(ovh_nbd, float(fields[5]))
                    ovh_nbc         = np.append(ovh_nbc, float(fields[6]))
                    ovh_nba         = np.append(ovh_nba, float(fields[7]))
                    ovh_tot         = np.append(ovh_tot, float(fields[8]))

            # fig, axs = plt.subplots(2, 2, figsize=(15, 10))
            fig, axs = plt.subplots(2, 2)
            fig.suptitle(f'Statistics folder: {d}')

            axs[0, 0].set_title('Compression')
            axs[0, 0].plot(fw_versions, patch_size / fw_size * 100)
            axs[0, 0].set_xlabel('FW version')
            axs[0, 0].set_ylabel('Patch compression [%]')
            axs[0, 0].grid()

            axs[0, 1].set_title('New Bytes')
            axs[0, 1].plot(fw_versions, np.ceil(n_nba / 1024))
            axs[0, 1].set_xlabel('FW version')
            axs[0, 1].set_ylabel('kB')
            axs[0, 1].grid()

            axs[1, 0].set_title('Overhead')
            axs[1, 0].plot(fw_versions, ovh_nbd, fw_versions, ovh_nbc, fw_versions, ovh_nba, fw_versions, ovh_tot)
            axs[1, 0].set_xlabel('FW version')
            axs[1, 0].set_ylabel('Overhead respect new bytes [%]')
            axs[1, 0].legend(['nbd', 'nbc', 'nba', 'total'])
            axs[1, 0].grid()

            width = 0.3  # the width of the bars
            species = np.arange(len(fw_versions))

            p1 = axs[1, 1].bar(species - width / 2, n_frag_fw, width, label='FW')
            axs[1, 1].bar_label(p1, label_type='edge')
            p2 = axs[1, 1].bar(species + width / 2, n_frag_patch, width, label='Patch')
            axs[1, 1].bar_label(p2, label_type='edge')

            axs[1, 1].set_title('Number of fragment comparison')
            axs[1, 1].set_xticks(species)
            axs[1, 1].set_xticklabels(fw_versions)
            axs[1, 1].legend()

            plt.tight_layout()
            plt.show()

exit()
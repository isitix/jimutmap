import os

if not os.path.exists('cvat_export'):
    os.makedirs('cvat_export')

import shutil
import glob

source_dir = 'satellite_images/*/'
destination_dir = 'cvat_export'

for subdir in glob.glob(source_dir):
    for file in glob.glob(subdir + '*.jpg'):  # Assuming images are .png files. Change format if needed.
        shutil.copy(file, destination_dir)

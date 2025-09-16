import os
import math
import tempfile
import shutil
import nibabel as nib
import numpy as np
from totalsegmentator.python_api import totalsegmentator
from mosamatic2.core.tasks.task import Task
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.utils import load_dicom

LOG = LogManager()

TOTAL_SEGMENTATOR_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), 'total_segmentator_output')
TOTAL_SEGMENTATOR_TASK = 'total'
Z_DELTA_OFFSETS = {
    'vertebrae_L3': 0.333,
    'vertebrae_T4': 0.5,
}


class SelectSliceFromScansTask(Task):
    INPUTS = ['scans']
    PARAMS = ['vertebra']

    def __init__(self, inputs, params, output, overwrite):
        super(SelectSliceFromScansTask, self).__init__(inputs, params, output, overwrite)

    def load_scan_dirs(self):
        scan_dirs = []
        for d in os.listdir(self.input('scans')):
            scan_dir = os.path.join(self.input('scans'), d)
            if os.path.isdir(scan_dir):
                scan_dirs.append(scan_dir)
        return scan_dirs
    
    def extract_masks(self, scan_dir):
        os.makedirs(TOTAL_SEGMENTATOR_OUTPUT_DIR, exist_ok=True)
        totalsegmentator(input=scan_dir, output=TOTAL_SEGMENTATOR_OUTPUT_DIR, fast=True)
        # os.system(f'TotalSegmentator -i {scan_dir} -o {TOTAL_SEGMENTATOR_OUTPUT_DIR} --fast')

    def delete_total_segmentator_output(self):
        if os.path.exists(TOTAL_SEGMENTATOR_OUTPUT_DIR):
            shutil.rmtree(TOTAL_SEGMENTATOR_OUTPUT_DIR)

    def get_z_delta_offset_for_mask(self, mask_name):
        if mask_name not in Z_DELTA_OFFSETS.keys():
            return None
        return Z_DELTA_OFFSETS[mask_name]

    def find_slice(self, scan_dir, vertebra):
        if vertebra == 'L3':
            vertebral_level = 'vertebrae_L3'
        elif vertebra == 'T4':
            vertebral_level = 'vertebrae_T4'
        else:
            raise RuntimeError(f'Unknown vertbra {vertebra}. Options are "L3" and "T4"')
        # Find Z-positions DICOM images
        z_positions = {}
        for f in os.listdir(scan_dir):
            f_path = os.path.join(scan_dir, f)
            p = load_dicom(f_path, stop_before_pixels=True)
            if p is not None:
                z_positions[p.ImagePositionPatient[2]] = f_path
        # Find Z-position L3 image
        mask_file = os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, f'{vertebral_level}.nii.gz')
        mask_obj = nib.load(mask_file)
        mask = mask_obj.get_fdata()
        affine_transform = mask_obj.affine
        indexes = np.array(np.where(mask == 1))
        index_min = indexes.min(axis=1)
        index_max = indexes.max(axis=1)
        world_min = nib.affines.apply_affine(affine_transform, index_min)
        world_max = nib.affines.apply_affine(affine_transform, index_max)
        z_direction = affine_transform[:3, 2][2]
        z_sign = math.copysign(1, z_direction)
        z_delta_offset = self.get_z_delta_offset_for_mask(vertebral_level)
        if z_delta_offset is None:
            return None
        z_delta = 0.333 * abs(world_max[2] - world_min[2]) # This needs to be vertebra-specific perhaps
        z_l3 = world_max[2] - z_sign * z_delta
        # Find closest L3 image in DICOM set
        positions = sorted(z_positions.keys())
        closest_file = None
        for z1, z2 in zip(positions[:-1], positions[1:]):
            if min(z1, z2) <= z_l3 <= max(z1, z2):
                closest_z = min(z_positions.keys(), key=lambda z: abs(z - z_l3))
                closest_file = z_positions[closest_z]
                LOG.info(f'Closest image: {closest_file}')
                break
        return closest_file

    def run(self):
        scan_dirs = self.load_scan_dirs()
        vertebra = self.param('vertebra')
        nr_steps = len(scan_dirs)
        for step in range(nr_steps):
            scan_dir = scan_dirs[step]
            scan_name = os.path.split(scan_dir)[1]
            self.extract_masks(scan_dir)
            file_path = self.find_slice(scan_dir, vertebra)
            if file_path is not None:
                extension = '' if file_path.endswith('.dcm') else '.dcm'
                target_file_path = os.path.join(self.output(), vertebra + '_' + scan_name + extension)
                shutil.copyfile(file_path, target_file_path)
            else:
                LOG.error(f'Could not find slice for vertebral level: {vertebra}')
            self.delete_total_segmentator_output()
            self.set_progress(step, nr_steps)
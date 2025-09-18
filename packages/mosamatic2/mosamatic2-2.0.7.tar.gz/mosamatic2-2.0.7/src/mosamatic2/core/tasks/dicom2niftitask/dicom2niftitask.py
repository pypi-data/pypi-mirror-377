import os
import dicom2nifti
from mosamatic2.core.tasks.task import Task
from mosamatic2.core.managers.logmanager import LogManager

LOG = LogManager()


class Dicom2NiftiTask(Task):
    INPUTS = ['images']
    PARAMS = []

    def __init__(self, inputs, params, output, overwrite):
        super(Dicom2NiftiTask, self).__init__(inputs, params, output, overwrite)

    def run(self):
        nifti_file_name = os.path.split(self.input('images'))[1] + '.nii.gz'
        LOG.info(f'Converting DICOM directory to {nifti_file_name}')
        dicom2nifti.dicom_series_to_nifti(
            self.input('images'),
            os.path.join(self.output(), nifti_file_name),
            reorient_nifti=True,
        )
        self.set_progress(0, 1)
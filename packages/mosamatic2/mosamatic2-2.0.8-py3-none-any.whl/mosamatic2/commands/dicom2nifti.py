import click

from mosamatic2.core.tasks import Dicom2NiftiTask


@click.command(help='Converts DICOM series to NIFTI')
@click.option(
    '--images', 
    required=True, 
    type=click.Path(exists=True), 
    help='Directory with images',
)
@click.option(
    '--output', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite [true|false]'
)
def dicom2nifti(images, output, overwrite):
    """
    Converts single DICOM series (scan) to NIFTI
    
    Parameters
    ----------
    --images : str
        Directory with DICOM images of a single series

    --output : str
        Path to output directory

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    task = Dicom2NiftiTask(
        inputs={'images': images},
        params=None,
        output=output,
        overwrite=overwrite,
    )
    task.run()
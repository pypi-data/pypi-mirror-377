import datetime
from pathlib import Path
from typing import cast

import dateutil.parser
import numpy as np

import pydicom
try:
    # pydicom > 3
    from pydicom import pixels
except ImportError:
    # pydicom < 3
    import pydicom.pixel_data_handlers as pixels  # type: ignore

from pydicom.errors import InvalidDicomError
from pydicom.multival import MultiValue

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, TabPane, TabbedContent
import typer

from textual_file_viewer.dicom_tree import DicomTree
from textual_file_viewer.image_viewer import ImageViewer

SUPPORTED_PHOTOMETRIC_INTERPRETATIONS = {'MONOCHROME1', 'MONOCHROME2', 'YBR_FULL_422', 'RGB'}

# Use in snapshot testing to disable clock in header
SHOW_CLOCK = True

app = typer.Typer(add_completion=False, no_args_is_help=True)


def create_top_left_text(dataset: pydicom.Dataset) -> list[str]:
    return [
        str(dataset.PatientName),
        str(dataset.PatientID),
        dateutil.parser.parse(dataset.PatientBirthDate).strftime("%d-%b-%Y"),
        str(dataset.StudyDescription),
        str(dataset.SeriesDescription),
    ]


def create_top_right_text(dataset: pydicom.Dataset) -> list[str]:
    study_time = datetime.datetime.strptime(dataset.StudyTime, "%H%M%S")
    return [
        str(dataset.InstitutionName),
        str(dataset.ManufacturerModelName),
        f'{dateutil.parser.parse(dataset.StudyDate).strftime("%d-%b-%Y")} {study_time.strftime("%H:%M:%S")}']


def create_bottom_left_text(dataset: pydicom.Dataset) -> list[str]:
    return [
        f'ST: {dataset.get("SliceThickness", 0.0)} mm, SL: {dataset.get("SliceLocation", 0.0):.3f}',
        str(dataset.Modality),
        f'Series: {dataset.SeriesNumber}',
    ]


def create_bottom_right_text(dataset: pydicom.Dataset) -> list[str]:
    return [f'{dataset.Rows} x {dataset.Columns}',
            f'{dataset.PixelSpacing[0]:.3f} mm x {dataset.PixelSpacing[1]:.3f} mm', ]


class DicomViewer(Static):
    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        with TabbedContent(id='dicom_viewer', initial='tab_tags'):
            with TabPane('Image', id='tab_image'):
                yield ImageViewer()
            with TabPane('Tags', id='tab_tags'):
                yield DicomTree(id='dicom_tree')

    def load_dicom(self, filename: Path) -> None:
        try:
            dataset = cast(pydicom.Dataset, pydicom.dcmread(filename))
        except InvalidDicomError:
            return

        self.query_one('#tab_image', TabPane).disabled = False

        self.query_one(DicomTree).set_dataset(dataset)

        if 'PhotometricInterpretation' not in dataset:
            self.notify(title='Unable to show image.',
                        message='DICOM dataset has no "PhotometricInterpretation" tag.')
            self.query_one(TabbedContent).active = "tab_tags"
            self.query_one('#tab_image', TabPane).disabled = True
            return

        if dataset.PhotometricInterpretation not in SUPPORTED_PHOTOMETRIC_INTERPRETATIONS:
            self.notify(message=f'Only {" ".join(SUPPORTED_PHOTOMETRIC_INTERPRETATIONS)} are supported',
                        title='No image view',
                        severity='warning')
            self.query_one(TabbedContent).active = "tab_tags"
            self.query_one('#tab_image', TabPane).disabled = True
            return

        np_array = self._get_image_data(dataset)

        image_viewer = self.query_one(ImageViewer)

        try:
            image_viewer.text_top_left = '\n'.join(create_top_left_text(dataset))
        except (ValueError, AttributeError):
            pass

        try:
            image_viewer.text_top_right = '\n'.join(create_top_right_text(dataset))
        except (ValueError, AttributeError):
            pass

        try:
            image_viewer.text_bottom_left = '\n'.join(create_bottom_left_text(dataset))
        except (ValueError, AttributeError):
            pass

        try:
            image_viewer.text_bottom_right = '\n'.join(create_bottom_right_text(dataset))
        except (ValueError, AttributeError):
            pass

        rgb: bool = dataset.PhotometricInterpretation in ('YBR_FULL_422', 'RGB')
        self.query_one(ImageViewer).set_array(np_array, rgb=rgb)

    @staticmethod
    def _get_image_data(dataset: pydicom.Dataset) -> np.ndarray:
        np_array = dataset.pixel_array

        match dataset.PhotometricInterpretation:
            case 'MONOCHROME1':
                # minimum is white, maximum is black
                # (https://dicom.innolitics.com/ciods/ct-image/image-pixel/00280004)
                np_array = pixels.apply_voi_lut(np_array, dataset)
                minimum, maximum = np.amin(np_array), np.amax(np_array)
                # noinspection PyUnresolvedReferences
                np_array = (maximum - np_array) * 255.0 / (maximum - minimum)
            case 'MONOCHROME2':
                center, width = dataset.WindowCenter, dataset.WindowWidth
                if isinstance(center, MultiValue):
                    center = center[0]
                if isinstance(width, MultiValue):
                    width = width[0]
                minimum, maximum = center - width / 2, center + width / 2

                np_array = np_array.astype(np.float64)
                np_array[np_array < minimum] = minimum
                np_array[np_array > maximum] = maximum
                np_array = (np_array - minimum) * 255.0 / (maximum - minimum)
            case 'YBR_FULL_422':
                np_array = pixels.convert_color_space(np_array, 'YBR_FULL', 'RGB')
            case 'RGB':
                np_array = np_array.astype(np.uint8)
            case _:
                pass
        return np_array


class DicomApp(App):
    CSS_PATH = 'file_viewer.tcss'

    def __init__(self, filename: Path) -> None:
        super().__init__()
        self.filename = filename

    def compose(self) -> ComposeResult:
        # yield Header(show_clock=SHOW_CLOCK)
        with Vertical(id='dicom_viewer'):
            yield DicomViewer()
        # yield Footer()

    async def on_mount(self) -> None:
        self.call_after_refresh(self.update)

    async def update(self) -> None:
        self.query_one(DicomViewer).load_dicom(self.filename)
        self.title = f'Dicom: {self.filename}'


@app.command()
def view(filename: Path) -> None:
    DicomApp(filename).run()


if __name__ == "__main__":
    app()

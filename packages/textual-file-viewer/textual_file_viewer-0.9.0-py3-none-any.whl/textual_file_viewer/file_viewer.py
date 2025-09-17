from pathlib import Path
from typing import Any

import pandas
import typer
from pydicom.errors import InvalidDicomError
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Header, Footer, ContentSwitcher
from textual_sortable_datatable.sortable_data_table import SortableDataTable

from textual_file_viewer.dicom_viewer import DicomViewer
from textual_file_viewer.mhd_nifti_viewer import MhdNiftiViewer


# Use in snapshot testing to disable clock in header
SHOW_CLOCK = True


app = typer.Typer(add_completion=False, no_args_is_help=True)


class Loading:
    def __init__(self, widget: Widget) -> None:
        self.widget = widget

    def __enter__(self) -> None:
        self.widget.loading = True

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.widget.loading = False


class FileViewer(App):
    CSS_PATH = 'file_viewer.tcss'

    BINDINGS = [
        Binding('f5', 'refresh', 'Refresh'),
    ]

    def __init__(self, filename: Path) -> None:
        super().__init__()
        self.filename = filename

    def compose(self) -> ComposeResult:
        yield Header(show_clock=SHOW_CLOCK)
        with ContentSwitcher(initial='dicom_viewer', id='content_switcher'):
            with Container(id='mhd_nifti_viewer'):
                yield MhdNiftiViewer()
            with Container(id='dicom_viewer'):
                yield DicomViewer()
            with Container(id='dataframe_table'):
                yield SortableDataTable()
        yield Footer()

    async def on_mount(self) -> None:
        self.call_after_refresh(self.update)

    async def action_refresh(self) -> None:
        self.notify('Reloading...', severity='information')
        await self.update()

    async def update(self) -> None:
        suffixes = ''.join(self.filename.suffixes)
        match suffixes:
            case '.xlsx':
                # noinspection PyTypeChecker
                self.query_one(SortableDataTable).set_data(pandas.read_excel(self.filename))
                self.query_one('#content_switcher', ContentSwitcher).current = 'dataframe_table'
                self.title = f'Excel: {self.filename}'  # type: ignore
                return
            case '.csv':
                # noinspection PyTypeChecker
                self.query_one(SortableDataTable).set_data(pandas.read_csv(self.filename))
                self.query_one('#content_switcher', ContentSwitcher).current = 'dataframe_table'
                self.title = f'CSV: {self.filename}'  # type: ignore
                return
            case '.mha' | '.mhd' | '.nii' | '.nii.gz':
                self.query_one(MhdNiftiViewer).load_image(self.filename)
                self.query_one('#content_switcher', ContentSwitcher).current = 'mhd_nifti_viewer'
                self.title = f'MetaImage/Nifti: {self.filename}'
                return
            case _:
                try:
                    self.query_one(DicomViewer).load_dicom(self.filename)
                    self.query_one('#content_switcher', ContentSwitcher).current = 'dicom_viewer'
                    self.title = f'Dicom: {self.filename}'
                    return
                except InvalidDicomError:
                    pass

        raise RuntimeError('Could not determine file type.')


@app.command()
def view(filename: Path) -> None:
    FileViewer(filename).run()


if __name__ == "__main__":
    app()

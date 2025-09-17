from pathlib import Path

import SimpleITK as sitk
from rich.markdown import Markdown
from textual.app import ComposeResult, App
from textual.containers import ScrollableContainer, Vertical
from textual.widgets import Static, Label, TabPane, TabbedContent, Header, Footer
import typer

from textual_file_viewer.image_viewer import ImageViewer

# Use in snapshot testing to disable clock in header
SHOW_CLOCK = True

app = typer.Typer(add_completion=False, no_args_is_help=True)


class MhdNiftiViewer(Static):
    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        with TabbedContent(id='image_viewer'):
            with TabPane('Image', id='tab_image'):
                yield ImageViewer()
            with TabPane('Tags', id='tab_tags'):
                yield ScrollableContainer(Label(id='image_tags'))

    def load_image(self, filename: Path) -> None:
        dataset = sitk.ReadImage(filename)
        self.query_one(ImageViewer).set_array(sitk.GetArrayFromImage(dataset))

        markdown = ['|Key|Value|', '|--|--|']
        for k in dataset.GetMetaDataKeys():  # type: ignore
            markdown.append(f'|{k}|{dataset.GetMetaData(k)}|')  # type: ignore

        self.query_one('#image_tags', Label).update(Markdown('\n'.join(markdown)))
        self.query_one('#image_viewer', TabbedContent).active = 'tab_image'


class MhdNiftiApp(App):
    CSS_PATH = 'file_viewer.tcss'

    def __init__(self, filename: Path) -> None:
        super().__init__()
        self.filename = filename

    def compose(self) -> ComposeResult:
        yield Header(show_clock=SHOW_CLOCK)
        with Vertical(id='dicom_viewer'):
            yield MhdNiftiViewer()
        yield Footer()

    async def on_mount(self) -> None:
        self.call_after_refresh(self.update)

    async def update(self) -> None:
        self.query_one(MhdNiftiViewer).load_image(self.filename)
        self.title = f'Dicom: {self.filename}'


@app.command()
def view(filename: Path) -> None:
    MhdNiftiApp(filename).run()


if __name__ == "__main__":
    app()

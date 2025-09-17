from pathlib import Path
from typing import Any, Final

import pydicom
import pydicom.dataset
import pydicom.dataelem
import pydicom.datadict
import pydicom.tag
import typer
from rich.style import Style
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Static, Tree
from textual.widgets.tree import TreeNode

PLACEHOLDER: Final[str] = '🔍'
KW_LENGTH: Final[int] = 70
INDENT_SIZE: Final[int] = 2
MAX_NUMBER_CHILDREN_AUTO_EXPAND: Final[int] = 10

app = typer.Typer(add_completion=False, no_args_is_help=True)


def _skip(element: pydicom.DataElement, filter_value: str) -> bool:
    try:
        keyword = pydicom.datadict.get_entry(element.tag)[2]
    except KeyError:
        keyword = None

    return keyword is not None and filter_value.casefold() not in keyword.casefold()


def _sequence(data_element: pydicom.DataElement, filter_value: str, parent_node: TreeNode, length: int = KW_LENGTH) -> None:
    num_elements = len(data_element.value)
    for index, sequence_element in enumerate(data_element):  # type: ignore
        if not isinstance(sequence_element, pydicom.dataset.Dataset):
            continue
        if index == 0 and num_elements > 1:
            keyword = pydicom.datadict.get_entry(data_element.tag)[2]
            parent_node.add_leaf(Text(f'ITEM {keyword} #{index}', style=Style(color='orange1', reverse=True)))

        for element in sequence_element:
            if element.VR == 'SQ':
                seq_node = parent_node.add(create_text(element, length=length - INDENT_SIZE), data=data_element)
                _sequence(element, filter_value=filter_value, parent_node=seq_node, length=length - INDENT_SIZE)
                if len(seq_node.children) <= MAX_NUMBER_CHILDREN_AUTO_EXPAND:
                    seq_node.expand()

            if _skip(element, filter_value):
                continue

            parent_node.add_leaf(create_text(element, length=length - INDENT_SIZE), element)
        if index < num_elements - 1:
            keyword = pydicom.datadict.get_entry(data_element.tag)[2]
            parent_node.add_leaf(Text(f'ITEM {keyword} #{index + 1}', style=Style(color='orange1', reverse=True)))


def create_text(data_element: pydicom.dataelem.DataElement, length: int = KW_LENGTH) -> Text:
    # noinspection PyTypeChecker
    tag: pydicom.tag.BaseTag = data_element.tag
    if tag.is_private:
        keyword = 'Unknown Tag & Data'
    else:
        keyword = pydicom.datadict.get_entry(tag)[2]

    text = Text()
    text.append(f'({tag.group:04X},{tag.element:04X})', style=Style(reverse=True))
    try:
        text.append(f' {keyword.ljust(length)[:length]}', style=Style(color='green'))
        text.append(f'{data_element.VR}',
                    style=Style(color='red', italic=True,
                                link='https://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html'))
        text.append(': ')
        text.append(f'{data_element.repval:75s}', style=Style(color='cyan'))
    except (TypeError, AttributeError, ValueError, KeyError):
        pass

    return text


class DicomTree(Static):
    DEFAULT_CSS = """
        Vertical {
        height: auto;
    }
    
    Horizontal {
        width: 1fr;
        height: auto;
    }
    """

    BINDINGS = [
        ('d', 'detail', 'Detail'),
        ('e', 'export', 'Export'),
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._dataset: pydicom.Dataset | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Input(placeholder=PLACEHOLDER, id='filter_input')
                yield Button(label='Filter', id='filter_button')
            tree: Tree = Tree(id='dicom_tree', label='Dicom')
            tree.show_root = False
            yield tree

    def set_dataset(self, dataset: pydicom.Dataset | None) -> None:
        self._dataset = dataset
        self._update_tree()

    @on(Input.Changed, '#filter_input')
    def filter_changed(self) -> None:
        value = self.query_one(Input)
        if value == PLACEHOLDER:
            return

        self._update_tree()

    def action_detail(self) -> None:
        ...

    def action_export(self) -> None:
        ...
        # # Provide export for Surface Segmentation Storage for now
        # if self._dataset.SOPClassUID != '1.2.840.10008.5.1.4.1.1.66.5':
        #     return

    def _update_tree(self) -> None:
        tree = self.query_one(Tree)
        tree.root.remove_children()

        if self._dataset is None:
            return

        filter_value: str = self.query_one(Input).value

        # noinspection PyUnresolvedReferences
        groups = {k.tag.group for k in self._dataset}
        nodes = {group: tree.root.add(Text(f'{group:04X}', 'reverse'), expand=group % 2 == 0) for group in sorted(groups)}

        for data_element in self._dataset:
            # noinspection PyTypeChecker
            tag: pydicom.tag.BaseTag = data_element.tag

            if tag.is_private:
                keyword = 'Unknown Tag & Data'
            else:
                keyword = pydicom.datadict.get_entry(tag)[2]

            if data_element.VR == 'SQ':
                _sequence(data_element, filter_value, parent_node=nodes[tag.group])
                continue

            if filter_value.casefold() not in keyword.casefold():
                continue

            nodes[tag.group].add_leaf(create_text(data_element), data=data_element)

        # Remove unpopulated nodes
        while True:
            for key, node in nodes.items():
                if len(node.children) == 0:
                    node.remove()
                    nodes.pop(key, None)
                    break
            else:
                break


def dummy_data_set() -> pydicom.Dataset:
    surface_1 = pydicom.Dataset()
    surface_1.SurfaceNumber = 1
    surface_1.RecommendedDisplayGrayscaleValue = 32768
    surface_1.RecommendedDisplayCIELabValue = [63659, 27249, 56955]

    surface_2 = pydicom.Dataset()
    surface_2.SurfaceNumber = 2
    surface_2.RecommendedDisplayGrayscaleValue = 32768
    surface_2.RecommendedDisplayCIELabValue = [21170, 53250, 5177]

    surface_3 = pydicom.Dataset()
    surface_3.SurfaceNumber = 3
    surface_3.RecommendedDisplayGrayscaleValue = 32768
    surface_3.RecommendedDisplayCIELabValue = [65535, 32786, 32768]

    surface_mesh = pydicom.Dataset()
    surface_mesh.NumberOfSurfaces = 3
    surface_mesh.SurfaceSequence = [surface_1, surface_2, surface_3]

    return surface_mesh


class DicomTreeApp(App):

    def __init__(self, filename: Path) -> None:
        super().__init__()
        self.filename = filename

    def compose(self) -> ComposeResult:
        yield DicomTree()

    async def on_mount(self) -> None:
        self.call_after_refresh(self.update)

    async def update(self) -> None:
        ds = pydicom.dcmread(self.filename)

        self.query_one(DicomTree).set_dataset(ds)
        self.title = f'Dicom: {self.filename}'


@app.command()
def view(filename: Path) -> None:
    DicomTreeApp(filename).run()


if __name__ == "__main__":
    app()

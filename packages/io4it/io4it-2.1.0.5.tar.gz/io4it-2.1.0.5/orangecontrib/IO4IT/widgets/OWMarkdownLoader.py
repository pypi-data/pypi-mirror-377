# ow_markdown_loader.py
import os
from pathlib import Path
import numpy as np

from AnyQt.QtWidgets import QLabel, QCheckBox
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.data import Domain, StringVariable, Table

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.IO4IT.utils import utils_md
else:
    from orangecontrib.IO4IT.utils import utils_md


class OWMarkdownLoader(widget.OWWidget):
    name = "Markdown Loader"
    description = "Charge tous les fichiers Markdown d’un dossier (récursif)"
    icon = "icons/load_md.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/load_md.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owmarkdownloader.ui")
    want_control_area = False
    priority = 1001

    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        md_files = Output("Markdown Files", Table)   # -> (file_path, content)
        data = Output("Data", Table)                 # passthrough de l'entrée

    def __init__(self):
        super().__init__()
        self.in_data = None
        self.input_dir = None
        self.recursive = True

        # UI minimal
        self.label = QLabel(self)
        self.checkbox = QCheckBox("Recherche récursive", self)
        self.checkbox.setChecked(True)
        self.checkbox.stateChanged.connect(self._on_recursive_toggled)

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.checkbox)
        self.warning("")

    def _on_recursive_toggled(self, _state):
        self.recursive = self.checkbox.isChecked()
        # Si on a déjà un dossier, on relance la production
        if self.input_dir:
            self._produce()

    @Inputs.data
    def set_data(self, in_data: Table | None):
        self.in_data = in_data
        self.warning("")

        # Toujours émettre le passthrough (même si None)
        self.Outputs.data.send(in_data)

        if not in_data:
            # Rien à charger côté MD : on émet une table vide sur Markdown Files
            self.Outputs.md_files.send(self._empty_md_table())
            return

        # Cherche la colonne 'input_dir' et récupère le premier dossier
        try:
            _ = in_data.domain["input_dir"]
            self.input_dir = str(in_data.get_column("input_dir")[0])
        except Exception:
            self.warning('"input_dir" (Text) est requis en entrée')
            self.Outputs.md_files.send(self._empty_md_table())
            return

        self.label.setText(f"Dossier : {self.input_dir}")
        self._produce()

    def _empty_md_table(self) -> Table:
        domain = Domain([], metas=[StringVariable("file_path"), StringVariable("content")])
        X = np.empty((0, 0))
        metas = np.empty((0, 2), dtype=object)
        return Table.from_numpy(domain, X, metas=metas)

    def _produce(self):
        base = Path(self.input_dir)
        patterns = ["*.md"]
        paths = []

        for patt in patterns:
            if self.recursive:
                paths.extend(base.rglob(patt))
            else:
                paths.extend(base.glob(patt))

        md_rows = []
        for p in sorted(set(paths)):
            try:
                md_rows.append([str(p), utils_md.try_read_text(p)])
            except Exception:
                md_rows.append([str(p), ""])

        # Construit la table pour "Markdown Files"
        domain = Domain([], metas=[StringVariable("file_path"), StringVariable("content")])
        X = np.empty((len(md_rows), 0))
        metas = np.array(md_rows, dtype=object) if md_rows else np.empty((0, 2), dtype=object)
        md_table = Table.from_numpy(domain, X, metas=metas)

        self.Outputs.md_files.send(md_table)
        # Le passthrough est déjà envoyé dans set_data ; on n'y retouche pas ici.

import os
import sys
from pathlib import Path
import numpy as np

from AnyQt.QtWidgets import QApplication
from AnyQt.QtCore import pyqtSignal
from Orange.data import Domain, StringVariable, Table, DiscreteVariable
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output

# Les imports sont adaptés pour correspondre au style de l'autre script
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.IO4IT.utils import utils_md
    from Orange.widgets.orangecontrib.AAIT.utils.thread_management import Thread
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
else:
    from orangecontrib.IO4IT.utils import utils_md
    from orangecontrib.AAIT.utils.thread_management import Thread
    from orangecontrib.AAIT.utils.import_uic import uic


class OWPdfType(widget.OWWidget):
    name = "PDF Type"
    description = "Checks if a PDF is text-based or image-based"
    category = "IO4IT"
    icon = "icons/check_pdf.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/check_pdf.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owpdftype.ui")
    want_control_area = False
    priority = 1002

    MAX_PAGES_TO_CHECK = 5

    # New signal to send single status updates from the thread
    status_update_signal = pyqtSignal(list)

    class Inputs:
        data = Input("PDF Table", Table)

    class Outputs:
        text_data = Output("Text PDF Table", Table)
        image_data = Output("Image PDF Table", Table)
        status_data = Output("Status Table", Table)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)

        self.data = None
        self.thread = None
        self.autorun = True
        self.result = None
        self.processed_statuses = []  # List to accumulate statuses
        self.post_initialized()

    @Inputs.data
    def set_data(self, in_data: Table | None):
        self.data = in_data
        if self.autorun:
            self.run()

    def run(self):
        if self.thread is not None and self.thread.isRunning():
            self.thread.safe_quit()

        if self.data is None:
            self.Outputs.text_data.send(None)
            self.Outputs.image_data.send(None)
            self.Outputs.status_data.send(None)
            return

        self.error("")
        try:
            self.data.domain["file_path"]
        except KeyError:
            self.error("You need a 'file_path' column in input data.")
            return

        if type(self.data.domain["file_path"]).__name__ != 'StringVariable':
            self.error("'file_path' column needs to be a Text.")
            return

        self.progressBarInit()
        self.processed_statuses = []  # Reset status list for a new run

        # Connect the internal status update signal to a new handler
        self.status_update_signal.connect(self.handle_status_update)

        # Pass the status update signal's emit method to the thread
        self.thread = Thread(self._process_pdfs, self.data, status_callback=self.status_update_signal.emit)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()

    def _process_pdfs(self, in_data: Table, progress_callback: callable, status_callback: callable) -> tuple[
        Table | None, Table | None]:
        paths = [str(x) for x in in_data.get_column("file_path")]
        text_indices = []
        image_indices = []

        total_files = len(paths)
        for i, p in enumerate(paths):
            progress_callback(i / total_files * 100)

            fp = Path(p)

            if not fp.exists() or fp.suffix.lower() != ".pdf":
                status_callback([p, "ko", "Invalid file or not a PDF"])
                continue

            try:
                is_text = utils_md.is_pdf_text_based(fp)
                if is_text:
                    text_indices.append(i)
                    status_callback([p, "ok", "Text-based PDF"])
                else:
                    image_indices.append(i)
                    status_callback([p, "ok", "Image-based PDF"])
            except Exception as e:
                status_callback([p, "ko", f"Error: {str(e)}"])

        progress_callback(100)

        # Create table for text PDFs
        if not text_indices:
            text_table = None
        else:
            text_table = in_data[text_indices]

        # Create table for image PDFs
        if not image_indices:
            image_table = None
        else:
            image_table = in_data[image_indices]

        # The final result is still returned here
        return text_table, image_table

    def handle_progress(self, value: float) -> None:
        self.progressBarSet(value)

    def handle_status_update(self, new_status: list):
        """
        Receives a single status update from the thread, appends it to the list,
        and sends a new, updated status table.
        """
        self.processed_statuses.append(new_status)

        # Correct Domain creation: move "file_path" to metas
        status_domain = Domain(
            [],  # The variables list should be empty
            metas=[
                StringVariable("file_path"),
                DiscreteVariable("status", values=["ok", "ko"]),
                StringVariable("details")
            ]
        )

        # Now, the data is correctly structured for the new domain
        status_table = Table.from_list(status_domain, self.processed_statuses)
        self.Outputs.status_data.send(status_table)

    def handle_result(self, result):
        try:
            text_table, image_table = result
            self.Outputs.text_data.send(text_table)
            self.Outputs.image_data.send(image_table)
        except Exception as e:
            print("An error occurred when sending out_data:", e)
            self.Outputs.text_data.send(None)
            self.Outputs.image_data.send(None)

    def handle_finish(self):
        print("PDF Type check finished")
        self.progressBarFinished()

    def post_initialized(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWPdfType()
    my_widget.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
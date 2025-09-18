from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QMessageBox,
    QDialog,
)
from PySide6.QtCore import Qt, QTimer
from .step import save_all_runs
from .style import Styled
from datetime import datetime
from PySide6.QtWebEngineWidgets import QWebEngineView
from .cache import ExternalLinkPage


def format_run(run):
    return "[" + run["timestamp"] + "] " + run["description"]


def now():
    return datetime.now().strftime("%y-%m-%d %H:%M")


class Results(Styled):
    def __init__(self, stacked_widget, runs, tag_descriptions):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.runs = runs
        self.tag_descriptions = tag_descriptions

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Top Row (Title & Buttons)
        self.top_container = QHBoxLayout()
        self.top_container.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Title label (Now aligned with buttons)
        self.title_label = QLabel("Analysis Outcome", self)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.top_container.addWidget(self.title_label)

        # Spacer between title and buttons
        self.top_container.addItem(
            QSpacerItem(
                10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )

        # Buttons (Square Icons with Short Hints & Mouse Hover Effect)
        self.variation_button = self.create_icon_button(
            "+", "#007bff", "New variation", self.create_variation
        )
        self.edit_button = self.create_icon_button(
            "✎", "#d39e00", "Edit", self.edit_run
        )
        self.delete_button = self.create_icon_button(
            "🗑", "#dc3545", "Delete", self.delete_run
        )
        self.close_button = self.create_icon_button(
            "❌", "#6c757d", "Close", self.switch_to_dashboard
        )

        self.top_container.addWidget(self.variation_button)
        self.top_container.addWidget(self.edit_button)
        self.top_container.addWidget(self.delete_button)
        self.top_container.addWidget(self.close_button)

        self.layout.addLayout(self.top_container)

        # Tags container (Left-aligned)
        self.tags_container = QHBoxLayout()
        self.tags_container.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(self.tags_container)

        # Results Viewer
        self.results_viewer = QWebEngineView(self)
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.results_viewer.setSizePolicy(size_policy)
        self.layout.addWidget(self.results_viewer, 1)

        self.setLayout(self.layout)

    def switch_to_dashboard(self):
        self.stacked_widget.slideToWidget(0)

    def showEvent(self, event):
        super().showEvent(event)

        # Update title and results
        if self.runs:
            run = self.runs[-1]
            self.title_label.setText(format_run(run))
            html_content = run.get("analysis", dict()).get(
                "return", "<p>No results available.</p>"
            )
            self.update_tags(run)  # Update tags
        else:
            html_content = "<p>No results available.</p>"

        # Use QTimer to ensure WebEngineView renders properly
        QTimer.singleShot(1, lambda: self.results_viewer.setHtml(html_content))
        self.results_viewer.show()

    def update_tags(self, run):
        """Refresh tags displayed below the title."""
        # Clear existing tags
        while self.tags_container.count():
            item = self.tags_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get tags
        tags = []
        if "dataset" in run:
            tags.append(run["dataset"]["module"])
        if "model" in run:
            tags.append(run["model"]["module"])
        if "analysis" in run:
            tags.append(run["analysis"]["module"])

        for tag in tags:
            self.tags_container.addWidget(
                self.create_tag_button(
                    f" {tag} ",
                    "Module info",
                    lambda checked, t=tag: self.show_tag_description(t),
                )
            )

    def show_tag_description(self, tag):
        dialog = QDialog()
        dialog.setWindowTitle("Module info")
        layout = QVBoxLayout(dialog)
        browser = QWebEngineView(self)
        browser.setFixedHeight(300)
        browser.setFixedWidth(800)
        # Example inline CSS and image
        html = self.tag_descriptions.get(tag, "No description available.")
        html = f"""
        <html>
        <head>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: #333;
                background-color: #fafafa;
                padding: 10px;
            }}
            h1 {{
                font-size: 18px;
                color: #0055aa;
            }}
            img {{
                max-width: 100%;
                border: 1px solid #ccc;
                border-radius: 4px;
            }}
        </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        browser.setPage(ExternalLinkPage(browser))
        browser.setHtml(html)

        layout.addWidget(browser)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        dialog.exec()

    def edit_run(self):
        if not self.runs:
            return
        reply = QMessageBox.question(
            self,
            "Edit?",
            f"Change modules and modify parameters of the analysis. "
            "However, this will also remove the results presented here. Consider creating a variation if you want to preserve current results.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.stacked_widget.slideToWidget(1)

    def create_variation(self):
        if not self.runs:
            return
        new_run = self.runs[-1].copy()
        new_run["status"] = "new"
        new_run["timestamp"] = now()
        self.runs.append(new_run)
        self.stacked_widget.slideToWidget(1)

    def delete_run(self):
        if not self.runs:
            return
        reply = QMessageBox.question(
            self,
            "Delete?",
            f"Will permanently remove this analysis and its outcome.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.runs.pop()
            self.stacked_widget.slideToWidget(0)
            save_all_runs("history.json", self.runs)

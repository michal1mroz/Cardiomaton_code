from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser

from src.frontend.ui_components.ui_factory import UIFactory


class AboutView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(50, 30, 50, 30)
        self.layout.setSpacing(20)

        self.title = UIFactory.create_label(self, "Cardiomaton", font_size=28)
        self.title.setObjectName("AboutTitle")

        self.subtitle = UIFactory.create_label(self, "Engineering Thesis 2025/2026", font_size=16)
        self.subtitle.setObjectName("Subtitle")

        self.authors = (
            "<b>Major:</b> Computer Science, The Faculty of Computer Science, AGH University of Krakow <br>"
            "<b>Supervisor:</b> Dr. ... <br>"
            "<b>Authors:</b> Gabriela Dumańska, Michał Mróz, Albert Pęciak, Maja Szczypka"
        )
        self.authors_label = UIFactory.create_label(self, self.authors, font_size=12, bold=False)
        self.authors_label.setObjectName("AuthorsLabel")

        self.description = QTextBrowser()
        self.description.setObjectName("AboutDescription")

        self.description.setHtml(f"""
            <div style="line-height: 150%;">
                <p><b>Cardiomaton</b>  is an interactive simulation tool designed to support medical education. 
                The project demonstrates the potential of Cellular Automata as a versatile tool 
                for modeling complex biological processes. The second motivation is to support students and 
                professionals seeking a clearer understanding of the cardiac conduction system, which is often
                considered abstract and difficult to visualize.  Ultimately, Cardiomaton is intended to serve as
                a bridge between abstract medical concepts and meaningful, experience-based learning.</p>
            </div>
        """)

        self.github_link = QLabel('<a href="https://github.com/michal1mroz/Cardiomaton_code" style="color: #5E83F2;'
                                  'text-decoration: none;">''View Source Code on GitHub</a>')
        self.github_link.setOpenExternalLinks(True)
        self.github_link.setObjectName("GithubLink")

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.subtitle)
        self.layout.addWidget(self.authors_label)
        self.layout.addStretch(1)
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.github_link)
        self.layout.addStretch(1)

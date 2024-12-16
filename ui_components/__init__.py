from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout
from qfluentwidgets import BodyLabel, TitleLabel, setFont, SimpleCardWidget
from core.translation import tr
from ui_lib import ScrollView



class ListView(QWidget):
    def __init__(self, tab_title: str | None):
        QWidget.__init__(self)

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title
        if tab_title:
            title = TitleLabel(text=tab_title)
            setFont(title, 24, QFont.Weight.Bold)
            self.layout.addWidget(title)

        self.layout.addWidget(SimpleCardWidget())

        # Scrollable Card Container
        self.scroll_container = ScrollView()
        self.layout.addWidget(self.scroll_container)

    def add_widget(self, w_: QWidget) -> None:
        self.scroll_container.add_widget(w_)

    def clear_widgets(self) -> None:
        self.scroll_container.clear_widgets()

    def get_widgets(self) -> list[QWidget]:
        return self.scroll_container.get_widgets()

    def widget_count(self) -> int:
        return self.scroll_container.widget_count()



class InfoPageWidget(BodyLabel):
    """This component displays info about VisiCopy"""
    def __init__(self):
        BodyLabel.__init__(self)
        # TODO put in strings resource file
        html: str = tr("""v1.0.0-beta<p>Under the hood, VisiCopy currently utilizes robocopy. In the future, support will be added for rsync and/or rclone."
In addition to the functionality that robocopy provides, VisiCopy introduces features such as multiprocessing & process management;
overall progress (rather than just the progress of a single file); and many other features.</p>
<p>I have developed VisiCopy as a free and open source software. I do not have any contributors yet; hence, this project takes 
a significant amount of time and dedication. You can help the development of this software through donations, code contributions, 
and sharing VisiCopy with others. Any support would be greatly appreciated.</p>
<p>Thank you for using VisiCopy!</p>

<h2>Support</h2>
<a href='https://www.artixios.com/software/visicopy.html'>Download Page</a>
<br/><a href='https://www.artixios.com/software/visicopy.html'>Documentation</a>

<br/><h2>Legal</h2>
License:  GPLv3 (Open Source)
<br/>© 2024 - VisiCopy Trademark

<br/><h2>Developer (Isaac M. Wolford)</h2>
<a href='https://www.artixios.com/about.html#dev_section'>About Me</a>
<br/><a href='https://pay.artixios.com/donate'>Donate Now</a>""")
        self.setWordWrap(True)
        self.setText(html)
        self.setOpenExternalLinks(True)


if __name__ == "__main__":
    pass

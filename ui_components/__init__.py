from qfluentwidgets import BodyLabel
from core.translation import tr


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

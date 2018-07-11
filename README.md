# auto-outline

A python program which takes pdf documents annotated in certain way and automatically generates a structured outline of their contents which can then be typeset using LaTex. Useful especially for academic texts. The program comes with a simple bash script to handle typesetting.

## Getting Started

### Prerequisites

The program was written in Python 3.5. Backwards compatibility has not yet been tested. 
It uses the following third party modules:
* [popplerqt5](https://github.com/wbsoft/python-poppler-qt5)
* [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro)
* [pylatexenc](https://github.com/phfaist/pylatexenc) 
* [pandas](https://pandas.pydata.org/)

Furthermore, in the bash script, [pdflatex](https://gist.github.com/rain1024/98dd5e2c6c8c28f9ea9d) is used for typesetting.

### Installing

Simply download the project to a location convenient to you. If you want to use run.sh, make sure to make that file executable, by navigating to its location and running
```
chmod u+x run.sh
```
## Author

**Paul Rehren**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details



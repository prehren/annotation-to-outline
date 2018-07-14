#
# Function for program annotation-to-outline. Responsible for extracting
# highlighted text, texboxes and underlines from annotated pdf.
#

import popplerqt5
import PyQt5
import sys
import re


def extractData(fileName, numFirstPage, numOfPages):
    # Extracts content and vertical positioning of highlighted and underlined text, as
    # well as textboxes from 'numOfPages' pages in file 'fileName', starting at page
    # number 'numFirstPage'

    doc = popplerqt5.Poppler.Document.load(fileName)  # load document
    highlightText, highlightTextPos = [], []
    underlineText, underlineTextPos = [], []
    textBoxText, textBoxTextPos = [], []

    for i in range(numFirstPage - 1, min(numOfPages, doc.numPages())):

        page = doc.page(i)  # page object
        annotations = page.annotations()  # annotations on page
        pWidth, pHeight = page.pageSize().width(), page.pageSize().height()

        for annotation in annotations:

            txt = ''

            if isinstance(annotation, popplerqt5.Poppler.TextAnnotation):
                # Extract contents and vertical positioning (top, center, bottom)
                # of textboxes

                txt = annotation.contents()
                textBoxText.append(txt)
                textBoxTextPos.append([i + 1, annotation.boundary().top() * pHeight,
                                       annotation.boundary().center().y() * pHeight,
                                       annotation.boundary().bottom() * pHeight])
                annotation.setContents('')

        for annotation in annotations:  # find all other annotations

            txt = ''

            if isinstance(annotation, popplerqt5.Poppler.HighlightAnnotation):
                # Extract contents and vertical positioning (top, center, bottom)
                # of highlighted and underlined text

                # List of quadrilaterals that describe the boundaries of every line
                # of highlighted or underlined text
                quads = annotation.highlightQuads()

                for quad in quads:

                    # Scaled boundaries of current line of highlighted or underlined text
                    boundaries = (quad.points[0].x() * pWidth,
                                  quad.points[0].y() * pHeight,
                                  quad.points[2].x() * pWidth,
                                  quad.points[2].y() * pHeight)
                    body = PyQt5.QtCore.QRectF()
                    body.setCoords(*boundaries)

                    # Extract text from current line
                    if re.match('\\.', str(page.text(body))[-1:]):
                        txt = txt + str(page.text(body))[:-1]
                    else:
                        txt = txt + str(page.text(body)) + ' '

                if annotation.highlightType() == 0:  # If annotation is a hightlight

                    highlightText.append(txt)
                    highlightTextPos.append([i + 1, quads[0].points[0].y() * pHeight,
                                             quads[-1].points[2].y() * pHeight])

                elif annotation.highlightType() == 2:  # If annotation is an underline

                    underlineText.append(txt)
                    underlineTextPos.append([i + 1, quads[0].points[0].y() * pHeight,
                                             quads[-1].points[2].y() * pHeight])

    # If no annotations and textboxes were found
    if not highlightText and not underlineText and not textBoxText:

        print('\nERROR: No annotations found in document\n')
        sys.exit()

    return highlightText, highlightTextPos, underlineText, underlineTextPos,\
        textBoxText, textBoxTextPos

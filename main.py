import sys
from functions import *


def main():

    fileName = sys.argv[1]  # input file name
    firstPage = int(sys.argv[2]) - 1  # number of the first page as numbered in input file
    outputFileName = sys.argv[3]  # output file name
    paperTitle = sys.argv[4]  # title
    author = sys.argv[5]  # author
    numFirstPage = int(sys.argv[6])  # number of the first page
    numOfPages = int(sys.argv[7])  # number of pages

    highlightText, highlightTextPos, underlineText, underlineTextPos,\
        textBoxText, textBoxTextPos = extract.extractData(fileName, numFirstPage, numOfPages)

    df = frame.frameData(highlightText, highlightTextPos, underlineText, underlineTextPos,
                         textBoxText, textBoxTextPos, firstPage, numFirstPage)
    df.loc[:, 'Page'] = df['Page'].astype('str')  # convert page column to string
    df.loc[:, 'Instructions'] = ''  # append instructions column
    df.loc[:, 'Type'] = ''  # append type column

    df = frame.dealWithBreaks(df)

    for item in df.index:
        ann = df['Annotation'][item]
        df.loc[item, 'Instructions'] = frame.extractInstructions(ann)
        df.loc[item, 'Title'] = frame.extractTitle(ann)
        df.loc[item, 'Type'] = frame.extractType(ann)

    defContents = latexify.latexifyDefinitions(df)
    otherContents = latexify.latexifyOtherAnnotations(df)
    titleContents = ("%s (%s)" % (paperTitle, author))

    write.writeToLatex(outputFileName, otherContents, defContents, titleContents)


if __name__ == "__main__":
    main()

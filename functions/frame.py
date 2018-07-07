import pandas as pd
import re


def extractInstructions(string):
    # extract instruction section from text

    # match instruction section of the annotation (without numbers)
    instructions = re.match('#[^\\w\\(]{0,12}(\\w|\\([A-Z][0-9]{0,2}\\)\\w)', string)

    if instructions:  # if instruction pattern has been matched

        instructions = instructions.group(0)  # regex match object to string
        instructions = instructions[1:-1]  # extract actual instructions

    else:  # if no instruction pattern match was found
        instructions = ''

    return instructions


def extractType(string):
    # extract type from text

    # match instruction section of the annotation (with numbers)
    temp = re.match('#[^\\w\\(]{0,12}(\\w|\\([A-Z][0-9]{0,2}\\)\\w)[0-9]{0,2}', string)

    if temp:  # if instruction pattern has been matched

        temp = temp.group(0)  # regex match object to string, cut "#"
        pattern = re.compile(re.escape(re.match('#[^\\w\\(]{0,12}(\\w|\\([A-Z][0-9]{0,2}\\)\\w)', temp).group(0)[:-1]))
        annotationType = re.sub(pattern, '', temp)

    else:  # if no instruction pattern match was found
        annotationType = ''

    return annotationType


def extractTitle(string):
    # extract title from text

    # match instruction section of the annotation (with numbers)
    temp = re.match('#[^\\w\\(]{0,12}(\\w|\\([A-Z][0-9]{0,2}\\)\\w)[0-9]{0,2}', string)

    if temp:  # if instruction pattern has been matched

        temp = temp.group(0)  # regex match object to string
        title = string[len(temp) + 1:]  # cut away instruction pattern

        # capitalize title
        if title:
            title = title[0].upper() + title[1:]

    else:  # if no instruction pattern match was found
        title = ''

    return title


def dealWithBreaks(df):
    # Deal with page breaks and breaks on a single page in highlighted and underlined text

    for item in reversed(df.index):
        if re.search('#\\.\\.\\.', df['Annotation'][item]):  # if page break

            textToAppend = df['Text'][item]
            df.loc[item - 1, 'Text'] = df['Text'][item - 1] + textToAppend
            df.loc[item - 1, 'Page'] = df['Page'][item - 1] + ", " + df['Page'][item]
            df = df.drop(item)

        elif re.search('#,,,', df['Annotation'][item]):  # if break on a single page

            textToAppend = df['Text'][item]
            df.loc[item - 1, 'Text'] = df['Text'][item - 1] + " [...] " + textToAppend
            df.loc[item - 1, 'Page'] = df['Page'][item - 1] + ", " + df['Page'][item]
            df = df.drop(item)

    return df


def frameData(highlightText, highlightTextPos, underlineText, underlineTextPos,
              textBoxText, textBoxTextPos, firstPage, numFirstPage):
    # Generate dataframe from highlighted text and content of textboxes. The latter are matched
    # to the former via comparison of vertical positioning

    pages = [(item[0] - numFirstPage + 1 + firstPage) for item in highlightTextPos]  # pages with highlighted text
    lowerLimit = [item[1] for item in highlightTextPos]  # lower vertical boundaries
    upperLimit = [item[2] for item in highlightTextPos]  # upper vertical boundaries
    midpoint = [(x + y) / 2 for x, y in zip(lowerLimit, upperLimit)]  # midpoint of vertical boundaries

    # Generate dataframe with highlighted text
    highlightDF = pd.DataFrame({'Page': pages, 'Text': highlightText,
                                'Lower': lowerLimit, 'Upper': upperLimit, 'Midpoint': midpoint})
    highlightDF = highlightDF.sort_values(by=['Page', 'Lower'])  # sort data in dataframe
    highlightDF = highlightDF.reset_index(drop=True)  # reindex dataframe

    pages = [(item[0] + firstPage - numFirstPage + 1) for item in textBoxTextPos]  # pages with textboxes
    midpoint = [item[2] for item in textBoxTextPos]  # midpoint of vertical boundaries

    # Generate dataframe with content from textboxes
    textBoxDF = pd.DataFrame({'Page': pages, 'Annotation': textBoxText, 'Midpoint': midpoint})
    textBoxDF = textBoxDF.sort_values(by=['Page', 'Midpoint'])  # sort data in dataframe
    textBoxDF = textBoxDF.reset_index(drop=True)  # reindex dataframe

    L = highlightDF.shape[0]  # number of elements in highlight-dataframe
    textList = [''] * L  # empty list for matching of highlighted text and textbox contents

    for pNumber in highlightDF.Page.unique():  # go through all pages with highlights on them

        # relevant part of both dataframes
        tempHighlightDF = highlightDF.loc[highlightDF['Page'] == pNumber]
        tempTextBoxDF = textBoxDF.loc[textBoxDF['Page'] == pNumber]

        # compare vertical positioning
        for k in tempHighlightDF.index:
            for l in tempTextBoxDF.index:
                # if midpoint of current textbox is located between vertical boundaries of highlighted text
                if tempHighlightDF['Lower'][k] < tempTextBoxDF['Midpoint'][l] < tempHighlightDF['Upper'][k]:

                    textList[k] = tempTextBoxDF['Annotation'][l]  # append contents of textbox

                    try:
                        textBoxDF = textBoxDF.drop(l)  # drop row from textbox dataframe
                    except KeyError:
                        print('KEY ERROR at page %d' % pNumber)

                    break

    textListDF = pd.DataFrame({'Annotation': textList})  # generate dataframe from textList
    df = pd.concat([highlightDF[['Page', 'Midpoint', 'Text']], textListDF], axis=1)
    textBoxDF.loc[:, 'Text'] = ''
    
    df = pd.concat([df, textBoxDF], sort=True)
    df = df.sort_values(by=['Page', 'Midpoint'])  # sort data in dataframe
    df = df.reset_index(drop=True)  # reindex dataframe

    return df

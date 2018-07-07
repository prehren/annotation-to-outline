import re
from pylatexenc import latexencode


def cleanUpText(string):

    cleanedUpText = re.sub("- ", "", string)
    cleanedUpText = re.sub(r"([><])", r"$\1$", cleanedUpText)
    cleanedUpText = re.sub("([a-z])([A-Z])", r"\1 \2", cleanedUpText)

    return cleanedUpText


def dealWithCommas(df):

    itemsToBeDropped = set([])
    indexSet = set(df.index)

    for item in indexSet:

        if item in itemsToBeDropped:
            continue

        elif re.search(',', df['Instructions'][item]):

            tempIter = {i for i in indexSet if (i > item)} - itemsToBeDropped

            for k in tempIter:
                if not df['Annotation'][k]:

                    df.loc[item, 'Text'] = df.loc[item, 'Text'] + " [...] " + df.loc[k, 'Text']
                    df.loc[item, 'Page'] = df.loc[item, 'Page'] + ", " + df.loc[k, 'Page']
                    itemsToBeDropped.add(k)
                    break

    df = df.drop(itemsToBeDropped)
    return df


def dealWithPageNumbers(string):

    firstPart = re.match('[0-9]{1,5},', string)

    if firstPart:
        firstPart = firstPart.group(0)[:-1]
        secondPart = re.search('[0-9]{1,5}$', string).group(0)

        outputNumber = ("%s" % firstPart)

        for k in range(0, len(firstPart)):

            numberFirstPart = firstPart[k]
            numberSecondPart = secondPart[k]

            if numberFirstPart != numberSecondPart:
                secondPart = secondPart[k:]
                outputNumber = ("%s-%s" % (firstPart, secondPart))
                break

        return outputNumber
    else:
        return string


def latexifyDefinitions(df):

    defContents = ''

    for item in df.index:  # go through entire definitions table
        if re.search('D', df['Type'][item]):  # if type is definition

            title = df['Title'][item]
            page = df['Page'][item]
            text = df['Text'][item]

            # append title, highlighted text to contents
            if title:
                defContents = defContents + "\\textbf{" + cleanUpText(latexencode.utf8tolatex(title, substitute_bad_chars=True)) + "}: "

            if text:
                defContents = defContents + (cleanUpText(latexencode.utf8tolatex(text, substitute_bad_chars=True)) +
                                             " (p. %s)." % dealWithPageNumbers(page) + "\\\\\n\n")

    return defContents


def findObjAns(df, parentName, index, contents, indent):

    tempIter = [i for i in df.index if (i > index)]
    counter = 1

    for k in tempIter:

        if counter == 1:
            pattern = re.compile('([OAQ]$|[OAQ]%d$)' % counter)
        else:
            pattern = re.compile('[OAQ]%d$' % counter)

        childName = df['Type'][k]
        childInstructions = df['Instructions'][k]
        childText = df['Text'][k]
        childTitle = df['Title'][k]
        childPage = df['Page'][k]

        if re.search("%s" % parentName, childName):
            break

        # if item is child item of parent item
        if re.search('\\(%s\\)' % parentName, childInstructions) and re.match(pattern, childName):

            contents = contents + ("\\setlength{\\leftskip}{%dcm}\n" % indent)

            if re.search('-', childInstructions):
                preamble = '$\\rightarrow$ '
                counter -= 1
            else:
                preamble = "\\textbf{(" + cleanUpText(latexencode.utf8tolatex(childName, substitute_bad_chars=True)) + ")} "

            contents = contents + preamble

            if childTitle:
                if childText and re.search('-', childInstructions):
                    contents = contents + ("\\textbf{" + cleanUpText(latexencode.utf8tolatex(childTitle, substitute_bad_chars=True)) + "}: ")
                elif childText and not re.search('-', childInstructions):
                    contents = contents + ("\\textbf{" + cleanUpText(latexencode.utf8tolatex(childTitle, substitute_bad_chars=True)) + "}" + "\\\\\n")
                else:
                    contents = contents + ("\\textbf{" + cleanUpText(latexencode.utf8tolatex(childTitle, substitute_bad_chars=True)) + "}" + "\\\\\n\n")

            if childText:
                contents = contents + (cleanUpText(latexencode.utf8tolatex(childText, substitute_bad_chars=True)) + " (p. %s)." % dealWithPageNumbers(childPage) + "\\\\\n\n")

            contents = findObjAns(df, childName, k, contents, indent + 1)
            counter += 1

    return contents


def latexifyOtherAnnotations(df):

    contents = ""

    for item in df.index:
        if re.search('S', df['Type'][item]):  # if type is statement

            title = df['Title'][item]
            page = df['Page'][item]
            text = df['Text'][item]
            instructions = df['Instructions'][item]

            if re.search('-', instructions):
                preamble = '$\\rightarrow$ '
            else:
                preamble = ''

            if title:
                if text:
                    contents = contents + (preamble + "\\textbf{" + cleanUpText(latexencode.utf8tolatex(title, substitute_bad_chars=True)) + "}: \n")
                    preamble = ''
                else:
                    contents = contents + (preamble + "\\textbf{" + cleanUpText(latexencode.utf8tolatex(title, substitute_bad_chars=True)) + "}\\\\\n\n")
            if text:
                contents = contents + (preamble + cleanUpText(latexencode.utf8tolatex(text, substitute_bad_chars=True)) +
                                       " (p. %s)." % dealWithPageNumbers(page) + "\\\\\n\n")

        elif re.search('L', df['Type'][item]):  # if type is list

            title = df['Title'][item]
            page = df['Page'][item]

            if title:
                contents = contents + ("\\textbf{" + cleanUpText(latexencode.utf8tolatex(title, substitute_bad_chars=True)) + "}\n\n")
                firstLetter = title[0]
            else:
                firstLetter = 'i'

            tempIter = [i for i in df.index if (i > item)]
            counter = 1

            contents = contents + ("\\begin{itemize}\n")

            for k in tempIter:

                instructions = df['Instructions'][k]
                annType = df['Type'][k]
                itemTitle = df['Title'][k]
                itemText = df['Text'][k]
                itemPage = df['Page'][k]

                if re.search('%s%d' % (firstLetter.lower(), counter), annType):

                    if re.search('-', instructions):
                        preamble = '[$\\rightarrow$] '
                    else:
                        preamble = ' '

                    contents = contents + ("\\item" + preamble)
                    if itemTitle:
                        contents = contents + ("\\textbf{" +
                                               cleanUpText(latexencode.utf8tolatex(itemTitle, substitute_bad_chars=True)) + "}: ")

                    contents = contents + (cleanUpText(latexencode.utf8tolatex(itemText, substitute_bad_chars=True)) +
                                           " (p. %s)." % dealWithPageNumbers(itemPage) + "\n")
                    counter += 1

                    if re.search('\\.', instructions):
                        break

            contents = contents + ("\\end{itemize}\n\n")

        elif re.search('[QOA]', df['Type'][item]):  # if type is question or objection

            if not re.search('\\([A-Z][0-9]{0,2}\\)', df['Instructions'][item]):  # if item is a parent

                indent = 0

                parentName = df['Type'][item]
                parentTitle = df['Title'][item]
                parentText = df['Text'][item]
                parentPage = df['Page'][item]
                parentInstructions = df['Instructions'][item]

                if re.search('[OA]', parentName):
                    indent += 1

                if re.search('-', parentInstructions):
                    preamble = '$\\rightarrow$ '
                else:
                    preamble = "\\textbf{(" + cleanUpText(latexencode.utf8tolatex(parentName, substitute_bad_chars=True)) + ")} "

                contents = contents + ("\n\\setlength{\\leftskip}{%dcm}\n\n" % indent)
                contents = contents + preamble

                if parentTitle:
                    if parentText and re.search('-', parentInstructions):
                        contents = contents + ("\\textbf{" + cleanUpText(latexencode.utf8tolatex(parentTitle, substitute_bad_chars=True)) + "}: ")
                    elif parentText and not re.search('-', parentInstructions):
                        contents = contents + ("\\textbf{" + cleanUpText(latexencode.utf8tolatex(parentTitle, substitute_bad_chars=True)) + "}" + "\\\\\n")
                    else:
                        contents = contents + ("\\textbf{" + cleanUpText(latexencode.utf8tolatex(parentTitle, substitute_bad_chars=True)) + "}" + "\\\\\n\n")

                if parentText:
                    contents = contents + (cleanUpText(latexencode.utf8tolatex(parentText, substitute_bad_chars=True)) + " (p. %s)." % dealWithPageNumbers(parentPage) + "\\\\\n\n")

                contents = findObjAns(df, parentName, item, contents, indent + 1)
                contents = contents + "\\setlength{\\leftskip}{0cm}\n\n"

    return contents

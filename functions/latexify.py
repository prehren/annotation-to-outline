#
# Functions for program auto-outline. Responsible for creating the
# LaTex structure out of the contents of the annotation object table.
#

import re
from pylatexenc import latexencode


def cleanUpText(string):
    # clean up text

    cleanedUpText = latexencode.utf8tolatex(string, substitute_bad_chars=True)
    cleanedUpText = re.sub("- ", "", string)
    cleanedUpText = re.sub(r"([><])", r"$\1$", cleanedUpText)
    cleanedUpText = re.sub("([a-z])([A-Z])", r"\1 \2", cleanedUpText)

    return cleanedUpText


def dealWithPageNumbers(string):
    # Format page numbers of objects extending over more than one page

    firstPart = re.match('[0-9]{1,5},', string)  # first page number

    if firstPart:
        outputNumber = firstPart = firstPart.group(0)[:-1]  # regex match object to string
        lastPart = re.search('[0-9]{1,5}$', string).group(0)  # last page number

        for k in range(0, len(firstPart)):

            numFirstPart = firstPart[k]  # k-th digit first page number
            numlastPart = lastPart[k]  # k-th digit last page number

            if numFirstPart != numlastPart:

                lastPart = lastPart[k:]
                outputNumber = ("%s-%s" % (firstPart, lastPart))
                break

        return outputNumber

    # If only a single page number or no page number is given, return input string
    else:
        return string


def buildDiscussionStructure(df, parentName, index, contents, indent):
    # Recursively build discussion structure eminating from current objection,
    # question or answer, create LaTex structure

    tempIter = [i for i in df.index if (i > index)]
    counter = 1  # set discussion object counter

    for k in tempIter:  # check all objects after parent object

        # set match pattern
        if counter == 1:
            pattern = re.compile('([OAQ]$|[OAQ]%d$)' % counter)
        else:
            pattern = re.compile('[OAQ]%d$' % counter)

        # child object stats
        childName = df['Type'][k]
        childInstructions = df['Instructions'][k]
        childText = df['Text'][k]
        childTitle = df['Title'][k]
        childPage = df['Page'][k]

        # break if child objects has the same name as parent object (as in this
        #  case, the discussion tree the child object belongs to has ended)
        if re.search("%s" % parentName, childName):
            break

        # if item is child item of parent item
        if re.search('\\(%s\\)' % parentName, childInstructions) and re.match(pattern, childName):

            contents = contents + ("\\setlength{\\leftskip}{%dcm}\n" % indent)  # set indent

            # set arrow preamble
            if re.search('-', childInstructions):
                preamble = '$\\rightarrow$ '
                counter -= 1
            else:
                preamble = "\\textbf{(" + cleanUpText(childName) + ")} "

            contents = contents + preamble

            # append child title, highlighted text belonging to child object, page number to LaTex structure
            if childTitle:
                if childText and re.search('-', childInstructions):
                    contents = contents + ("\\textbf{" + cleanUpText(childTitle) + "}: ")
                elif childText and not re.search('-', childInstructions):
                    contents = contents + ("\\textbf{" + cleanUpText(childTitle) + "}" + "\\\\\n")
                else:
                    contents = contents + ("\\textbf{" + cleanUpText(childTitle) + "}" + "\\\\\n\n")
            if childText:
                contents = contents + (cleanUpText(childText) + " (p. %s)." % dealWithPageNumbers(childPage) + "\\\\\n\n")

            # recursively search for discussion structure eminating from child object (new parent object)
            contents = buildDiscussionStructure(df, childName, k, contents, indent + 1)

            counter += 1  # increment discussion object counter

    return contents


def latexifyAnnotations(df):
    # Create LaTex structure from annotations

    defContents = ''  # LaTex structure for definitions
    contents = ''  # LaTex structure for other object types

    for item in df.index:  # go through annotation object table

        objectType = df['Type'][item]  # object type
        objectTitle = df['Title'][item]  # object title
        objectText = df['Text'][item]  # object text
        objectPage = df['Page'][item]  # object page number(s)
        objectInstructions = df['Instructions'][item]  # object instructions

        if re.search('D', objectType):  # if object is a definition

            # append title, highlighted text, page number to LaTex structure
            if objectTitle:
                defContents = defContents + "\\textbf{" + cleanUpText(objectTitle) + "}: "
            if objectText:
                defContents = defContents + (cleanUpText(objectText) +
                                             " (p. %s)." % dealWithPageNumbers(objectPage) + "\\\\\n\n")

        elif re.search('S', objectType):  # if object is a statement

            # set arrow preamble
            if re.search('-', objectInstructions):
                preamble = '$\\rightarrow$ '
            else:
                preamble = ''

            # append title, highlighted text, page number to LaTex structure
            if objectTitle:
                if objectText:
                    contents = contents + preamble + "\\textbf{" + cleanUpText(objectTitle) + "}: \n"
                    preamble = ''
                else:
                    contents = contents + preamble + "\\textbf{" + cleanUpText(objectTitle) + "}\\\\\n\n"
            if objectText:
                contents = contents + (preamble + cleanUpText(objectText) +
                                       " (p. %s)." % dealWithPageNumbers(objectPage) + "\\\\\n\n")

        elif re.search('L', objectType):  # if object is a list

            # append list title to LaTex structure
            # set identifier of list items
            if objectTitle:
                contents = contents + "\\textbf{" + cleanUpText(objectTitle) + "}\n\n"
                firstLetter = objectTitle[0]
            else:
                firstLetter = 'i'

            tempIter = [i for i in df.index if (i > item)]
            counter = 1  # list item object counter

            contents = contents + ("\\begin{itemize}\n")  # begin list

            for k in tempIter:  # check all objects after list title object

                # child object stats
                childInstructions = df['Instructions'][k]
                childType = df['Type'][k]
                childTitle = df['Title'][k]
                childText = df['Text'][k]
                childPage = df['Page'][k]

                # if child object is a list item
                if re.search('%s%d' % (firstLetter.lower(), counter), childType):

                    # set arrow preamble
                    if re.search('-', objectInstructions):
                        preamble = '[$\\rightarrow$] '
                        counter -= 1
                    else:
                        preamble = ' '

                    contents = contents + "\\item" + preamble

                    # append title, highlighted text, page number to LaTex structure
                    if childTitle:
                        contents = contents + ("\\textbf{" +
                                               cleanUpText(childTitle) + "}: ")
                    contents = contents + (cleanUpText(childText) +
                                           " (p. %s)." % dealWithPageNumbers(childPage) + "\n")
                    counter += 1  # increment list item object counter

                    # end search if child object is the last item in the list
                    if re.search('\\.', childInstructions):
                        break

            contents = contents + ("\\end{itemize}\n\n")

        # if object is an initial question, objection or answer
        elif re.search('[QOA]', objectType) and not re.search('\\([A-Z][0-9]{0,2}\\)', objectInstructions):

            # set indent for formatting
            if re.search('[OA]', objectType):
                indent = 1
            else:
                indent = 0

            # set arrow preamble
            if re.search('-', objectInstructions):
                preamble = '$\\rightarrow$ '
            else:
                preamble = "\\textbf{(" + cleanUpText(objectType) + ")} "

            contents = contents + ("\n\\setlength{\\leftskip}{%dcm}\n\n" % indent)  # set indent
            contents = contents + preamble  # set preamble

            # append title, highlighted text, page number to LaTex structure
            if objectTitle:
                if objectText and re.search('-', objectInstructions):
                    contents = contents + ("\\textbf{" + cleanUpText(objectTitle) + "}: ")
                elif objectText and not re.search('-', objectInstructions):
                    contents = contents + ("\\textbf{" + cleanUpText(objectTitle) + "}" + "\\\\\n")
                else:
                    contents = contents + ("\\textbf{" + cleanUpText(objectTitle) + "}" + "\\\\\n\n")
            if objectText:
                contents = contents + (cleanUpText(objectText) +
                                       " (p. %s)." % dealWithPageNumbers(objectPage) + "\\\\\n\n")

            # recursively build discussion structure eminating from current objection, question or answer
            contents = buildDiscussionStructure(df, objectType, item, contents, indent + 1)

            contents = contents + "\\setlength{\\leftskip}{0cm}\n\n"

    return contents, defContents

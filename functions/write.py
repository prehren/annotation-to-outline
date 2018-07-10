#
# Function for program auto-outline. Responsible for writing the
# LaTex structure to file.
#


def writeToLatex(fileName, outlineContents, defContents, titleContents):
    # Write contents to .tex file

    f = open(fileName, 'w')  # file object

    # write LaTex preamble to file
    f.write("\\documentclass[10pt,a4paper,draft]{report}\n\
            \\usepackage{geometry}\\geometry{a4paper,\
            left=22mm,\n\
            right=22mm,\n\
            top=25mm,\n\
            bottom=30mm,\n\
            }\n\
            \\usepackage[utf8]{inputenc}\n\
            \\usepackage[english]{babel}\n\
            \\usepackage{amsmath}\n\
            \\usepackage{amsfonts}\n\
            \\usepackage{amssymb}\n\
            \\usepackage{textcomp}\n\
            \\setlength\\parindent{0pt}\n\
            \\begin{document}\n\n")

    if titleContents:
        f.write("\\begin{center}\n\\section*{Summary -- %s}\n\\end{center}\n\n" % titleContents)

    if defContents:
        f.write("\n\\subsection*{Definitions}\n\n%s\n\n" % defContents)

    if outlineContents:
        f.write("\\subsection*{Outline}\n\n%s" % outlineContents)

    f.write("\n\n\\end{document}")  # end LaTex document
    f.close()  # close file

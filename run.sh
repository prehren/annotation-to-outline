#!/bin/bash

workingDir=`pwd` # working directory
inputFileName="$workingDir/$1" # input file name
outputFileName="${BASH_SOURCE%/*}/Summary $4 $3" # output file name
movedName="$workingDir/Summary $4 $3" # file name after having been moved

# check if the appropriate number of arguments has been given
if [ "$#" -ne 6 ]; then
    printf "\nERROR: Not the appropriate number of arguments given. Please provide:
            \n\t-argv[1]: input file name (str -- in working directory)
            \n\t-argv[2]: number of the first page (as numbered in input, int)
            \n\t-argv[3]: paper title (str)
            \n\t-argv[4]: author (str)
            \n\t-argv[5]: number of first page to be extracted from input file (int)
            \n\t-argv[6]: number of total pages to be extracted from input file (int)\n\n"
    exit 1
fi

# call main.py
python3.5 ${BASH_SOURCE%/*}/main.py "$inputFileName" $2 "$outputFileName.tex" "$3" "$4" $5 $6

if [ -f "$outputFileName.tex" ]; then
    
    cd ${BASH_SOURCE%/*}
    pdflatex "$outputFileName.tex" # run pdflatex over .tex file
    # move .pdf, .tex file to working directory
    mv "$outputFileName.pdf" "$movedName.pdf"
    mv "$outputFileName.tex" "$movedName.tex"
    rm "$outputFileName".* # remove all other output files from pdflatex
    cd "$workingDir"

    printf "\n\nSucess!\n\n"
fi


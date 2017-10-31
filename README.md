How to run the program:
Example : python individual_election_contributor.py  ./input/itcont.txt ./output/medianvals_by_zip.txt  ./output/medianvals_by_date.txt
The input file and the output filenames for running median and median by date have to be passed as parameters.
The script will process the donation information for each recipient
from the input file and calculate the running median by zipcode
and median by date

class RecipientInfo
This object holds details of transaction amounts by zipcode per recipient id
and transaction amounts by transaction date per recipient id

class MedianCalculator
Reads input file line by line
Parse the columns from the input
For each recipient id creates a RecipientInfo object
Calculate the running median of transaction amount by zipcode
Calculate the median of transaction amount by date

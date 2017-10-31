import datetime
import logging
import sys

from RecipientInfo import RecipientInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler('individual_election_contributor.log')
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


class MedianCalculator(object):
    """
        Parent class that reads the input file and creates two output files
    """

    def __init__(self, input_file, output_file_by_zip, output_file_by_date):
        """
            Initialize variables for file names, file handlers for the output files
            and the main data structure that holds the recipient details

        :param input_file: File with details of donor , recipient and contribution information
        :param output_file_by_zip: Output file to write running median by zipcode
        :param output_file_by_date: Output file to write median by date
        """
        self.input_file = input_file
        self.output_file_by_zip = output_file_by_zip
        self.output_file_by_zip_fd = self._file_open(output_file_by_zip)
        self.output_file_by_date_fd = self._file_open(output_file_by_date)
        self.output_file_by_date = output_file_by_date
        self.recepient_dict = {}

    def _readfiles(self, input_file):
        """
            Read line from the input file
            :param input_file: input file name
            :return: Single line at a time from the file
        """
        with open(self.input_file, 'r') as fd:
            for line in fd:
                yield line

    def _get_parsed_info(self, lines):
        """
        Get the columns cmte_id , zipcode,transaction_amt,transaction_dt, other_id from file
        :param lines: Line from the file
        :return: cmte_id, zipcode, transaction_dt, transaction_amt
        """

        for line in lines:
            try:
                columns = line.strip().split('|')
                other_id = columns[15].strip()
                transaction_amt = columns[14].strip()
                cmte_id = columns[0].strip()
                zipcode = str(columns[10])[0:5].strip()
                transaction_dt = str(columns[13]).strip()
            except:
                logger.exception("Skipping line with invalid data ")
                continue

            # Skipping rows for processing if cmte_td or transaction_amt is empty or if other_id is non empty
            if other_id != "" or transaction_amt == '' or cmte_id == '':
                logger.debug("Skipping invalid line. other_id: {}, transaction_amt: {},"
                             " cmte_id: {}".format(other_id, transaction_amt, cmte_id))
                continue

            # Validating zipcode
            if len(zipcode) == 0 or len(zipcode) < 5:
                zipcode = 'INVALID'

            # Validating transaction_dt
            try:
                datetime.datetime.strptime(transaction_dt, '%m%d%Y')
            except:
                transaction_dt = 'INVALID'

            yield cmte_id, zipcode, transaction_dt, transaction_amt

    def _update_recipient_info(self, cmte_id, zipcode, transaction_dt, transaction_amt):
        """
        Update the fields contribution_by_zip_code and contribution_by_date in the object that holds the recipient info
        :param cmte_id: Recipient Id
        :param zipcode: Zipcode of the donor
        :param transaction_dt: Transaction Date
        :param transaction_amt: Transaction Amount
        :return: None
        """
        recipient_info = self.recepient_dict.get(cmte_id, None)
        if recipient_info is None:
            recipient_info = RecipientInfo(cmte_id)
        self.recepient_dict[cmte_id] = recipient_info
        recipient_info.set_contribution_by_zipcode(zipcode, transaction_amt)
        recipient_info.set_contribution_by_date(transaction_dt, transaction_amt)

    def get_median(self, list_transaction_amt):
        """
        Calculate median for the input list
        :param list_transaction_amt: List of transaction_amt
        :return: Median for transaction_amt
        """
        list_transaction_amt = sorted(list_transaction_amt)
        center = len(list_transaction_amt) / 2
        if len(list_transaction_amt) % 2 == 0:
            return sum(list_transaction_amt[center - 1:center + 1]) / 2.0
        else:
            return list_transaction_amt[center]

    def _file_open(self, output_file):
        fh = open(output_file, 'w')
        return fh

    def _file_close(self, fh):
        fh.close()

    def close_open_files(self):
        """
        Method to close all open file descriptors
        :return: None
        """
        if self.output_file_by_date_fd:
            self._file_close(self.output_file_by_date_fd)
        if self.output_file_by_zip_fd:
            self._file_close(self.output_file_by_zip_fd)

    def _write_running_median_by_zip(self, cmte_id, zipcode):
        """
        Calculates running median by zipcode and writes to a file
        :param cmte_id: Recipient id
        :param zipcode: Zip code
        :return:None
        """
        recipient_info = self.recepient_dict.get(cmte_id)
        if zipcode != 'INVALID':
            running_median_by_zipcode = self.get_median(recipient_info.contribution_by_zipcode[zipcode])

            running_median_info = str(cmte_id) + '|' + str(zipcode) + '|' + \
                                  str(int(round(running_median_by_zipcode))) + '|' + \
                                  str(len(recipient_info.contribution_by_zipcode[zipcode])) + '|' + \
                                  str(int(round(sum(recipient_info.contribution_by_zipcode[zipcode])))) + "\n"

            self.output_file_by_zip_fd.write(running_median_info)
        else:
            logger.error("Skipping invalid zipcode for running median calculation.")

    def _write_median_by_date(self):
        """
        Calculates median by date and writes to a file
        :return: None
        """
        for cmte_id in sorted(self.recepient_dict):
            recipient_info = self.recepient_dict[cmte_id]
            for transaction_date in sorted(recipient_info.contribution_by_date):
                if transaction_date <> 'INVALID':
                    median_by_date = self.get_median(recipient_info.contribution_by_date[transaction_date])
                    median_info = str(cmte_id) + '|' + str(transaction_date) + '|' + \
                                  str(int(round(median_by_date))) + '|' + \
                                  str(len(recipient_info.contribution_by_date[transaction_date])) + '|' + \
                                  str(int(round(sum(recipient_info.contribution_by_date[transaction_date])))) + '\n'
                    self.output_file_by_date_fd.write(median_info)
                else:
                    logger.error("Skipping invalid date for median calculation.")
    def compute_medians (self):
        """
        Read input file and calculate both running median by zip and median by date
        """
        try:
            lines = self._readfiles(self.input_file)
            while 1:
                cmte_id, zipcode, transaction_dt, transaction_amt = self._get_parsed_info(lines).next()
                self._update_recipient_info(cmte_id, zipcode, transaction_dt, transaction_amt)
                self._write_running_median_by_zip(cmte_id, zipcode)
        except StopIteration:
            logger.debug("Completed calculating running median.")
            self._write_median_by_date()
        except:
            logger.exception("Error calculating median information. Exiting application.")

        finally:
            self.close_open_files()


if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file_by_zip = sys.argv[2]
    output_file_by_date =sys.argv[3]

    median_calculator = MedianCalculator(input_file, output_file_by_zip, output_file_by_date)
    median_calculator.compute_medians()

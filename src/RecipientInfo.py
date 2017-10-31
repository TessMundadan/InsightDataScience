class RecipientInfo(object):
    """
        Object that encapsulate the data for each recipient and all its corresponding transaction amounts by zip
        and transaction amounts by date
    """
    def __init__(self, cmte_id):
        self.cmte_id = cmte_id
        self.contribution_by_zipcode = {}
        self.contribution_by_date = {}

    def set_contribution_by_zipcode(self, zipcode, transaction_amt):
        if self.contribution_by_zipcode.get(zipcode, None) is None:
            self.contribution_by_zipcode[zipcode] = [float(transaction_amt)]
        else:
            self.contribution_by_zipcode[zipcode].append(float(transaction_amt))

    def set_contribution_by_date(self, transaction_dt, transaction_amt):
        if self.contribution_by_date.get(transaction_dt, None) is None:
            self.contribution_by_date[transaction_dt] = [float(transaction_amt)]
        else:
            self.contribution_by_date[transaction_dt].append(float(transaction_amt))
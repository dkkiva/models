import arrow
import csv
import pprint

# relative file paths to repayments_expected & repayments_collected
file_dict = {
    'expected': '../data/repayments_expected.csv',
    'collected': '../data/repayments_collected.csv'
}
fieldname_dict = {
    'expected': ['zip_loan_id', 'amount_due', 'repayment_expected_time'],
    'collected': ['zip_loan_id', 'amount_collected', 'repayment_collected_time']
}


def read_in_files(file_dict, fieldname_dict):
    """
    Read in DictCSVs and skip the header column.
    """
    expected_csv = csv.DictReader(open(file_dict['expected'], 'r+'), fieldnames=fieldname_dict['expected'])
    collected_csv = csv.DictReader(open(file_dict['collected'], 'r+'), fieldnames=fieldname_dict['collected'])
    print("Read in both files.")
    expected_csv.next()
    collected_csv.next()
    print("Skipping headers.")

def format_csv_arrays(expected_csv, collected_csv):
    """
    Transform read-in CSVs into dictionary with top level keys of "zip_loan_id"


    Any expected payments that do not appear in the "collected" payments
    are output into a CSV called "immediately_defaulted_loans.csv" which is
    stashed in this folder.
    """
    for row in expected_csv:
        zip_loan_id = row['zip_loan_id']
        if zip_loan_id not in id_dict.keys():
            id_dict[zip_loan_id] = {'expected_payments':[], 'collected_payments':[]}
        repayment_date = arrow.get(row['repayment_expected_time'], 'M/D/YYYY H:mm').date()
        expected_payment = {'amount': row['amount_due'], 'date': repayment_date}
        id_dict[zip_loan_id]['expected_payments'].append(expected_payment)
    for row in collected_csv:


def infer_number_of_payments_expected():
    pass

if __name__ == "__main__":
    read_in_files(file_dict, fieldname_dict)

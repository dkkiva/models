import arrow
import csv
import pprint
import datetime

p = pprint.PrettyPrinter()

expected_payment_file = 'data/repayments_expected.csv'
expected_fieldnames = ['zip_loan_id', 'amount_due', 'repayment_expected_time']
collected_payment_file = 'data/repayments_collected.csv'
collected_fieldnames = ['zip_loan_id', 'amount_collected', 'repayment_collected_time']

expected_csv = csv.DictReader(open(expected_payment_file, 'r+'), fieldnames=expected_fieldnames)
expected_csv.next()

id_dict = {}

for row in expected_csv:
    zip_loan_id = row['zip_loan_id']
    if zip_loan_id not in id_dict.keys():
        id_dict[zip_loan_id] = {'expected_payments':[], 'collected_payments':[]}
    repayment_date = arrow.get(row['repayment_expected_time'], 'M/D/YY H:mm').date()
    expected_payment = {'amount': row['amount_due'], 'date': repayment_date}
    id_dict[zip_loan_id]['expected_payments'].append(expected_payment)

print('done reading in expected_csv')

collected_csv = csv.DictReader(open(collected_payment_file, 'r+'), fieldnames=collected_fieldnames)
collected_csv.next()

for row in collected_csv:
    zip_loan_id = row['zip_loan_id']
    if zip_loan_id not in id_dict.keys():
        id_dict[zip_loan_id] = {'expected_payments':[], 'collected_payments':[]}
    if row['repayment_collected_time'] != '':
        repayment_date = arrow.get(row['repayment_collected_time'], 'M/D/YY H:mm').date()
    else:
        repayment_date = ''
    collected_payment = {'amount': row['amount_collected'], 'date': repayment_date}
    id_dict[zip_loan_id]['collected_payments'].append(collected_payment)

print('done reading in collected_csv')

# format everything -- FIX IT
for key, val in id_dict.items():
    pass

output = csv.DictWriter(open('data/output.csv', fieldname=[
                                                  'zip_loan_id',
                                                  'repayment_expected_date',
                                                  'repayment_expected_amount',
                                                  'cumulative_expected_amount',
                                                  'payment_amount',
                                                  'repayment_date']))

# write everything to the csv

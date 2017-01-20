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

print('{} entries in the id_dict'.format(len(id_dict.keys())))
print('Sample entry: {}'.format(id_dict['15']))
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

print('Sample entry: {}'.format(id_dict['15']))
print('done reading in collected_csv')

# format everything -- FIX IT
output_rows = []
for zip_id, dictionary in id_dict.items():
    cumulative_expected_amount = 0
    cumulative_repaid_amount = 0
    expected_payment_index = 0
    current_payment_index = 0

    iteration_length = len(dictionary['expected_payments'])
    try:
        expected_payment = dictionary['expected_payments'][expected_payment_index]
        expected_payment_index += 1
    except:
        expected_payment = []
        # print('Skipping loan {} due to lack of repayment data'.format(zip_id))
        continue

    current_payment = dictionary['collected_payments'][current_payment_index]
    current_payment_index += 1

    while expected_payment_index < iteration_length:

        # fix the input problems from the csv
        try:
            expected_payment_amount = int(expected_payment['amount'])
        except ValueError:
            expected_payment_amount = float(expected_payment['amount'])
        cumulative_expected_amount = cumulative_expected_amount + expected_payment_amount

        try:
            current_payment_amount = int(current_payment['amount'])
        except ValueError:
            current_payment_amount = float(current_payment['amount'])      
        cumulative_repaid_amount = cumulative_repaid_amount + current_payment_amount

        if cumulative_repaid_amount > cumulative_expected_amount:
            this_row = {'zip_loan_id': zip_id,
                        'repayment_expected_date': expected_payment['date'],
                        'repayment_expected_amount': expected_payment['amount'],
                        'cumulative_expected_amount': cumulative_expected_amount,
                        'repayment_amount': current_payment['amount'],
                        'repayment_date': current_payment['date']}
            output_rows.append(this_row)
            print(this_row)
            expected_payment = dictionary['expected_payments'][expected_payment_index]
            expected_payment_index += 1

        elif cumulative_repaid_amount < cumulative_expected_amount:
            current_payment = dictionary['collected_payments'][current_payment_index]
            current_payment_index += 1

print(output_rows)

output = csv.DictWriter(open('data/output.csv', 'w+'), fieldnames=[
                                                  'zip_loan_id',
                                                  'repayment_expected_date',
                                                  'repayment_expected_amount',
                                                  'cumulative_expected_amount',
                                                  'repayment_amount',
                                                  'repayment_date'])

for row in output_rows:
    output.writerow(row)

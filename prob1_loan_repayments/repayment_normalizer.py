import arrow
import csv
import pprint

p = pprint.PrettyPrinter()

thing = []

expected_payment_file = '../data/repayments_expected.csv'
expected_fieldnames = ['zip_loan_id', 'amount_due', 'repayment_expected_time']
collected_payment_file = '../data/repayments_collected.csv'
collected_fieldnames = ['zip_loan_id', 'amount_collected', 'repayment_collected_time']

expected_csv = csv.DictReader(open(expected_payment_file, 'r+'), fieldnames=expected_fieldnames)
expected_csv.next()

id_dict = {}

for row in expected_csv:
    zip_loan_id = row['zip_loan_id']
    if zip_loan_id not in id_dict.keys():
        id_dict[zip_loan_id] = {'expected_payments':[], 'collected_payments':[]}
    repayment_date = arrow.get(row['repayment_expected_time'], 'M/D/YYYY H:mm').date()
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
        print('{} not in collected csv. Skipping'.format(zip_loan_id))
        continue
    if row['repayment_collected_time'] != '': #handle blank repayments
        repayment_date = arrow.get(row['repayment_collected_time'], 'M/D/YYYY H:mm').date()
    else:
        repayment_date = ''
    collected_payment = {'amount': row['amount_collected'], 'date': repayment_date}
    id_dict[zip_loan_id]['collected_payments'].append(collected_payment)

print('Sample entry: {}'.format(id_dict['15']))
print('done reading in collected_csv')

output_rows = []
id_dict_len = len(id_dict.keys())
index = 0
for zip_id, dictionary in id_dict.items():

    cumulative_expected_amount = 0
    cumulative_repaid_amount = 0
    expected_payment_index = 0
    current_payment_index = 0

    index += 1
    print('{} of {} ids'.format(index, id_dict_len))

    iteration_length = len(dictionary['expected_payments'])
    print('{} for {} iters'.format(zip_id, iteration_length))
    print('Expected payment length: {}'.format(len(dictionary['expected_payments'])))
    print('Actual repayment length: {}'.format(len(dictionary['collected_payments'])))

    if dictionary['collected_payments'] == []:
        print('Skipping loan {} because no repayment data.'.format(zip_id))
        continue

    if dictionary['expected_payments'] == []:
        print('Skipping loan {} because no expected payment data'.format(zip_id))
        continue

    current_payment = dictionary['collected_payments'][current_payment_index]
    current_payment_index += 1
    expected_payment = dictionary['expected_payments'][expected_payment_index]
    expected_payment_index += 1

    payments_not_made_list = []
    expected_payment_amount = float(expected_payment['amount'])
    cumulative_expected_amount = cumulative_expected_amount + expected_payment_amount

    current_payment_amount = float(current_payment['amount'])
    cumulative_repaid_amount = cumulative_repaid_amount + current_payment_amount

    while expected_payment_index < iteration_length:
        skip_final = False

        if cumulative_repaid_amount > cumulative_expected_amount:
            while cumulative_repaid_amount > cumulative_expected_amount:
                number_of_constituent_payments = len(payments_not_made_list)+1
                # if number_of_constituent_payments == 0:
                #     number_of_constituent_payments = 1
                this_row = {'zip_loan_id': zip_id,
                            'expected_date': expected_payment['date'],
                            'expected_amount': expected_payment['amount'],
                            'expected_cumulative_amount': cumulative_expected_amount,
                            'repayment_date': current_payment['date'],
                            'place': 0.01,
                            'repayment_amount': current_payment['amount'],
                            'repayment_cumulative_amount': cumulative_repaid_amount,
                            'number_of_smaller_payments_to_make_this_amount': number_of_constituent_payments}
                output_rows.append(this_row)
                try:
                    expected_payment = dictionary['expected_payments'][expected_payment_index]
                except IndexError:
                    skip_final = True
                    break
                expected_payment_index += 1
                expected_payment_amount = float(expected_payment['amount'])
                cumulative_expected_amount = cumulative_expected_amount + expected_payment_amount
                payments_not_made_list = []
            try:
                current_payment = dictionary['collected_payments'][current_payment_index]
            except IndexError:
                # break
                # # skip_final = True
                # if expected_payment_index == iteration_length:
                #     this_row = {'zip_loan_id': zip_id,
                #             'expected_date': expected_payment['date'],
                #             'expected_amount': expected_payment['amount'],
                #             'expected_cumulative_amount': cumulative_expected_amount,
                #             'repayment_date': current_payment['date'],
                #             'place': 0.1,
                #             'repayment_amount': current_payment['amount'],
                #             'repayment_cumulative_amount': cumulative_repaid_amount}
                #     output_rows.append(this_row)
                # else:
                    while expected_payment_index < iteration_length:
                    # means there is no repayment to match this amount yet
                        this_row = {'zip_loan_id': zip_id,
                            'expected_date': expected_payment['date'],
                            'expected_amount': expected_payment['amount'],
                            'expected_cumulative_amount': cumulative_expected_amount,
                            'repayment_amount': 'not made',
                            'place': 0,
                            'repayment_date': 'not made',
                            'repayment_cumulative_amount': 'not made',
                            'number_of_smaller_payments_to_make_this_amount': 'none made'}
                        payments_not_made_list.append(this_row)
                        expected_payment = dictionary['expected_payments'][expected_payment_index]
                        expected_payment_index += 1
                        expected_payment_amount = float(expected_payment['amount'])
                        cumulative_expected_amount = cumulative_expected_amount + expected_payment_amount
                    if len(payments_not_made_list) > 0:
                        for payment_row in payments_not_made_list:
                            output_rows.append(payment_row)
                    break
            current_payment_index += 1
            current_payment_amount = float(current_payment['amount'])
            cumulative_repaid_amount = cumulative_repaid_amount + current_payment_amount

        elif cumulative_repaid_amount == cumulative_expected_amount:
            this_row = {'zip_loan_id': zip_id,
                        'expected_date': expected_payment['date'],
                        'expected_amount': expected_payment['amount'],
                        'expected_cumulative_amount': cumulative_expected_amount,
                        'repayment_date': current_payment['date'],
                        'place': 1,
                        'repayment_amount': current_payment['amount'],
                        'repayment_cumulative_amount': cumulative_repaid_amount,
                        'number_of_smaller_payments_to_make_this_amount': 1}
            output_rows.append(this_row)

            try:
                current_payment = dictionary['collected_payments'][current_payment_index]
            except IndexError:
                skip_final = True
                # expected_payment_index += 1
                try:
                    expected_payment = dictionary['expected_payments'][expected_payment_index]
                except IndexError:
                    break
                expected_payment_amount = float(expected_payment['amount'])
                cumulative_expected_amount = cumulative_expected_amount + expected_payment_amount

                while expected_payment_index < iteration_length:
                # means there is no repayment to match this amount yet
                    this_row = {'zip_loan_id': zip_id,
                        'expected_date': expected_payment['date'],
                        'expected_amount': expected_payment['amount'],
                        'expected_cumulative_amount': cumulative_expected_amount,
                        'repayment_amount': 'not made',
                        'place': 2,
                        'repayment_date': 'not made',
                        'repayment_cumulative_amount': 'not made',
                        'number_of_smaller_payments_to_make_this_amount': 'none made'}
                    payments_not_made_list.append(this_row)
                    expected_payment_index += 1
                    try:
                        expected_payment = dictionary['expected_payments'][expected_payment_index]
                    except IndexError:
                        break
                    expected_payment_amount = float(expected_payment['amount'])
                    cumulative_expected_amount = cumulative_expected_amount + expected_payment_amount

                if len(payments_not_made_list) > 0:
                    for payment_row in payments_not_made_list:
                        output_rows.append(payment_row)
                break

            try:
                expected_payment = dictionary['expected_payments'][expected_payment_index]
            except IndexError:
                break

            expected_payment_index += 1
            expected_payment_amount = float(expected_payment['amount'])
            cumulative_expected_amount = cumulative_expected_amount + expected_payment_amount

            current_payment_index += 1
            current_payment_amount = float(current_payment['amount'])
            cumulative_repaid_amount = cumulative_repaid_amount + current_payment_amount

            payments_not_made_list = []

        elif cumulative_repaid_amount < cumulative_expected_amount:
            try:
                current_payment = dictionary['collected_payments'][current_payment_index]
                this_row = {'zip_loan_id': zip_id,
                    'expected_date': expected_payment['date'],
                    'expected_amount': expected_payment['amount'],
                    'expected_cumulative_amount': cumulative_expected_amount,
                    'repayment_amount': 'not made',
                    'repayment_date': 'not made',
                    'place': 3,
                    'repayment_cumulative_amount': 'not made',
                    'number_of_smaller_payments_to_make_this_amount': 'none made'}

                payments_not_made_list.append(this_row)

                current_payment_index += 1
            except IndexError:
                skip_final = True
                while expected_payment_index < iteration_length:
                # means there is no repayment to match this amount yet
                    this_row = {'zip_loan_id': zip_id,
                        'expected_date': expected_payment['date'],
                        'expected_amount': expected_payment['amount'],
                        'expected_cumulative_amount': cumulative_expected_amount,
                        'repayment_amount': 'not made',
                        'place': 4,
                        'repayment_date': 'not made',
                        'repayment_cumulative_amount': 'not made',
                        'number_of_smaller_payments_to_make_this_amount': 'none made'}

                    payments_not_made_list.append(this_row)
                    expected_payment = dictionary['expected_payments'][expected_payment_index]
                    expected_payment_index += 1
                    expected_payment_amount = float(expected_payment['amount'])
                    cumulative_expected_amount = cumulative_expected_amount + expected_payment_amount
                if len(payments_not_made_list) > 0:
                    for payment_row in payments_not_made_list:
                        output_rows.append(payment_row)
                this_row = {'zip_loan_id': zip_id,
                    'expected_date': expected_payment['date'],
                    'expected_amount': expected_payment['amount'],
                    'expected_cumulative_amount': cumulative_expected_amount,
                    'repayment_amount': 'not made',
                    'place': 5,
                    'repayment_date': 'not made',
                    'repayment_cumulative_amount': 'not made',
                    'number_of_smaller_payments_to_make_this_amount': 'none made'}

                payments_not_made_list.append(this_row)

    if skip_final is False:
        if len(payments_not_made_list) > 0:
            this_row = {'zip_loan_id': zip_id,
                'expected_date': expected_payment['date'],
                'expected_amount': expected_payment['amount'],
                'expected_cumulative_amount': cumulative_expected_amount,
                'repayment_date': 'not made',
                'repayment_amount': 'not made',
                'repayment_cumulative_amount': 'not made',
                'number_of_smaller_payments_to_make_this_amount': 'none made'}
        else:
            this_row = {'zip_loan_id': zip_id,
                'expected_date': expected_payment['date'],
                'expected_amount': expected_payment['amount'],
                'expected_cumulative_amount': cumulative_expected_amount,
                'repayment_date': current_payment['date'],
                'repayment_amount': current_payment['amount'],
                'repayment_cumulative_amount': cumulative_repaid_amount,
                'number_of_smaller_payments_to_make_this_amount': 1}
        output_rows.append(this_row)

output = csv.DictWriter(open('data/output.csv', 'wb'), fieldnames=[
                                                  'zip_loan_id',
                                                  'expected_date',
                                                  'expected_amount',
                                                  'expected_cumulative_amount',
                                                  'repayment_date',
                                                  'repayment_amount',
                                                  'repayment_cumulative_amount',
                                                  'number_of_smaller_payments_to_make_this_amount',
                                                  'place'])

output.writeheader()
for row in output_rows:
    output.writerow(row)

# still to address
# first repayment date is repeated
# what is 4022 doing, why does it jump from 200 to 4900

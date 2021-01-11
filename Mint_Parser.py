from datetime import datetime
import calendar
import argparse
import json
import re
import os


def get_args():
    action_choices = ["ParseTransactionPatterns", "ParseDescriptions"]
    sum_period_choices = ["Daily", "Weekly", "Monthly", "Yearly"]
    add_help = "Pass the -h argument for more information"
    actions_args_dict = {
        "ParseTransactionPatterns": [
            "transactions_file",
            "pattern_file",
            "output_file",
            "sum_period",
        ],
        "ParseDescriptions": [
            "transactions_file",
            "output_file",
            "sum_period",
        ]
    }

    parser = argparse.ArgumentParser(description='Used to process arguments passed to the Mint_Parser.py.')

    parser.add_argument('--action', nargs='+', choices=action_choices, help='List of actions to perform.  Currently there is only one action that can be passed, which is ParseTransactions. {}'.format(add_help))
    parser.add_argument('--transactions_file', default="transactions.csv", help='Used to point to the transaction file that was exported from Mint. Default is transactions.csv. {}'.format(add_help))
    parser.add_argument('--pattern_file', default="category_patterns.json", help='JSON file that contains a series of patterns. See category_patterns.json.template for an example. The patterns are regulare expressions. {}'.format(add_help))
    parser.add_argument('--output_file', default="output.json", help='File to output the results of matching the patterns from the --pattern_file argument. {}'.format(add_help))
    parser.add_argument('--sum_period', default="Monthly", choices=sum_period_choices, help='The method of summation to use on the transactions when building the report. {}'.format(add_help))

    args = parser.parse_args()

    for key, value in actions_args_dict.items():
        pass

    # Check that arguments are valid
    if "ParseTransactionPatterns" in args.action and not os.path.exists(args.transactions_file):
        msg = "Error: --transactions_file must point to a valid file when passing the argument --action ParseTransactions."
        raise argparse.ArgumentError(msg)
    if "ParseTransactionPatterns" in args.action and not os.path.exists(args.pattern_file):
        msg = "Error: --pattern_file must point to a valid file when passing the argument --action ParseTransactions."
        raise argparse.ArgumentError(msg)

    return args


def main():
    args = get_args()
    for a in args.action:
        if a == "ParseTransactionPatterns":
            parse_transaction_patterns(args)
        elif a == "ParseDescriptions":
            parse_descriptions(args)


def parse_transaction_patterns(args):
    category_dict = {}

    # Read in all transactions
    with open(args.transactions_file, 'r') as file_in_transactions:
        file_lines = file_in_transactions.readlines()

    # Read in all patterns
    with open(args.pattern_file, 'r') as file_in_pattern:
        category_dict_pattern = json.load(file_in_pattern)

    count = 0
    found_start = False
    for line in file_lines:
        # Don't parse first line
        if count == 0:
            count += 1
            continue

        # Split the columns
        line_split = line.split("\",\"")
        line_split[0] = line_split[0].lstrip('"')
        line_split[-1] = line_split[-1].lstrip('"\n')

        # Extract date and make date formats match
        date_obj = datetime.strptime(line_split[0], "%m/%d/%Y")
        date_str = get_date_key(args, date_obj)

        # Extract amount
        amount_flt = float(line_split[3])

        found_match = False
        for key, value in category_dict_pattern.items():
            for pattern in value:
                match = re.findall(pattern, line)
                if match:
                    found_match = True
                    if key not in category_dict.keys():
                        category_dict[key] = {
                            "Transactions": [line],
                            "Total": amount_flt,
                            args.sum_period: {},
                        }
                    else:
                        category_dict[key]["Transactions"].append(line)
                        category_dict[key]["Total"] = category_dict[key]["Total"] + amount_flt

                    if date_str not in category_dict[key][args.sum_period].keys():
                        category_dict[key][args.sum_period][date_str] = amount_flt
                    else:
                        category_dict[key][args.sum_period][date_str] = category_dict[key][args.sum_period][date_str] + amount_flt

                    # If match was found, then continue to next line
                    break
            if found_match:
                break

        # Record the transaction if no pattern matched it
        if not found_match:
            if "NO_MATCH" not in category_dict.keys():
                category_dict["NO_MATCH"] = {"Transactions": [line]}
                category_dict["NO_MATCH"] = {"Total": [line]}
                category_dict["NO_MATCH"] = {args.sum_period: [line]}
            else:
                category_dict["NO_MATCH"]["Transactions"].append(line)
                category_dict["NO_MATCH"] = {"Total": [line]}
                category_dict["NO_MATCH"] = {args.sum_period: [line]}
        count += 1

    # Write dictionary to json file
    with open(args.output_file, 'w') as file_out:
        json.dump(category_dict, file_out, sort_keys=True, indent=4, ensure_ascii=False)


def parse_descriptions(args):
    category_dict = {}

    # Read in all transactions
    with open(args.transactions_file, 'r') as file_in_transactions:
        file_lines = file_in_transactions.readlines()

    count = 0
    for line in file_lines:
        # Don't parse first line
        if count == 0:
            count += 1
            continue

        # Split the columns
        line_split = line.split("\",\"")
        line_split[0] = line_split[0].lstrip('"')
        line_split[-1] = line_split[-1].lstrip('"\n')

        # Extract date and make date formats match
        date_obj = datetime.strptime(line_split[0], "%m/%d/%Y")
        date_str = get_date_key(args, date_obj)

        # Extract description
        description = line_split[1]

        # Extract amount
        amount_flt = float(line_split[3])

        # Add month to dict
        if date_str not in category_dict.keys():
            category_dict[date_str] = {}

        # Add transaction to dict
        if description not in category_dict[date_str].keys():
            category_dict[date_str][description] = amount_flt
        else:
            category_dict[date_str][description] = category_dict[date_str][description] + amount_flt

    # Write dictionary to json file
    with open(args.output_file, 'w') as file_out:
        json.dump(category_dict, file_out, sort_keys=True, indent=4, ensure_ascii=False)


def get_date_key(args, date_obj):
    date_str = ""

    # Nothing need to be done here
    if args.sum_period == "Daily":
        date_str = date_obj.strftime("%m/%d/%Y")

    # Need to set date_obj to nearest week
    elif args.sum_period == "Weekly":
        # 1st week
        if date_obj.day < 8:
            date_str = date_obj.strftime("%m/01/%Y-%m/07/%Y")
        # 2nd week
        elif date_obj.day < 15:
            date_str = date_obj.strftime("%m/08/%Y-%m/14/%Y")
        # 3rd week
        elif date_obj.day < 21:
            date_str = date_obj.strftime("%m/15/%Y-%m/21/%Y")
        # 4th week
        else:
            last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
            date_str = date_obj.strftime("%m/21/%Y-%m/{}/%Y".format(last_day))

    # Need to set date_obj to current month
    elif args.sum_period == "Monthly":
        date_str = date_obj.strftime("%Y-%m")

    # Need to set date_obj to current year
    elif args.sum_period == "Yearly":
        date_str = date_obj.strftime("%Y")

    # Return date key
    return date_str


if __name__ == "__main__":
    main()
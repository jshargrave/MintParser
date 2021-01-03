from datetime import datetime
import argparse
import json
import re
import os

trans_file = "transactions.csv"
output_file = "transactions_parsed.csv"
output_monthly_file = "transactions_parsed_monthly.csv"

def get_args():
    action_choices = ["ParseTransactions"]
    add_help = "Pass the -h argument for more information"
    actions_args_dict = {
        "ParseTransactions": [
            "transactions_file",
            "pattern_file",
            "output_file",
        ],
    }

    parser = argparse.ArgumentParser(description='Used to process arguments passed to the Mint_Parser.py.')

    parser.add_argument('--action', nargs='+', choices=action_choices, help='List of actions to perform. {}'.format(add_help))
    parser.add_argument('--transactions_file', default="transactions.csv", help='transaction file export from Mint. {}'.format(add_help))
    parser.add_argument('--pattern_file', default="category_patterns.json", help='JSON file that contains a series of patterns. See category_patterns.json.template for an example. The patterns are regulare expressions. {}'.format(add_help))
    parser.add_argument('--output_file', default="output.json", help='File used to write output to. {}'.format(add_help))

    args = parser.parse_args()

    # Check that arguments are valid
    if "ParseTransactions" in args.action and not os.path.exists(args.transactions_file):
        msg = "Error: --transactions_file must point to a valid file when passing the argument --action ParseTransactions."
        raise argparse.ArgumentError(msg)
    if "ParseTransactions" in args.action and not os.path.exists(args.pattern_file):
        msg = "Error: --pattern_file must point to a valid file when passing the argument --action ParseTransactions."
        raise argparse.ArgumentError(msg)

    return args


def main():
    args = get_args()
    for a in args.action:
        if a == "ParseTransactions":
            parse_transactions(args)


def parse_transactions(args):
    category_dict = {}

    # Read in all transactions
    with open(args.transactions_file, 'r') as file_in_transactions:
        file_lines = file_in_transactions.readlines()

    # Read in all patterns
    with open(args.pattern_file, 'r') as file_in_pattern:
        category_dict_pattern = json.load(file_in_pattern)

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

        # Cleanup line and make date formats match
        date_obj = datetime.strptime(line_split[0], "%m/%d/%Y")
        date_str = date_obj.strftime("%m/%d/%Y")
        line_split[0] = date_str

        # Extract month
        match = re.match("([0-9]+)/[0-9]+/([0-9]+)", line_split[0])
        month_str = "{1}-{0}".format(match.group(1), match.group(2))

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
                            "Monthly": {},
                        }
                    else:
                        category_dict[key]["Transactions"].append(line)
                        category_dict[key]["Total"] = category_dict[key]["Total"] + amount_flt

                    if month_str not in category_dict[key]["Monthly"].keys():
                        category_dict[key]["Monthly"][month_str] = amount_flt
                    else:
                        category_dict[key]["Monthly"][month_str] = category_dict[key]["Monthly"][month_str] + amount_flt

                    # If match was found, then continue to next line
                    break
            if found_match:
                break

        # Record the transaction if no pattern matched it
        if not found_match:
            if "NO_MATCH" not in category_dict.keys():
                category_dict["NO_MATCH"] = {"Transactions": [line]}
                category_dict["NO_MATCH"] = {"Total": [line]}
                category_dict["NO_MATCH"] = {"Monthly": [line]}
            else:
                category_dict["NO_MATCH"]["Transactions"].append(line)
                category_dict["NO_MATCH"] = {"Total": [line]}
                category_dict["NO_MATCH"] = {"Monthly": [line]}
        count += 1

    # Write dictionary to json file
    with open(args.output_file, 'w') as file_out:
        json.dump(category_dict, file_out, sort_keys=True, indent=4, ensure_ascii=False)


def format_transactions(args):
    pass


if __name__ == "__main__":
    main()
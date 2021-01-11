from datetime import datetime
import calendar
import argparse
import json
import re
import os


def get_args():
    action_choices = ["CategoriesByPattern", "CategoriesByColumn"]
    sum_period_choices = ["Daily", "Weekly", "Monthly", "Yearly"]
    add_help = "Pass the -h argument for more information"
    actions_args_dict = {
        "CategoriesByPattern": [
            "transactions_file",
            "pattern_file",
            "output_file",
            "sum_period",
        ],
        "CategoriesByColumn": [
            "transactions_file",
            "output_file",
            "column",
            "sum_period",
        ],
    }

    parser = argparse.ArgumentParser(description='Used to process arguments passed to the Mint_Parser.py.')

    parser.add_argument('--action', nargs='+', choices=action_choices, help='List of actions to perform.  Currently there is only one action that can be passed, which is ParseTransactions.')
    parser.add_argument('--transactions_file', default="transactions.csv", help='Used to point to the transaction file that was exported from Mint. Default is transactions.csv.')
    parser.add_argument('--pattern_file', default="category_patterns.json", help='JSON file that contains a series of patterns. See category_patterns.json.template for an example. The patterns are regulare expressions.')
    parser.add_argument('--output_file', default="output.json", help='File to output the results of matching the patterns from the --pattern_file argument.')
    parser.add_argument('--column', default="Description", help='Column to group the transactions by. Must match to a column name in --transactions_file')
    parser.add_argument('--sum_period', default="Monthly", choices=sum_period_choices, help='The period of summation to use on the transactions when building the report.')

    args = parser.parse_args()

    # Check that arguments are valid
    # Make sure action was passed
    if args.action is None:
        msg = "Error: --action argument must be passed. {}".format(add_help)
        raise argparse.ArgumentError(msg)

    # See if we are missing any arguments
    for a in args.action:
        for key in actions_args_dict[a]:
            if key not in vars(args).keys():
                msg = "Error: The argument --{} is required when passing the argument --action {}. {}".format(key, args.action, add_help)
                raise argparse.ArgumentError(msg)

    # CategoriesByPattern
    if "CategoriesByPattern" in args.action and not os.path.exists(args.transactions_file):
        msg = "Error: --transactions_file must point to a valid file when passing the argument --action ParseTransactions. {}".format(add_help)
        raise argparse.ArgumentError(msg)
    if "CategoriesByPattern" in args.action and not os.path.exists(args.pattern_file):
        msg = "Error: --pattern_file must point to a valid file when passing the argument --action ParseTransactions. {}".format(add_help)
        raise argparse.ArgumentError(msg)

    # CategoriesByColumn
    if "CategoriesByColumn" in args.action and not os.path.exists(args.transactions_file):
        msg = "Error: --transactions_file must point to a valid file when passing the argument --action ParseTransactions. {}".format(add_help)
        raise argparse.ArgumentError(msg)

    return args


def main():
    args = get_args()
    for a in args.action:
        if a == "CategoriesByPattern":
            categories_by_pattern(args)
        elif a == "CategoriesByColumn":
            categories_by_column(args)


def categories_by_pattern(args):
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
            header_text = line
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


def categories_by_column(args):
    category_dict = {}

    # Read in all transactions
    with open(args.transactions_file, 'r') as file_in_transactions:
        file_lines = file_in_transactions.readlines()

    count = 0
    header_text = ""
    for line in file_lines:
        # Don't parse first line
        if count == 0:
            header_text = line
            count += 1
            continue

        # Split the columns
        line_split = line.split("\",\"")
        line_split[0] = line_split[0].lstrip('"')
        line_split[-1] = line_split[-1].lstrip('"\n')

        # Extract date and make date formats match
        date_str_temp = get_column_value("Date", line, header_text)
        date_obj = datetime.strptime(date_str_temp, "%m/%d/%Y")
        date_str = get_date_key(args, date_obj)

        # Extract description
        column_key = get_column_value(args.column, line, header_text)

        # Extract amount
        amount_flt = float(line_split[3])

        # Add month to dict
        if date_str not in category_dict.keys():
            category_dict[date_str] = {}

        # Add transaction to dict
        if column_key not in category_dict[date_str].keys():
            category_dict[date_str][column_key] = amount_flt
        else:
            category_dict[date_str][column_key] = category_dict[date_str][column_key] + amount_flt

    # Write dictionary to json file
    with open(args.output_file, 'w') as file_out:
        json.dump(category_dict, file_out, sort_keys=True, indent=4, ensure_ascii=False)


def get_column_value(column, line, header_line):
    # Split the header
    header_line_split = header_line.split("\",\"")
    header_line_split[0] = header_line_split[0].lstrip('"')
    header_line_split[-1] = header_line_split[-1].lstrip('"\n')

    # Split the columns
    line_split = line.split("\",\"")
    line_split[0] = line_split[0].lstrip('"')
    line_split[-1] = line_split[-1].lstrip('"\n')

    for key, value in zip(header_line_split, line_split):
        if key == column:
            return value
    return ""


def get_date_key(args, date_obj):
    date_str = ""

    # Nothing need to be done here
    if args.sum_period == "Daily":
        date_str = date_obj.strftime("%Y-%m-%d")

    # Need to set date_obj to nearest week
    elif args.sum_period == "Weekly":
        # 1st week
        if date_obj.day < 8:
            date_str = date_obj.strftime("%Y-%m-01 to %Y-%m-07")
        # 2nd week
        elif date_obj.day < 15:
            date_str = date_obj.strftime("%Y-%m-08 to %Y-%m-14")
        # 3rd week
        elif date_obj.day < 22:
            date_str = date_obj.strftime("%Y-%m-15 to %Y-%m-21")
        # 4th week
        else:
            last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
            date_str = date_obj.strftime("%Y-%m-22 to %Y-%m-{}".format(last_day))

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
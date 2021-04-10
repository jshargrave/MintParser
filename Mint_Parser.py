from datetime import datetime
import calendar
import argparse
import json
import copy
import re
import os


def get_args():
    action_choices = ["GroupByPatternFile", "GroupByColumnValue", "GroupBySearchPattern"]
    date_period_choices = ["Daily", "Weekly", "Monthly", "Yearly"]
    add_help = "Pass the -h argument for more information"
    actions_args_dict = {
        "GroupByPatternFile": [
            "transactions_file",
            "pattern_file",
            "output_file",
            "date_period",
            "date_column",
            "amount_column",
        ],
        "GroupByColumnValue": [
            "transactions_file",
            "output_file",
            "date_period",
            "categorize_column",
            "date_column",
            "amount_column",
        ],
        "GroupBySearchPattern": [
            "transactions_file",
            "search_pattern",
            "output_file",
            "date_period",
            "date_column",
            "amount_column",
        ],
    }

    usage = " Mint_Parser.py [-h]\n" \
            "                       --action GroupByPatternFile --transactions_file TRANSACTIONS_FILE --pattern_file PATTERN_FILE\n" \
            "                       --action GroupByColumnValue --transactions_file TRANSACTIONS_FILE --categorize_column CATEGORIZE_COLUMN\n" \
            "                       --action GroupBySearchPattern --transactions_file TRANSACTIONS_FILE --search_pattern SEARCH_PATTERN\n"

    parser = argparse.ArgumentParser(description='Used to process arguments passed to the Mint_Parser.py.', usage=usage)

    parser.add_argument('--action', default=["GroupByPatternFile"], nargs='+', choices=action_choices, help='List of actions to perform. Can be one or multiples of the following: \"{}\"'.format("\" \"".join(action_choices)))
    parser.add_argument('--transactions_file', default="transactions.csv", help='Used to point to the transaction file exported from Mint. Default is transactions.csv.')
    parser.add_argument('--pattern_file', default="category_patterns_default.json", help='JSON file that contains a series of regular expressions to match patterns in the --transactions_file. See category_patterns_default.json for an example.')
    parser.add_argument('--search_pattern', help='Regular expression to use for searching through transactions.')
    parser.add_argument('--output_file', default="output.json", help='File to output the results to.')
    parser.add_argument('--date_period', default="Monthly", choices=date_period_choices, help='The period of summation to use on the transactions when building the report. Can be one of the following: \"{}\"'.format("\" \"".join(date_period_choices)))
    parser.add_argument('--categorize_column', default="Category", help='Column to group transactions by. Must match to a column name in --transactions_file')
    parser.add_argument('--date_column', default="Date", help='Column to extract the amount date from. Must match a column name in --transactions_file')
    parser.add_argument('--amount_column', default="Amount", help='Column to extract the amount from. Must match a column name in --transactions_file')

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
                msg = "Error: The argument --{} is required when passing the argument --action {}. {}".format(key, ", ".join(args.action), add_help)
                raise argparse.ArgumentError(msg)

    # GroupByPatternFile
    if "GroupByPatternFile" in args.action and not os.path.exists(args.transactions_file):
        msg = "Error: --transactions_file must point to a valid file when passing the argument --action GroupByPatternFile. {}".format(add_help)
        raise argparse.ArgumentError(msg)
    if "GroupByPatternFile" in args.action and not os.path.exists(args.pattern_file):
        msg = "Error: --pattern_file must point to a valid file when passing the argument --action GroupByPatternFile. {}".format(add_help)
        raise argparse.ArgumentError(msg)

    # GroupByColumnValue
    if "GroupByColumnValue" in args.action and not os.path.exists(args.transactions_file):
        msg = "Error: --transactions_file must point to a valid file when passing the argument --action GroupByColumnValue. {}".format(add_help)
        raise argparse.ArgumentError(msg)

    # GroupBySearchPattern
    if "GroupBySearchPattern" in args.action and not os.path.exists(args.transactions_file):
        msg = "Error: --transactions_file must point to a valid file when passing the argument --action GroupBySearchPattern. {}".format(add_help)
        raise argparse.ArgumentError(msg)

    return args


def main():
    args = get_args()
    for a in args.action:
        if a == "GroupByPatternFile":
            group_by_pattern_file(args)
        elif a == "GroupByColumnValue":
            group_by_column_value(args)
        elif a == "GroupBySearchPattern":
            group_by_search_pattern(args)


def group_by_pattern_file(args):
    temp_category_dict = {
        "Total": 0,
        "Transactions": [],
        args.date_period: {},
    }
    category_dict = {}

    # Check that transactions file is valid path before opening
    if not os.path.exists(args.transactions_file):
        print("Error: {} not found.".format(args.transactions_file))
        print("Override by passing path to --transactions_file if needed.")
        exit(1)

    # Read in all transactions
    with open(args.transactions_file, 'r') as file_in_transactions:
        file_lines = file_in_transactions.readlines()

    # Check that pattern file is valid path before opening
    if not os.path.exists(args.pattern_file):
        print("Error: {} not found.".format(args.pattern_file))
        print("Override by passing path to --pattern_file if needed.")
        exit(1)

    # Read in all patterns
    try:
        with open(args.pattern_file, 'r') as file_in_pattern:
            category_dict_pattern = json.load(file_in_pattern)
    except ValueError as err:
        print("Error: {} is not valid json.\n{}".format(args.pattern_file, err))
        exit(1)

    count = 0
    header_text = ""
    for line in file_lines:
        # Don't parse first line
        if count == 0:
            header_text = line
            count += 1
            continue

        # Extract date and make date formats match
        date_str = get_column_value(args.date_column, line, header_text)
        date_key = get_date_key(args, date_str)

        # Extract amount
        amount_flt = float(get_column_value(args.amount_column, line, header_text))

        found_match = False
        for key, value in category_dict_pattern.items():
            for pattern in value:
                match = re.findall(pattern, line)
                if match:
                    found_match = True
                    if key not in category_dict.keys():
                        category_dict[key] = copy.deepcopy(temp_category_dict)

                    if date_key not in category_dict[key][args.date_period].keys():
                        category_dict[key][args.date_period][date_key] = amount_flt
                    else:
                        category_dict[key][args.date_period][date_key] += amount_flt

                    category_dict[key]["Transactions"].append(line)
                    category_dict[key]["Total"] += amount_flt

                    # If match was found, then continue to next line
                    break
            if found_match:
                break

        # Record the transaction if no pattern matched it
        if not found_match:
            key = "NO_MATCH"
            if key not in category_dict.keys():
                category_dict[key] = copy.deepcopy(temp_category_dict)

            if date_key not in category_dict[key][args.date_period].keys():
                category_dict[key][args.date_period][date_key] = amount_flt
            else:
                category_dict[key][args.date_period][date_key] += amount_flt

            category_dict[key]["Transactions"].append(line)
            category_dict[key]["Total"] += amount_flt
        count += 1

    # Write dictionary to json file
    with open(args.output_file, 'w') as file_out:
        json.dump(category_dict, file_out, sort_keys=True, indent=4, ensure_ascii=False)


def group_by_column_value(args):
    temp_category_dict = {
        "Total": 0,
        "Transactions": [],
        args.date_period: {},
    }
    category_dict = {}

    # Check that transactions file is valid path before opening
    if not os.path.exists(args.transactions_file):
        print("Error: {} not found.".format(args.transactions_file))
        print("Override by passing path to --transactions_file if needed.")
        exit(1)

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

        # Extract date and make date formats match
        date_str = get_column_value(args.date_column, line, header_text)
        date_key = get_date_key(args, date_str)

        # Extract column to group by
        column_key = get_column_value(args.categorize_column, line, header_text)

        # Extract amount
        amount_flt = float(get_column_value(args.amount_column, line, header_text))

        if column_key not in category_dict.keys():
            category_dict[column_key] = copy.deepcopy(temp_category_dict)

        if date_key not in category_dict[column_key][args.date_period]:
            category_dict[column_key][args.date_period][date_key] = amount_flt
        else:
            category_dict[column_key][args.date_period][date_key] += amount_flt

        if date_key not in category_dict[column_key][args.date_period]:
            category_dict[column_key][args.date_period][date_key] = {}

        category_dict[column_key]["Transactions"].append(line)
        category_dict[column_key]["Total"] += amount_flt

        count += 1

    # Write dictionary to json file
    with open(args.output_file, 'w') as file_out:
        json.dump(category_dict, file_out, sort_keys=True, indent=4, ensure_ascii=False)


def group_by_search_pattern(args):
    category_dict = {
        "Total": 0,
        "Transactions": [],
        args.date_period: {},
    }

    # Check that transactions file is valid path before opening
    if not os.path.exists(args.transactions_file):
        print("Error: {} not found.".format(args.transactions_file))
        print("Override by passing path to --transactions_file if needed.")
        exit(1)

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

        # Extract date and make date formats match
        date_str = get_column_value(args.date_column, line, header_text)
        date_key = get_date_key(args, date_str)

        # Extract amount
        amount_flt = float(get_column_value(args.amount_column, line, header_text))

        match = re.findall(args.search_pattern, line)
        if match:
            if date_key not in category_dict[args.date_period]:
                category_dict[args.date_period][date_key] = amount_flt
            else:
                category_dict[args.date_period][date_key] += amount_flt

            category_dict["Transactions"].append(line)
            category_dict["Total"] += amount_flt
        count += 1

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


def get_date_key(args, date_str):
    date_key = date_str
    date_obj = datetime.strptime(date_str, "%m/%d/%Y")

    # Nothing need to be done here
    if args.date_period == "Daily":
        date_key = date_obj.strftime("%Y-%m-%d")

    # Need to set date_obj to nearest week
    elif args.date_period == "Weekly":
        # 1st week
        if date_obj.day < 8:
            date_key = date_obj.strftime("%Y-%m-01 to %Y-%m-07")
        # 2nd week
        elif date_obj.day < 15:
            date_key = date_obj.strftime("%Y-%m-08 to %Y-%m-14")
        # 3rd week
        elif date_obj.day < 22:
            date_key = date_obj.strftime("%Y-%m-15 to %Y-%m-21")
        # 4th week
        else:
            last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
            date_key = date_obj.strftime("%Y-%m-22 to %Y-%m-{}".format(last_day))

    # Need to set date_obj to current month
    elif args.date_period == "Monthly":
        date_key = date_obj.strftime("%Y-%m")

    # Need to set date_obj to current year
    elif args.date_period == "Yearly":
        date_key = date_obj.strftime("%Y")

    # Return date key
    return date_key


if __name__ == "__main__":
    main()
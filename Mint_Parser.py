from datetime import datetime
import calendar
import argparse
import json
import copy
import csv
import re
import os


def get_args():
    action_choices = ["GroupByPatternFile", "GroupByColumnValue", "GroupBySearchPattern"]
    date_period_choices = ["Real", "Daily", "Biweekly", "Weekly", "Monthly", "Yearly"]
    valid_file_args = ["transactions_file", "pattern_file"]
    add_help = "Pass the -h argument for more information"
    actions_args_dict = {
        "GroupByPatternFile": [
            "transactions_file",
            "pattern_file",
            "output_file_json",
            "output_file_csv",
            "date_period",
            "date_column",
            "amount_column",
        ],
        "GroupByColumnValue": [
            "transactions_file",
            "categorize_column",
            "output_file_json",
            "output_file_csv",
            "date_period",
            "date_column",
            "amount_column",
        ],
        "GroupBySearchPattern": [
            "transactions_file",
            "search_pattern",
            "output_file_json",
            "output_file_csv",
            "date_period",
            "date_column",
            "amount_column",
        ],
    }

    usage = " Mint_Parser.py [-h]\n" \
            "                       --action GroupByPatternFile --pattern_file PATTERN_FILE\n" \
            "                       --action GroupByColumnValue --categorize_column CATEGORIZE_COLUMN\n" \
            "                       --action GroupBySearchPattern --search_pattern SEARCH_PATTERN\n"

    parser = argparse.ArgumentParser(description='Used to process arguments passed to the Mint_Parser.py.', usage=usage)

    parser.add_argument('--action', nargs='+', choices=action_choices, help='List of actions to perform. Can be one or multiples of the following: \"{}\"'.format("\" \"".join(action_choices)))
    parser.add_argument('--transactions_file', default="transactions.csv", help='Used to point to the transaction file exported from Mint. Default is transactions.csv.')
    parser.add_argument('--pattern_file', default="category_patterns_default.json", help='JSON file that contains a series of regular expressions to match patterns in the --transactions_file. See category_patterns_default.json for an example.')
    parser.add_argument('--search_pattern', help='Regular expression to use for searching through transactions.')
    parser.add_argument('--output_file_json', default="output.json", help='File to output the json results to.')
    parser.add_argument('--output_file_csv', default="output.csv", help='File to output the csv results to.')
    parser.add_argument('--date_period', choices=date_period_choices, help='The period of summation to use on the transactions when building the report. Can be one of the following: \"{}\"'.format("\" \"".join(date_period_choices)))
    parser.add_argument('--categorize_column', default="Category", help='Column to group transactions by. Must match to a column name in --transactions_file')
    parser.add_argument('--date_column', default="Date", help='Column to extract the amount date from. Must match a column name in --transactions_file')
    parser.add_argument('--amount_column', default="Amount", help='Column to extract the amount from. Must match a column name in --transactions_file')

    # Optional arguments
    parser.add_argument('--start_date', help='Column to extract the amount from. Must match a column name in --transactions_file')
    parser.add_argument('--end_date', help='Column to extract the amount from. Must match a column name in --transactions_file')
    parser.add_argument("--user_interface", type=str2bool, nargs='?', const=True, default=True, help='Can be used to disable user interface.  Any requests for argument values will result in a exception being thrown.')

    args = parser.parse_args()

    # Check that arguments are valid
    # Make sure action was passed
    if args.action is None:
        msg = "--action argument must be passed. {}".format(add_help)
        args.action = request_arg(args, msg, action_choices, True)
        if args.action is None:
            parser.error(msg)

    # See if we are missing any arguments
    for a in args.action:
        for key in actions_args_dict[a]:
            if key not in vars(args).keys() or vars(args)[key] is None:
                msg = "The argument --{} is required when passing the argument --action {}. {}".format(key, ", ".join(args.action), add_help)
                if key == "date_period":
                    vars(args)[key] = request_arg(args, msg, date_period_choices)
                else:
                    vars(args)[key] = request_arg(args, msg)
                if key not in vars(args).keys() or vars(args)[key] is None:
                    parser.error(msg)
            elif key in valid_file_args and not os.path.exists(vars(args)[key]):
                msg = "Argument --{} does not point to a valid file ({}). {}".format(key, vars(args)[key], add_help)
                vars(args)[key] = request_arg(args, msg)
                if not os.path.exists(vars(args)[key]):
                    parser.error(msg)

    return args


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def request_arg(args, msg, choices=None, allow_multiples=False):
    # If user interface disabled, then just return None
    if not args.user_interface:
        return None

    print(msg)

    # List of choice was passed
    if choices:
        choice_dict = {str(i + 1): choices[i] for i in range(0, len(choices))}

        for key, value in choice_dict.items():
            print("{}. {}".format(key, value))

        # User can select a list of values for the argument
        if allow_multiples:
            user_input = input("Pick a space separated list of numbers for the argument value now... ")
            print("")
            user_input = user_input.strip(" ")
            user_input_split = user_input.split(" ")
            arg_choice_list = []
            for i in user_input_split:
                if i not in choice_dict.keys():
                    return None
                else:
                    arg_choice_list.append(choice_dict[i])
            return arg_choice_list
        else:
            user_input = input("Pick a number for the argument value now... ")
            print("")

            if user_input in choice_dict.keys():
                return choice_dict[user_input]
            else:
                return None
    else:
        user_input = input("Enter the value for the argument now... ")
        print("")

        if user_input:
            return user_input
        else:
            return None


def main():
    args = get_args()
    for a in args.action:
        # If this a multiple action run, we want to change the output file so that we don't overwrite results
        if len(args.action) > 1:
            split_file_json = os.path.splitext(args.output_file_json)
            args.output_file_json = "{}-{}{}".format(split_file_json[0], a, split_file_json[1])
            split_file_csv = os.path.splitext(args.output_file_csv)
            args.output_file_csv = "{}-{}{}".format(split_file_csv[0], a, split_file_csv[1])

        # Run action
        print("Running {} action".format(a))
        if a == "GroupByPatternFile":
            group_by_pattern_file(args)
        elif a == "GroupByColumnValue":
            group_by_column_value(args)
        elif a == "GroupBySearchPattern":
            group_by_search_pattern(args)
        print("Output results to {} and {}".format(args.output_file_json, args.output_file_csv))


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

                    # Save to category_dict
                    add_transaction_json(args, category_dict, key, date_key, amount_flt, line)

                    # If match was found, then continue to next line
                    break
            if found_match:
                break

        # Record the transaction if no pattern matched it
        if not found_match:
            key = "NO_MATCH"

            # Save to category_dict
            add_transaction_json(args, category_dict, key, date_key, amount_flt, line)
        count += 1

    # Write date to files
    save_transaction_json(args, category_dict)
    save_transaction_csv(args, category_dict)


def group_by_column_value(args):
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

        # Save to category_dict
        add_transaction_json(args, category_dict, column_key, date_key, amount_flt, line)

        count += 1

    # Write date to files
    save_transaction_json(args, category_dict)
    save_transaction_csv(args, category_dict)


def group_by_search_pattern(args):
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

        # Extract amount
        amount_flt = float(get_column_value(args.amount_column, line, header_text))

        match = re.findall(args.search_pattern, line)
        if match:
            # Save to category_dict
            add_transaction_json(args, category_dict, args.search_pattern, date_key, amount_flt, line)
        count += 1

    # Write date to files
    save_transaction_json(args, category_dict)
    save_transaction_csv(args, category_dict)


def add_transaction_json(args, category_dict, key, date_key, amount_flt, line):
    temp_category_dict = {
        "Total": 0,
        "Transactions": [],
        args.date_period: {},
    }

    if key not in category_dict.keys():
        category_dict[key] = copy.deepcopy(temp_category_dict)

    if date_key not in category_dict[key][args.date_period]:
        category_dict[key][args.date_period][date_key] = amount_flt
    else:
        category_dict[key][args.date_period][date_key] += amount_flt

    category_dict[key]["Transactions"].append(line)
    category_dict[key]["Total"] += amount_flt


def save_transaction_json(args, category_dict):
    # Write dictionary to json file
    with open(args.output_file_json, 'w') as file_out:
        json.dump(category_dict, file_out, sort_keys=True, indent=4, ensure_ascii=False)


def save_transaction_csv(args, category_dict):
    with open(args.output_file_csv, 'w', newline='') as file_out:
        # Writing header
        fieldnames = ['Key', "{} Date".format(args.date_period), "{} Total".format(args.date_period), 'Total']
        writer = csv.DictWriter(file_out, fieldnames=fieldnames)
        writer.writeheader()

        for key1, value1 in category_dict.items():
            count = 0
            for key2, value2 in value1[args.date_period].items():
                if count == 0:
                    writer.writerow({"Key": key1, "Total": value1["Total"], "{} Date".format(args.date_period): key2, "{} Total".format(args.date_period): value2})
                else:
                    writer.writerow({"{} Date".format(args.date_period): key2, "{} Total".format(args.date_period): value2})
                count += 1
            # Skip a line
            writer.writerow({"Key": ""})


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
    # Set date-key to date_str just in case no if condition pass
    date_key = date_str

    # Don't group by date, just convert to common format
    if args.date_period == "Real":
        date_key = date_str
    else:
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")

        # Nothing need to be done here
        if args.date_period == "Daily":
            date_key = date_obj.strftime("%Y-%m-%d")

        # Return back the date range of 1 week
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

        # Return back the date range of 2 weeks
        elif args.date_period == "Biweekly":
            # Weeks 1 and 2
            if date_obj.day < 15:
                date_key = date_obj.strftime("%Y-%m-01 to %Y-%m-14")
            # Weeks 3 and 4
            else:
                last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
                date_key = date_obj.strftime("%Y-%m-15 to %Y-%m-{}".format(last_day))

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
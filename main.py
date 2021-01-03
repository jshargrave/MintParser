from datetime import datetime
import json
import re

trans_file = "transactions.csv"
output_file = "transactions_parsed.csv"
output_monthly_file = "transactions_parsed_monthly.csv"




def main():
    file_in = open(trans_file, 'r')
    file_in_cat = open("category_patterns.json", 'r')
    file_out = open(output_file, 'w')
    file_out_monthly = open(output_monthly_file, 'w')

    category_dict_pattern = json.load(file_in_cat)
    category_dict = {}

    description_list = []

    # Get next line from file
    file_lines = file_in.readlines()
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
        month_str = "{}-{}".format(match.group(1), match.group(2))

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

        # Extract description
        match = re.match("\"[0-9/]+\",\"([a-zA-Z0-9-#*.'-~&%$ ]+)\"", line)
        if match:
            if match.group(1) not in description_list:
                description_list.append(match.group(1))
        else:
            print("failed to match with\n{}".format(line))

    description_list.sort()

    file_in.close()
    file_out.close()
    file_out_monthly.close()


if __name__ == "__main__":
    main()
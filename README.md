# Mint_Parser
Used to parse the transactions exported from Mint into useful categories to perform analysis on

# Arguments
## --action
List of actions to perform.  Currently there is only one action that can be passed, which is ParseTransactions.
## --transactions_file
Used to point to the transaction file that was exported from Mint. Default is transactions.csv.
## --pattern_file
JSON file that contains a series of patterns. See category_patterns.json.template for an example. The patterns are regulare expressions.
## --output_file
File to output the results of matching the patterns from the --pattern_file argument.

# Usage
Currently the only real usage is to break up multiple transactions into their own specific categories based on the regular expression patterns that get defined.  Someone wishing to use this program should do the following.
1. Export a list of all transactions from Mint by:
1. Navigating to [https://www.mint.com/](https://www.mint.com/).
1. Log in.
1. Click on the Transactions tab.
1. Scroll all the way to the bottom and click the 'export all ### transactions.' You will have some number in the place of ###.
1. Save the transactions.csv somewhere where it will be easily accessible.  Additionally you can download the same link by following the [link](https://mint.intuit.com/transactionDownload.event?queryNew=&offset=0&filterType=cash&comparableType=8) after logging in.
1. Navigate to the project directory and call the python file using the following command.
`Python Mint_Parser.py --action ParseTransactions`

# MintParser
This is a small tool that attempts to parse Mint.com Transaction data in a more useful format.  The idea is that the user has complete control over how transactions are grouped together using Regular Expressions and arguemnts passed to the tool.  Transactions are grouped using a pattern to search for and a date period to group them by.

# Motivation
I've been using Mint.com for serveral years now for tracking all of transactions accross multiple accounts.  Mint.com makes easy to add accounts and record transactions that occur.  The problem I find is that Mint.com often makes mistakes in how it categorizes transactions.  Often they will get added to the completely wrong category.  Further more there is now way to setup rules to add them automatically to the correct category.  IF I wanted to do it in Mint.com I would have to update each miscategorized transaction manually.

I considered trying to standup a API that would login, pull data, make modifications, ect.  This seemed way more effort than it was worth.  If that is something you are interested in I would look at [mintapi](https://github.com/mrooney/mintapi).

One helpful this is the Mint.com allows you to export all of your transactions.  I then spent some time in Google Sheets importing the data, modifying, and then producing some sheets.  Using Google Sheets definitely makes it easy when working with the data.  I still had the problem of correctly grouping transactions together that were miscategorized.

This led me to think if only there was a way to quickly parse the transactions and group them using Regular Expressions.  That is when I started working on MintParser.  MintParser will take a series of Regular Expressions and searches the Mint.com transactions and groups them together by the matches and a date period.

Technically MintParser supports any csv formatted transaction document.  You only need to override a few arguments that are defaulted to work for Mint.com Transactions.  Just need to tell which columns contain the amount and date information.

# Arguments
# <a name="arguments"></a>
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
1. Export a list of all transactions from Mint by navigating to [https://www.mint.com/](https://www.mint.com/).
1. Log in.
1. Click on the Transactions tab.
1. Scroll all the way to the bottom and click the 'export all ### transactions.' You will have some number in the place of ###.
1. Save the transactions.csv somewhere where it will be easily accessible.
1. Rename the category_patterns.json.template to category_patterns.json.
1. Inside this file we want to define how we will break up the transactions.  Each entry to this file should start with a key to array of strings.  The key will be the name of the group of transactions that matched.  Inside the key's array the user should define the lists of regular expressions to match to the transactions. After the user has finished editing this file they can proceed to the next step.  Note that any transaction that matches a pattern will not match another pattern from the same or a different group.  If no match is found, then the transaction is saved underneath the "NO_MATCH" group.
1. Navigate to the project directory and call the python file using the following command. `Python Mint_Parser.py --action ParseTransactions` For information on what arguments can be passed see the [Arguments](#arguments) section.

# Examples
category_patterns.json
~~~
{
	"DEPOSIT CHECKS": 
	[
		".*eCheck Deposit.*"
	]
}
~~~

output.json
~~~
    "DEPOSIT CHECKS": {
        "Monthly": {
            "2018-03": 1322.0,
            "2018-04": 1102.29,
            "2018-05": 3525.65,
            "2018-06": 197.75,
            "2019-03": 87.58,
            "2020-03": 80.0,
            "2020-09": 340.0,
            "2020-12": 4.29
        },
        "Total": 6659.5599999999995,
        "Transactions": [
            "\"12/28/2020\",\"eCheck Deposit\",\"eCheck Deposit\",\"4.29\",\"credit\",\"Income\",\"Interest Checking\",\"\",\"\"\n",
            "\"9/17/2020\",\"eCheck Deposit\",\"eCheck Deposit\",\"300.00\",\"credit\",\"Income\",\"Interest Checking\",\"\",\"\"\n",
            "\"9/02/2020\",\"eCheck Deposit\",\"eCheck Deposit\",\"40.00\",\"credit\",\"Income\",\"Interest Checking\",\"\",\"\"\n",
            "\"3/30/2020\",\"eCheck Deposit\",\"eCheck Deposit\",\"80.00\",\"credit\",\"Income\",\"Interest Checking\",\"\",\"\"\n",
            "\"3/13/2019\",\"Echeck Deposit\",\"eCheck Deposit\",\"87.58\",\"credit\",\"Income\",\"Interest Checking\",\"\",\"\"\n",
            "\"6/19/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"197.75\",\"credit\",\"Income\",\"Interest Checking\",\"\",\"\"\n",
            "\"5/14/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"3523.00\",\"credit\",\"Income\",\"Emergency Fund\",\"\",\"\"\n",
            "\"5/04/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"2.65\",\"credit\",\"Income\",\"Interest Checking\",\"\",\"\"\n",
            "\"4/16/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"597.71\",\"credit\",\"Income\",\"Interest Checking\",\"\",\"\"\n",
            "\"4/02/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"504.58\",\"credit\",\"Income\",\"Interest Checking\",\"\",\"\"\n",
            "\"3/09/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"1322.00\",\"credit\",\"Income\",\"Interest Checking\",\"\",\"\"\n"
        ]
    },
~~~

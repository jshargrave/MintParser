# MintParser
This is a small tool that attempts to parse Mint.com Transaction data in a more useful format.  The idea is that the user has complete control over how transactions are grouped together using Regular Expressions and arguemnts passed to the tool.  Transactions are grouped using a pattern to search for and a date period to group them by.

Technically MintParser supports any csv formatted transaction document.  You only need to override a few arguments that are defaulted to work for Mint.com Transactions.  You will need to tell it which columns contain the amount and date information.  That is it.

MintParser supports a user interface but all arguments required can be provided from the command line to allow for a user free interaction run.

# Motivation
I've been using Mint.com for serveral years now for tracking all of transactions accross multiple accounts.  Mint.com makes easy to add accounts and record transactions that occur.  The problem I find is that Mint.com often makes mistakes in how it categorizes transactions.  Often they will get added to the completely wrong category.  Further more there is now way to setup rules to add them automatically to the correct category.  IF I wanted to do it in Mint.com I would have to update each miscategorized transaction manually.

I considered trying to standup a API that would login, pull data, make modifications, ect.  This seemed way more effort than it was worth.  If that is something you are interested in I would look at [mintapi](https://github.com/mrooney/mintapi).

One helpful this is the Mint.com allows you to export all of your transactions.  I then spent some time in Google Sheets importing the data, modifying, and then producing some sheets.  Using Google Sheets definitely makes it easy when working with the data.  I still had the problem of correctly grouping transactions together that were miscategorized.

This led me to think if only there was a way to quickly parse the transactions and group them using Regular Expressions.  That is when I started working on MintParser.  MintParser will take a series of Regular Expressions and searches the Mint.com transactions and groups them together by the matches and a date period.

# Quick Start
1. Clone repo
1. Export all transactions from Mint.com by navigating to [https://www.mint.com/](https://www.mint.com/) and logging in.
1. Click on the Transactions tab. Scroll all the way to the bottom and click the "export all ### transactions" link. You will have some number in the place of ###.
1. Drop the csv file into the same directory where you cloned the repo.
1. Run Mint_Parser.py

# Usage
MintParser can be run with the following commands.  There are several additional arguments you can pass to override the values.  Normally the default value is taken unless there is something wrong with that value like pointing to a invalid file path.  Additionally some values will be requested from the user if not provided like --action or --date_period.
~~~
Mint_Parser.py [-h]
               --action GroupByPatternFile   --pattern_file      PATTERN_FILE
               --action GroupByColumnValue   --categorize_column CATEGORIZE_COLUMN
               --action GroupBySearchPattern --search_pattern    SEARCH_PATTERN
~~~

## Arguments
List of arguements below.  I go into further detail about the usage and values of each argument below.
~~~
--action            ACTION	        List of actions to perform
--transactions_file TRANSACTION_FILE    Transactions file from Mint.com
--pattern_file      PATTERN_FILE        Pattern file contain series of Regular Expressions
--categorize_column CATEGORIZE_COLUMN   Column to group transactions by
--search_pattern    SEARCH_PATTERN      Search pattern to group transactions by
--output_file       OUTPUT_FILE         Output file where results are written
--date_period       DATE_PERIOD         Date period to group matching transactions by
--date_column       DATE_COLUMN         Column in --transactions_file to extract date from
--amount_column     AMOUNT_COLUMN       Column in --transactions_file to extract amount from
~~~

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

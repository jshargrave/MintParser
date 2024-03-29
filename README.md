# MintParser
This is a small tool that parses Mint.com Transaction data in a more useful format.  The idea is that the user has complete control over how transactions are grouped together using Regular Expressions and arguemnts passed to the tool.  Transactions are grouped using a pattern to search for and a date period to group them by.

Technically MintParser supports any csv formatted transaction document.  You only need to override a few arguments that are defaulted to work for Mint.com Transactions.  You will need to tell it which columns contain the amount and date information.  That is it.

MintParser supports a user interface but all arguments required can be provided from the command line to allow for a user free interaction run.

# Requirements
Python 3

# Motivation
I've been using Mint.com for serveral years now for tracking all of transactions accross multiple accounts.  Mint.com makes easy to add accounts and record transactions that occur.  The problem I find is that Mint.com often makes mistakes in how it categorizes transactions.  Often they will get added to the completely wrong category.  Further more there is now way to setup rules to add them automatically to the correct category.  IF I wanted to do it in Mint.com I would have to update each miscategorized transaction manually.

I considered trying to standup a API that would login, pull data, make modifications, ect.  This seemed way more effort than it was worth.  If that is something you are interested in I would look at [mintapi](https://github.com/mrooney/mintapi).

One helpful this is the Mint.com allows you to export all of your transactions.  I then spent some time in Google Sheets importing the data, modifying, and then producing some sheets.  Using Google Sheets definitely makes it easy when working with the data.  I still had the problem of correctly grouping transactions together that were miscategorized.

This led me to think if only there was a way to quickly parse the transactions and group them using Regular Expressions.  That is when I started working on MintParser.  MintParser will take a series of Regular Expressions and searches the Mint.com transactions and groups them together by the matches and a date period.

Once I got going I was able to calculate things like income vs. spending similiar to what you see below.
![image](https://user-images.githubusercontent.com/14623411/114279263-9703c080-99e8-11eb-8956-2d441924e368.png)


# Quick Start
1. Clone repo
1. Export all transactions from Mint.com by navigating to [https://www.mint.com/](https://www.mint.com/) and logging in.
1. Click on the Transactions tab. Scroll all the way to the bottom and click the "export all ### transactions" link. You will have some number in the place of ###.
1. Drop the csv transactions file into the cloned repo directory.
1. Run Mint_Parser.py

# Usage
MintParser can be run with the following commands.  There are several additional arguments you can pass to override the values.  Normally the default value is taken unless there is something wrong with that value like pointing to a invalid file path.  Additionally some values will be requested from the user if not provided like [--action](#--action) or [--date_period](#--date_period).
~~~
Mint_Parser.py [-h]
               --action GroupByPatternFile   --pattern_file      PATTERN_FILE
               --action GroupByColumnValue   --categorize_column CATEGORIZE_COLUMN
               --action GroupBySearchPattern --search_pattern    SEARCH_PATTERN
~~~

## Arguments
List of arguements below.  I go into further detail about the usage and values of each argument below.  If argument only takes a list of values then those values are listed.  Otherwise the argument name is repeated with all upercase to indicate that it needs to be replaced with a real value.
~~~
--action            			GroupByPatternFile			List of actions to perform
		    			GroupByColumnValue
		    			GroupBySearchPattern	        
--transactions_file 		     	TRANSACTION_FILE    			Transactions file from Mint.com
--transactions_file_search_pattern   	TRANSACTIONS_FILE_SEARCH_PATTERN 	Used to search for transaction files when one was not provided.
--transactions_file_search_directory 	TRANSACTIONS_FILE_SEARCH_DIRECTORY 	Used to search for transaction files when one was not provided.
--pattern_file      			PATTERN_FILE        			Pattern file contain series of Regular Expressions
--categorize_column 			CATEGORIZE_COLUMN   			Column to group transactions by
--search_pattern    			SEARCH_PATTERN      			Search pattern to group transactions by
--output_file_json  			OUTPUT_FILE_JSON    			Output file where results are written
--output_file_csv   			OUTPUT_FILE_CSV     			Output file where results are written
--date_period       			Real					Date period to group matching transactions by
		    			Daily
		    			Biweekly
		    			Weekly
		    			Monthly
		    			Yearly         		
--date_format       			DATE_FORMAT				The format of the date in the --transaction_file
--date_column       			DATE_COLUMN         			Column in --transactions_file to extract date from
--date_range        			All					The date range to parse transactions
		    			YTD
		    			Year
		    			CurrentMonth
		    			PreviousMonth
		    			Custom
--amount_column     			AMOUNT_COLUMN       			Column in --transactions_file to extract amount from

------------------------------------------------------------(Optional)----------------------------------------------------------------------
--start_date        			START_DATE				Start date to start searching for transactions
--end_date          			END_DATE				End date to stop searching for transactions
--user_interface    			True					Enable or disable user interface
		    			False								
~~~

### --action
The --action argument is the most high level argument there is.  It is the argument that tells MintParser which logic to run.  Valid values are "GroupByPatternFile", "GroupByColumnValue", "GroupBySearchPattern".

### --action GroupByPatternFile
This action will group the transactions by utilizing a series of Regular Expressions defined in a json file.  The file that contains the Regular Expressions is defined with the [--pattern_file](#--pattern_file) argument.

### --action GroupByColumnValue
This action will group the transactions based on the value of a column in the csv transactions file.  The column it picks to match is defined by the [--categorize_column](#--categorize_column) argument.

### --action GroupBySearchPattern
This action will group the transactions by utilizing a single Regular Expression passed in.  The Regular Expression is passed by the [--search_pattern](#--search_pattern) argument.

### --transactions_file
This argument points to the csv transactions file exported from Mint.com.  The default value is transactions.csv.  If this is not a valid path the user will be prompted to provide a valid path.

### --transactions_file_search_pattern   	
This argument is used to search for transaction files when the argument [--transactions_file](#--transactions_file) value does not point to a valid file. The default search pattern is transactions*.csv.

### --transactions_file_search_directory
This argument is used to search for transaction files when the argument [--transactions_file](#--transactions_file) vlaue does not point to a valid file. The default directory location is the current run directory.

### --pattern_file
This argument points to the json pattern file that defines all of the regular expressions to group the transactions by.  The default value is category_patterns_default.json which is a file provided in the repo as an example of how to setup you're own pattern file.

### --categorize_column
Stores the column name to retrieve the value from and group the transactions by.  The default value is Category.  Note that there is not smart matching involved.  The value either matches or does not.  This often leads to similiar values found being seperated.

### --search_pattern
The Regular Expression pattern to use when grouping the the transactions together.  Note that this can be a full Regular Expression or just some text you want to search for contained in transactions.

### --output_file_json
Where the results are written.  The default value is output.json.  Note that if you run a query with multiple actions then the action name will be appeneded to the end of the output file to keep from overwriting results.

### --output_file_csv
Where the results are written.  The default value is output.csv.  Note that if you run a query with multiple actions then the action name will be appeneded to the end of the output file to keep from overwriting results.

### --date_period
Argument used to specify what date period to seperate the grouped transactions by.  Valid values are "Real", "Daily", "Weekly", "Biweekly", "Monthly", "Yearly".  The Real option will not modify that date at all and transactions will be grouped by whatever dates match in the --transactions_file.

### --date_format
Can be used to override the date format.  This value is used to parse the date in the --transactions_file, --start_date, and --end_date.  The default is %m/%d/%Y.

### --date_column
Name of the column to extract the date from.  Default value is "Date".  This value can be overwritten if you are using a transactions csv document that is not from Mint.com.

### --date_range
The date_range argument is used to determine what the date range is that the transactions should be parsed.  Valid values are "All", "YTD", "Year", "CurrentMonth", "PreviousMonth", "Custom".  If a "Custom" value is entered then the user will be prompted to enter dates for arguments [--start_date](#--start_date) and [--end_date](#--end_date).

### --amount_column
Name of the column to extract the amount from.  Default value is "Amount".  This value can be overwritten if you are using a transactions csv document that is not from Mint.com.

### --start_date
The start date to start searching for transactions. Enter the date in the same format as [--date_format](#--date_format), if nothing is passed to that argument then use %m/%d/%Y.

### --end_date
The end date to start searching for transactions. Enter the date in the same format as [--date_format](#--date_format), if nothing is passed to that argument then use %m/%d/%Y.

### --user_interface
Can be used to disable the user interface.  Note that if any errors occur a exception will be thrown.  This argument implements a string to bool parsing function.  So it supports a series of values that can be interpreted as true/false.  Some of the values are 'yes', 'true', 't', 'y', '1', 'no', 'false', 'f', 'n', '0'.  An exception is thrown if an invalid value is passed.

# Examples
Currently MintParser only outputs results in a json format.  These results are pretty simple to incorporate into a Excel or Sheets document.  However it become tedious since it requires you to scroll around, select the values you want, and then copy past them into the document.  Future efforts will probably add a csv output support to make it more of a drag and drop to incorporate into your document that does some metrics analysis.

Below are some example output obtained when running the MintParser using a pattern file shown below.


## Pattern File Contents Example
~~~
{
	"DEPOSIT CHECKS": 
	[
		".*eCheck Deposit.*"
	]
}
~~~

## Output File Contents JSON Example
~~~
    "DEPOSIT CHECKS": {
        "Monthly": {
	    "2020-12": 1,199.00,
	    "2020-11": 2,708.00,
	    "2020-10": 1,290.00,
	    "2020-09": 1,597.00,
	    "2020-08": 1,910.00,
	    "2020-07": 2,283.00,
	    "2020-06": 1,788.00,
	    "2020-05": 2,105.00,
	    "2020-04": 2,651.00
        },
        "Total": 6659.5599999999995,
        "Transactions": [
            "\"12/28/2020\",\"eCheck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n",
            "\"9/17/2020\",\"eCheck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n",
            "\"9/02/2020\",\"eCheck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n",
            "\"3/30/2020\",\"eCheck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n",
            "\"3/13/2019\",\"Echeck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n",
            "\"6/19/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n",
            "\"5/14/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n",
            "\"5/04/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n",
            "\"4/16/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n",
            "\"4/02/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n",
            "\"3/09/2018\",\"Echeck Deposit\",\"eCheck Deposit\",\"###\",\"credit\",\"Income\",\"###\",\"\",\"\"\n"
        ]
    },
~~~

## Output File Contents CSV Example
![image](https://user-images.githubusercontent.com/14623411/114281748-054e8000-99f5-11eb-8d79-db34c0046c6a.png)


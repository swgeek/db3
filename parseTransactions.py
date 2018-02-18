#!/usr/bin/python

import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument("fileToParse", nargs=1, help="csv file to parse")
args = parser.parse_args()

inputFile = args.fileToParse[0]

transactionList = []

with open(inputFile, "rb") as csvfile:
    csvReader = csv.reader(csvfile)

    for row in csvReader:
        if len(row) > 5:
            entry = {}
            entry["date"] = row[0]
            entry["action"] = row[2].split()[0]
            entry["symbol"] = row[4]
            entry["price"] = row[5]
            try:
                entry["quantity"] = int(row[3])
                entry["transactionFee"] = float(row[6])
                entry["amount"] = float(row[7])
                entry["balance"] = float(row[8])
                transactionList.append(entry)
            except:
                continue



summarizedTransactionList = []
currentEntry = transactionList[0]
for entry in transactionList[1:]:
    if entry["date"] == currentEntry["date"] and \
       entry["action"] == currentEntry["action"] and \
       entry["symbol"] == currentEntry["symbol"] and \
       entry["price"] == currentEntry["price"]:
           # probably part of same transaction, just broken up
           currentEntry["quantity"] += entry["quantity"]
           currentEntry["transactionFee"] += entry["transactionFee"]
           currentEntry["amount"] += entry["amount"]
           currentEntry["balance"] = entry["balance"]
    else:
        # changed, flush previous entry, start new one
        summarizedTransactionList.append(currentEntry)
        currentEntry = entry
summarizedTransactionList.append(currentEntry)


totalTransactionFees = 0
for row in summarizedTransactionList:
    totalTransactionFees += row["transactionFee"]
    description = "%s %d %s @ %s" % (row["action"], row["quantity"], row["symbol"], row["price"])
    print "%s, %s, %.2f, %.2f\n" % (row["date"], description, row["transactionFee"] + row["amount"], row["balance"])

print "\nTotal Transaction Fees: %.2f" % totalTransactionFees




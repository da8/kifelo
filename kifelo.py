import operator
from auxialary import get_json_data, to_json
from operator import itemgetter
from math import isclose

contributions_file_path = "./data/contributions.json"
epsilon = 0.001
to_seperator = "->"

def get_creditors_debitors(contributions, contribution_expected):
    creditors = []
    debitors = []
    for contributor in contributions:
        balance = contributor["contribution"] - contribution_expected
        if balance >= 0:
            creditors.append(
                {
                    "name" : contributor["name"],
                    "balance": balance
                }
            )
        else:
            debitors.append(
                {
                    "name" : contributor["name"],
                    "balance": balance
                }
            )
    return creditors, debitors

def equilize_creditors_debitors(creditors, debitors):
    print("equilize_creditors_debitors(creditors, debitors)")
    debitors_sorted = sorted(debitors, key = itemgetter('balance'))
    print("debitors sorted: ", to_json(debitors_sorted))
    creditors_sorted = sorted(creditors, key = itemgetter('balance'))
    print("creditors sorted: ", to_json(creditors_sorted))
    transactions = []
    while (len(debitors_sorted) > 0) and (len(creditors_sorted) > 0):
        debitor_biggest = debitors_sorted[0]
        creditor_smallest = creditors_sorted[0]
        if abs(debitor_biggest["balance"]) > creditor_smallest["balance"]:
            transaction_amount = creditor_smallest["balance"]
            debitor_biggest["balance"] = debitor_biggest["balance"] + transaction_amount if not isclose(0, debitor_biggest["balance"] + transaction_amount, abs_tol = epsilon) else 0
            creditor_smallest["balance"] = 0
            print("transaction: {} -> {} = {}".format(debitor_biggest["name"], creditor_smallest["name"], transaction_amount))
            transactions.append({
                "from" : debitor_biggest["name"],
                "to" : creditor_smallest["name"],
                "amount": transaction_amount
            })
        elif abs(debitor_biggest["balance"]) == creditor_smallest["balance"]:
            transaction_amount = creditor_smallest["balance"]
            debitor_biggest["balance"] =  0
            creditor_smallest["balance"] = 0
            print("transaction: {} -> {} = {}".format(debitor_biggest["name"], creditor_smallest["name"], transaction_amount))
            transactions.append({
                "from" : debitor_biggest["name"],
                "to" : creditor_smallest["name"],
                "amount": transaction_amount
            })
        else:
            transaction_amount = abs(debitor_biggest["balance"])
            debitor_biggest["balance"] =  0 
            creditor_smallest["balance"] = creditor_smallest["balance"] - transaction_amount if not isclose(0, creditor_smallest["balance"] - transaction_amount, abs_tol = epsilon) else 0
            print("transaction: {} -> {} = {}".format(debitor_biggest["name"], creditor_smallest["name"], transaction_amount))
            transactions.append({
                "from" : debitor_biggest["name"],
                "to" : creditor_smallest["name"],
                "amount": transaction_amount
            })
        if isclose(0, debitors_sorted[0]["balance"],  abs_tol = epsilon):
            debitors_sorted.pop(0)
        if isclose(0, creditors_sorted[0]["balance"],  abs_tol = epsilon):
            creditors_sorted.pop(0)
    print("creditors_sorted: ", to_json(creditors_sorted))
    print("debitors_sorted: ", to_json(debitors_sorted))
    return transactions

def consolidate_transactions(transactions):
    consolidated_transactions = {}
    for transaction in transactions:
        key = "{}{}{}".format(transaction["from"],to_seperator, transaction["to"])
        if key in consolidated_transactions:
            consolidated_transactions[key] += transaction["amount"]
        else:
            consolidated_transactions[key] = transaction["amount"]
    return consolidated_transactions

def fullfill_transactions(contributions, consolidated_transactions):
    print("fullfill_transactions(contributions, consolidated_transactions)")
    print("contributions: " + to_json(contributions))
    print("consolidated_transactions: " + to_json(consolidated_transactions))
    contributions_balanced = contributions.copy()
    print("contributions_balanced: " + to_json(contributions_balanced))
    for k,v in consolidated_transactions.items():
        transaction_from = k.split(to_seperator)[0]
        transaction_to = k.split(to_seperator)[1]
        transaction_amount = v
        contribution_from = [contribution for contribution in contributions_balanced if contribution["name"] == transaction_from][0]
        print("contribution_from", to_json(contribution_from))
        contribution_from["contribution"] += transaction_amount
        contribution_to = [contribution for contribution in contributions_balanced if contribution["name"] == transaction_to][0]
        print("contribution_to", to_json(contribution_to))
        contribution_to["contribution"] -= transaction_amount
    return contributions_balanced

def are_transactions_fair(contributions_balanced, contribution_expected):
    for contribution in contributions_balanced:
        if not isclose(contribution["contribution"], contribution_expected, abs_tol = epsilon):
            return False
    return True

def pretty_print_consolidated_transactions(consolidated_transactions):
    print("pretty_print_consolidated_transactions(consolidated_transactions)")
    print("consolidated_transactions: " + to_json(consolidated_transactions))
    consolidated_transactions_sorted_list = sorted(consolidated_transactions.items(), key = operator.itemgetter(1), reverse = True)
    print("fullfill the following transactions to settle the expenses:")
    for consolidated_transaction in consolidated_transactions_sorted_list:
        debitor = consolidated_transaction[0].split(to_seperator)[0]
        creditor = consolidated_transaction[0].split(to_seperator)[1]
        amount = consolidated_transaction[1]
        print("from {} to {} -> {:.2f} €".format(debitor, creditor, amount))

def main():
    print("main()")
    contributions = get_json_data(contributions_file_path)["contributions"]
    expenses_total = sum([contribution["contribution"] for contribution in contributions])
    contribution_expected = expenses_total / len(contributions)
    print("expenses_total: {}".format(expenses_total))
    print("contribution_expected: {}".format(contribution_expected))
    creditors, debitors = get_creditors_debitors(contributions, contribution_expected)
    print("creditors: ", to_json(creditors))
    print("debitors: ", to_json(debitors))
    transactions = equilize_creditors_debitors(creditors, debitors)
    print("transactions: " + to_json(transactions))
    consolidated_transactions = consolidate_transactions(transactions)
    print("consolidated_transactions: " + to_json(consolidated_transactions))    
    contributions_balanced = fullfill_transactions(contributions, consolidated_transactions)
    print("contributions_balanced: " + to_json(contributions_balanced))
    print("are transactions fair: {}".format(are_transactions_fair(contributions_balanced, contribution_expected)))
    pretty_print_consolidated_transactions(consolidated_transactions)

if __name__ == "__main__":
    print("3 2 1 ...")
    main()
    print("done!")
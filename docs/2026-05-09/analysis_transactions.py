"""
Cobou Agency LLC - Transaction Analysis & Categorization
Generated: May 9, 2026
"""

transactions = [
    ("2025-10-06", "Compte rechargé (USD)", 31.00, "CAPITAL_INJECTION"),
    ("2025-10-06", "Acquisition numéros compte Wise", -31.00, "BANKING_FEES"),
    ("2025-10-25", "Gunay Cirak - Deposit", 200.00, "CLIENT_REVENUE"),
    ("2025-10-31", "Payoneer INC - Paiement", 423.24, "CLIENT_REVENUE"),
    ("2025-11-01", "Noa Fleury - Paiement reçu", 9.98, "CLIENT_REVENUE"),
    ("2025-11-01", "Wise Fee - Noa Fleury", -0.68, "BANKING_FEES"),
    ("2025-11-04", "Virement Thomas Cogne", -100.00, "TEAM_PAYMENT"),
    ("2025-11-08", "Gunay Cirak - Reversal", -200.00, "CLIENT_REFUND"),
    ("2025-11-10", "Elyes BEN OTHMANE", 35.00, "CLIENT_REVENUE"),
    ("2025-11-17", "Elyes BEN OTHMANE", 20.00, "CLIENT_REVENUE"),
    ("2025-11-18", "Wael deposit", 272.00, "CAPITAL_INJECTION"),
    ("2025-11-19", "Virement Thomas Cogne", -7.00, "TEAM_PAYMENT"),
    ("2025-11-20", "EUR->MAD conv (50 MAD)", -4.67, "CURRENCY_CONVERSION"),
    ("2025-11-20", "Wise fee conv", -0.09, "BANKING_FEES"),
    ("2025-11-20", "EUR->MAD conv (210 MAD)", -19.62, "CURRENCY_CONVERSION"),
    ("2025-11-20", "Wise fee conv", -0.40, "BANKING_FEES"),
    ("2025-11-20", "Virement Issam GOOGLE REVIEWS", -20.00, "BIZ_EXPENSE"),
    ("2025-11-22", "Thomas - Rida travel", -40.00, "TEAM_PAYMENT"),
    ("2025-11-22", "Wael deposit (for Thomas)", 30.00, "CAPITAL_INJECTION"),
    ("2025-11-22", "Thomas (from Wael)", -30.00, "TEAM_PAYMENT"),
    ("2025-11-22", "Thomas - Exception Travel", -40.00, "TEAM_PAYMENT"),
    ("2025-11-22", "Virement Wael", -70.00, "OWNER_WITHDRAWAL"),
    ("2025-11-23", "Card Lws PARIS MAD", -6.75, "BIZ_EXPENSE"),
    ("2025-11-23", "Wise fee", -0.14, "BANKING_FEES"),
    ("2025-11-24", "Card Lws PARIS MAD", -11.10, "BIZ_EXPENSE"),
    ("2025-11-24", "Wise fee", -0.23, "BANKING_FEES"),
    ("2025-11-25", "Virement Wael", -130.00, "OWNER_WITHDRAWAL"),
    ("2025-11-29", "Virement Wael", -97.00, "OWNER_WITHDRAWAL"),
    ("2025-12-01", "Elyes BEN OTHMANE", 10.00, "CLIENT_REVENUE"),
    ("2025-12-01", "Wael deposit", 226.00, "CAPITAL_INJECTION"),
    ("2025-12-03", "Card Thomas Lws PARIS", -10.76, "TEAM_PAYMENT"),
    ("2025-12-04", "EUR->MAD (1800 MAD)", -167.18, "CURRENCY_CONVERSION"),
    ("2025-12-04", "Wise fee conv", -3.43, "BANKING_FEES"),
    ("2025-12-04", "Virement Wael BOURSOMA", -50.00, "OWNER_WITHDRAWAL"),
    ("2025-12-05", "Wael deposit", 50.00, "CAPITAL_INJECTION"),
    ("2025-12-05", "Western Union IN", 128.99, "PASS_THROUGH"),
    ("2025-12-05", "Western Union OUT", -128.99, "PASS_THROUGH"),
    ("2025-12-05", "Virement Thomas", -32.50, "TEAM_PAYMENT"),
    ("2025-12-05", "Western Union IN 2", 128.99, "PASS_THROUGH"),
    ("2025-12-05", "Western Union OUT 2", -128.99, "PASS_THROUGH"),
    ("2025-12-05", "Virement Hichem Taghi", -125.00, "BIZ_EXPENSE"),
    ("2025-12-08", "Virement Wael DARKSHOP", -6.00, "BIZ_EXPENSE"),
    ("2025-12-11", "Card Lws PARIS MAD", -1.23, "BIZ_EXPENSE"),
    ("2025-12-11", "Wise fee", -0.03, "BANKING_FEES"),
    ("2025-12-13", "Card Lws PARIS (debit)", -1.19, "BIZ_EXPENSE"),
    ("2025-12-16", "Card Lws PARIS (refund)", 1.19, "BIZ_EXPENSE"),
    ("2025-12-19", "Virement Wael DEPOT 2000rub", -20.00, "BIZ_EXPENSE"),
    ("2025-12-19", "Crypto shopping", -20.00, "OWNER_WITHDRAWAL"),
    ("2025-12-19", "Crypto shopping return", 20.00, "OWNER_WITHDRAWAL"),
    ("2025-12-20", "Webshare Proxy", -2.55, "BIZ_EXPENSE"),
    ("2025-12-20", "Wise fee card", -0.01, "BANKING_FEES"),
    ("2025-12-22", "Elyes BEN OTHMANE", 10.00, "CLIENT_REVENUE"),
    ("2025-12-24", "Virement Wael", -1.00, "OWNER_WITHDRAWAL"),
    ("2025-12-24", "Virement Wael RIDA POP", -14.00, "TEAM_PAYMENT"),
    ("2025-12-28", "Virement Wael", -50.00, "OWNER_WITHDRAWAL"),
    ("2025-12-28", "Virement Wael", -2.00, "OWNER_WITHDRAWAL"),
    ("2025-12-28", "Virement Wael", -3.00, "OWNER_WITHDRAWAL"),
    ("2025-12-31", "Wael deposit (large)", 1267.50, "CAPITAL_INJECTION"),
    ("2025-11-20", "MAD: Transfer M. Boudrioua", -200.00, "BIZ_EXPENSE"),
    ("2025-11-20", "MAD: Wise fees", -39.65, "BANKING_FEES"),
    ("2025-12-04", "MAD: Transfer to Wael", -1790.51, "OWNER_WITHDRAWAL"),
    ("2025-12-04", "MAD: Wise fees", -9.49, "BANKING_FEES"),
    ("2025-12-14", "MAD: Card refund", 13.23, "BIZ_EXPENSE"),
]

summary = {}
for t in transactions:
    cat = t[3]
    amt = t[2]
    summary.setdefault(cat, {"count": 0, "total": 0.0})
    summary[cat]["count"] += 1
    summary[cat]["total"] += amt

print("=" * 70)
print("COBOU AGENCY LLC - ANALYSE TRANSACTIONS (Oct-Dec 2025)")
print("=" * 70)
print(f"\n{'Catégorie':<25} {'Nb':<5} {'Montant (EUR)':<15}")
print("-" * 45)

for cat in ["CLIENT_REVENUE", "CAPITAL_INJECTION", "PASS_THROUGH", "TEAM_PAYMENT",
             "BIZ_EXPENSE", "BANKING_FEES", "CURRENCY_CONVERSION", "OWNER_WITHDRAWAL", "CLIENT_REFUND"]:
    data = summary.get(cat, {"count": 0, "total": 0.0})
    print(f"{cat:<25} {data['count']:<5} {data['total']:<15.2f}")

# Calculate business net
client_rev = summary["CLIENT_REVENUE"]["total"]
biz_exp = abs(summary["BIZ_EXPENSE"]["total"])
team_pay = abs(summary["TEAM_PAYMENT"]["total"])
bank_fees = abs(summary["BANKING_FEES"]["total"])
conv_loss = abs(summary["CURRENCY_CONVERSION"]["total"])
refunds = abs(summary["CLIENT_REFUND"]["total"]) if "CLIENT_REFUND" in summary else 0

total_expenses = biz_exp + team_pay + bank_fees + conv_loss
net_income = client_rev - total_expenses

print(f"\n{'':-^70}")
print(f"RÉSULTAT NET D'EXPLOITATION")
print(f"{'':-^70}")
print(f"\nRevenus clients (tiers):           €{client_rev:>8.2f}")
print(f"Dépenses d'exploitation:")
print(f"  - Paiements équipe:              €{team_pay:>8.2f}")
print(f"  - Dépenses pro (services):       €{biz_exp:>8.2f}")
print(f"  - Frais bancaires:               €{bank_fees:>8.2f}")
print(f"  - Pertes de conversion:          €{conv_loss:>8.2f}")
print(f"{'':-^45}")
print(f"TOTAL DÉPENSES:                     €{total_expenses:>8.2f}")
print(f"BÉNÉFICE NET:                       €{net_income:>8.2f}")
print(f"BÉNÉFICE NET (USD @ 1.08):         ${net_income * 1.08:>8.2f}")
print(f"\nCapital injecté par Wael:          €{summary['CAPITAL_INJECTION']['total']:>8.2f}")
print(f"Retraits de Wael:                  €{abs(summary['OWNER_WITHDRAWAL']['total']):>8.2f}")


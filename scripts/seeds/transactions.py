import random
import csv
import os
from pathlib import Path
from datetime import date, timedelta

from faker import Faker

fake = Faker()

category_list = (
    ("groceries", (20.0, 70.0)),
    ("public transport", (2.0, 4.0)),
    ("taxi", (8.0, 15.0)),
    ("restaurants", (40.0, 120.0)),
    ("education", (10.0, 100.0)),
    ("children education", (40.0, 80.0)),
    ("medicine", (20.0, 70.0)),
    ("entertainment", (5.0, 25.0)),
    ("culture", (5.0, 40.0)),
    ("household", (5.0, 60.0)),
    ("services", (10.0, 50.0)),
    ("internet & TV", (10.0, 35.0)),
    ("mobile phone", (10.0, 50.0)),
    ("communal services", (35.0, 135.0)),
    ("car maintenance", (50.0, 250.0)),
    ("fuel", (10.0, 50.0)),
    ("insurance", (50.0, 150.0)),
    ("other", (2.0, 35.0)),
)

risks = (
    ("online bookmaker", "1xBet"),
    ("microfinance", "Credit Expert"),
    ("online gambling", "Casino 777"),
)

first_income = 1500.0
second_income = 2000.0
save_balance = 30.0

# (email, starting_balance, day_of_first_income, day_of_second_income, rental_rate, employer, have_risk)
customer_data = (
    ("customer1@mail.com", 450.0, 10, 25, 600.0, "Campbell&Co", 1),
    ("customer2@mail.com", 600.0, 5, 20, 550.0, "Solar", 0),
    ("customer3@mail.com", 800.0, 7, 22, 700.0, "NewEra", 0),
)

report_dates = (
    ('2024-05-01', '2024-05-31'), ('2024-06-01', '2024-06-30')
)

fields = ("date", "email", "type", "amount", "balance", "category", "details")


def create_fake_report(data, dates_list) -> list:
    email, init_balance, first, second, rent, company, risk = data
    balance = init_balance
    transactions = []
    for dates in dates_list:
        txn_list = []
        start, end = dates
        start_date = date(*[int(i) for i in start.split('-')])
        finish_date = date(*[int(i) for i in end.split('-')])
        saving = False
        stop_spending = False
        current = start_date
        while current <= finish_date:
            txn_available = 5
            if current.day in (first, second):
                stop_spending = False
                if current.day == first:
                    balance += first_income
                    income = first_income
                else:
                    saving = True
                    balance += second_income
                    income = second_income
                txn_list.append(
                    {
                        "date": current,
                        "email": email,
                        "type": "deposit",
                        "amount": income,
                        "balance": balance,
                        "category": "salary",
                        "details": company
                    }
                )
                if current.day == second:
                    balance -= rent
                    txn_list.append(
                        {
                            "date": current,
                            "email": email,
                            "type": "credit",
                            "amount": rent,
                            "balance": balance,
                            "category": "apartment rent",
                            "details": fake.name()
                        }
                    )
            while balance > save_balance and not stop_spending and txn_available:
                spending = random.randint(0, 1)
                if spending:
                    if not saving:
                        random_chance = random.randint(10, 15)
                        estimate_balance = save_balance * random_chance
                    else:
                        estimate_balance = init_balance
                    if balance < estimate_balance:
                        break
                    category, limits = random.choice(category_list)
                    amount = random.randrange(*[int(limit) for limit in limits])
                    new_balance = balance - amount
                    if new_balance < save_balance:
                        stop_spending = True
                        break
                    balance = new_balance
                    txn = {
                        "date": current,
                        "email": email,
                        "type": "credit",
                        "amount": float(amount),
                        "balance": balance,
                        "category": category,
                        "details": fake.company()
                    }
                    txn_list.append(txn)
                    txn_available -= 1
            current = current + timedelta(days=1)
        if risk:
            rs_txns = random.randint(1, 5)
            while rs_txns:
                rsk = random.choice(risks)
                risk_cat, risk_name = rsk
                while True:
                    txn = random.choice(txn_list)
                    if txn.get("type") == "credit" and txn.get("category") != risk_cat:
                        txn["category"] = risk_cat
                        txn["details"] = risk_name
                        rs_txns -= 1
                        break
                    continue
        transactions.extend(txn_list)
    return transactions


def create_csv_report(data, dates):
    txns = create_fake_report(data, dates)
    customer = data[0].split("@")[0]
    dir_path = Path(f"reports")
    if not os.path.exists(dir_path):
        dir_path.mkdir(parents=True)
    file_path = os.path.join(dir_path, f"{customer}_report.csv")
    with open(file_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(txns)


for obj in customer_data:
    create_csv_report(obj, report_dates)

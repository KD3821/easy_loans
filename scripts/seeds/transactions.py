import random
import csv
import os
from pathlib import Path
from datetime import date, timedelta

from faker import Faker

fake = Faker()

new_category_list = (
    ("groceries", (0.7, 2.0)),
    ("public transport", (0.05, 0.1)),
    ("taxi", (0.2, 0.4)),
    ("restaurants", (1.2, 3.6)),
    ("education", (0.3, 3.0)),
    ("children education", (1.2, 2.4)),
    ("medicine", (0.6, 2.5)),
    ("entertainment", (0.15, 1.0)),
    ("culture", (0.15, 1.2)),
    ("household", (0.15, 1.8)),
    ("services", (0.3, 1.5)),
    ("internet & TV", (0.3, 1.2)),
    ("mobile phone", (0.3, 1.5)),
    ("communal services", (1.0, 4.0)),
    ("car maintenance", (1.5, 7.5)),
    ("fuel", (0.3, 1.5)),
    ("insurance", (1.5, 4.5)),
    ("other", (0.05, 0.9)),
)

fake_risks = (
    ("online bookmaker", "1xBet"),
    ("microfinance", "Credit Expert"),
    ("online gambling", "Casino 777"),
)

fake_first_income = 1500.0
fake_second_income = 2000.0
fake_save_balance = 30.0

# (email, month_salary, starting_balance, day_of_first_income, day_of_second_income, rental_rate, employer, have_risk)
fake_customer_data = (
    ("customer4@mail.com", 3500.0, 450.0, 10, 25, 600.0, "Campbell&Co", 1),
    ("customer5@mail.com", 3500.0, 600.0, 5, 20, 550.0, "Solar", 0),
    ("customer6@mail.com", 3500.0, 800.0, 7, 22, 700.0, "NewEra", 0),
)

fake_report_dates = (
    ('2024-05-01', '2024-05-31'), ('2024-06-01', '2024-06-30')
)


def create_fake_txns(data, dates_list, first_income, second_income, save_balance, risks) -> list:
    email, salary, init_balance, first, second, rent, company, risk = data
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
                    category, limits = random.choice(new_category_list)
                    percent = random.uniform(*limits)
                    amount = round((salary * percent / 100), 2)
                    new_balance = round((balance - amount), 2)
                    if new_balance < save_balance:
                        stop_spending = True
                        break
                    balance = new_balance
                    txn = {
                        "date": current,
                        "email": email,
                        "type": "credit",
                        "amount": amount,
                        "balance": balance,
                        "category": category,
                        "details": fake.company()
                    }
                    txn_list.append(txn)
                    txn_available -= 1
            current = current + timedelta(days=1)
        print(*txn_list, sep="\n")
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
        transactions.extend(txn_list)
    return transactions


def create_csv_report(data, dates, first_income, second_income, save_balance, risks):
    txns = create_fake_txns(
        data=data,
        dates_list=dates,
        first_income=first_income,
        second_income=second_income,
        save_balance=save_balance,
        risks=risks
    )
    customer = data[0].split("@")[0]
    dir_path = Path(f"uploaded_reports")
    if not os.path.exists(dir_path):
        dir_path.mkdir(parents=True)
    file_path = os.path.join(dir_path, f"{customer}_report.csv")
    with open(file_path, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["date", "email", "type", "amount", "balance", "category", "details"]
        )
        writer.writeheader()
        writer.writerows(txns)


for obj in fake_customer_data:
    create_csv_report(
        data=obj,
        dates=fake_report_dates,
        first_income=fake_first_income,
        second_income=fake_second_income,
        save_balance=fake_save_balance,
        risks=fake_risks
    )

import random
import csv
import os
from pathlib import Path
from datetime import date, timedelta

from faker import Faker

from scripts.db_session import db_session
from apps.risks.models import Risk

fake = Faker()

upload_dirname = "uploaded_reports"

category_list = (
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
    ("online bookmaker", "WilliamsBet"),
    ("microfinance", "Credit Expert"),
    ("microfinance", "ZapZap"),
    ("online gambling", "Casino 777"),
    ("online gambling", "PokerStars"),
    ("entertainment", "Maximus"),
    ("entertainment", "7 Sins")
)


def create_fake_txns(data, dates, first_income, second_income, save_balance):
    customer_id, salary, init_balance, first, second, rent, company, risk = data
    balance = init_balance
    fixed_finish_date = None
    transactions = []
    start_date, finish_date = dates
    saving = False
    stop_spending = False
    if start_date.day > second:
        saving = True
        if start_date.day <= second + 2:
            balance = init_balance * 3
        elif start_date.day <= second + 5:
            balance = init_balance * 1.5
    current = start_date
    while current <= finish_date:
        txn_available = 5
        if current.day == 1:
            saving = False
            stop_spending = False
        elif current.day in (first, second):
            stop_spending = False
            if current.day == first:
                balance += first_income
                income = first_income
            else:
                saving = True
                balance += second_income
                income = second_income
            transactions.append(
                {
                    "date": current,
                    "customer_id": customer_id,
                    "type": "deposit",
                    "amount": income,
                    "balance": balance,
                    "category": "salary",
                    "details": company
                }
            )
            if current.day == second:
                balance -= rent
                transactions.append(
                    {
                        "date": current,
                        "customer_id": customer_id,
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
                    random_chance = random.randint(5, 10)
                    estimate_balance = save_balance * random_chance
                else:
                    estimate_balance = init_balance
                if balance < estimate_balance:
                    break
                category, limits = random.choice(category_list)
                percent = random.uniform(*limits)
                amount = round((salary * percent / 100), 2)
                new_balance = round((balance - amount), 2)
                if new_balance < save_balance:
                    stop_spending = True
                    break
                balance = new_balance
                txn = {
                    "date": current,
                    "customer_id": customer_id,
                    "type": "credit",
                    "amount": amount,
                    "balance": balance,
                    "category": category,
                    "details": fake.company()
                }
                transactions.append(txn)
                txn_available -= 1
        current = current + timedelta(days=1)
        if current == date.today() + timedelta(days=1):
            fixed_finish_date = (current - timedelta(days=1)).strftime("%Y-%m-%d")
            break
    if risk:
        rs_txns = random.randint(1, int(len(transactions) / 10))
        risks = db_session.query(Risk).all()
        db_session.close()
        if not risks:
            risks = fake_risks
        while rs_txns:
            rsk = random.choice(risks)
            risk_category = rsk.category
            risk_details = rsk.details
            while True:
                txn = random.choice(transactions)
                if txn.get("type") == "credit" and txn.get("category") != risk_category:
                    txn["category"] = risk_category
                    txn["details"] = risk_details
                    rs_txns -= 1
                    break
    return transactions, fixed_finish_date


def create_csv_report(data, dates, first_income, second_income, save_balance):
    txns, fixed_date = create_fake_txns(
        data=data,
        dates=dates,
        first_income=first_income,
        second_income=second_income,
        save_balance=save_balance
    )

    customer_id = data[0]
    date_start = dates[0]

    if fixed_date is not None:
        date_finish = fixed_date
    else:
        date_finish = dates[-1]

    fieldnames = ["date", "customer_id", "type", "amount", "balance", "category", "details"]
    filename = f"report_{customer_id}_{date_start}_{date_finish}.csv"
    dir_path = Path(upload_dirname)

    if not os.path.exists(dir_path):
        dir_path.mkdir(parents=True)

    file_path = os.path.join(dir_path, filename)

    with open(file_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(txns)

    return file_path, filename

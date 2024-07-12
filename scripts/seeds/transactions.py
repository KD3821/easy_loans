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
    ("online gambling", "PokerStars"),
)

fake_first_income = 1500.0
fake_second_income = 2000.0
fake_save_balance = 30.0

# (customer_id, month_salary, starting_balance, first_income_day, second_income_day, rental_rate, employer, have_risk)
fake_customer_data = (
    (1, 3500.0, 450.0, 10, 25, 600.0, "Campbell&Co", 1),
    (2, 3500.0, 600.0, 5, 20, 550.0, "Solar", 0),
    (3, 3500.0, 800.0, 7, 22, 700.0, "NewEra", 0),
)

fake_report_dates = (
    (date(2024, 6, 1), date(2024, 7, 11)),
)


def create_fake_txns(data, dates, first_income, second_income, save_balance, risks):
    customer_id, salary, init_balance, first, second, rent, company, risk = data
    balance = init_balance
    fixed_finish_date = None
    transactions = []
    start_date, finish_date = dates
    saving = False
    if start_date.day > second:
        saving = True
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
        rs_txns = random.randint(1, 5)
        while rs_txns:
            rsk = random.choice(risks)
            risk_cat, risk_name = rsk
            while True:
                txn = random.choice(transactions)
                if txn.get("type") == "credit" and txn.get("category") != risk_cat:
                    txn["category"] = risk_cat
                    txn["details"] = risk_name
                    rs_txns -= 1
                    break
    return transactions, fixed_finish_date


def create_csv_report(data, dates, first_income, second_income, save_balance, risks):
    txns, fixed_date = create_fake_txns(
        data=data,
        dates=dates,
        first_income=first_income,
        second_income=second_income,
        save_balance=save_balance,
        risks=risks
    )

    customer_id = data[0]
    date_start = dates[0]

    if fixed_date is not None:
        date_finish = fixed_date
    else:
        date_finish = dates[-1]

    fieldnames = ["date", "customer_id", "type", "amount", "balance", "category", "details"]
    filename = f"report_{customer_id}_{date_start}_{date_finish}.csv"
    dir_path = Path(f"uploaded_reports")

    if not os.path.exists(dir_path):
        dir_path.mkdir(parents=True)

    file_path = os.path.join(dir_path, filename)

    with open(file_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(txns)

    return file_path, filename


# for obj in fake_customer_data:
#     create_csv_report(
#         data=obj,
#         dates=fake_report_dates,
#         first_income=fake_first_income,
#         second_income=fake_second_income,
#         save_balance=fake_save_balance,
#         risks=fake_risks
#     )

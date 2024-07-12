import csv

from sqlalchemy.orm import registry, Session
from sqlalchemy import MetaData, Table, create_engine
from settings import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

from .schemas import TransactionCelery

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


def upload_transactions(customer_id, file_data):
    reader = csv.DictReader(
        (line.decode() for line in file_data)
    )
    next(reader)  # to skip reading of header part
    txn_list = []
    for row in reader:
        txn_list.append(TransactionCelery.model_validate(row))
    file_data.close()

    # work-around: import of transactions.models.Transaction causes 'circular import' error in report_cases
    MappedClass = type('MappedClass', (), {})  # empty class to use for mapping
    metadata = MetaData()
    transaction_table = Table("transactions", metadata, autoload_with=engine)
    mapper_registry = registry()
    mapper_registry.map_imperatively(MappedClass, transaction_table)  # noqa (to avoid circular import error)

    with Session(engine) as session:
        transactions = []

        for transaction_data in txn_list:
            transactions.append(MappedClass(**transaction_data.dict()))  # noqa

        session.add_all(transactions)
        session.commit()

    return {"customer_id": customer_id, "transactions_uploaded": len(txn_list)}

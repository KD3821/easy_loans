import csv
from datetime import datetime

from sqlalchemy.orm import registry, Session
from sqlalchemy import MetaData, Table, create_engine, select
from settings import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

from .schemas import TransactionCelery

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


def upload_transactions(customer_id, file_data, upload_id, task_id):
    reader = csv.DictReader(
        (line.decode() for line in file_data)
    )
    next(reader)  # to skip reading of header part
    txn_list = []
    for row in reader:
        row.update({"upload_id": upload_id})
        txn_list.append(TransactionCelery.model_validate(row))
    file_data.close()

    # work-around: import of transactions.models.Transaction causes 'circular import' error in report_cases
    MappedClassTXN = type('MappedClassTXN', (), {})  # empty class to use for mapping
    MappedClassUPLOAD = type('MappedClassUPLOAD', (), {})  # empty class to use for mapping
    metadata = MetaData()
    transaction_table = Table("transactions", metadata, autoload_with=engine)
    transaction_upload_table = Table("transaction_uploads", metadata, autoload_with=engine)
    mapper_registry = registry()
    mapper_registry.map_imperatively(MappedClassTXN, transaction_table)  # noqa (to avoid circular import)
    mapper_registry.map_imperatively(MappedClassUPLOAD, transaction_upload_table)  # noqa (to avoid circular import)

    with Session(engine) as session:
        transactions = []

        for transaction_data in txn_list:
            transactions.append(MappedClassTXN(**transaction_data.dict()))  # noqa

        query = session.execute(
            select(MappedClassUPLOAD)
            .filter_by(id=upload_id)
        )
        txn_upload = query.scalars().first()

        txn_upload.task_id = task_id
        txn_upload.status = "completed"  # hardcoded
        txn_upload.updated_at = datetime.utcnow()

        session.add_all(transactions)
        session.commit()

    return {"customer_id": customer_id, "upload_id": upload_id, "total_uploaded": len(transactions)}

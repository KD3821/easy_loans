from ..storages import TransactionStorage


class TransactionCases:
    def __init__(self, transaction_repo: TransactionStorage):
        self._transaction_repo = transaction_repo

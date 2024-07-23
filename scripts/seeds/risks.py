from apps.risks.models import Risk
from core import logger

from scripts.db_session import db_session


RISKS = [
    ("online bookmaker", "1xBet"),
    ("online bookmaker", "WilliamsBet"),
    ("microfinance", "Credit Expert"),
    ("microfinance", "ZapZap"),
    ("online gambling", "Casino 777"),
    ("online gambling", "PokerStars"),
    ("entertainment", "Maximus"),
    ("entertainment", "7 Sins"),
]


def perform(*args, **kwargs):
    for risk in RISKS:
        category, details = risk
        risk_exists = (
            db_session.query(Risk).filter_by(category=category, details=details).all()
        )

        if not risk_exists:
            db_session.add(Risk(category=category, details=details))
        else:
            logger.info(f"Risk with {category=} & {details=} already exists")

    db_session.commit()
    db_session.close()

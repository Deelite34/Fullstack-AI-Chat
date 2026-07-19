from sqlalchemy.orm import Session


class BaseRepository:
    db: Session

    def __init__(self, db: Session):
        if not db:
            raise ValueError(
                "Session is required for repository. "
                "Create repository throught getter function with this dependency injected"
            )
        self.db = db

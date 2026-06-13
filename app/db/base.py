from app.db.base_class import Base

# Import every SQLAlchemy model here so Base.metadata knows about all tables.
from app.models.review import Review, ReviewComment  # noqa: F401
from app.models.submission import Submission  # noqa: F401
from app.models.user import User  # noqa: F401

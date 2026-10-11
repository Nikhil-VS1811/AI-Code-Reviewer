import asyncio
import unittest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.user import User
from app.models.submission import Submission
from app.models.review import Review
from app.services.submission_service import list_user_submissions
from app.services.review_service import list_user_reviews
from app.main import app
from app.services.auth_service import get_current_user


class TestPaginationService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create two distinct test users
        self.user1 = User(
            id=1,
            username="userone",
            email="userone@example.com",
            hashed_password="fakehashedpassword",
        )
        self.user2 = User(
            id=2,
            username="usertwo",
            email="usertwo@example.com",
            hashed_password="fakehashedpassword",
        )
        self.db.add_all([self.user1, self.user2])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_submission_pagination_defaults_and_limits(self):
        # Insert 5 submissions for user1
        for i in range(1, 6):
            sub = Submission(
                id=i,
                language="python",
                code=f"print({i})",
                user_id=self.user1.id,
                created_at=datetime(2026, 1, i, tzinfo=timezone.utc),
            )
            self.db.add(sub)
        # Insert 2 submissions for user2
        for i in range(6, 8):
            sub = Submission(
                id=i,
                language="python",
                code=f"print({i})",
                user_id=self.user2.id,
                created_at=datetime(2026, 1, i, tzinfo=timezone.utc),
            )
            self.db.add(sub)
        self.db.commit()

        # Default: limit=20, offset=0 -> user1 should get 5 submissions, newest first
        res = list_user_submissions(self.db, self.user1, limit=20, offset=0)
        self.assertEqual(len(res), 5)
        self.assertEqual([s.id for s in res], [5, 4, 3, 2, 1])

        # Pagination: limit=2, offset=0 -> first 2
        res_page1 = list_user_submissions(self.db, self.user1, limit=2, offset=0)
        self.assertEqual(len(res_page1), 2)
        self.assertEqual([s.id for s in res_page1], [5, 4])

        # Pagination: limit=2, offset=2 -> next 2
        res_page2 = list_user_submissions(self.db, self.user1, limit=2, offset=2)
        self.assertEqual(len(res_page2), 2)
        self.assertEqual([s.id for s in res_page2], [3, 2])

        # User isolation: user2 should only see their 2 submissions
        res_user2 = list_user_submissions(self.db, self.user2, limit=20, offset=0)
        self.assertEqual(len(res_user2), 2)
        self.assertEqual([s.id for s in res_user2], [7, 6])

    def test_review_pagination_defaults_and_limits(self):
        # Insert 4 reviews for user1
        for i in range(1, 5):
            sub = Submission(
                id=10 + i,
                language="python",
                code="pass",
                user_id=self.user1.id,
                created_at=datetime(2026, 1, i, tzinfo=timezone.utc),
            )
            self.db.add(sub)
            self.db.flush()

            rev = Review(
                id=i,
                submission_id=sub.id,
                overall_score=85,
                security_score=90,
                performance_score=80,
                maintainability_score=85,
                readability_score=85,
                summary=f"Review summary {i}",
                created_at=datetime(2026, 1, i, tzinfo=timezone.utc),
            )
            self.db.add(rev)
        self.db.commit()

        # Default limit/offset
        all_revs = list_user_reviews(self.db, self.user1, limit=20, offset=0)
        self.assertEqual(len(all_revs), 4)
        self.assertEqual([r.id for r in all_revs], [4, 3, 2, 1])

        # Limit 2, offset 1
        sliced = list_user_reviews(self.db, self.user1, limit=2, offset=1)
        self.assertEqual(len(sliced), 2)
        self.assertEqual([r.id for r in sliced], [3, 2])

        # User isolation: user2 has 0 reviews
        user2_revs = list_user_reviews(self.db, self.user2, limit=20, offset=0)
        self.assertEqual(len(user2_revs), 0)


class TestPaginationRouteValidation(unittest.TestCase):
    def setUp(self):
        self.test_user = User(
            id=1,
            username="testuser",
            email="testuser@example.com",
            hashed_password="pw",
        )
        app.dependency_overrides[get_current_user] = lambda: self.test_user

    def tearDown(self):
        app.dependency_overrides.pop(get_current_user, None)

    def _run_asgi(self, method: str, path: str, query_string: bytes = b""):
        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": method,
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string,
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        }
        messages = []

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            messages.append(message)

        asyncio.run(app(scope, receive, send))
        status_code = next(m["status"] for m in messages if m["type"] == "http.response.start")
        body_parts = [m.get("body", b"") for m in messages if m["type"] == "http.response.body"]
        return status_code, b"".join(body_parts)

    def test_invalid_query_parameters_return_422(self):
        # submission endpoint bounds
        status, _ = self._run_asgi("GET", "/submissions", b"limit=0")
        self.assertEqual(status, 422)

        status, _ = self._run_asgi("GET", "/submissions", b"limit=101")
        self.assertEqual(status, 422)

        status, _ = self._run_asgi("GET", "/submissions", b"offset=-1")
        self.assertEqual(status, 422)

        # review endpoint bounds
        status, _ = self._run_asgi("GET", "/reviews", b"limit=0")
        self.assertEqual(status, 422)

        status, _ = self._run_asgi("GET", "/reviews", b"limit=101")
        self.assertEqual(status, 422)

        status, _ = self._run_asgi("GET", "/reviews", b"offset=-1")
        self.assertEqual(status, 422)


if __name__ == "__main__":
    unittest.main()

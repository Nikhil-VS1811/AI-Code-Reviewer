import unittest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import (
    create_user,
    authenticate_user,
    get_user_by_email,
    normalize_email,
)


class TestEmailNormalization(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_normalize_email_helper(self):
        self.assertEqual(normalize_email(" Test@Example.Com "), "test@example.com")
        self.assertEqual(normalize_email("USER@DOMAIN.ORG"), "user@domain.org")
        self.assertEqual(normalize_email(""), "")
        self.assertEqual(normalize_email(None), "")

    def test_schema_normalizes_email(self):
        payload = UserCreate(
            username="testuser",
            email="  MixedCase.User@Domain.Com  ",
            password="Password123!",
        )
        self.assertEqual(payload.email, "mixedcase.user@domain.com")

        login_payload = UserLogin(
            email="LOGIN.USER@Domain.com",
            password="Password123!",
        )
        self.assertEqual(login_payload.email, "login.user@domain.com")

    def test_create_user_stores_lowercase_email(self):
        user = create_user(
            self.db,
            UserCreate(
                username="alice",
                email="Alice.Smith@Example.COM",
                password="SecurePassword123!",
            ),
        )
        self.assertEqual(user.email, "alice.smith@example.com")

    def test_case_insensitive_lookup_and_auth(self):
        create_user(
            self.db,
            UserCreate(
                username="bob",
                email="bob.builder@construction.org",
                password="SecurePassword123!",
            ),
        )

        # Lookup with uppercase
        user = get_user_by_email(self.db, "BOB.BUILDER@CONSTRUCTION.ORG")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "bob")

        # Authenticate with mixed case
        authenticated = authenticate_user(
            self.db,
            "BoB.BuiLdeR@Construction.Org",
            "SecurePassword123!",
        )
        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.id, user.id)

    def test_duplicate_registration_with_different_casing_rejected(self):
        create_user(
            self.db,
            UserCreate(
                username="carol",
                email="carol@domain.com",
                password="SecurePassword123!",
            ),
        )

        with self.assertRaises(HTTPException) as ctx:
            create_user(
                self.db,
                UserCreate(
                    username="carol2",
                    email="CAROL@DOMAIN.COM",
                    password="DifferentPassword123!",
                ),
            )
        self.assertEqual(ctx.exception.status_code, 409)


class TestCaseInsensitiveEmailMigration(unittest.TestCase):
    def setUp(self):
        import importlib.util
        from pathlib import Path

        migration_path = (
            Path(__file__).resolve().parent.parent
            / "migrations"
            / "versions"
            / "2026_10_11_0002_case_insensitive_email.py"
        )
        spec = importlib.util.spec_from_file_location("migration_0002", migration_path)
        self.migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.migration)

        self.engine = create_engine("sqlite:///:memory:")
        with self.engine.begin() as conn:
            conn.exec_driver_sql(
                "CREATE TABLE users ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "username VARCHAR(50) NOT NULL, "
                "email VARCHAR(255) NOT NULL UNIQUE, "
                "hashed_password VARCHAR(255) NOT NULL"
                ")"
            )

    def tearDown(self):
        self.engine.dispose()

    def test_migration_normalizes_and_creates_unique_lower_index(self):
        from unittest.mock import patch
        from alembic.operations import Operations
        from alembic.runtime.migration import MigrationContext
        from sqlalchemy.exc import IntegrityError
        import sqlalchemy as sa

        with self.engine.begin() as conn:
            conn.execute(
                sa.text(
                    "INSERT INTO users (username, email, hashed_password) "
                    "VALUES ('u1', 'Mixed.User@Example.COM', 'pw1'), "
                    "('u2', 'second.user@example.com', 'pw2')"
                )
            )
            ctx = MigrationContext.configure(conn)
            op_instance = Operations(ctx)
            with patch.object(self.migration, "op", op_instance):
                self.migration.upgrade()

            emails = [
                row[0]
                for row in conn.execute(
                    sa.text("SELECT email FROM users ORDER BY id")
                ).fetchall()
            ]
            self.assertEqual(
                emails,
                ["mixed.user@example.com", "second.user@example.com"],
            )

            # Verify case-insensitive unique index is enforced at the database level
            with self.assertRaises(IntegrityError):
                conn.execute(
                    sa.text(
                        "INSERT INTO users (username, email, hashed_password) "
                        "VALUES ('u3', 'MIXED.USER@EXAMPLE.COM', 'pw3')"
                    )
                )

            # Verify downgrade drops the expression index cleanly
            with patch.object(self.migration, "op", op_instance):
                self.migration.downgrade()

    def test_migration_fails_explicitly_on_duplicates_without_exposing_pii_or_mutating(self):
        from unittest.mock import patch
        from alembic.operations import Operations
        from alembic.runtime.migration import MigrationContext
        import sqlalchemy as sa

        with self.engine.begin() as conn:
            conn.execute(
                sa.text(
                    "INSERT INTO users (username, email, hashed_password) "
                    "VALUES ('u1', 'Secret.Person@PrivateDomain.org', 'pw1'), "
                    "('u2', 'secret.person@privatedomain.org', 'pw2')"
                )
            )
            ctx = MigrationContext.configure(conn)
            op_instance = Operations(ctx)
            with patch.object(self.migration, "op", op_instance):
                with self.assertRaises(RuntimeError) as err_ctx:
                    self.migration.upgrade()

            error_msg = str(err_ctx.exception)
            self.assertIn("1 case-insensitive duplicate email group(s)", error_msg)
            self.assertNotIn("secret.person", error_msg.lower())
            self.assertNotIn("privatedomain.org", error_msg.lower())

            # Verify accounts were not merged, deleted, or renamed
            rows = conn.execute(
                sa.text("SELECT username, email FROM users ORDER BY id")
            ).fetchall()
            self.assertEqual(
                rows,
                [
                    ("u1", "Secret.Person@PrivateDomain.org"),
                    ("u2", "secret.person@privatedomain.org"),
                ],
            )

    def test_migration_propagates_database_query_failure(self):
        from unittest.mock import MagicMock, patch
        from sqlalchemy.exc import OperationalError

        mock_op = MagicMock()
        mock_bind = MagicMock()
        mock_bind.execute.side_effect = OperationalError(
            "SELECT count(*) ...", {}, Exception("database connection lost")
        )
        mock_op.get_bind.return_value = mock_bind

        with patch.object(self.migration, "op", mock_op):
            with self.assertRaises(OperationalError):
                self.migration.upgrade()
        mock_op.create_index.assert_not_called()


if __name__ == "__main__":
    unittest.main()

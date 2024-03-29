import os
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

SECRET_KEY = "super-secret-key"
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

os.environ["SECRET_KEY"] = SECRET_KEY
os.environ["SQLALCHEMY_DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

from .. import models
from ..main import app, get_db


@pytest.fixture
def anyio_backend():
    """A fixture for tests that are going to access the database layer directly."""
    return "asyncio"


@pytest.fixture
def context():
    """The context for a test case (test client, DB engine, DB session maker)."""
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = async_sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )

    # Overriding the lifespan handler.
    @asynccontextmanager
    async def override_lifespan(app: FastAPI):
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        yield
        await engine.dispose()

    app.router.lifespan_context = override_lifespan

    async def override_get_db() -> AsyncSession:
        """
        Note: This is async, but it is replacing function within
        FastAPI, so we assume that FastAPI know how to handle it.
        """
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            await db.close()

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    client.__enter__()
    try:
        # Some tests may want to access the database directly.
        yield client, engine, TestingSessionLocal
    finally:
        client.__exit__()
        # engine.dispose() will be called by the lifespan handler.


@pytest.fixture
def classroom_create_data():
    return {
        "name": "CS3560 Spring 2022-2023",
        "begin_date": "2023-01-01",
        "end_date": "2023-05-05",
    }


@pytest.fixture
def classroom_api_data():
    return {
        "id": 1,
        "end_date": "2023-05-05",
        "name": "CS3560 Spring 2022-2023",
        "begin_date": "2023-01-01",
        "github_classroom_link": None,
    }


@pytest.fixture
def logged_in_token(context):
    client, _, _ = context
    # TODO: Create user in the database.

    # Log in with the username and password.
    response = client.post(
        "/token",
        data={
            "username": "johndoe",
            "password": "secret",
        },
    )
    token = response.json()
    yield token["access_token"]
    # Cleaning if needed.


def test_get_index(context, logged_in_token):
    client, _, _ = context
    response = client.get("/", headers={"Authorization": "Bearer " + logged_in_token})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "hello world"}


class TestClassroomCRUD:
    def test_list_empty(self, context, logged_in_token):
        client, _, _ = context
        response = client.get(
            "/classrooms/", headers={"Authorization": "Bearer " + logged_in_token}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list(
        self, context, classroom_create_data, classroom_api_data, logged_in_token
    ):
        client, _, _ = context
        response = client.post(
            "/classrooms/",
            json=classroom_create_data,
            headers={"Authorization": "Bearer " + logged_in_token},
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = client.get(
            "/classrooms/", headers={"Authorization": "Bearer " + logged_in_token}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [classroom_api_data]

    def test_create(
        self, context, classroom_create_data, classroom_api_data, logged_in_token
    ):
        client, _, _ = context
        response = client.post(
            "/classrooms/",
            json=classroom_create_data,
            headers={"Authorization": "Bearer " + logged_in_token},
        )
        print(response.json())

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == classroom_api_data

    def test_get(
        self, context, classroom_create_data, classroom_api_data, logged_in_token
    ):
        client, _, _ = context

        # Create the object to perform get later.
        response = client.post(
            "/classrooms/",
            json=classroom_create_data,
            headers={"Authorization": "Bearer " + logged_in_token},
        )
        classroom_id = response.json()["id"]

        # Test.
        response = client.get(
            f"/classrooms/{classroom_id}",
            headers={"Authorization": "Bearer " + logged_in_token},
        )
        assert response.status_code == status.HTTP_200_OK
        obj = response.json()
        assert obj["id"] == 1
        assert obj == classroom_api_data

    def test_delete(self, context, classroom_create_data, logged_in_token):
        client, _, _ = context

        # Create the object to perform get later.
        response = client.post(
            "/classrooms/",
            json=classroom_create_data,
            headers={"Authorization": "Bearer " + logged_in_token},
        )
        classroom_id = response.json()["id"]

        # Test.
        response = client.delete(
            f"/classrooms/{classroom_id}",
            headers={"Authorization": "Bearer " + logged_in_token},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_get_not_exist(self, context, logged_in_token):
        client, _, _ = context
        response = client.get(
            f"/classrooms/1", headers={"Authorization": "Bearer " + logged_in_token}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.anyio
    async def test_import_bb_students(
        self, anyio_backend, context, classroom_create_data, logged_in_token
    ):
        client, _, TestingSessionLocal = context

        # Create a classroom.
        response = client.post(
            "/classrooms/",
            json=classroom_create_data,
            headers={"Authorization": "Bearer " + logged_in_token},
        )
        classroom_id = response.json()["id"]

        # Import the students.
        response = client.post(
            f"/classrooms/{classroom_id}/import/students-from-bb",
            headers={"Authorization": "Bearer " + logged_in_token},
            json={
                "results": [
                    {
                        "id": "an-id",
                        "userId": "a-user-id",
                        "user": {
                            "id": "a-user-id",
                            "uuid": "super-unique-identified",
                            "userName": "bc555555",
                            "studentId": "P123456789",
                            "pronouns": "he/him/his",
                            "modified": "2023-05-18T16:21:03.682Z",
                            "institutionRoleIds": ["STUDENT"],
                            "systemRoleIds": ["User"],
                            "availability": {"available": "Yes"},
                            "name": {
                                "given": "Bob (The TA)",
                                "family": "Cat",
                                "preferredDisplayName": "GivenName",
                            },
                            "contact": {"email": "an-email-handle@a-domain.com"},
                            "avatar": {
                                "viewUrl": "an-url",
                                "source": "Default",
                            },
                        },
                        "courseRoleId": "TeachingAssistant",
                    },
                    {
                        "id": "an-id",
                        "userId": "a-user-id",
                        "user": {
                            "id": "a-user-id",
                            "uuid": "super-unique-identified",
                            "userName": "bc555550",
                            "studentId": "P123456780",
                            "pronouns": "he/him/his",
                            "modified": "2023-05-18T16:21:03.682Z",
                            "institutionRoleIds": ["STUDENT"],
                            "systemRoleIds": ["User"],
                            "availability": {"available": "Yes"},
                            "name": {
                                "given": "Bob (The Student)",
                                "family": "Cat",
                                "preferredDisplayName": "GivenName",
                            },
                            "contact": {"email": "an-email-handle@a-domain.com"},
                            "avatar": {
                                "viewUrl": "an-url",
                                "source": "Default",
                            },
                        },
                        "courseRoleId": "Student",
                    },
                    {
                        "id": "an-id",
                        "userId": "a-user-id",
                        "user": {
                            "id": "a-user-id",
                            "uuid": "super-unique-identified",
                            "userName": "bc",
                            "studentId": "P123456781",
                            "pronouns": "he/him/his",
                            "modified": "2023-05-18T16:21:03.682Z",
                            "institutionRoleIds": ["STUDENT"],
                            "systemRoleIds": ["User"],
                            "availability": {"available": "Yes"},
                            "name": {
                                "given": "Bob (The Instructor)",
                                "family": "Cat",
                                "preferredDisplayName": "GivenName",
                            },
                            "contact": {"email": "an-email-handle@a-domain.com"},
                            "avatar": {
                                "viewUrl": "an-url",
                                "source": "Default",
                            },
                        },
                        "courseRoleId": "Instructor",
                    },
                ]
            },
        )

        # print(response.content)
        assert response.status_code == status.HTTP_200_OK

        # Test by checking DB directly.
        async with TestingSessionLocal() as session:
            query = select(models.Student).where(
                models.Student.classroom_id == classroom_id
            )
            results = await session.execute(query)
            students = results.scalars().all()

            assert len(students) == 1


class TestStudentCRUD:
    def test_get_students_not_exist(self, context, logged_in_token):
        client, _, _ = context

        response = client.get(
            "/classrooms/1/students/1",
            headers={"Authorization": "Bearer " + logged_in_token},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_students_not_exist(self, context, logged_in_token):
        client, _, _ = context

        response = client.get(
            "/classrooms/1/students",
            headers={"Authorization": "Bearer " + logged_in_token},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == list()

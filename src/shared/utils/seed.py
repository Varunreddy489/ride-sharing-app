import asyncio

from sqlalchemy import text

from src.shared.db.db_manager import async_session_factory


async def seed_users(session):
    users = [
        {
            "name": f"User {i}",
            "email": f"user{i}@gmail.com",
            "phone_number": f"900000000{i}",
            "password": "$2b$12$examplehashedpassword",
            "role": "RIDER",
        }
        for i in range(1, 11)
    ]

    for user in users:
        await session.execute(
            text("""
                INSERT INTO users
                (name, email, phone_number, password, role)
                VALUES
                (:name, :email, :phone_number, :password, :role)
                ON CONFLICT (email) DO NOTHING
                """),
            user,
        )

    await session.commit()


async def seed_drivers(session):
    result = await session.execute(
        text("""
            SELECT id
            FROM users
            WHERE role='RIDER'
            ORDER BY id
            LIMIT 10
            """)
    )

    users = result.fetchall()

    for index, user in enumerate(users, start=1):
        await session.execute(
            text("""
                INSERT INTO drivers
                (
                    user_id,
                    license_number,
                    is_online,
                    is_available
                )
                VALUES
                (
                    :user_id,
                    :license_number,
                    :is_online,
                    :is_available
                )
                ON CONFLICT (user_id) DO NOTHING
                """),
            {
                "user_id": user.id,
                "license_number": f"DL202600{index:03}",
                "is_online": True,
                "is_available": True,
            },
        )

    await session.commit()


async def main():
    async with async_session_factory() as session:
        await seed_users(session)
        await seed_drivers(session)

    print("Database seeded successfully.")


if __name__ == "__main__":
    asyncio.run(main())

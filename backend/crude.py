import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User, db_helper


async def create_user(
    session: AsyncSession,
) -> User:
    user = User(
        username="testuser",
        hashed_password="password",
        email="test@example.com",
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    await session.commit()
    return user


async def demo_crude(
    session: AsyncSession,
):
    user = await create_user(session)
    print(user)


async def main():
    async with db_helper.session_factory() as session:
        await demo_crude(session)


if __name__ == "__main__":
    asyncio.run(main())

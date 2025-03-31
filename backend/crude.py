import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User, db_helper


async def create_user(
    session: AsyncSession,
) -> User:
    user = User(
        username="mike3",
        password="12311114",
        email="user3@gmail.com",
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

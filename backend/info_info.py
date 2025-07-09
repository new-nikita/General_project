# import random
# import string
# import aiohttp
# import asyncio
# from faker import Faker
#
# fake = Faker("ru_RU")  # Можно выбрать нужную локаль
#
#
# def random_username():
#     return "".join(random.choices(string.ascii_lowercase, k=10))
#
#
# def random_password():
#     return "1q2W3e4R!"
#
#
# def generate_user_data():
#     password = random_password()
#     return {
#         "username": random_username(),
#         "email": fake.unique.email(),
#         "password": password,
#         "password2": password,
#         "first_name": fake.first_name(),
#         "last_name": fake.last_name(),
#         "middle_name": fake.middle_name(),
#         "birth_date": fake.date_of_birth(
#             minimum_age=18,
#             maximum_age=60,
#         ).strftime(
#             "%Y-%m-%d"
#         ),
#         "gender": random.choice(["male", "female"]),
#         "phone_number": fake.phone_number(),
#         "country": fake.country(),
#         "city": fake.city(),
#         "street": fake.street_address(),
#         "bio": fake.text(max_nb_chars=200),
#     }
#
#
# async def register_user(session, url, user_data):
#     async with session.post(url, data=user_data) as response:
#         status = response.status
#         text = await response.text()
#         return status, text
#
#
# async def main():
#     url = "http://localhost:8000/register"
#     tasks = []
#     async with aiohttp.ClientSession() as session:
#         for _ in range(10000):
#             user_data = generate_user_data()
#             task = asyncio.create_task(register_user(session, url, user_data))
#             tasks.append(task)
#         results = await asyncio.gather(*tasks)
#     return results
#
#
# if __name__ == "__main__":
#     results = asyncio.run(main())
#     for i, (status, text) in enumerate(results[:10]):
#         print(f"Request {i+1}: Status {status}, Response: {text[:100]}...")

from faker import Faker


class DataUtils:
    def __init__(self):
        self.fake = Faker()

    def gen_random_name(self):
        return self.fake.name()

    def gen_random_email(self):
        return self.fake.email()

    def gen_phone_number(self):
        return self.fake.phone_number()

    def gen_password(self):
        return self.fake.password()

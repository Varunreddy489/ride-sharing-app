import bcrypt


class AuthUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        # Implement your password hashing logic here
        # For example, you can use bcrypt or any other hashing library
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        print(f"hashed_password:{hashed_password}")
        print(f"hashed_password.decode('utf-8'):{hashed_password.decode('utf-8')}")
        return hashed_password.decode("utf-8")

import bcrypt


class AuthUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        # Implement your password hashing logic here
        # For example, you can use bcrypt or any other hashing library
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        # Implement your password verification logic here
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    # def create_access_token(self,):

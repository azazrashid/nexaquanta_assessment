from passlib.context import CryptContext


class PasswordHandler:
    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
    )

    @staticmethod
    def hash(password: str):
        """
        Generate a hashed password for the given plain password.

        Args:
            password (str): The plain password to hash.

        Returns:
            str: The hashed password.
        """
        return PasswordHandler.pwd_context.hash(password)

    @staticmethod
    def verify(plain_password, hashed_password):
        """
        Verify if the plain password matches the hashed password.

        Args:
            plain_password (str): The plain password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return PasswordHandler.pwd_context.verify(plain_password, hashed_password)

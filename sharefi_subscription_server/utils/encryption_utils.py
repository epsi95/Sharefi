from cryptography.fernet import Fernet


# defining encryption function
def encrypt_data(data_string, COOKIE_ENCRYPTION_KEY):
    f = Fernet(COOKIE_ENCRYPTION_KEY.encode())
    return f.encrypt(data_string.encode()).decode()


def decrypt_data(data_string, COOKIE_ENCRYPTION_KEY):
    print("COOKIE_ENCRYPTION_KEY>>" + COOKIE_ENCRYPTION_KEY)
    f = Fernet(COOKIE_ENCRYPTION_KEY.encode())
    return f.decrypt(data_string.encode()).decode()


if __name__ == "__main__":
    pass

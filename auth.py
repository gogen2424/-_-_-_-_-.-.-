# Пример логина и пароля
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

# Логин и пароль для пользователя "user"
USER_USERNAME = 'user'
USER_PASSWORD = 'user'

def authenticate(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return 'admin'
    elif username == USER_USERNAME and password == USER_PASSWORD:
        return 'user'
    return None

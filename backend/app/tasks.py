def write_notification(email: str, message=""):
    with open("log.txt", mode="a") as email_file:
        content = f"\nnotification for {email}: {message}"
        email_file.write(content)

import smtplib


def send_code (email_smtp_server, email_login, email_pwd, email_to, email_code):
    smtpObj = smtplib.SMTP_SSL(email_smtp_server, 465)
    smtpObj.login(email_login,email_pwd)
    receivers = [email_to]
    message = 'To: {}\nFrom: {}\nSubject: {}\n\nYour code for CoffeeBot: {}'.format(email_to, email_login, "Your code for CoffeeBot", str(email_code))
    smtpObj.sendmail(email_login, email_to, message)
    smtpObj.quit()

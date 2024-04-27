from models import *


def get_user(uid, login=""):
    user = User.get_or_none(user_id=uid)
    if not user:
        user = User.create(user_id=uid)
        user.login = login
        user.save()
    if login:
        if login != user.login:
            user.login = login
            user.save()
    return user


def set_balance(user: User, new_balance):
    user.balance = new_balance
    user.save()


def set_issue(link, last_interaction, message, closed=False):
    issue = Issue.get_or_none(link=link)
    if issue:
        issue.last_interaction = last_interaction
        issue.last_date = datetime.datetime.now()
        issue.closed = closed
        issue.save()

        Action.create(type="issue", link=link, user=last_interaction, message=message).save()
    else:
        Action.create(type=link, link=link, user=last_interaction, message=message).save()

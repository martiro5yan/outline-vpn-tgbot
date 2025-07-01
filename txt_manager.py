


def save_failed_ids(user_id):
    with open('retry_subscriptions.txt', 'a') as file:
        file.write(user_id)


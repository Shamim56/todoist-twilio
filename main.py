from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime
import todoist, yaml, os

load_dotenv()
api = todoist.TodoistAPI()
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

def read_yaml():
   """
   reads in the accounts file as a map

   return<Map>: a map of the accounts.yml
   """
   data = None
   with open('accounts.yml') as f:
      data = yaml.load(f, Loader=yaml.FullLoader)
   return data


def send_text_message(sender, receipient, message):
    """
    reads in the items of your todoist inbox and sends a text message of the ones due today
    """
    client = Client(account_sid, auth_token)
    message = client.messages.create(
                     body=message,
                     from_=sender,
                     to=receipient
                )


def get_todays_tasks():
    """
    Get tasks due on the current utc day and the backlog
    """
    config = read_yaml()
    todoist_accounts = config["todoist"]
    for account in todoist_accounts:
        api.user.login(account["email"], account["password"])
        response = api.sync()

        inbox = len(response['items'])
        due_today = 0
        today = datetime.now()
        for item in response['items']:
            if item["due"]:
                item_date = datetime.strptime(item["due"]["date"], '%Y-%m-%d')
                if item_date == today or item_date < today:
                    due_today += 1
        
        send_text_message(config["twilio"]["from_phone_number"], account["number"], \
                f'Good Morning {account["name"]}. You currently have {due_today} items due today, and {inbox} in your inbox.'
            )


if __name__ == "__main__":
    get_todays_tasks()
    sched = BlockingScheduler(daemon=True)
    sched.add_job(get_todays_tasks, 'cron', hour='09', minute='00')
    sched.start()

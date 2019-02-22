import os
import time
import psutil
import argparse
from slackclient import SlackClient
from threading import Thread
import datetime

parser = argparse.ArgumentParser(description='Runs the slackbot on your machine.')
parser.add_argument("machineid", help="The id you'd like to assign to this machine.", nargs=1)
args = parser.parse_args()
machine_id = args.machineid[0]



# instantiate Slack client
slack_client = SlackClient(os.environ["ProcessTrackerToken"])
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
pids_tracked = {}

def parse_bot_commands(slack_events):
	"""
		Parses a list of events coming from the Slack RTM API to find bot commands.
		If a bot command is found, this function returns a tuple of command and channel.
		If its not found, then this function returns None, None.
	"""
	for event in slack_events:
		if event["type"] == "message" and not "subtype" in event:
			return event['text'], event["channel"]
	return None, None

def track_pid(proc, channel):
	cmdline = " ".join(proc.cmdline())
	pids_tracked[proc] = (channel, time.time(), cmdline)
	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text="Started tracking process `{}` with PID `{}`".format(cmdline, proc.pid))

def handle_command(command, channel):
	"""
		Executes bot command if the command is known
	"""
	# Default response is help text for the user

	parts = command.split(" ")
	if len(parts) != 2:
		return
	command_machine_id, command_pid = parts
	if command_machine_id != machine_id:
		return

	if command_pid.isdigit() and not psutil.pid_exists(int(command_pid)):
		slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text="PID `{}` Could not be found".format(command_pid))
		return
	proc = psutil.Process(int(command_pid))

	track_pid(proc, channel)

def check_tracked_pids():
	while(True):
		gone, alive = psutil.wait_procs(pids_tracked.keys(), timeout=0.1)
		for proc in gone:
			total_time = int(time.time() - pids_tracked[proc][1])
			slack_client.api_call(
			"chat.postMessage",
			channel=pids_tracked[proc][0],
			text="Process `{}` with PID `{}` finished after `{}`.".format(pids_tracked[proc][2], proc.pid, str(datetime.timedelta(seconds=total_time))))
			pids_tracked.pop(proc)
		time.sleep(1)
	



if __name__ == "__main__":
	if slack_client.rtm_connect(with_team_state=False):
		print("Starter Bot connected and running!")
		# Read bot's user ID by calling Web API method `auth.test`
		starterbot_id = slack_client.api_call("auth.test")["user_id"]
		print(starterbot_id)
		tracking_thread = Thread(target=check_tracked_pids)
		tracking_thread.daemon = True
		tracking_thread.start()
		while True:
			try:
				command, channel = parse_bot_commands(slack_client.rtm_read())
				if command:
					handle_command(command, channel)
				time.sleep(RTM_READ_DELAY)
			except:
				slack_client.rtm_connect(with_team_state=False)
	else:
		print("Connection failed. Exception traceback printed above.")
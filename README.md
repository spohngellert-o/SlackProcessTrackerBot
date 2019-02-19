# SlackProcessTrackerBot

Use this to track any long running processes through slack! This app uses the slack bot api to allow users to track processes, and receive a notification when they finish.

### Set Up

Run the following to install the library dependencies:

```bash
pip install psutil
pip install slackclient
```

Next, install the bot into slack. See the following guide for doing this: https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

Finally, set the environment variable `ProcessTrackerToken` to the Bot User Access Token seen in the blog above. You can use the following command in linux:

```bash
export ProcessTrackerToken='YOUR_TOKEN'
```

### Running The Bot

Typically, a user will run the slackbot in the background. Once set up, you can run the following command:

```bash
python slackbot.py YOUR_MACHINE_ID &> out.log &
```

Give it whatever machine id you'd like, as this will be used to identify which machine should be used to track processes.

### Using The Bot

Using the bot is fairly simple. In slack, simply send the bot a message with the following format:

```
MACHINE_ID PID
```

If the bot found the process, it'll send you a message saying it found it and that it is now tracking! Once the process completes, it'll send you a message telling you it has completed, along with how long it took to complete.
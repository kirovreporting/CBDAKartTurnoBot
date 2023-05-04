# Bot for detecting free windows for the Buenos Aires Kartodromo

It just looks for free slots at [this page](https://www.turnonet.com/2010-club-argentino-de-karting-ac) and texts you if new one is found.
Runs on python3 with selenium, beautifulsoup4, webdriver-manager and pytz packages.
To specify bot token, chat ID and working hours create bot.config file in the same directory; see bot.config.example.
Use .service and .timer files to run it every 5 mins with your VM's systemd — move them to `/etc/systemd/system`, then do `systemctl daemon-reload` and `systemctl enable CDBAKartTurnoBot.timer`.
Pay attention to chromium version installed on your server and specify proper webdriver version in config. List of available drivers can be found [here](https://chromedriver.storage.googleapis.com).
#!/usr/bin/env python
#
# Script (to be run by cron job) to monitor running zeno simulations and alert
# someone if they aren't working.

import os,ConfigParser,re,email

config = ConfigParser.RawConfigParser()
config.read('zeno_monitor.cfg')

email=config.get('Monitor','email')

if not(os.isfile('/tmp/zeno_monitor')):
  os.mkfifo('/tmp/zeno_monitor')
  os.system('ps > /tmp/zeno_monitor')



# send an email if there's anything wrong:
#http://stackoverflow.com/questions/6270782/sending-email-with-python

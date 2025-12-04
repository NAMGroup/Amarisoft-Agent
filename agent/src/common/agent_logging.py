# https://tutorialedge.net/python/python-logging-best-practices/
import logging
import logging.handlers as handlers
import time
import sys


# logger = logging.getLogger('my_app')
# logger.setLevel(logging.INFO)

# logHandler = handlers.TimedRotatingFileHandler('timed_app.log', when='M', interval=1)
# logHandler.setLevel(logging.INFO)
# logger.addHandler(logHandler)

print(logging)
print(logging.handlers)
logger = logging.getLogger('agent')
logger.setLevel(logging.DEBUG)

## Here we define our formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logHandler = handlers.TimedRotatingFileHandler('../agent.log', when='D', interval=1, backupCount=0)
logHandler.setLevel(logging.DEBUG)
logHandler.setFormatter(formatter)

errorLogHandler = handlers.RotatingFileHandler('../error.log', maxBytes=5000, backupCount=0)
errorLogHandler.setLevel(logging.ERROR)
errorLogHandler.setFormatter(formatter)


consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(formatter)

logger.addHandler(logHandler)
logger.addHandler(errorLogHandler)
logger.addHandler(consoleHandler)
# def main():
#     while True:
#         time.sleep(1)
#         logger.info("A ssssSample Log Statement")
#         logger.error("An eeeerror log statement")

# main()

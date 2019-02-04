
# creating log file directory...
import logging
import os

if not os.path.exists('./log'):
    os.makedirs('./log')

# creating tracker file directory...
if not os.path.exists('./track'):
    os.makedirs('./track')

# Create a custom logger
logger = logging.getLogger(__name__)

# need to set this root level logger for the handler log level to take effect...
logger.setLevel(logging.DEBUG)
# Create handlers
c_handler = logging.StreamHandler()
# Generating log file in the directory where the script file is kept...
f_handler = logging.FileHandler('./log/application.log')
c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

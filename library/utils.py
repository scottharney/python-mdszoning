# utils.py
# 
# General utilities functions

class bcolors:
    OKGREEN = '\033[92m' # Green
    WARNING = '\033[93m' # Yellow
    FAIL = '\033[91m' # Red
    OKBLUE = '\033[94m' # Blue
    HEADER = '\033[95m' # Pink
    BOLD = '\033[1m' # Bold text
    UNDERLINE = '\033[4m' # Underline text
    ENDC = '\033[0m' # EOL

def confirm(prompt=None, resp=False):
    """ Prompts yes or no response to user user.
    Returns True for yes and False for no """
    
    # Set a default message if no param was received
    if prompt is None:
        prompt = 'Confirm?'

    # Check if 'resp' was set to True the default answer will be set to Y (yes),
    # if varible wasn't set the default answer will be N (No)
    if resp:
        prompt = '%s [%s/%s]: ' % (prompt, 'Y', 'n')
    else:
        prompt = '%s [%s/%s]: ' % (prompt, 'y', 'N')
        
    # Create a while loop to read the answer from terminal.
    # If no answer, the print will be returned
    while True:
        answer = raw_input(prompt)
        if not answer:
            return resp
        if answer not in ['y', 'Y', 'n', 'N']:
            print 'Please enter y or n.\n'
            continue
        if answer == 'y' or answer == 'Y':
            return True
        if answer == 'n' or answer == 'N':
            return False

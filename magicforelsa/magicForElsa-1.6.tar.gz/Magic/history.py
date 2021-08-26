import datetime, webbrowser, os


def user_file(username, command, task_did):  # sourcery skip: ensure-file-closed
    """[Used to save the history of the user]

    Args:
        username ([str]): [The username of the user]
        command ([str]): [What was the command that the user asked to do]
        task_did ([str]): [Action taken]
    """
    userpth = os.getcwd() + f'\\resources\\ {username}.elsa'
    history = open(userpth, 'a')
    history.write(
        f'{datetime.datetime.now()} user input: {command}, output: {task_did}')
    history.write('\n')
    history.close()


def user_read(event="", username="admin"):
    """[Open the user history file]

    Args:
        event (str, optional): [Not imp]. Defaults to "".
        username (str, optional): [Name of the user to be opened]. Defaults to "admin".
    """
    userpth = os.getcwd() + f'\\resources\\ {username}.elsa'
    webbrowser.open(userpth)


def clear_history(name):  # sourcery skip: ensure-file-closed
    """[Clears the history of the user]

    Args:
        name ([str]): [Name of the user to clear]
    """
    userpth = os.getcwd() + f'\\resources\\ {name}.elsa'
    history = open(userpth, 'w')
    history.write('')
    history.close()

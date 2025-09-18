BUILD = 'Build'
CANCEL = 'Cancel'
CHECK = 'Check'
CLEAR = 'Clear'
CLOSE = 'Close'
CODE = 'Code'
COMPARE = 'Compare'
CONFIG = 'Config'
COPY = 'Copy'
DELETE = 'Delete'
DELETE_THESE_ITEMS = 'Are you sure you want to delete these item(s)?'
DIFF = 'Diff'
DONE = 'Done'
EDIT = 'Edit'
EVENT = 'Event'
EXIT = 'Exit'
HELP = 'Help'
NEW = 'New'
NEXT = 'Next'
NO = 'No'
NO_SUCH_FILE = 'no such file or directory'
OK = 'OK'
OPEN = 'Open'
PAUSE = 'Pause'
PREFERENCES = 'Preferences'
PREVIOUS = 'Prev'
PROCESS = 'Process'
QUIT = 'Quit'
REDO = 'Redo'
REFRESH = 'Refresh'
REPORT = 'Report'
RENAME = 'Rename'
RESET = 'Reset'
REVERT = 'Revert'
RUN = 'Run'
SAVE = 'Save'
SCRIPT = 'Script'
SAVE_PDF = 'Save as PDF'
SEARCH = 'Search'
SEND = 'Send'
START = 'Start'
UPDATE = 'Update'
UPGRADE = 'Upgrade'
USE = 'Use'
WINDOWS = 'Windows'
YES = 'Yes'


strings = {
    'BUILD': 'Build',
    'CANCEL': 'Cancel',
    'CHECK': 'Check',
    'CLEAR': 'Clear',
    'CLOSE': 'Close',
    'CODE': 'Code',
    'COMPARE': 'Compare',
    'CONFIG': 'Config',
    'COPY': 'Copy',
    'DELETE': 'Delete',
    'DELETE_THESE_ITEMS': 'Are you sure you want to delete these item(s)?',
    'DIFF': 'Diff',
    'DONE': 'Done',
    'EDIT': 'Edit',
    'ELLIPSIS': ' ...',
    'EVENT': 'Event',
    'EXIT': 'Exit',
    'HELP': 'Help',
    'NEW': 'New',
    'NEXT': 'Next',
    'NO': 'No',
    'NO_SUCH_FILE': 'no such file or directory',
    'OK': 'OK',
    'OPEN': 'Open',
    'PAUSE': 'Pause',
    'PREFERENCES': 'Preferences',
    'PREVIOUS': 'Prev',
    'PROCESS': 'Process',
    'QUIT': 'Quit',
    'REDO': 'Redo',
    'REFRESH': 'Refresh',
    'REPORT': 'Report',
    'RENAME': 'Rename',
    'RESET': 'Reset',
    'REVERT': 'Revert',
    'RUN': 'Run',
    'SAVE': 'Save',
    'SCRIPT': 'Script',
    'SAVE_PDF': 'Save as PDF',
    'SEARCH': 'Search',
    'SEND': 'Send',
    'START': 'Start',
    'UPDATE': 'Update',
    'UPGRADE': 'Upgrade',
    'USE': 'Use',
    'WINDOWS': 'Windows',
    'YES': 'Yes',
}


class Text():
    """Combines package level and psiutils strings."""
    def __init__(self, compare: dict = None) -> None:
        """
        Initialize the object with attributes based on the key-value pairs
        in the `strings` dictionary.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
        self.strings = strings
        for key, string in strings.items():
            setattr(self, key, string)

        # Optionally display contents of `strings`
    def display(self, compare: dict = None) -> None:
        if not compare:
            compare = {}
        for item in sorted(list(strings)):
            output = f'{item:.<20} {strings[item]}'
            if item in compare:
                if strings[item] != compare[item]:
                    output = f'{output}, {compare[item]} ***'
                else:
                    output = f'{output} <{"="*10} //duplicate//'
            print(output)

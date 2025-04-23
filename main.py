import os
import argparse
from datetime import datetime

from logger import InputLogger

__prog__ = 'loginput'


def create_parser():
    tab = '\x1b[C' * 4
    text = f'This in an {__prog__} app. Input logger tracks mouse and keyboard input and saves it to a SQL database.'

    # Main parser
    parser = argparse.ArgumentParser(prog=__prog__, description=text, add_help=False)

    # Required arguments
    required = parser.add_argument_group('arguments')
    exclusive_required = required.add_mutually_exclusive_group(required=True)
    exclusive_required.add_argument('-f', '--folder', type=path_type, help=tab + 'Output folder', default=None, metavar='\b')
    exclusive_required.add_argument('-d', '--database', type=path_type, help=tab + 'Output ".db" database', default=None, metavar='\b')

    # Optional arguments
    options = parser.add_argument_group('options')
    options.add_argument('-V', '--version', action='version', version='1.0.0', help='Show version and exit.')
    options.add_argument('-h', '--help', action='help', help='Show help and exit.')
    options.add_argument('-v', '--verbose', action='store_true', help='Show input log.')

    # Mutually exclusive group
    exclusive_options = options.add_mutually_exclusive_group()
    exclusive_options.add_argument('--only_mouse', action='store_true', help='Only log mouse input.')
    exclusive_options.add_argument('--only_keyboard', action='store_true', help='Only log keyboard input.')

    # Return the parser
    return parser


def path_type(value):
    value = fr'{str(value)}'
    value = os.path.abspath(value)
    return value


# Run main function
if __name__ == "__main__":

    # Parse arguments
    args_parser = create_parser()
    args = args_parser.parse_args()

    # Define output
    if args.folder is not None:
        os.makedirs(args.folder, exist_ok=True)
        database = f'{datetime.today().strftime("%Y-%m-%d_%H-%M-%S")}.db'
        database = os.path.join(args.folder, database)
    elif args.database is not None:
        if not args.database.endswith('.db'):
            raise argparse.ArgumentTypeError('"--database" must be in ".db" format.')
        os.makedirs(os.path.dirname(args.database), exist_ok=True)
        database = args.database
    else:
        raise argparse.ArgumentTypeError('Specify "--folder" or a "--database".')

    # Logging selection
    if args.only_mouse:
        logger = InputLogger(database, True, True, True, False, args.verbose)
    elif args.only_keyboard:
        logger = InputLogger(database, False, False, False, True, args.verbose)
    else:
        logger = InputLogger(database, True, True, True, True, args.verbose)

    # Run the logger
    logger.run()

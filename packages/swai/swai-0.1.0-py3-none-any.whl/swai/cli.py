import argparse
from pathlib import Path
import os
import sys
from swai.const import SWAI_API_URL
from swai.controller import Controller

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def parse_args():
    parser = argparse.ArgumentParser()
    
    subparsers = parser.add_subparsers(title='command', dest='command', 
                                    description='swai commands:\n login for user authentication, submit for task submission')
    
    # Login command
    login_parser = subparsers.add_parser('login', help='swai login <api_key>')
    login_parser.add_argument('api_key', type=str, help='Your API key for authentication')
    
    # Submit command
    submit_parser = subparsers.add_parser('submit', 
                            help='swai submit --task_type {swbind, swdocking} --task_input <task_input_file>')
    submit_parser.add_argument('-t', '--task_type', type=str, required=True,
                                                choices=['swbind', 'swdocking'], 
                                                help='swai task type for submit {swbind, swdocking}')
    submit_parser.add_argument('-i', '--task_input', type=str, required=True,
                                                help='swai task input file path (.zip) for submit')
    submit_parser.add_argument('-d', '--description', type=str, required=True,
                                                help='swai task commit message and description')
    submit_parser.add_argument('--subscribe_email', type=str2bool, default=False,
                                                help='swai task subscribe email for submit, send email to user when task is finished')

    # List command
    list_parser = subparsers.add_parser('list', help='swai list {status, id, type, limit} -s/--status {queued, running, done, failed, cancelled, all} -i/--id <task_id> -t/--type <task_type> -l/--limit <limit>')
    list_parser.add_argument('-s', '--status', type=str, choices=['queued', 'running', 'done', 'failed', 'cancelled', 'all'], default='all', help='swai task status for list {queued, running, finished, failed, cancelled}')
    list_parser.add_argument('-t', '--task_type', type=str, choices=['swbind', 'swdocking', 'all'], default='all', help='swai task type for list {swbind, swdocking}')
    list_parser.add_argument('-l', '--limit', type=int, default=50, help='swai task limit for list')
    list_parser.add_argument('-i', '--task_id', type=str, default=None, help='swai task id for list')
    
    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='swai cancel <task_id>')
    cancel_parser.add_argument('task_id', type=str, help='swai task id for cancel')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('download', help='swai download <task_id>')
    fetch_parser.add_argument('task_id', type=str, help='swai task id for download')
    fetch_parser.add_argument('-o', '--output', type=str, help='swai task output file path for fetch, default: <task_id>.zip')

    # help command
    help_parser = subparsers.add_parser('help', help='swai help')
    return parser


def main():
    root = Path(os.path.realpath(__file__))
    sys.path.append(str(root))
    parser = parse_args()
    
    Controller(parser).run()


if __name__ == "__main__":
    main()
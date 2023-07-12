import argparse
from create import create
from run import run
from models import sync_models
from fmt import fmt
from io import TextIOWrapper

parser = argparse.ArgumentParser(description='''Welcome to Flython!
                                 
                                 To create a full stack application with Flython, run 'flython create <your project name>'.
                                 To run the front end for the generated example, run
                                 
                                 ```
                                 cd <your project name>
                                 flython run front
                                 ```

                                 To run the back end, run
                                 ```
                                 flython run back
                                 ```
                                 ''')
parser.add_argument('command', 
                    choices= ['create', 'run', 'sync', 'fmt'], 
                    help='What do you want to do with Flython?')
parser.add_argument('project_name', 
                    type=str, 
                    help='''What is your project called? 
NOTE: This is a required positional argument for all commands!''', 
                    )
parser.add_argument('-server',
                    choices=['front','back'],
                    required=False,
                    help='Are you running the front or the back end?',
                    )
parser.add_argument('-models', 
                    required=False,
                    type=open,
                    help='''What models are you using?
Provide A JSON file representing the models for communicating between your front and back end.
Formatting rules for this model structure can be viewed by running "flython fmt".''')
args = parser.parse_args()

if args.command == 'create':
    create(args.project_name)
elif args.command == 'run':
    run(args.server)
elif args.command == 'sync':
    if args.models != None:
        models_wrapper:TextIOWrapper = TextIOWrapper(args.models)
        
        models_str = str(models_wrapper.buffer.read())
        sync_models(project=args.project_name, models_str=models_str)
    else:
        print('Currently, only synchronizing models from a JSON file is supported. Please refer to the help documentation.')
elif args.command == 'fmt':
    fmt()
else:
    print('Invalid command. Run "flython -h" for a list of valid commands.')

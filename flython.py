import argparse
from create import create
from run import run
from models import sync_models
from fmt import fmt
from io import TextIOWrapper
from os import getcwd, path

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

subparsers = parser.add_subparsers(title='Commands', dest='command')

create_parser = subparsers.add_parser('create', help='Create a new Flython project')
create_parser.add_argument('project_name', help='The name of the new project')

run_parser = subparsers.add_parser('run', help='Run the Flython application')
run_parser.add_argument('-server', choices=['front', 'back'], required=False, help='Specify the front or back end to run separately')

fmt_parser = subparsers.add_parser('fmt', help='Get instructions for formatting integration models')

sync_parser = subparsers.add_parser('sync', help='Synchronize front and back end models to a JSON specification')
sync_parser.add_argument('models', type=open, help='''What models are you using?
Provide A JSON file representing the models for communicating between your front and back end.
Formatting rules for this model structure can be viewed by running "flython fmt".''')
args = parser.parse_args()
dir = getcwd()
dir_name = path.basename(dir)

if args.command == 'create':
    create(args.project_name)
elif args.command == 'run':
    
    if args.server != None:
        run(dir_name=dir_name, server=args.server)
    else:
        run(dir_name)
elif args.command == 'sync':
    if args.models != None:
        models_wrapper:TextIOWrapper = TextIOWrapper(args.models)
        
        models_str = str(models_wrapper.buffer.read())
        sync_models(project=dir_name, models_str=models_str)
    else:
        print('Currently, only synchronizing models from a JSON file is supported. Please refer to the help documentation.')
elif args.command == 'fmt':
    fmt()
else:
    print('Invalid command. Run "flython -h" for a list of valid commands.')

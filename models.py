import json
from python_models import build_python_models
from flutter_models import build_flutter_models

def sync_models(project:str, models_str:str):
    models_dict = json.loads(models_str)
    models = []
    model_names = []
    for key in models_dict.keys():
        model_name = key
        model = models_dict[key]
        models.append(model)
        model_names.append(model_name)
    build_python_models(models, model_names)
    build_flutter_models(models, model_names, project)

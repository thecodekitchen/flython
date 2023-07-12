import json

def models(project:str, models_str:str):
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
          
def build_python_models(models, model_names):
    with open(f'./app/models.py', 'w') as f:
        f.write('''from pydantic import BaseModel
''')
        for idx, model in enumerate(models):
            f.write(f'''
class {model_names[idx]}(BaseModel):''')
            for key in model.keys():
                attr_type = model[key]
                optional:bool = str(key).startswith('?')
                if optional:
                    key = str(key).removeprefix('?')
                if(attr_type=='string'):
                    if optional:
                        f.write(f'''
    {key}: str | None''')
                    else:
                        f.write(f'''
    {key}: str''')
                elif(attr_type=='int'):
                    if optional:
                        f.write(f'''
    {key}: int | None''')
                    else:
                        f.write(f'''
    {key}: int''')
                elif(attr_type=='float'):
                    if optional:
                        f.write(f'''
    {key}: float | None''')
                    else:
                        f.write(f'''
    {key}: float''')
                else:
                    # In this case, the type is likely a nested model to be described later, so we just pass it as is.
                    if optional:
                        f.write(f'''
    {key}: {attr_type} | None''')
                    else:
                        f.write(f'''
    {key}: {attr_type}''')
            f.write('''
''')
                    
def build_flutter_models(models, model_names, project):
    with open(f'./{project}_fe/lib/models.dart', 'w') as f:
        f.write('''class Model {
  Map toJson() => {};
}
''')
        for idx, model in enumerate(models):
            f.write(f'''
class {model_names[idx]} extends Model {{''')
            for key in model.keys():
                attr_type = model[key]
                optional:bool = str(key).startswith('?')
                if optional:
                    key = str(key).removeprefix('?')
                if attr_type=='string':
                    if optional:
                        f.write(f'''
  String? {key} = '';''')
                    else:
                        f.write(f'''
  String {key} = '';''')
                elif attr_type=='int':
                    if optional:
                        f.write(f'''
  int? {key} = 0;''')
                    else:
                        f.write(f'''
  int {key} = 0;''')
                elif attr_type=='float':
                    if optional:
                        f.write(f'''
  Double? {key} = 0.0;''')
                    else:
                        f.write(f'''
  Double {key} = 0.0;''')
                else:
                    if optional:
                        f.write(f'''
  {attr_type}? {key};''')
                    else:
                        f.write(f'''
  {attr_type} {key};''')
            f.write('''
''')
            f.write(f'''
  {model_names[idx]}({{''')
            
            for key in model.keys():
                attr_type = model[key]
                optional:bool = str(key).startswith('?')
                if optional:
                    key = str(key).removeprefix('?')
                if attr_type=='string':
                    if optional:
                        f.write(f'''
    this.{key},''')
                    else:
                        f.write(f'''
    required this.{key},''')
                elif attr_type=='int':
                    if optional:
                        f.write(f'''
    this.{key},''')
                    else:
                        f.write(f'''
    required this.{key},''')
                elif attr_type=='float':
                    if optional:
                        f.write(f'''
    this.{key},''')
                    else:
                        f.write(f'''
    required this.{key},''')
                else:
                    if optional:
                        f.write(f'''
    this.{key},''')
                    else:
                        f.write(f'''
    required this.{key},''')
            f.write('''
  });
''')
            f.write('''
  @override
  Map toJson() => {''')
            for key in model.keys():
                if str(key).startswith('?'):
                    key = str(key).removeprefix('?')
                f.write(f'''
    '{key}':{key},''')
            f.write('''
  };
}
''')
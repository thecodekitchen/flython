def build_flutter_models(models, model_names, project):
    with open(f'./{project}_fe/lib/models.dart', 'w') as f:
        f.write('''class BaseModel {
  Map toJson() => {};
}
''')
        for idx, model in enumerate(models):
            f.write(f'''
class {model_names[idx]} extends BaseModel {{''')
            for key in model.keys():
                attr_type = model[key]
                is_optional:bool = str(key).startswith('?')
                is_list:bool = str(key).endswith('[]')

                # remove prefixes and suffixes to get clean class attribute names
                if is_optional:
                    key = str(key).removeprefix('?')
                if is_list:
                    key = str(key).removesuffix('[]')

                if attr_type=='string':
                    if is_optional:
                        if is_list:
                            f.write(f'''
  List<String>? {key};''')
                        else:
                            f.write(f'''
  String? {key};''')
                    else:
                        if is_list:
                            f.write(f'''
  List<String> {key};''')
                        else:
                            f.write(f'''
  String {key};''')
                elif attr_type=='int':
                    if is_optional:
                        if is_list:
                            f.write(f'''
  List<int>? {key};''')
                        else:
                            f.write(f'''
  int? {key};''')
                    else:
                        if is_list:
                            f.write(f'''
  List<int> {key};''')
                        else:
                            f.write(f'''
  int {key};''')
                elif attr_type=='float':
                    if is_optional:
                        if is_list:
                            f.write(f'''
  List<Double>? {key};''')
                        else:
                            f.write(f'''
  Double? {key};''')
                    else:
                        if is_list:
                            f.write(f'''
  List<Double> {key};''')
                        else:
                            f.write(f'''
  Double {key};''')
                elif attr_type=='bool':
                    if is_optional:
                        if is_list:
                            f.write(f'''
  List<bool>? {key};''')
                        else:
                            f.write(f'''
  bool? {key};''')
                    else:
                        if is_list:
                            f.write(f'''
  List<bool> {key};''')
                        else:
                            f.write(f'''
  bool {key};''')
                else:
                    if is_optional:
                        if is_list:
                            f.write(f'''
  List<{attr_type}>? {key};''')
                        else:
                            f.write(f'''
  {attr_type}? {key};''')
                    else:
                        if is_list:
                            f.write(f'''
  List<{attr_type}> {key};''')
                        else:
                            f.write(f'''
  {attr_type} {key};''')
            
            f.write('''
''')
            f.write(f'''
  {model_names[idx]}({{''')
            
            for key in model.keys():
                attr_type = model[key]
                is_optional:bool = str(key).startswith('?')
                is_list:bool = str(key).endswith('[]')

                if is_list:
                    key = str(key).removesuffix('[]')

                if is_optional:
                    key = str(key).removeprefix('?')
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
                if str(key).endswith('[]'):
                    key = str(key).removesuffix('[]')

                f.write(f'''
    '{key}': {key},''')
            f.write('''
  };
}
''')
        f.close()

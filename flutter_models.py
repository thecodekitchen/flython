import re

def find_class_extension(class_name:str):
    start_index = class_name.find("(")
    end_index = class_name.find(")")
    name = class_name[0:start_index]
    extension = class_name[start_index + 1:end_index]
    print(f'name:{name}, ext:{extension}')
    return dict({'name': name, 'ext': extension})

def sanitize_model_names (names:list[str]):
    sanitized_model_names = []
    for name in names:
        pattern = r"\(.*?\)"
        model_name = re.sub(pattern, "", name)
        sanitized_model_names.append(model_name)
    return sanitized_model_names

def merge_dictionaries (dict1, dict2):
    merged_dict = {}
    for key, value in dict1.items():
        if key not in merged_dict:
            merged_dict[key] = value
    for key, value in dict2.items():
        if key not in merged_dict:
            merged_dict[key] = value
    return merged_dict

def get_super_properties (models, model_names:list[str], super:str):
    sanitized_model_names = sanitize_model_names(model_names)

    if sanitized_model_names.__contains__(super):
        super_index = sanitized_model_names.index(super)
        # if the base model itself has a base model ...
        if model_names[super_index].__contains__('('):
            ext = find_class_extension(model_names[super_index])['ext']
            base_model:dict = get_super_properties(models, model_names, ext)
            extended_model:dict = merge_dictionaries(base_model, models[super_index])
            return extended_model
        return models[super_index]
    else:
        print(f'''
Invalid model extension. 
Attempted to extend non-existent model {super}. 
Ensure that the extending model is declared after the extended model in the JSON file. Extending non-model classes is not allowed.''')
        exit(code=1)

def build_flutter_models(models, model_names, project):
    
    with open(f'./{project}_fe/lib/models.dart', 'w') as f:
        f.write('''class BaseModel {
  String? type = 'BaseModel';
  BaseModel({this.type = 'BaseModel'});
  Map toJson() => {
    'type': 'BaseModel'
  };
}
''')
        for idx, model in enumerate(models):
            no_extensions = model_names[idx].find('(') == -1 or model_names[idx].find(')') == -1
            if no_extensions:
                f.write(f'''
class {model_names[idx]} extends BaseModel {{''')
            else:
                class_dict = find_class_extension(model_names[idx])
                f.write(f'''
class {class_dict['name']} extends {class_dict['ext']} {{''')
            for key in model.keys():
                attr_type:str = model[key]
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
  List<double>? {key};''')
                        else:
                            f.write(f'''
  double? {key};''')
                    else:
                        if is_list:
                            f.write(f'''
  List<double> {key};''')
                        else:
                            f.write(f'''
  double {key};''')
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
            if no_extensions:
                f.write(f'''
  {model_names[idx]}({{''')
                f.write(f'''
  super.type = '{model_names[idx]}',''')
            else:
                class_name = find_class_extension(model_names[idx])['name']
                f.write(f'''
  {class_name}({{''')
                f.write(f'''
  super.type = '{class_name}',''')
            for key in model.keys():
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
            if no_extensions == False:
                ext = find_class_extension(model_names[idx])['ext']
                super_model = get_super_properties(models, model_names, ext)
                for key in super_model.keys():
                    is_optional:bool = str(key).startswith('?')
                    is_list:bool = str(key).endswith('[]')

                    if is_list:
                        key = str(key).removesuffix('[]')

                    if is_optional:
                        key = str(key).removeprefix('?')
                        f.write(f'''
    super.{key},''')
                    else:
                        f.write(f'''
    required super.{key},''')
            f.write('''
  });
''')
            f.write('''
  @override
  Map toJson() {''')
            for key in model.keys():
                unsanitized = key
                isList = False
                isOptional = False
                if str(key).startswith('?'):
                    key = str(key).removeprefix('?')
                    isOptional = True
                if str(key).endswith('[]'):
                    key = str(key).removesuffix('[]')
                    isList = True
                if isList:
                    if (model_names.__contains__(model[unsanitized])):
                        if isOptional:
                            f.write(f'''
    List<Map> {key}List = [];
    for ({model[unsanitized]} item in {key}??[]){{
        {key}List.add(item.toJson());''')
                        else:
                            f.write(f'''
    List<Map> {key}List = [];
    for ({model[unsanitized]} item in {key}){{
        {key}List.add(item.toJson());''')
                        f.write('''
        }
''')
            if no_extensions == False:
                ext = find_class_extension(model_names[idx])['ext']
                super_model = get_super_properties(models, model_names, ext)
                for key in super_model.keys():
                    unsanitized = key
                    isList = False
                    isOptional = False
                    if str(key).startswith('?'):
                        key = str(key).removeprefix('?')
                        isOptional = True
                    if str(key).endswith('[]'):
                        key = str(key).removesuffix('[]')
                        isList = True
                    if isList:
                        if (model_names.__contains__(super_model[unsanitized])):
                            if isOptional:
                                f.write(f'''
        List<Map> {key}List = [];
        for ({super_model[unsanitized]} item in {key}??[]){{
            {key}List.add(item.toJson());''')
                            else:
                                f.write(f'''
        List<Map> {key}List = [];
    for ({super_model[unsanitized]} item in {key}){{
        {key}List.add(item.toJson());''')
                        f.write('''
        }
''')
            f.write('''
    return {''')
            if no_extensions:
                f.write(f'''
    'type': '{model_names[idx]}',''')
            else:
                class_name = find_class_extension(model_names[idx])['name']
                f.write(f'''
    'type': '{class_name}',''')
            for key in model.keys():
                unsanitized = key
                isList = False
                isOptional = False
                if str(key).startswith('?'):
                    key = str(key).removeprefix('?')
                    isOptional = True
                if str(key).endswith('[]'):
                    key = str(key).removesuffix('[]')
                    isList = True
                if (model_names.__contains__(model[unsanitized])):
                    if isList == False:
                        if isOptional:
                            f.write(f'''
    '{key}': {key} != null ? {key}!.toJson() : null,''')
                        else:
                            f.write(f'''
    '{key}': {key}.toJson(),''')
                    else:
                        f.write(f'''
    '{key}': {key}List,''')
                else:
                    f.write(f'''
    '{key}': {key},''')
            if no_extensions == False:
                ext = find_class_extension(model_names[idx])['ext']
                super_model = get_super_properties(models, model_names, ext)
                for key in super_model:
                    unsanitized = key
                    isList = False
                    isOptional = False
                    if str(key).startswith('?'):
                        key = str(key).removeprefix('?')
                        isOptional = True
                    if str(key).endswith('[]'):
                        key = str(key).removesuffix('[]')
                        isList = True
                    if (model_names.__contains__(super_model[unsanitized])):
                        if isList:
                            f.write(f'''
    '{key}': {key}List,''')
                        else:
                            f.write(f'''
    '{key}': {key}.toJson(),''')
                    else:
                        f.write(f'''
    '{key}': {key},''')
            f.write('''
    };
  }
''')
            if no_extensions:
                f.write(f'''
  static {model_names[idx]} fromJson(Map json) {{''')
                for key in model.keys():
                    unsanitized = key
                    isList = False
                    isOptional = False
                    if str(key).startswith('?'):
                        key = str(key).removeprefix('?')
                    if str(key).endswith('[]'):
                        key = str(key).removesuffix('[]')
                        isList = True
                    if (model_names.__contains__(model[unsanitized])):
                        if isList:
                            f.write(f'''
    List<{model[unsanitized]}> {key}List = [];''')
                            f.write(f'''
    for (Map<dynamic, dynamic> item in json['{key}']) {{
      {key}List.add({model[unsanitized]}.fromJson(item));''')
                            f.write('''
    }''')
                f.write(f'''
    return {model_names[idx]}(''')
                f.write(f'''
        type: '{model_names[idx]}',''')
            # case: There are extensions
            else:
                class_extension = find_class_extension(model_names[idx])
                class_name = class_extension['name']
                ext = class_extension['ext']
                super_model = get_super_properties(models, model_names, ext)
                
                f.write(f'''
  static {class_name} fromJson(Map json) {{''')
                
                for key in model.keys():
                    unsanitized = key
                    isList = False
                    isOptional = False
                    if str(key).startswith('?'):
                        key = str(key).removeprefix('?')
                        isOptional = True
                    if str(key).endswith('[]'):
                        key = str(key).removesuffix('[]')
                        isList = True
                    if (model_names.__contains__(model[unsanitized])):
                        if isList:
                            f.write(f'''
    List<{model[unsanitized]}> {key}List = [];''')
                            f.write(f'''
    for (Map<dynamic, dynamic> item in json['{key}']) {{
      {key}List.add({model[unsanitized]}.fromJson(item));''')
                            f.write('''
    }''')
                # repeat process for super classes
                for key in super_model.keys():
                    unsanitized = key
                    isList = False
                    isOptional = False
                    if str(key).startswith('?'):
                        key = str(key).removeprefix('?')
                        isOptional = True
                    if str(key).endswith('[]'):
                        key = str(key).removesuffix('[]')
                        isList = True
                    if (model_names.__contains__(super_model[unsanitized])):
                        if isList:
                            f.write(f'''
    List<{super_model[unsanitized]}> {key}List = [];''')
                            f.write(f'''
    for (Map<dynamic, dynamic> item in json['{key}']) {{
      {key}List.add({super_model[unsanitized]}.fromJson(item));''')
                            f.write('''
    }''')
                f.write(f'''
    return {class_name}(''')
                f.write(f'''
        type: '{class_name}',''')        
            for key in model.keys():
                unsanitized = key
                isOptional = False
                isList = False
                if str(key).startswith('?'):
                    key = str(key).removeprefix('?')
                    isOptional = True
                if str(key).endswith('[]'):
                    key = str(key).removesuffix('[]')
                    isList = True
                if (model_names.__contains__(model[unsanitized])):
                    if isList:
                        f.write(f'''
        {key}: {key}List,''')
                    else:
                        if isOptional:
                            f.write(f'''
        {key}: json['{key}'] != null ? 
                    {model[unsanitized]}.fromJson(json['{key}']) : 
                    null,''')
                        else:
                            f.write(f'''
        {key}: {model[unsanitized]}.fromJson(json['{key}']),''')
                else:
                    f.write(f'''
        {key}: json['{key}'],''')
            if no_extensions == False:
                ext = find_class_extension(model_names[idx])['ext']
                super_model = get_super_properties(models, model_names, ext)
                for key in super_model:
                    unsanitized = key
                    isList = False
                    isOptional = False
                    if str(key).startswith('?'):
                        key = str(key).removeprefix('?')
                        isOptional = True
                    if str(key).endswith('[]'):
                        key = str(key).removesuffix('[]')
                        isList = True
                    if (model_names.__contains__(super_model[unsanitized])):
                        if isList:
                            f.write(f'''
        {key}: {key}List,''')
                        else:
                            if isOptional:
                                f.write(f'''
        {key}: json['{key}'] != null ? 
                    {super_model[unsanitized]}.fromJson(json['{key}']) : 
                    null,''')
                            else:
                                f.write(f'''
        {key}: {super_model[unsanitized]}.fromJson(json['{key}']),''')
                    else:
                        f.write(f'''
        {key}: json['{key}'],''')
            f.write('''
    );
  }            
}
''')
        f.write('''
BaseModel parseModel(Map<dynamic, dynamic> modelMap) {
  switch (modelMap['type']) {''')
        sanitized_model_names = sanitize_model_names(model_names)
        for name in sanitized_model_names:
            f.write(f'''
    case '{name}':
        {{
            return {name}.fromJson(modelMap);''')
            f.write('''
        }''')
        f.write('''
    default:
      throw const FormatException('invalid model map');
  }
}''')

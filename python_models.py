def build_python_models(models, model_names):
    with open(f'./app/models.py', 'w') as f:
        f.write('''from pydantic import BaseModel
''')
        for idx, model in enumerate(models):
            f.write(f'''
class {model_names[idx]}(BaseModel):''')
            for key in model.keys():
                attr_type = model[key]
                is_optional:bool = str(key).startswith('?')
                is_list:bool = str(key).endswith('[]')

                if is_optional:
                    key = str(key).removeprefix('?')
                
                if is_list:
                    key = str(key).removesuffix('[]')
                if attr_type=='string':
                    if is_optional:
                        if is_list:
                            f.write(f'''
    {key}: list[str] | None''')
                        else:
                            f.write(f'''
    {key}: str | None''')
                    else:
                        if is_list:
                            f.write(f'''
    {key}: list[str]''')
                        else:
                            f.write(f'''
    {key}: str''')
                elif attr_type=='int':
                    if is_optional:
                        if is_list:
                            f.write(f'''
    {key}: list[int] | None''')
                        else:
                            f.write(f'''
    {key}: int | None''')
                    else:
                        if is_list:
                            f.write(f'''
    {key}: list[int]''')
                        else:
                            f.write(f'''
    {key}: int''')
                elif attr_type=='float':
                    if is_optional:
                        if is_list:
                            f.write(f'''
    {key}: list[float] | None''')
                        else:
                            f.write(f'''
    {key}: float | None''')
                    else:
                        if is_list:
                            f.write(f'''
    {key}: list[float]''')
                        else:
                            f.write(f'''
    {key}: float''')
                elif attr_type == 'bool':
                    if is_optional:
                        if is_list:
                            f.write(f'''
    {key}: list[bool] | None''')
                        else:
                            f.write(f'''
    {key}: bool | None''')
                    else:
                        if is_list:
                            f.write(f'''
    {key}: list[bool]''')
                        else:
                            f.write(f'''
    {key}: bool''')
                else:
                    # In this case, the type is likely a nested model to be described later, so we just pass it as is.
                    if is_optional:
                        if is_list:
                            f.write(f'''
    {key}: list[{attr_type}] | None''')
                        else:
                            f.write(f'''
    {key}: {attr_type} | None''')
                    else:
                        if is_list:
                            f.write(f'''
    {key}: list[{attr_type}]''')
                        else:
                            f.write(f'''
    {key}: {attr_type}''')
            f.write('''
''')
        f.close()

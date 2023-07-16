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

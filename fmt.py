def fmt():
    print('''
The strategy Flython uses to synchronize models between front and back end languages and tool sets involves
referring to any nested hash maps (objects within objects in Javascript terms) 
as their own model types which are described separately as additional top-level models.

Here is an example.

{
    "User": {
        "name": "string",
        "age": "int"
    },
    "Foo": {
        "bar": "string",
        "user": "User"
    }
}
          
In this JSON format, what could have looked like this:

{
    "Foo": {
        "bar": "string",
        "user": {
            "name": "string",
            "age": "int"
        }
    }
}
          
is expanded so that the 'user' object becomes its own top-level type declaration:
          
"User": {
        "name": "string",
        "age": "int"
    }
          
and is then referred to as a child element of the "Foo" object:
"Foo": {
        "bar": "string",
        "user": "User"
    }
          
In this way, model and schema computation is limited to a single
layer of nested types, and table structures become far more intuitive when
dealing with SQL-like databases.
          
If you need a field in one of your models to be optional, simply prefix it with a '?' in the json like so:

{
    "User":{
          "name": "string",
          "?age": "int"
    }
}
          
Flython's code generation algorithms will implement the necessary patterns for using 
optional values on the front and back end servers smoothly in tandem. This avoids situations
where one side of an http call expects values not supplied by the other. The JSON file is a single
source of truth to be referenced by both front and back end developers when custom types are
being exchanged between the front and back end.
''')
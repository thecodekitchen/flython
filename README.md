# Flython
Flutter business in the front, Python party in the back.

# What It's For
Making full stack apps! 
Specifically, if you like using Python libraries, but you hate trying to debug cross-platform UIs in Python,
do a Flutter instead!
Even better, do a Flython!

After you install the prerequisites listed below, you will be able to run

```
flython create <your-project-name>
```

and Flython will generate three things:

1. A containerized back end API application written with the FastAPI framework in Python
2. A Flutter front end application with a specific file structure that enables extremely simplified
   integration with the back end API
3. A JSON file defining a shared model schema that can be automatically translated across the front and back end data structures

From there, you can run

```
cd <your-project-name>
flython run -server=front
```

to run the front end or

```
cd <your-project-name>
flython run -server=back
```

to run the back end server.
Or even just
```
flython run
```
to run both from a single terminal! At the moment, that gets a little chaotic since the server logs for the back end server are mixed in with the debug logs for the front end application. This is especially messy when debugging mobile front ends. However, the recommended approach is to do your main integration testing in a less verbose desktop build for the front end (option 1 in the run command typically) and run the back end server separately when debugging the mobile implementation.

There will be a top level file called test_models.json in the built directory.
Notice that there is one more model in the JSON than the generated front and back end model files.
This is so that you can run the 'flython sync' command as described below and see how it works by adding
a model that way.

# Model Synchronization
Changes to the model schema should be made to a json file and applied with the 'flython sync' command like so:

```
flython sync test_models.json
```

You can synchronize the model schema for the front and back end in this way with any JSON file, allowing for 
versioned backups of prior configurations. However, breaking changes can occur if either the front or back end 
model files are edited independently. The whole point is to never do this. If you need a unique class in the front
or back end logic, that's fine. Just don't extend them from the BaseModel class (in the back end) or the Model class (in the front end).

Those class extensions operate as indicators that the front and back end need to synchronize those classes in a shared schema.
Any class that doesn't extend those base classes should be declared outside the models.py and models.dart files respectively.

Any optional attribute names for your model should be prefixed with a '?' in the JSON specification like so:
```
{
   "User": {
      "name": "string",
      "?age": "int"
}
```

Any list attributes should be suffixed with '[]' like so:
```
{
   "User": {
      "name": "string",
      "aliases[]": "string"
   }
}
```

Optional list attributes should combine the two syntaxes:
```
{
   "User": {
      "name": "string",
      "?aliases[]": "string"
   }
}
```
In the last case, the 'aliases' attribute of the User model will be treated in the generated model files as an optional List of strings on the User class which extends the the BaseModel (back end) or Model (front end) class.

For details on how to format your JSON models for optimal use with Flython, run 
```
flython fmt
```

# Prerequisites

1. python 3.10
2. pip
3. A Flutter installation with 'flutter doctor' running error-free
4. The pyinstaller Python package

[Download and install Python 3.10](https://www.python.org/downloads/release/python-3100/)

[Make sure pip is installed](https://pip.pypa.io/en/stable/installation/)

[Configure your Flutter stack](https://docs.flutter.dev/get-started/install)

[Install the pyinstaller package](https://pyinstaller.org/en/stable/installation.html)

# Building and Installation

After cloning this repo, cd into it and run

```
pyinstaller flython.py --onefile
```

That should generate an executable for your native platform  in the dist directory that you can move into whatever directory your favorite shell grabs its executables from. After doing so, you should be able to call 'flython' CLI commands in any directory.




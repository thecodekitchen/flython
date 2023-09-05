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
cd <your-project-name>
flython run
```
to run both from a single terminal!

There will be a top level file called test_models.json in the built directory.
Notice that there is one more model in the JSON than the generated front and back end model files.
This is so that you can run the 'flython sync' command as described below and see how it works by adding
a model that way.

# Model Synchronization
Changes to the model schema should be made to a json file and applied with the 'flython sync' command like so:

```
flython sync test_models.json
```

Rule 1:

You can synchronize the model schema for the front and back end in this way with any JSON file, allowing for 
versioned backups of prior configurations. However, breaking changes can occur if either the front or back end 
model files are edited independently. The whole point is to never do this. If you need a unique class in the front
or back end logic, that's fine. Just don't extend them from the BaseModel class in either code base. Also, don't include them in the models file for either codebase or else they will be written over and deleted when the models file is re-generated.

Those class extensions operate as indicators that the front and back end need to synchronize those classes in a shared schema.

** To reiterate, any class that doesn't extend those base classes should be declared outside the models.py and models.dart files respectively.**

Don't worry, that was the most complicated rule.

Rule 2:

Any optional attribute names for your model should be prefixed with a '?' in the JSON specification like so:
```
{
   "User": {
      "name": "string",
      "?age": "int"
}
```

Rule 3:

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
In the last case, the 'aliases' attribute of the User model will be treated in the generated model files as an optional List of strings on the User class which extends the the BaseModel class.

Rule 4:

Don't nest objects! Just create new ones and reference them. For instance, instead of this:

**Bad! Very bad!**
```
{
   "User": {
      "name",
      "documents[]": [
         {
            "name": "string",
            "content": "string"
         }
      ]
   }
}
```

do this:

**nice**
```
{
   "Document": {
      "name": "string",
      "content": "string"
   },
   "User": {
      "name": "string",
      "documents[]": "Document"
   }
}
```

Flython will automatically interpret this as an array (list) of 'Document' objects. To avoid compatibility bugs, the only complex (structured) data types that should be declared as attribute types in models should be other declared models. The simple data types that are currently supported include "string", "int", "float", and "bool". More granular data type support is on the roadmap, but the goal of simple, readable models seems to be mostly served within these limitations.

Rule 5:

Models need to be referenced AFTER they are declared. The reason that 'Document' came first in the above example is because the 'User' model references 'Document' in one of its attributes. This is mainly to appease the Python side of Flython, but I like it as a general rule because it gets you in the habit of only referencing what you've already defined. Wishful thinking in the opposite direction, in my experience, often leads to referencing things I forgot to build.

That's all the rules to the model synchronization game! Go have fun!

# New Rule!

I know five was a nice round number, but I decided things would go a lot smoother if I added class extensions. Now we can say
```
{
   "Document": {
      "name": "string",
      "content": "string"
   },
   "User": {
      "name": "string",
      "documents[]": "Document"
   },
   "Project: {
      "name": "string"
   },
   "FlythonUser(User)": {
      "projects[]": "Project
   }
}
```
and the FlythonUser class will be an extension of the User class containing one extra property, projects, which is a list of Project instances.

To see details on your command line of how to format your JSON models for optimal use with Flython, run 
```
flython fmt
```

# Supabase Authentication
You can now use the optional flag 
```
flython create my_project -supabase_auth=my-deeplink-scheme
```
to auto-generate Supabase integration code in both your front and back end code bases. You can provide the url and anonymous key of a Supabase project (free tier is fine) in the generated .env file. Be sure to add your chosen deep link scheme (used to redirect back to your app on mobile and desktop builds) to the list of allowed redirect urls in the Url Configuration section of Supabase's Authentication console for your project. This will need to be the same as the deep link scheme chosen when you created the project since it gets hard coded into the platform-specific codebases (currently just Android and web). The project will be configured by default to accept redirects at my-deeplink-scheme://home, but that can be configured by changing the host section of the redirect url in your Supabase Auth configuration. For example, if you wanted the auth process to redirect logged in users to a route called 'profile', you could set the allowed redirect url to my-deeplink-scheme://profile, checking for auth values in the initState function of the ProfilePage in order to prevent viewing of sensitive data.

The backend will be equipped with middleware that will check backend requests for a Supabase token in the header and validates their user information in order to determine access scope for backend resources. Middleware can be customized separately to check for specific Supabase user data. Rudimentary admin checks are provided as an example.

This is not guaranteed to be a fully secure solution to authentication/authorization of your backend in production. It is provided as a simple, automated way to implement certain basic security procedures that normally consume a lot of a developer's time and are easy to misconfigure.

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

WARNING: This was developed on Linux and hasn't yet been tested on Windows or Mac! Please let me know what bugs you experience, if any, when attempting to follow these instructions on those platforms. I will be happy to debug them with you.


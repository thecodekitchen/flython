import subprocess

def create (project:str):
  subprocess.run(['mkdir', project])
  subprocess.run(['touch', 'Dockerfile'], cwd=f'./{project}')
  subprocess.run(['touch', 'requirements.txt'], cwd=f'./{project}')

  with open(f'{project}/Dockerfile', 'w') as f:
      f.write(
'''FROM python:3.10
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
''')
      f.close()

  with open(f'{project}/requirements.txt', 'w') as f:
      f.write(
'''fastapi>=0.68.0,<0.69.0
pydantic>=1.8.0,<2.0.0
uvicorn>=0.15.0,<0.16.0
''')

  subprocess.run(['pip', 'install', '-r', 'requirements.txt', '--upgrade', '--no-cache-dir'], cwd=f'./{project}')
  subprocess.run(['sudo', 'apt', 'install', 'uvicorn'])
  subprocess.run(['mkdir', 'app'], cwd=f'./{project}')
  # subprocess.run(['touch', '__init__.py'], cwd=f'./{project}/app')
  subprocess.run(['touch', 'main.py'], cwd=f'./{project}/app')
  subprocess.run(['touch', 'models.py'], cwd=f'./{project}/app')

  with open(f'{project}/app/main.py', 'w') as f:
      f.write(
'''from fastapi import FastAPI
import app.models as models

app = FastAPI()

@app.post("/")
async def root(user: models.User):
    return {"message": f"Hello {user.name}"}
''')
      f.close()

  with open(f'{project}/app/models.py', 'w') as f:
      f.write(
'''from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
''')

  subprocess.run(['flutter', 'create', f'{project}_fe'], cwd=f'./{project}')
  subprocess.run(['flutter', 'pub', 'add', 'http'], cwd=f'./{project}/{project}_fe')
  subprocess.run(['touch', 'models.dart'], cwd=f'{project}/{project}_fe/lib')
  subprocess.run(['touch', 'backend.dart'], cwd=f'{project}/{project}_fe/lib')

  with open(f'{project}/{project}_fe/lib/models.dart', 'w') as f:
      f.write(
'''class Model {
  Map toJson() => {};
}

class User extends Model {
  String name = '';
  int age = 0;

  User({this.name = 'user', this.age = 0});

  @override
  Map toJson() => {
        'name': name,
        'age': age,
      };
}
''')

  with open(f'{project}/{project}_fe/lib/backend.dart', 'w') as f:
      f.write(
'''import 'package:http/http.dart';
import './models.dart';
import 'dart:convert';

class Backend {
  Uri baseUrl = Uri.parse('http://localhost:8000');

  Future<String> POST(Model model,
      {String? route, Map<String, String>? headers}) async {
    Map<String, String> postHeaders =
        Map.fromEntries([const MapEntry('Content-Type', 'application/json')]);
    if (headers != null) {
      postHeaders.addAll(headers);
    }
    if (route == null) {
      Response response =
          await post(baseUrl, headers: postHeaders, body: jsonEncode(model));
      return response.body;
    } else {
      Uri url = Uri.parse('$baseUrl/$route');
      Response response = await post(url, body: jsonEncode(model));
      return response.body;
    }
  }
}
''')

  with open(f'{project}/{project}_fe/lib/main.dart', 'w') as f:
      f.write(
'''import 'package:flutter/material.dart';
import './models.dart';
import './backend.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flython Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Flython Demo'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _response = '';
  User _user = User(name: 'doofus', age: 23);
  Backend backend = Backend();
  TextEditingController name = TextEditingController();
  void getResponse() async {
    String response = await backend.POST(_user);
    setState(() {
      _response = response;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.indigo,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          TextField(
              controller: name,
              onChanged: (text) => {setState(() => _user.name = text)},
              decoration: const InputDecoration(hintText: 'Enter your name')),
          FloatingActionButton(
            onPressed: getResponse,
            backgroundColor: Colors.indigo,
            child: const Text('Click to say Hello'),
          ),
          Text(_response)
        ]),
      ),
    );
  }
}
''')
# At this point, we need to implement our flashy ASCII art logo and provide brief instructions for how to run the front end.
  

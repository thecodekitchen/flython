def create_dockerfile (project:str):
    with open(f'{project}/Dockerfile', 'w') as f:
      f.write(
'''FROM python:3.10
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
''')

def create_main (project:str, supabase:bool):
    if supabase:
        with open(f'{project}/app/main.py', 'w') as f:
            f.write(
'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_auth_middleware import AuthMiddleware
from app.middleware import verify_header
from starlette.authentication import requires
from starlette.requests import Request

origins = [
  'http://localhost:3000'
]
app = FastAPI()
app.add_middleware(
    AuthMiddleware, 
    verify_header=verify_header)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

@app.get("/")
@requires("user")
def root(request: Request):
    return {"message": f"Hello, {request.user.username}! You are now an authenticated user!"}

@app.get("/admin")
@requires("admin")
def admin(request: Request):
    return {"message": f"Hello, {request.user.username}! You are now an authenticated admin!"}
''')
    else:
        with open(f'{project}/app/main.py', 'w') as f:
            f.write(
'''from fastapi import FastAPI
import app.models as models

app = FastAPI()

@app.post("/")
async def root(user: models.User):
    return {"message": f"Hello {user.name}"}
''')

def create_models(project):
    with open(f'{project}/app/models.py', 'w') as f:
      f.write(
'''from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
''')

def create_requirements (project:str, supabase:bool):
    if supabase:
        with open(f'{project}/requirements.txt', 'w') as f:
            f.write(
'''fastapi>=0.101.0
fastapi_auth_middleware==1.0.2
pydantic>=2.0.0
uvicorn>=0.15.0
python-dotenv==1.0.0
supabase>=1.0.3
''')
    else:
        with open(f'{project}/requirements.txt', 'w') as f:
          f.write(
'''fastapi>=0.68.0,<0.69.0
pydantic>=1.8.0,<2.0.0
uvicorn>=0.15.0,<0.16.0
''')

def create_test_models (project: str):
    with open(f'{project}/test_models.json', 'w') as f:
      f.write('''{
  "User": {
    "name": "string",
    "age": "int"
  },
  "Foo": {
      "bar": "string",
      "user": "User"
  }
}''')
              
def create_middleware(project:str):
   with open(f'{project}/app/middleware.py', 'w') as f:
      f.write(
'''import os
from typing import Tuple, List
from starlette.authentication import BaseUser
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url= os.getenv('SUPABASE_URL')
key= os.getenv('SUPABASE_API_KEY')

class AppUser(BaseUser):
    username: str
    email: str
    def __init__(self, username:str, email:str):
        self.username = username
        self.email = email
    

def verify_header (headers:str) -> Tuple[List[str], BaseUser]:
    client: Client = create_client(url, key)
    token = headers['authorization'].removeprefix('Bearer ')
    supabase_user = client.auth.get_user(token)
    user = AppUser('', '')
    scopes = []
    if supabase_user.user != None:
        scopes.append('user')
        username = supabase_user.user.user_metadata['username']
        if supabase_user.user.user_metadata.__contains__('admin'):
            scopes.append('admin')
        email = supabase_user.user.email
        user.username = username
        user.email = email
    return scopes, user
''')

def create_backend_dart(project: str, supabase:bool):
   if supabase:
      with open(f'{project}/{project}_fe/lib/backend.dart', 'w') as f:
        f.write(
'''import 'dart:convert';

import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import './models.dart';

class Backend {
  SupabaseClient? client;
  String? deviceIp;
  String? deploymentUrl;

  Backend({this.client, this.deviceIp, this.deploymentUrl});

  Future<bool> detectEmulator() async {
    final DeviceInfoPlugin deviceInfo = DeviceInfoPlugin();
    bool? isEmulator;

    if (defaultTargetPlatform == TargetPlatform.android) {
      final androidInfo = await deviceInfo.androidInfo;
      isEmulator = !androidInfo.isPhysicalDevice;
    } else if (defaultTargetPlatform == TargetPlatform.iOS) {
      final iosInfo = await deviceInfo.iosInfo;
      isEmulator = !iosInfo.isPhysicalDevice;
    } else {
      isEmulator = false;
    }
    return isEmulator;
  }

  Future<String> baseUrl() async {
    if (deploymentUrl != null) {
      return deploymentUrl!;
    }

    final bool isEmulator = await detectEmulator();
    if (isEmulator) {
      if (defaultTargetPlatform == TargetPlatform.android) {
        return 'http://10.0.2.2:8000';
      }
      if (defaultTargetPlatform == TargetPlatform.iOS) {
        return 'http://127.0.0.1:8000';
      }
    }
    if (kIsWeb) {
      return 'http://localhost:8000';
    }
    // if deviceIp is null at this point in execution,
    // platform is likely desktop, so localhost still works.
    return 'http://${deviceIp ?? 'localhost'}:8000';
  }

  Future<String> POST(BaseModel model,
      {String? route, Map<String, String>? headers}) async {
    String baseUrlString = await baseUrl();
    Uri base = Uri.parse(baseUrlString);

    Map<String, String> postHeaders =
        Map.fromEntries([const MapEntry('Content-Type', 'application/json')]);
    if (client != null) {
      try {
        final String accessToken = client!.auth.currentSession!.accessToken;
        postHeaders
            .addEntries([MapEntry('Authorization', 'Bearer $accessToken')]);
      } catch (err) {
        print(err);
      }
    }
    if (headers != null) {
      postHeaders.addAll(headers);
    }
    if (route == null) {
      Response response =
          await post(base, headers: postHeaders, body: jsonEncode(model));
      return response.body;
    } else {
      Uri url = Uri.parse('$baseUrlString/$route');
      Response response =
          await post(url, headers: postHeaders, body: jsonEncode(model));
      return response.body;
    }
  }

  Future<String> GET({String? route, Map<String, String>? headers}) async {
    String baseUrlString = await baseUrl();
    Uri base = Uri.parse(baseUrlString);
    Map<String, String> getHeaders = Map.fromEntries([]);
    if (client != null) {
      try {
        final String accessToken = client!.auth.currentSession!.accessToken;
        getHeaders
            .addEntries([MapEntry('Authorization', 'Bearer $accessToken')]);
      } catch (err) {
        print(err);
      }
    }
    if (headers != null) {
      getHeaders.addAll(headers);
    }
    if (route == null) {
      Response response = await get(base, headers: getHeaders);
      return response.body;
    } else {
      Uri url = Uri.parse('$baseUrlString/$route');
      Response response = await get(url, headers: getHeaders);
      return response.body;
    }
  }

  Future<String> DELETE({String? route, Map<String, String>? headers}) async {
    String baseUrlString = await baseUrl();
    Uri base = Uri.parse(baseUrlString);
    Map<String, String> deleteHeaders = Map.fromEntries([]);
    if (client != null) {
      try {
        final String accessToken = client!.auth.currentSession!.accessToken;
        deleteHeaders
            .addEntries([MapEntry('Authorization', 'Bearer $accessToken')]);
      } catch (err) {
        print(err);
      }
    }
    if (headers != null) {
      deleteHeaders.addAll(headers);
    }
    if (route == null) {
      Response response = await delete(base, headers: deleteHeaders);
      return response.body;
    } else {
      Uri url = Uri.parse('$baseUrlString/$route');
      Response response = await delete(url, headers: deleteHeaders);
      return response.body;
    }
  }

  Future<String> PUT(BaseModel model,
      {String? route, Map<String, String>? headers}) async {
    String baseUrlString = await baseUrl();
    Uri base = Uri.parse(baseUrlString);
    Map<String, String> putHeaders =
        Map.fromEntries([const MapEntry('Content-Type', 'application/json')]);
    if (client != null) {
      try {
        final String accessToken = client!.auth.currentSession!.accessToken;
        putHeaders
            .addEntries([MapEntry('Authorization', 'Bearer $accessToken')]);
      } catch (err) {
        print(err);
      }
    }
    if (headers != null) {
      putHeaders.addAll(headers);
    }
    if (route == null) {
      Response response =
          await put(base, headers: putHeaders, body: jsonEncode(model));
      return response.body;
    } else {
      Uri url = Uri.parse('$baseUrlString/$route');
      Response response =
          await post(url, headers: putHeaders, body: jsonEncode(model));
      return response.body;
    }
  }
}
''')
   else:
      with open(f'{project}/{project}_fe/lib/backend.dart', 'w') as f:
        f.write(
'''import 'dart:convert';

import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart';

import './models.dart';

class Backend {
  String? deviceIp;
  String? deploymentUrl;

  Backend({this.deviceIp, this.deploymentUrl});

  Future<bool> detectEmulator() async {
    final DeviceInfoPlugin deviceInfo = DeviceInfoPlugin();
    bool? isEmulator;

    if (defaultTargetPlatform == TargetPlatform.android) {
      final androidInfo = await deviceInfo.androidInfo;
      isEmulator = !androidInfo.isPhysicalDevice;
    } else if (defaultTargetPlatform == TargetPlatform.iOS) {
      final iosInfo = await deviceInfo.iosInfo;
      isEmulator = !iosInfo.isPhysicalDevice;
    } else {
      isEmulator = false;
    }
    return isEmulator;
  }

  Future<String> baseUrl() async {
    if (deploymentUrl != null) {
      return deploymentUrl!;
    }

    final bool isEmulator = await detectEmulator();
    if (isEmulator) {
      if (defaultTargetPlatform == TargetPlatform.android) {
        return 'http://10.0.2.2:8000';
      }
      if (defaultTargetPlatform == TargetPlatform.iOS) {
        return 'http://127.0.0.1:8000';
      }
    }
    if (kIsWeb) {
      return 'http://localhost:8000';
    }
    // if deviceIp is null at this point in execution,
    // platform is likely desktop, so localhost still works.
    return 'http://${deviceIp ?? 'localhost'}:8000';
  }

  Future<String> POST(BaseModel model,
      {String? route, Map<String, String>? headers}) async {
    String baseUrlString = await baseUrl();
    Uri base = Uri.parse(baseUrlString);
    Map<String, String> postHeaders =
        Map.fromEntries([const MapEntry('Content-Type', 'application/json')]);
    if (headers != null) {
      postHeaders.addAll(headers);
    }
    if (route == null) {
      Response response =
          await post(base, headers: postHeaders, body: jsonEncode(model));
      return response.body;
    } else {
      Uri url = Uri.parse('$baseUrlString/$route');
      Response response =
          await post(url, headers: postHeaders, body: jsonEncode(model));
      return response.body;
    }
  }

  Future<String> GET({String? route, Map<String, String>? headers}) async {
    String baseUrlString = await baseUrl();
    Uri base = Uri.parse(baseUrlString);
    Map<String, String> getHeaders = Map.fromEntries([]);
    if (headers != null) {
      getHeaders.addAll(headers);
    }
    if (route == null) {
      Response response = await get(base, headers: getHeaders);
      return response.body;
    } else {
      Uri url = Uri.parse('$baseUrlString/$route');
      Response response = await get(url, headers: getHeaders);
      return response.body;
    }
  }

  Future<String> DELETE({String? route, Map<String, String>? headers}) async {
    String baseUrlString = await baseUrl();
    Uri base = Uri.parse(baseUrlString);
    Map<String, String> deleteHeaders = Map.fromEntries([]);
    if (headers != null) {
      deleteHeaders.addAll(headers);
    }
    if (route == null) {
      Response response = await delete(base, headers: deleteHeaders);
      return response.body;
    } else {
      Uri url = Uri.parse('$baseUrlString/$route');
      Response response = await delete(url, headers: deleteHeaders);
      return response.body;
    }
  }

  Future<String> PUT(BaseModel model,
      {String? route, Map<String, String>? headers}) async {
    String baseUrlString = await baseUrl();
    Uri base = Uri.parse(baseUrlString);
    Map<String, String> putHeaders =
        Map.fromEntries([const MapEntry('Content-Type', 'application/json')]);
    if (headers != null) {
      putHeaders.addAll(headers);
    }
    if (route == null) {
      Response response =
          await put(base, headers: putHeaders, body: jsonEncode(model));
      return response.body;
    } else {
      Uri url = Uri.parse('$baseUrlString/$route');
      Response response =
          await post(url, headers: putHeaders, body: jsonEncode(model));
      return response.body;
    }
  }
}
''')

def create_models_dart(project:str):
   with open(f'{project}/{project}_fe/lib/models.dart', 'w') as f:
      f.write(
'''class BaseModel {
  Map toJson() => {};
}

class User extends BaseModel {
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

def create_main_dart (project:str, supabase:bool):
    if supabase:
      with open(f'{project}/{project}_fe/lib/main.dart', 'w') as f:
        f.write(
'''import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import './pages/error_page.dart';
import './pages/login_page.dart';
import 'pages/home_page.dart';
import './pages/admin_page.dart';
import './pages/admin_login_page.dart';

Future<void> main() async {
  await dotenv.load();
  String supabaseUrl = dotenv.get('SUPABASE_URL');
  String supabaseApiKey = dotenv.get('SUPABASE_API_KEY');
  await Supabase.initialize(url: supabaseUrl, anonKey: supabaseApiKey);
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  SupabaseClient client = Supabase.instance.client;
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flython Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const SignUpPage(),
        '/error': (context) => const ErrorPage(error: ''),
        '/home': (context) => const HomePage(),
        '/admin': (context) => const AdminPage(),
        '/admin-login': (context) => const AdminSignUpPage()
      },
    );
  }
}
''')
    else:
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

def create_login_page(project:str, scheme:str):
   with open(f'{project}/{project}_fe/lib/pages/login_page.dart', 'w') as f:
      f.write(
f'''import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:supabase_auth_ui/supabase_auth_ui.dart';

class SignUpPage extends StatelessWidget {{
  const SignUpPage({{Key? key}}) : super(key: key);

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(title: const Text('Sign Up / Sign In')),
      body: ListView(
        padding: const EdgeInsets.all(24.0),
        children: [
          SupaEmailAuth(
            redirectTo: kIsWeb ? null : '{scheme}://home',
            onSignInComplete: (response) {{
              Navigator.of(context).pushReplacementNamed('/home');
            }},
            onSignUpComplete: (response) {{
              Navigator.of(context).pushReplacementNamed('/home');
            }},
            metadataFields: [
              MetaDataField(
                prefixIcon: const Icon(Icons.person),
                label: 'Username',
                key: 'username',
                validator: (val) {{
                  if (val == null || val.isEmpty) {{
                    return 'Please enter something';
                  }}
                  return null;
                }},
              ),
            ],
          ),
          const Divider(),
          const Text('Logging in or signing up as an admin?'),
          FloatingActionButton(
              onPressed: () => Navigator.pushNamed(context, '/admin-login'),
              child: const Text('click here'))
        ],
      ),
    );
  }}
}}
''')
      
def create_home_page (project:str):
   with open(f'{project}/{project}_fe/lib/pages/home_page.dart', 'w') as f:
      f.write(
'''import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../backend.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  SupabaseClient client = Supabase.instance.client;
  bool sessionIsValid = false;
  String? _backend_response;
  String? _username;
  Backend backend = Backend(client: Supabase.instance.client);

  void testBackend() async {
    String response = await backend.GET();
    setState(() => _backend_response = response);
  }

  @override
  void initState() {
    if (client.auth.currentUser != null && client.auth.currentSession != null) {
      sessionIsValid = true;
      _username = client.auth.currentUser!.userMetadata!['username'];
    }
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
            title:
                Text(sessionIsValid ? "Welcome, $_username" : 'Unauthorized!')),
        body: sessionIsValid
            ? Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text(
                      'Click below to confirm the backend recognizes you.'),
                  FloatingActionButton(
                      onPressed: testBackend,
                      child: const Text('test backend')),
                  _backend_response != null
                      ? Text(_backend_response!)
                      : const SizedBox(height: 0)
                ],
              )
            : const Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                    Text("You don't have permission to view this page!")
                  ]));
  }
}
''')

def create_error_page (project:str):
   with open(f'{project}/{project}_fe/lib/pages/error_page.dart', 'w') as f:
      f.write(
'''import 'package:flutter/material.dart';

class ErrorPage extends StatelessWidget {
  const ErrorPage({super.key, required this.error});

  final String error;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("ERROR"),
        backgroundColor: Colors.red,
      ),
      body: Text(error),
    );
  }
}
''')

def create_admin_page(project:str):
   with open(f'{project}/{project}_fe/lib/pages/admin_page.dart', 'w') as f:
      f.write(
'''import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../backend.dart';

class AdminPage extends StatefulWidget {
  const AdminPage({super.key});

  @override
  State<AdminPage> createState() => _AdminPageState();
}

class _AdminPageState extends State<AdminPage> {
  SupabaseClient client = Supabase.instance.client;
  bool sessionIsValid = false;
  Backend backend = Backend();
  String? _backendResponse;

  void testBackend() async {
    String accessToken = client.auth.currentSession!.accessToken;
    String response = await backend
        .GET(route: '/admin', headers: {'Authorization': accessToken});
    setState(() => _backendResponse = response);
  }

  @override
  void initState() {
    if (client.auth.currentUser != null &&
        client.auth.currentSession != null &&
        client.auth.currentUser!.userMetadata?['admin'] == true) {
      sessionIsValid = true;
    }
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(title: Text(sessionIsValid ? "Admin" : 'Unauthorized!')),
        body: sessionIsValid
            ? Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('Congrats! You are an admin!'),
                  FloatingActionButton(
                      onPressed: testBackend,
                      child: const Text('test admin backend')),
                  _backendResponse != null
                      ? Text(_backendResponse!)
                      : const Placeholder()
                ],
              )
            : const Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                    Text("You don't have permission to view this page!")
                  ]));
  }
}
''')

def create_admin_login_page (project:str, scheme: str):
   with open(f'{project}/{project}_fe/lib/pages/admin_login_page.dart', 'w') as f:
      f.write(
f'''import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:supabase_auth_ui/supabase_auth_ui.dart';

class AdminSignUpPage extends StatelessWidget {{
  const AdminSignUpPage({{Key? key}}) : super(key: key);

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(title: const Text('Sign Up / Sign In')),
      body: ListView(
        padding: const EdgeInsets.all(24.0),
        children: [
          SupaEmailAuth(
            redirectTo: kIsWeb ? null : '{scheme}://projects',
            onSignInComplete: (response) {{
              Navigator.of(context).pushReplacementNamed('/home');
            }},
            onSignUpComplete: (response) {{
              Supabase.instance.client.auth.currentUser!.userMetadata!
                  .addEntries([const MapEntry('admin', true)]);
              print(Supabase.instance.client.auth.currentUser!.userMetadata
                  .toString());
              Navigator.of(context).pushReplacementNamed('/home');
            }},
            metadataFields: [
              MetaDataField(
                prefixIcon: const Icon(Icons.person),
                label: 'Username',
                key: 'username',
                validator: (val) {{
                  if (val == null || val.isEmpty) {{
                    return 'Please enter something';
                  }}
                  return null;
                }},
              ),
            ],
          ),
          const Divider(),
          const Text('Logging in or signing up as a regular user?'),
          FloatingActionButton(
              onPressed: () => Navigator.pushNamed(context, '/'),
              child: const Text('click here'))
        ],
      ),
    );
  }}
}}
''')
      
def create_env (project:str):
  env_file = '''SUPABASE_URL=''
SUPABASE_API_KEY=''
'''
  with open(f'{project}/app/.env', 'w') as f:
    f.write(env_file)
  with open(f'{project}/{project}_fe/.env', 'w') as f:
    f.write(env_file)
   
def edit_ios_runner (project: str, scheme: str):
   with open(f'{project}/{project}_fe/ios/Runner/Info.plist', 'w') as f:
      f.write(
f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleDevelopmentRegion</key>
	<string>$(DEVELOPMENT_LANGUAGE)</string>
	<key>CFBundleDisplayName</key>
	<string>Flython Builder Fe</string>
	<key>CFBundleExecutable</key>
	<string>$(EXECUTABLE_NAME)</string>
	<key>CFBundleIdentifier</key>
	<string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>flython_builder_fe</string>
	<key>CFBundleURLTypes</key>
	<array>
		<dict>
		<key>CFBundleTypeRole</key>
		<string>Editor</string>
		<key>CFBundleURLSchemes</key>
		<array>
			<string>{scheme}</string>
		</array>
		</dict>
	</array>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>$(FLUTTER_BUILD_NAME)</string>
	<key>CFBundleSignature</key>
	<string>????</string>
	<key>CFBundleVersion</key>
	<string>$(FLUTTER_BUILD_NUMBER)</string>
	<key>LSRequiresIPhoneOS</key>
	<true/>
	<key>UILaunchStoryboardName</key>
	<string>LaunchScreen</string>
	<key>UIMainStoryboardFile</key>
	<string>Main</string>
	<key>UISupportedInterfaceOrientations</key>
	<array>
		<string>UIInterfaceOrientationPortrait</string>
		<string>UIInterfaceOrientationLandscapeLeft</string>
		<string>UIInterfaceOrientationLandscapeRight</string>
	</array>
	<key>UISupportedInterfaceOrientations~ipad</key>
	<array>
		<string>UIInterfaceOrientationPortrait</string>
		<string>UIInterfaceOrientationPortraitUpsideDown</string>
		<string>UIInterfaceOrientationLandscapeLeft</string>
		<string>UIInterfaceOrientationLandscapeRight</string>
	</array>
	<key>UIViewControllerBasedStatusBarAppearance</key>
	<false/>
	<key>CADisableMinimumFrameDurationOnPhone</key>
	<true/>
	<key>UIApplicationSupportsIndirectInputEvents</key>
	<true/>
</dict>
</plist>
''')

def edit_android_manifest (project:str, scheme:str):
  with open(f'{project}/{project}_fe/android/app/src/main/AndroidManifest.xml', 'w') as f:
      f.write(
f'''<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:label="flython_builder_fe"
        android:name="${{applicationName}}"
        android:icon="@mipmap/ic_launcher">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
            android:hardwareAccelerated="true"
            android:windowSoftInputMode="adjustResize">
            <!-- Specifies an Android theme to apply to this Activity as soon as
                 the Android process has started. This theme is visible to the user
                 while the Flutter UI initializes. After that, this theme continues
                 to determine the Window background behind the Flutter UI. -->
            <meta-data
              android:name="io.flutter.embedding.android.NormalTheme"
              android:resource="@style/NormalTheme"
            />
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data
                android:scheme="{scheme}"
                android:host="home" />
            </intent-filter>
        </activity>
        <!-- Don't delete the meta-data below.
             This is used by the Flutter tool to generate GeneratedPluginRegistrant.java -->
        <meta-data
            android:name="flutterEmbedding"
            android:value="2" />
    </application>
</manifest>
''')
      
def edit_pubspec (project:str):
   with open(f'{project}/{project}_fe/pubspec.yaml', 'w') as f:
    f.write(
f'''name: {project}_fe
description: A new Flutter project.
# The following line prevents the package from being accidentally published to
# pub.dev using `flutter pub publish`. This is preferred for private packages.
publish_to: 'none' # Remove this line if you wish to publish to pub.dev

# The following defines the version and build number for your application.
# A version number is three numbers separated by dots, like 1.2.43
# followed by an optional build number separated by a +.
# Both the version and the builder number may be overridden in flutter
# build by specifying --build-name and --build-number, respectively.
# In Android, build-name is used as versionName while build-number used as versionCode.
# Read more about Android versioning at https://developer.android.com/studio/publish/versioning
# In iOS, build-name is used as CFBundleShortVersionString while build-number is used as CFBundleVersion.
# Read more about iOS versioning at
# https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/CoreFoundationKeys.html
# In Windows, build-name is used as the major, minor, and patch parts
# of the product and file versions while build-number is used as the build suffix.
version: 1.0.0+1

environment:
  sdk: '>=3.0.3 <4.0.0'

# Dependencies specify other packages that your package needs in order to work.
# To automatically upgrade your package dependencies to the latest versions
# consider running `flutter pub upgrade --major-versions`. Alternatively,
# dependencies can be manually updated by changing the version numbers below to
# the latest version available on pub.dev. To see which dependencies have newer
# versions available, run `flutter pub outdated`.
dependencies:
  flutter:
    sdk: flutter


  # The following adds the Cupertino Icons font to your application.
  # Use with the CupertinoIcons class for iOS style icons.
  cupertino_icons: ^1.0.2
  http: ^1.1.0
  device_info_plus: ^9.0.2
  supabase_flutter: ^1.10.9
  supabase_auth_ui: ^0.2.1
  flutter_dotenv: ^5.1.0

dev_dependencies:
  flutter_test:
    sdk: flutter

  # The "flutter_lints" package below contains a set of recommended lints to
  # encourage good coding practices. The lint set provided by the package is
  # activated in the `analysis_options.yaml` file located at the root of your
  # package. See that file for information about deactivating specific lint
  # rules and activating additional ones.
  flutter_lints: ^2.0.0

# For information on the generic Dart part of this file, see the
# following page: https://dart.dev/tools/pub/pubspec

# The following section is specific to Flutter packages.
flutter:

  # The following line ensures that the Material Icons font is
  # included with your application, so that you can use the icons in
  # the material Icons class.
  uses-material-design: true

  assets:
    - .env

  # An image asset can refer to one or more resolution-specific "variants", see
  # https://flutter.dev/assets-and-images/#resolution-aware

  # For details regarding adding assets from package dependencies, see
  # https://flutter.dev/assets-and-images/#from-packages

  # To add custom fonts to your application, add a fonts section here,
  # in this "flutter" section. Each entry in this list should have a
  # "family" key with the font family name, and a "fonts" key with a
  # list giving the asset and other descriptors for the font. For
  # example:
  # fonts:
  #   - family: Schyler
  #     fonts:
  #       - asset: fonts/Schyler-Regular.ttf
  #       - asset: fonts/Schyler-Italic.ttf
  #         style: italic
  #   - family: Trajan Pro
  #     fonts:
  #       - asset: fonts/TrajanPro.ttf
  #       - asset: fonts/TrajanPro_Bold.ttf
  #         weight: 700
  #
  # For details regarding fonts from package dependencies,
  # see https://flutter.dev/custom-fonts/#from-packages
''')
      
def edit_build_gradle (project:str):
   with open(f'{project}/{project}_fe/android/app/build.gradle', 'w') as f:
      f.write(
f'''def localProperties = new Properties()
def localPropertiesFile = rootProject.file('local.properties')
if (localPropertiesFile.exists()) {{
    localPropertiesFile.withReader('UTF-8') {{ reader ->
        localProperties.load(reader)
    }}
}}

def flutterRoot = localProperties.getProperty('flutter.sdk')
if (flutterRoot == null) {{
    throw new GradleException("Flutter SDK not found. Define location with flutter.sdk in the local.properties file.")
}}

def flutterVersionCode = localProperties.getProperty('flutter.versionCode')
if (flutterVersionCode == null) {{
    flutterVersionCode = '1'
}}

def flutterVersionName = localProperties.getProperty('flutter.versionName')
if (flutterVersionName == null) {{
    flutterVersionName = '1.0'
}}

apply plugin: 'com.android.application'
apply plugin: 'kotlin-android'
apply from: "$flutterRoot/packages/flutter_tools/gradle/flutter.gradle"

android {{
    namespace "com.example.{project}_fe"
    compileSdkVersion flutter.compileSdkVersion
    ndkVersion flutter.ndkVersion

    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}

    kotlinOptions {{
        jvmTarget = '1.8'
    }}

    sourceSets {{
        main.java.srcDirs += 'src/main/kotlin'
    }}

    defaultConfig {{
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId "com.example.flython_builder_fe"
        // You can update the following values to match your application needs.
        // For more information, see: https://docs.flutter.dev/deployment/android#reviewing-the-gradle-build-configuration.
        minSdkVersion 19
        targetSdkVersion flutter.targetSdkVersion
        versionCode flutterVersionCode.toInteger()
        versionName flutterVersionName
    }}

    buildTypes {{
        release {{
            // TODO: Add your own signing config for the release build.
            // Signing with the debug keys for now, so `flutter run --release` works.
            signingConfig signingConfigs.debug
        }}
    }}
}}

flutter {{
    source '../..'
}}

dependencies {{
    implementation "org.jetbrains.kotlin:kotlin-stdlib-jdk7:$kotlin_version"
}}
''')

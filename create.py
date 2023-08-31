import subprocess
import platform
from codegen import *

def create (project:str, supabase_scheme:str|None = None):
  supabase:bool = supabase_scheme != None
  subprocess.run(['mkdir', project])
  subprocess.run(['touch', 'Dockerfile'], cwd=f'./{project}')
  subprocess.run(['touch', 'requirements.txt'], cwd=f'./{project}')
  subprocess.run(['touch', 'test_models.json'], cwd=f'./{project}')

  create_dockerfile(project)
  create_requirements(project, supabase)
  create_test_models(project)
              
  subprocess.run(['pip', 'install', '-r', 'requirements.txt', '--upgrade', '--no-cache-dir'], cwd=f'./{project}')
  if platform.system() == 'Linux':
    subprocess.run(['sudo', 'apt', 'install', 'uvicorn'])
  else:
    subprocess.run(['pip', 'install', "'uvicorn[standard]'"])
  subprocess.run(['mkdir', 'app'], cwd=f'./{project}')
  subprocess.run(['touch', 'main.py'], cwd=f'./{project}/app')
  subprocess.run(['touch', 'models.py'], cwd=f'./{project}/app')
  if supabase:
    subprocess.run(['pip', 'install', 'supabase', 'fastapi_auth_middleware', 'python-dotenv', '--upgrade', '--no-cache-dir'], cwd=f'./{project}')
    subprocess.run(['touch', 'middleware.py'], cwd=f'./{project}/app')
    
  create_main(project, supabase)
  create_models(project)
  if supabase:
     create_middleware(project)

  subprocess.run(['flutter', 'create', f'{project}_fe'], cwd=f'./{project}')
  subprocess.run(['flutter', 'pub', 'add', 'http', 'device_info_plus'], cwd=f'./{project}/{project}_fe')
  subprocess.run(['touch', 'models.dart'], cwd=f'{project}/{project}_fe/lib')
  subprocess.run(['touch', 'backend.dart'], cwd=f'{project}/{project}_fe/lib')
  if supabase:
    subprocess.run(['mkdir', 'pages'], cwd=f'{project}/{project}_fe/lib')
    subprocess.run(['touch', 'login_page.dart'], cwd=f'{project}/{project}_fe/lib/pages')
    subprocess.run(['touch', 'home_page.dart'], cwd=f'{project}/{project}_fe/lib/pages')
    subprocess.run(['touch', 'error_page.dart'], cwd=f'{project}/{project}_fe/lib/pages')
    subprocess.run(['touch', 'admin_page.dart'], cwd=f'{project}/{project}_fe/lib/pages')
    subprocess.run(['touch', 'admin_login_page.dart'], cwd=f'{project}/{project}_fe/lib/pages')
    create_login_page(project, supabase_scheme)
    create_admin_login_page(project, supabase_scheme)
    create_admin_page(project)
    create_home_page(project)
    create_error_page(project)
    create_env(project)
    edit_android_manifest(project, supabase_scheme)
    edit_ios_runner(project, supabase_scheme)
    edit_pubspec(project)
    subprocess.run(['flutter', 'pub', 'get'], cwd=f'{project}/{project}_fe')

  create_models_dart(project)
  create_backend_dart(project, supabase)
  create_main_dart(project, supabase)
  edit_build_gradle(project)

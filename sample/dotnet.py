import os, glob, shutil, subprocess

framework_version = '4.0.30319'
nunit_version = '2.6.2'
nunit_path = os.path.join(os.path.dirname(__file__), 'NUnit.Runners.' + nunit_version, 'tools', 'nunit-console.exe')
nuget_path = os.path.join(os.path.dirname(__file__), 'NuGet.exe')

def msbuild(project_path, *targets, **properties):
	msbuild_path = os.path.join(os.environ['SystemRoot'], 'Microsoft.NET', 'Framework', 'v' + framework_version, 'MSBuild.exe')
	call_args = [msbuild_path, project_path, '/verbosity:minimal', '/nologo']
	if targets: call_args.append('/t:' + ';'.join(targets))
	call_args.extend(['/p:%s=%s' % (k, v) for k, v in properties.iteritems()])
	subprocess.check_call(call_args)

def nuget_restore(solution_path):
	subprocess.check_call([nuget_path, 'restore', solution_path])

def nunit(*dll_globs):
	nunit_command = [nunit_path, '/nologo' , '/noresult' , '/framework=' + framework_version]
	for dll_glob in dll_globs:
		nunit_command.extend(glob.glob(dll_glob))
	subprocess.check_call(nunit_command)

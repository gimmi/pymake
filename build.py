import os, glob, shutil, subprocess, buildutil

cfg = {
  'tasks': ['init', 'install_deps', 'assembly_info'],
	'framework_version': '4.0.30319',
	'build_configuration': 'Release',
	'project_version': '3.0.0',
	'prerelease_tag': 'b',
	'build_number': '0',
	'nuget_package_source': 'https://nuget.org/api/v2/'
}

def init():
	cfg['base_path'] = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
	cfg['nuget_exe'] = os.path.join(cfg['base_path'], 'tools', 'NuGet.exe')

	cfg['nuget_version'] = cfg['project_version']
	if cfg['prerelease_tag']:
		cfg['nuget_version'] += '-' + cfg['prerelease_tag'] + cfg['build_number'].rjust(6, '0')

	cfg['assembly_version'] = cfg['project_version'] + '.0'

	cfg['out_path'] = os.path.join(cfg['base_path'], 'out')

	buildutil.dump_cfg()

def install_deps():
	subprocess.check_call([cfg['nuget_exe'], 'install', 'NUnit.Runners', '-Version', '2.6.2', '-ExcludeVersion', '-OutputDirectory', os.path.join(cfg['base_path'], 'tools'), '-Source', cfg['nuget_package_source']])

	for pkg_cfg in glob.glob('src/*/packages.config'):
		subprocess.check_call([
			cfg['nuget_exe'],
			'install', pkg_cfg,
			'-OutputDirectory', os.path.join(cfg['base_path'], 'src', 'packages'),
			'-Source', cfg['nuget_package_source']
		])

def assembly_info():
	shared_assembly_info = """\
[assembly: System.Reflection.AssemblyProduct("ProductName")]
[assembly: System.Reflection.AssemblyCopyright("")]
[assembly: System.Reflection.AssemblyTrademark("")]
[assembly: System.Reflection.AssemblyCompany("")]
[assembly: System.Reflection.AssemblyConfiguration("{build_configuration}")]
[assembly: System.Reflection.AssemblyVersion("{assembly_version}")]
[assembly: System.Reflection.AssemblyFileVersion("{assembly_version}")]
[assembly: System.Reflection.AssemblyInformationalVersion("{nuget_version}")]
	""".format(**cfg)

	with open(os.path.join(cfg['base_path'], 'src', 'SharedAssemblyInfo.cs'), 'w') as f:
		f.write(shared_assembly_info)

def compile():
	msbuild_path = os.path.join(os.environ['SystemRoot'], 'Microsoft.NET', 'Framework', 'v' + cfg['framework_version'], 'MSBuild.exe')
	subprocess.check_call([
		msbuild_path, '/verbosity:minimal', '/nologo', 
		os.path.join(cfg['base_path'], 'src', 'Product.sln'), 
		'/t:Rebuild',
		'/p:Configuration=' + cfg['build_configuration'] +';Platform=Any CPU'
	])

def test():
	nunit_command = [
		os.path.join(cfg['base_path'],'tools','NUnit.Runners','tools','nunit-console.exe'),
		'/nologo' ,
		'/noresult' ,
		'/framework=' + cfg['framework_version']
	]

	nunit_command.extend(glob.glob('src/*/bin/' + cfg['build_configuration'] +'/*.Tests.dll'))

	subprocess.check_call(nunit_command)

def pack():
	if os.path.exists(cfg['out_path']): shutil.rmtree(cfg['out_path'])

	shutil.copytree(os.path.join(cfg['base_path'], 'src', 'ProductName', 'bin', cfg['build_configuration']), os.path.join(cfg['out_path'], 'nupkg', 'lib', 'net40'))

	nuspec_content = """\
<?xml version="1.0"?>
<package xmlns="http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd">
  <metadata>
    <id>DaqFiles</id>
    <version>{nuget_version}</version>
    <authors>Gerri</authors>
    <owners>Gerri</owners>
    <description>something wrong</description>
  </metadata>
</package>
	""".format(**cfg)

	nuspec_file = os.path.join(cfg['out_path'], 'nupkg', 'Package.nuspec')

	with open(nuspec_file, 'w') as f:
		f.write(nuspec_content)

	subprocess.check_call([cfg['nuget_exe'], 'pack', nuspec_file, '-Symbols', '-OutputDirectory', cfg['out_path']])

def publish():
	nupkg_file = os.path.join(cfg['out_path'], 'DaqFiles.' + cfg['nuget_version'] + '.nupkg')
	subprocess.check_call([cfg['nuget_exe'], 'push', nupkg_file, '-Source', cfg['nuget_package_source']])

if __name__ == '__main__':
	buildutil.main()

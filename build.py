import os, glob, shutil, subprocess, buildutil

framework_version = '4.0.30319'
build_configuration = 'Release'
build_platform = 'Any CPU'
project_version = '3.0.0'
prerelease = True
build_number = 0
nuget_package_source = 'https://nuget.org/api/v2/'
project_name = 'MyProject'

def nuget_version():
	ret = project_version
	if prerelease:
		ret += '-b%06d' % build_number
	return ret

def bjoin(*args):
	base_path = os.path.dirname(os.path.realpath(__file__))
	return os.path.join(base_path, *args)

def install_deps():
	subprocess.check_call([bjoin('tools', 'NuGet.exe'), 'install', 'NUnit.Runners', '-Version', '2.6.2', '-ExcludeVersion', '-OutputDirectory', bjoin('tools'), '-Source', nuget_package_source])

	for pkg_cfg in glob.glob('src/*/packages.config'):
		subprocess.check_call([
			bjoin('tools', 'NuGet.exe'),
			'install', pkg_cfg,
			'-OutputDirectory', bjoin('packages'),
			'-Source', nuget_package_source
		])

def assembly_info():
	shared_assembly_info = """\
[assembly: System.Reflection.AssemblyProduct("{name}")]
[assembly: System.Reflection.AssemblyCopyright("")]
[assembly: System.Reflection.AssemblyTrademark("")]
[assembly: System.Reflection.AssemblyCompany("")]
[assembly: System.Reflection.AssemblyConfiguration("{cfg}")]
[assembly: System.Reflection.AssemblyVersion("{ver}.0")]
[assembly: System.Reflection.AssemblyFileVersion("{ver}.0")]
[assembly: System.Reflection.AssemblyInformationalVersion("{nuget_ver}")]
	""".format(name=project_name, cfg=build_configuration, ver=project_version, nuget_ver=nuget_version())

	with open(bjoin('src', 'SharedAssemblyInfo.cs'), 'w') as f:
		f.write(shared_assembly_info)

def compile():
	msbuild_path = os.path.join(os.environ['SystemRoot'], 'Microsoft.NET', 'Framework', 'v' + framework_version, 'MSBuild.exe')
	subprocess.check_call([
		msbuild_path, '/verbosity:minimal', '/nologo', 
		bjoin('src', project_name + '.sln'), 
		'/t:Rebuild',
		'/p:Configuration=' + build_configuration +';Platform=' + build_platform
	])

def test():
	nunit_command = [
		bjoin('tools', 'NUnit.Runners', 'tools', 'nunit-console.exe'),
		'/nologo' ,
		'/noresult' ,
		'/framework=' + framework_version
	]

	nunit_command.extend(glob.glob('src/*/bin/' + build_configuration +'/*.Tests.dll'))

	subprocess.check_call(nunit_command)

def pack():
	if os.path.exists(bjoin('out')): shutil.rmtree(bjoin('out'))

	shutil.copytree(bjoin('src', project_name, 'bin', build_configuration), bjoin('out', 'nupkg', 'lib', 'net40'))

	nuspec_content = """\
<?xml version="1.0"?>
<package xmlns="http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd">
	<metadata>
		<id>{id}</id>
		<version>{version}</version>
		<authors></authors>
		<owners></owners>
		<description></description>
	</metadata>
</package>
	""".format(id=project_name, version=nuget_version())

	nuspec_file = bjoin('out', 'nupkg', 'Package.nuspec')

	with open(nuspec_file, 'w') as f:
		f.write(nuspec_content)

	subprocess.check_call([bjoin('tools', 'NuGet.exe'), 'pack', nuspec_file, '-Symbols', '-OutputDirectory', bjoin('out')])

def publish():
	nupkg_file = os.path.join(bjoin('out'), 'DaqFiles.' + nuget_version + '.nupkg')
	subprocess.check_call([bjoin('tools', 'NuGet.exe'), 'push', nupkg_file, '-Source', nuget_package_source])

if __name__ == '__main__':
	buildutil.main()

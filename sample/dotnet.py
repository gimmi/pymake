import os
import glob
import subprocess

framework_version = '4.0.30319'
nunit_version = '2.6.2'
nugetcheck_version = '0.1.8'
sqlmigrator_version = '0.9.1'
sqlserver_version = '110'

base_dir = os.path.join(os.path.dirname(__file__))


def msbuild(project_path, *targets, **properties):
    msbuild_path = os.path.join(os.environ['SystemRoot'], 'Microsoft.NET', 'Framework', 'v' + framework_version, 'MSBuild.exe')
    call_args = [msbuild_path, project_path, '/verbosity:minimal', '/nologo']
    if targets:
        call_args.append('/t:' + ';'.join(targets))
    call_args.extend(['/p:%s=%s' % (k, v) for k, v in properties.iteritems()])
    subprocess.check_call(call_args)


def nuget_restore(*args):
    subprocess.check_call([os.path.join(base_dir, 'NuGet.exe'), 'restore'] + list(args))


def nuget_install(*args):
    subprocess.check_call([os.path.join(base_dir, 'NuGet.exe'), 'install'] + list(args))


def nuget_push(*args):
    subprocess.check_call([os.path.join(base_dir, 'NuGet.exe'), 'push'] + list(args))


def nuget_pack(*args):
    subprocess.check_call([os.path.join(base_dir, 'NuGet.exe'), 'pack'] + list(args))


def nuget_check(sln_path):
    nuget_install('NuGetCheck', '-Version', nugetcheck_version, '-OutputDirectory', base_dir)
    subprocess.check_call([os.path.join(base_dir, 'NuGetCheck.' + nugetcheck_version, 'tools', 'NuGetCheck.exe'), 'PackageVersionMismatch', sln_path])


def nunit(*dll_globs):
    report_path = os.path.join(base_dir, 'TestResult.xml')
    nuget_install('NUnit.Runners', '-Version', nunit_version, '-OutputDirectory', base_dir)
    nunit_command = [
        os.path.join(base_dir, 'NUnit.Runners.' + nunit_version, 'tools', 'nunit-console.exe'),
        '/nologo',
        '/framework=' + framework_version,
        '/noshadow',
        '/xml=' + report_path
    ]
    for dll_glob in dll_globs:
        nunit_command.extend(glob.glob(dll_glob))
    subprocess.check_call(nunit_command)
    tc_print("importData type='nunit' path='%s'" % report_path)


def assembly_info(filepath, **kwargs):
    with open(filepath, 'w') as f:
        f.write('\n'.join(['[assembly: System.Reflection.%s("%s")]' % (k, v) for k, v in kwargs.iteritems()]))


def tc_print(s):
    print("##teamcity[%s]" % s)


def webdeploy_sync_server(master, *slaves):
    for slave in slaves:
        msdeploy('-verb:sync', '-source:webserver,computername=' + master, '-dest:auto,computername=' + slave)


def get_reg_value(key_name, value_name, default_value=None):
    import Microsoft.Win32
    return Microsoft.Win32.Registry.GetValue(key_name, value_name, default_value)


def msdeploy(*args):
    # For some reason, MSDeploy refuse to understand standard check_call arguments, so i had to construct the commandline by hand
    msdeploy_dir = get_reg_value(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\IIS Extensions\MSDeploy\1', 'InstallPath')
    msdeploy_cmd = '"' + os.path.join(msdeploy_dir, 'msdeploy.exe') + '" ' + ' '.join(args)
    print(msdeploy_cmd)
    subprocess.check_call(msdeploy_cmd)


def robocopy(src, dest):
    returncode = subprocess.call(['robocopy.exe', src, dest, '/MIR'])
    if returncode > 8:
        raise Exception('ROBOCOPY failed with exit code %s' % returncode)


def sql_query(conn_str, sql):
    rows = []

    with sql_open_conn(conn_str) as conn:
        with conn.CreateCommand() as cmd:
            cmd.CommandText = sql
            with cmd.ExecuteReader() as rdr:
                while rdr.Read():
                    rows.append(dict([(rdr.GetName(idx), rdr[idx]) for idx in range(rdr.FieldCount)]))

    return rows


def sql_exec(conn_str, sql):
    with sql_open_conn(conn_str) as conn:
        with conn.CreateCommand() as cmd:
            cmd.CommandText = sql
            return cmd.ExecuteNonQuery()


def sql_scalar(conn_str, sql):
    with sql_open_conn(conn_str) as conn:
        with conn.CreateCommand() as cmd:
            cmd.CommandText = sql
            return cmd.ExecuteScalar()


# def sqlcmd(*args):
#   sqlcmd_dir = dotnet.get_reg_value(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Microsoft SQL Server\110\Tools\ClientSetup', 'Path', '.')
#   sqlcmd_path = os.path.join(sqlcmd_path, 'sqlcmd.exe')
#   if not os.path.isfile(sqlcmd_path):
#       raise Exception('Unable to locate SQLServer 2012 command line tool. Is SQLServer LocalDB installed?')
#   subprocess.check_call([sqlcmd_path] + list(args))


def sqllocaldb(*args):
    sqllocaldb_path = os.path.join(get_sqlserver_tools_dir(), 'SqlLocalDB.exe')
    subprocess.check_call([sqllocaldb_path] + list(args))


def get_sqlserver_tools_dir():
    reg_dir = ['HKEY_LOCAL_MACHINE', 'SOFTWARE', 'Microsoft', 'Microsoft SQL Server', sqlserver_version, 'Tools', 'ClientSetup']
    sqllocaldb_dir = get_reg_value('\\'.join(reg_dir), 'Path')
    if not sqllocaldb_dir:
        raise Exception('Unable to locate SQLServer tools. Is SQLServer v%s installed?' % sqlserver_version)
    return sqllocaldb_dir


def sql_open_conn(conn_str):
    import clr
    clr.AddReference('System.Data')
    import System.Data

    conn = System.Data.SqlClient.SqlConnection(conn_str)
    conn.Open()
    return conn


def sql_migrator(**kwargs):
    nuget_install('SqlMigrator', '-Version', sqlmigrator_version, '-OutputDirectory', base_dir, '-Verbosity', 'quiet')

    sqlmigrator_command = [
        os.path.join(base_dir, 'SqlMigrator.' + sqlmigrator_version, 'tools', 'SqlMigrator.exe')
    ]

    for k, v in kwargs.iteritems():
        sqlmigrator_command.append('/' + k)
        sqlmigrator_command.append(v)

    subprocess.check_call(sqlmigrator_command)

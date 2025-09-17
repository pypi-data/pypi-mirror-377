import subprocess

class pip:
    def __init__(self):
        self.quiet_output = False
        self.verbose = False
        self.pip_version_check = True
        self.log_path = None
        return None
    
    def process_run(self, args, capture=None):
        if self.quiet_output:
            args.append('--quiet')

        if self.verbose:
            args.append('--verbose')
        
        if not self.pip_version_check:
            args.append('--disable-pip-version-check')

        if isinstance(self.log_path, str):
            args.append('--log')
            args.append(self.log_path)
            
        kwargs = {'check': True}

        if capture:
            kwargs.update({'capture_output': True})
            call = subprocess.run(args, **kwargs)
            return call.stdout
        else:
            subprocess.run(args, **kwargs)
    def install(self, package_name=None, from_filepath=None, upgrade=None, py_version=None, no_cache=None, user_only=None, no_deps=None):
        # these are basic arguments
        args = ["python3", "-m", "pip", "install"]
        # here, it checks for any optional arguments before running the basic command 
        if from_filepath != None:
            args.append("-r")
            args.append(from_filepath)
        else:
            if from_filepath == None and isinstance(package_name, str):
                args.append(package_name)
            else:
                raise SyntaxError("The package name for pip cannot be anything but a string.")
        # check if user wants forced upgrade
        if upgrade:
            args.append("--upgrade")

        # check if user wants specific python version
        if py_version:
            args.append("--python-version")
            args.append(f"{py_version}")
        
        # ignore available cache in system
        if no_cache:
            args.append("--no-cache-dir")

        # ignore system-wide libraries
        if user_only:
            args.append("--user")

        if no_deps:
            args.append('--no-deps')

        self.process_run(args)
    def freeze(self, user_only=None, to_file=None):
        args = ['python3', '-m', 'pip', 'freeze']

        # check for user-only selection to freeze
        if user_only:
            args.append('--user')
        if to_file:
            args.append('>')
            args.append('requirements.txt')

        result = self.process_run(args, capture=True)
        godot = result.decode('utf-8')
        result_str = godot.replace('\n', ' \n')
        return result_str
    def uninstall(self, package_name=None, from_filepath=None, always_confirm=None, break_packages=None):
        # these are basic arguments
        args = ["python3", "-m", "pip", "uninstall"]
        # here, it checks for any optional arguments before running the basic command 
        if from_filepath:
            args.append("-r")
            args.append(from_filepath)
        else:
            if not from_filepath and isinstance(package_name, str):
                args.append(package_name)
            else:
                raise SyntaxError("The package name for uninstallation cannot be anything but a string.")

        if always_confirm:
            args.append('--yes')
        
        if break_packages:
            args.append('--break-system-packages')

        self.process_run(args)
    def list(self, user_only=None, outdated=None, uptodate=None, editable=None, unstable=None):
        # it's just nicer freeze
        args = ['python3', '-m', 'pip', 'freeze']

        # check for user-only selection to freeze
        if user_only:
            args.append('--user')
        # check if user wants to include outdated packages
        if outdated:
            args.append('--outdated')
        # check if user wants to include uptodate packages
        if uptodate:
            args.append('--uptodate')
        # check if user wants to include editable packages
        if editable:
            args.append('--editable')
        # check if user wants to include unstable, pre-release and development packages 
        if unstable:
            args.append('--pre')

        result = self.process_run(args, capture=True)
        godot = result.decode('utf-8')
        result_str = godot.replace('\n', ' \n')
        return result_str
    def show(self, package_name, show_files=None):
        args = ['python3', '-m', 'pip', 'show']
        
        if show_files:
            args.append('--files')

        if isinstance(package_name, str):
            args.append(package_name)
        else:
            raise SyntaxError('A package name is required for pip show.')

        result = self.process_run(args, capture=True)
        godot = result.decode('utf-8')
        result_str = godot.replace('\n', ' \n')
        return result_str
    def debug(self):
        args = ['python3', '-m', 'pip', 'debug']

        self.process_run(args)
    def inspect(self, user_only=None, path=None):
        args = ['python3', '-m', 'pip', 'inspect']

        if user_only:
            args.append('--user')

        if isinstance(path, str):
            args.append('--path')
            args.append(path)

        result = self.process_run(args, capture=True)
        godot = result.decode('utf-8')
        result_str = godot.replace('\n', ' \n')
        return result_str

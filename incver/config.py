import os
import textwrap
import subprocess
from dkfileutils.path import Path

from dkcode.configs.dkbuildini import read_dkbuild_ini
from dkcode.configs.dkbuildyml import read_dkbuild_yml
from dkcode.configs.dkconfig import Config
from dkcode.exceptions import FileMissing

_CONFIG_CACHE = {}  # type: dict[str, DKBuildIni]


class Config(object):
    #: ordering of files that will be searched for configuration
    source_order = [
        'pyproject.toml',
        'setup.cfg',
        '.incver.yml',
        '.incver.yaml',
    ]

    #: the current version according to the config file
    current_version = None
    #: the config file used
    config_file = None

    # defaults
    version_re = '\d+\.\d+(\.\d+)?'
    version_str = r'''(['"])$VERSION\1'''
    version_eq = r'''^version\s?=\s?u?$VERSION_STR'''
    version_dunder = r'''^__version__\s?=\s?$VERSION_STR'''
    version_js = r'''^export const version = $VERSION_STR'''
    version_yml = r'''version: $VERSION'''
    version_json = r'''"version":\s?"$VERSION"'''

    files = [
        '/setup.py',
        '/setup.cfg',
        '/package.json',
        '/package.ini',
        '/package.yaml',
        '/dkbuild.yml',
        '/pyproject.toml',
        '/docs/conf.py',
        '**/version.*',
        '**/index.*',
        '**/__init__.py',
        '**/_version.py',
    ]

    def __init__(self) -> None:
        self.version_re = self.version_re.replace("$VERSION", self.version_re)
        self.version_str = self.version_str.replace('$VERSION_STR', self.version_str)
        self.version_eq = self.version_eq.replace('$VERSION_STR', self.version_str)
        self.version_dunder = self.version_dunder.replace('$VERSION_STR', self.version_str)
        self.version_js = self.version_js.replace('$VERSION_STR', self.version_str)
        self.version_yml = self.version_yml.replace('$VERSION', self.version_re)
        self.version_json = self.version_json.replace('$VERSION', self.version_re)

        for source in self.source_order:
            if os.path.exists(source):
                self.config_file = source
                self.read_config_source(source)
                break
        else:
            cmd = ['python', 'setup.py', '--version']
            pipe = subprocess.run(cmd, stdout=subprocess.PIPE)
            self.current_version = pipe.stdout.decode().strip()
            self.config_file = 'setup.py'

    def read_config_source(self, fname):
        if fname == 'setup.cfg':
            import iniconfig
            conf = iniconfig.IniConfig(fname)
            self.__dict__.update(dict(conf['tool:incver'].items()))
            
        name, ext = os.path.splitext(fname)
        print("FOUND:", name, ext)


    def __repr__(self):
        files = '\n        '.join(f for f in self.files)
        return textwrap.dedent("""
        Config:
            current_version: {self.current_version}
            config_file: {self.config_file}
            defaults:
                version_re:     {self.version_re}
                version_str:    {self.version_str}
                version_eq:     {self.version_eq}
                version_dunder: {self.version_dunder}
                version_js:     {self.version_js}
                version_yml:    {self.version_yml}
                version_json:   {self.version_json}
            files: 
                $FILES
            dict: $DICT
        """.format(self=self)).replace("$FILES", files).replace('$DICT', repr(self.__dict__))


if __name__ == "__main__":
    conf = Config()
    print(repr(conf))

# def get_defaults():
#     """Get default values, preferrably from :file:`dkbuild.yml` (secondarily
#        from :file:`dkbuld.ini`).

#        Raises a FileMissing exception if neither :file:`dkbuild.ini` nor
#        :file:`dkbuild.yml` can be found.
#     """
#     key = Path.curdir() / 'dkbuild'
#     cfg = Config()
#     # print("CONFIG:package_name:", cfg.package_name)
#     # print("CONFIG:name:", cfg.name)
#     if key not in _CONFIG_CACHE:
#         for ini_reader in (read_dkbuild_ini, read_dkbuild_yml):
#             try:
#                 val = ini_reader(cfg)
#                 break
#             except FileMissing:
#                 pass
#         else:
#             raise FileMissing("None of :file:`dkbuild.ini`, dkbuild.yml found. \n\n\t"
#                               "Run `dk init`")
#         _CONFIG_CACHE[key] = val
#     return _CONFIG_CACHE[key]

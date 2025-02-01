import subprocess, sys, platform, os, json
from pathlib import Path
from typing import List, Dict, Optional

if platform.system() == 'Windows':
    import winreg

LANGUAGE_CONFIGS = {
    'python'     : { 'url': 'https://github.com/tree-sitter/tree-sitter-python'     },
    'javascript' : { 'url': 'https://github.com/tree-sitter/tree-sitter-javascript' },
    'typescript' : { 'url': 'https://github.com/tree-sitter/tree-sitter-typescript' },
    'rust'       : { 'url': 'https://github.com/tree-sitter/tree-sitter-rust'       },
    'go'         : { 'url': 'https://github.com/tree-sitter/tree-sitter-go'         },
    'cpp'        : { 'url': 'https://github.com/tree-sitter/tree-sitter-cpp'        },
    'c'          : { 'url': 'https://github.com/tree-sitter/tree-sitter-c'          },
    'java'       : { 'url': 'https://github.com/tree-sitter/tree-sitter-java'       },
    'ruby'       : { 'url': 'https://github.com/tree-sitter/tree-sitter-ruby'       },
    'php'        : { 'url': 'https://github.com/tree-sitter/tree-sitter-php'        },
    'c_sharp'    : { 'url': 'https://github.com/tree-sitter/tree-sitter-c-sharp'    },
    'html'       : { 'url': 'https://github.com/tree-sitter/tree-sitter-html'       },
    'css'        : { 'url': 'https://github.com/tree-sitter/tree-sitter-css'        },
    'bash'       : { 'url': 'https://github.com/tree-sitter/tree-sitter-bash'       },
    'yaml'       : { 'url': 'https://github.com/ikatyang/tree-sitter-yaml'          },
    'json'       : { 'url': 'https://github.com/tree-sitter/tree-sitter-json'       },
    'toml'       : { 'url': 'https://github.com/tree-sitter/tree-sitter-toml'       },
    'regex'      : { 'url': 'https://github.com/tree-sitter/tree-sitter-regex'      },
    'markdown'   : { 'url': 'https://github.com/ikatyang/tree-sitter-markdown'      }
}

class TreeSitterSetup:
    def __init__(self, install_dir: Optional[Path] = None):
        self.install_dir = install_dir or Path.home() / '.tree-sitter'
        self.parsers_dir = self.install_dir / 'parsers'
        self.build_dir = self.install_dir / 'build'
        self.installed_file = self.install_dir / '.installed'
        self.installed_languages = set()
        self._load_installed_languages()

    def _load_installed_languages(self):
        if self.installed_file.exists():
            try:
                with open(self.installed_file, 'r') as f:
                    self.installed_languages = set(json.load(f))
            except:
                self.installed_languages = set()

    def _save_installed_languages(self):
        with open(self.installed_file, 'w') as f:
            json.dump(list(self.installed_languages), f)

    def _check_dependencies(self):
        try:
            import tree_sitter
        except ImportError:
            print("Installing tree-sitter Python package...")
            if platform.system() == 'Linux':
                venv_dir = self.install_dir / 'venv'
                print(venv_dir)
                if not venv_dir.exists():
                    print("Creating virtual environment...")
                    subprocess.check_call([sys.executable, '-m', 'venv', str(venv_dir)])
                
                pip_path = venv_dir / 'bin' / 'pip'
                python_path = venv_dir / 'bin' / 'python'
                
                if not pip_path.exists():
                    raise RuntimeError("Failed to create virtual environment. Please ensure python3-venv is installed.")
                
                try:
                    subprocess.check_call([str(pip_path), 'install', '--upgrade', 'pip'])
                    subprocess.check_call([str(pip_path), 'install', 'tree-sitter'])
                except subprocess.CalledProcessError:
                    print("Failed to install tree-sitter package.")
                    print("Please try one of the following:")
                    print("1. Install using system package manager: sudo apt-get install python3-tree-sitter")
                    print("2. Create a virtual environment manually:")
                    print("   python3 -m venv .venv")
                    print("   source .venv/bin/activate")
                    print("   pip install tree-sitter")
                    sys.exit(1)
                
                sys.path.insert(0, str(venv_dir / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'))
            else:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tree-sitter'])
        
        if platform.system() == 'Linux':
            required_packages = ['git', 'gcc', 'g++']
            missing_packages = []
            
            for package in required_packages:
                if subprocess.run(['which', package], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
                    missing_packages.append(package)
            
            if missing_packages:
                print(f"Missing required packages: {', '.join(missing_packages)}")
                print("Please install them using:")
                print(f"sudo apt-get install {' '.join(missing_packages)}")
                sys.exit(1)
                
        elif platform.system() == 'Windows':
            try:
                subprocess.run(['cl'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                print("Microsoft Visual C++ Build Tools not found.")
                print("Please install Visual Studio with C++ development tools.")
                sys.exit(1)

    def _clone_parser(self, language: str, url: str) -> Path:
        parser_dir = self.parsers_dir / language
        if not parser_dir.exists():
            print(f"Cloning {language} parser...")
            subprocess.run(['git', 'clone', url, str(parser_dir)], check=True)
            
            if language == 'typescript':
                subprocess.run(['git', 'submodule', 'init'], cwd=parser_dir, check=True)
                subprocess.run(['git', 'submodule', 'update'], cwd=parser_dir, check=True)
        
        return parser_dir

    def _setup_msvc_environment(self):
        if platform.system() != 'Windows':
            return

        def find_vs_installation():
            try:
                program_files = os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')
                vswhere_path = os.path.join(program_files, 'Microsoft Visual Studio', 'Installer', 'vswhere.exe')
                
                if os.path.exists(vswhere_path):
                    result = subprocess.run([
                        vswhere_path,
                        '-latest',
                        '-products', '*',
                        '-requires', 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
                        '-property', 'installationPath'
                    ], capture_output=True, text=True, check=True)
                    
                    if result.stdout.strip():
                        return result.stdout.strip()
                
                if platform.system() == 'Windows':
                    versions = ['2022', '2019', '2017']
                    for version in versions:
                        try:
                            key_path = f"SOFTWARE\\Microsoft\\VisualStudio\\{version}\\Setup\\VS"
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                                return winreg.QueryValueEx(key, 'ProductDir')[0]
                        except WindowsError:
                            try:
                                key_path = f"SOFTWARE\\WOW6432Node\\Microsoft\\VisualStudio\\{version}\\Setup\\VS"
                                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                                    return winreg.QueryValueEx(key, 'ProductDir')[0]
                            except WindowsError:
                                continue
                                
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\VisualStudio\SxS\VS7") as key:
                            versions = []
                            i = 0
                            while True:
                                try:
                                    versions.append(winreg.EnumValue(key, i))
                                    i += 1
                                except WindowsError:
                                    break
                            if versions:
                                latest = sorted(versions, key=lambda x: x[0])[-1]
                                return latest[1]
                    except WindowsError:
                        pass
                
            except Exception as e:
                print(f"Error finding Visual Studio: {e}")
            return None

        def find_windows_sdk_path():
            if platform.system() != 'Windows':
                return None
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows Kits\Installed Roots") as key:
                    return winreg.QueryValueEx(key, "KitsRoot10")[0]
            except WindowsError:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows Kits\Installed Roots") as key:
                        return winreg.QueryValueEx(key, "KitsRoot10")[0]
                except WindowsError:
                    return None

        def find_windows_sdk_version():
            if platform.system() != 'Windows':
                return None
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows Kits\Installed Roots") as key:
                    versions = []
                    i = 0
                    while True:
                        try:
                            version = winreg.EnumKey(key, i)
                            if version.startswith("10."):
                                versions.append(version)
                            i += 1
                        except WindowsError:
                            break
                    return sorted(versions)[-1] if versions else None
            except WindowsError:
                return None

        vs_path = find_vs_installation()
        if not vs_path:
            raise RuntimeError("Could not find Visual Studio installation. Please install Visual Studio with C++ development tools.")
        
        msvc_path = os.path.join(vs_path, "VC")
        sdk_path = find_windows_sdk_path()
        sdk_version = find_windows_sdk_version()
        
        if not (msvc_path and sdk_path and sdk_version):
            raise RuntimeError("Could not find required Visual Studio components. Please install Visual Studio with C++ development tools.")
        
        arch = 'x64' if platform.machine().endswith('64') else 'x86'
        
        msvc_tools_path = os.path.join(msvc_path, "Tools", "MSVC")
        if os.path.exists(msvc_tools_path):
            versions = sorted(os.listdir(msvc_tools_path))
            if versions:
                msvc_tools_path = os.path.join(msvc_tools_path, versions[-1])
                
                paths = [
                    os.path.join(msvc_tools_path, "bin", "Host" + arch, arch),
                    os.path.join(sdk_path, "bin", sdk_version, arch),
                    os.path.join(msvc_tools_path, "include"),
                    os.path.join(sdk_path, "Include", sdk_version, "ucrt"),
                    os.path.join(sdk_path, "Include", sdk_version, "um"),
                    os.path.join(sdk_path, "Include", sdk_version, "shared"),
                    os.path.join(msvc_tools_path, "lib", arch),
                    os.path.join(sdk_path, "Lib", sdk_version, "ucrt", arch),
                    os.path.join(sdk_path, "Lib", sdk_version, "um", arch)
                ]
                
                os.environ["PATH"] = ";".join(paths) + ";" + os.environ.get("PATH", "")
                os.environ["INCLUDE"] = ";".join([
                    os.path.join(msvc_tools_path, "include"),
                    os.path.join(sdk_path, "Include", sdk_version, "ucrt"),
                    os.path.join(sdk_path, "Include", sdk_version, "um"),
                    os.path.join(sdk_path, "Include", sdk_version, "shared")
                ])
                os.environ["LIB"] = ";".join([
                    os.path.join(msvc_tools_path, "lib", arch),
                    os.path.join(sdk_path, "Lib", sdk_version, "ucrt", arch),
                    os.path.join(sdk_path, "Lib", sdk_version, "um", arch)
                ])
                
                stdbool_path = Path(msvc_tools_path) / "include" / "stdbool.h"
                if not stdbool_path.exists():
                    stdbool_content = """
#ifndef _STDBOOL_H
#define _STDBOOL_H

#define __bool_true_false_are_defined 1

#ifndef __cplusplus

#define bool    _Bool
#define false   0
#define true    1

#endif /* __cplusplus */

#endif /* _STDBOOL_H */
"""
                    stdbool_path.write_text(stdbool_content)
            else:
                raise RuntimeError("No MSVC versions found. Please repair/reinstall Visual Studio.")
        else:
            raise RuntimeError("MSVC tools path not found. Please install Visual Studio with C++ development tools.")

    def _build_parser(self, language: str, parser_dir: Path):
        print(f"Building {language} parser...")
        build_dir = self.build_dir / language
        build_dir.mkdir(parents=True, exist_ok=True)
        
        c_files = self._get_source_files(language, parser_dir)
        if not c_files:
            raise RuntimeError(f"No source files found for {language}")

        if platform.system() == 'Windows':
            self._build_windows(language, parser_dir, build_dir, c_files)
        else:
            self._build_unix(language, parser_dir, build_dir, c_files)

    def _get_source_files(self, language: str, parser_dir: Path) -> List[Path]:
        c_files = []
        if language == 'typescript':
            ts_dir = parser_dir / "typescript" / "src"
            if ts_dir.exists():
                c_files.extend(ts_dir.glob('*.c'))
            scanner_dir = parser_dir / "src"
            if scanner_dir.exists():
                c_files.extend(scanner_dir.glob('*.c'))
        elif language == 'php':
            c_files.extend(parser_dir.glob('php/src/*.c'))
            scanner_file = parser_dir / "php" / "src" / "scanner.cc"
            if scanner_file.exists():
                c_files.append(scanner_file)
            scanner_c = parser_dir / "php" / "src" / "scanner.c"
            if scanner_c.exists():
                c_files.append(scanner_c)
        elif language in ['yaml', 'markdown']:
            c_files.extend(parser_dir.glob('src/*.c'))
            scanner_file = parser_dir / "src" / "scanner.cc"
            if scanner_file.exists():
                c_files.append(scanner_file)
            scanner_c = parser_dir / "src" / "scanner.c"
            if scanner_c.exists():
                c_files.append(scanner_c)
        else:
            c_files = list(parser_dir.glob('src/*.c'))
            if not c_files:
                c_files = list(parser_dir.rglob('*.c'))
        return c_files

    def _build_windows(self, language: str, parser_dir: Path, build_dir: Path, c_files: List[Path]):
        if language == 'php':
            self._build_windows_php(language, parser_dir, build_dir, c_files)
            return

        self._setup_msvc_environment()
        
        response_file = build_dir / "sources.rsp"
        with open(response_file, "w") as f:
            for c_file in c_files:
                f.write(f'"{c_file}"\n')
        
        try:
            cmd = [
                'cl',
                '/nologo',
                '/O2',
                '/MT',
                '/D_CRT_SECURE_NO_WARNINGS',
                '/DNDEBUG',
                '/LD',
                '/utf-8',
                '/W3',
                '/Zi',
                '/std:c++20',
                '/I', str(parser_dir / 'src')
            ]
            
            if language == 'typescript':
                cmd.extend(['/I', str(parser_dir / 'typescript' / 'src')])
            elif language in ['yaml', 'markdown']:
                cmd.extend([
                    '/I', str(parser_dir),
                    '/DLOG_TOKENS',
                    '/DYYDEBUG'
                ])
            elif language == 'php':
                cmd.extend(['/TP', '/D_CRT_SECURE_NO_WARNINGS'])
            
            if language in ['yaml', 'markdown']:
                scanner_h = parser_dir / "php_only" / "src" / "scanner.h"
                if scanner_h.exists():
                    cmd.extend(['/FI', str(scanner_h)])
            
            cmd.extend([
                f'/Fe:{build_dir / "parser.dll"}',
                f'@{response_file}'
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Compilation failed for {language}:")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                
                if language in ['yaml', 'markdown']:
                    self._build_windows_scanner(language, parser_dir, build_dir)
                else:
                    raise RuntimeError(f"Compilation failed for {language}")
            
        finally:
            try:
                response_file.unlink()
            except:
                pass
            
            self._cleanup_build_artifacts(build_dir)

    def _build_windows_php(self, language: str, parser_dir: Path, build_dir: Path, c_files: List[Path]):
        print(f"Building {language} parser with Clang on Windows...")
        object_files = []
        include_path = str(parser_dir / 'php_only' / 'src')
        for src in set(c_files):
            obj_file = build_dir / (src.stem + '.obj')
            cmd = [
                'clang',
                '-O2',
                '-std=c11',
                '-D_CRT_SECURE_NO_WARNINGS',
                '-DNDEBUG',
                '-I', include_path,
                '-c',
                str(src),
                '-o', str(obj_file)
            ]
            subprocess.run(cmd, check=True)
            object_files.append(obj_file)
        link_cmd = [
            'clang',
            '-shared',
            '-O2',
            '-o', str(build_dir / 'parser.dll')
        ] + [str(obj) for obj in object_files]
        subprocess.run(link_cmd, check=True)
        self._cleanup_build_artifacts(build_dir)

    def _build_windows_scanner(self, language: str, parser_dir: Path, build_dir: Path):
        print(f"Attempting to compile scanner separately for {language}...")
        scanner_file = parser_dir / "src" / "scanner.c"
        if scanner_file.exists():
            scanner_cmd = [
                'cl',
                '/nologo',
                '/O2',
                '/MT',
                '/c',
                '/D_CRT_SECURE_NO_WARNINGS',
                '/DNDEBUG',
                '/I', str(parser_dir / 'src'),
                '/Fo' + str(build_dir / 'scanner.obj'),
                str(scanner_file)
            ]
            subprocess.run(scanner_cmd, check=True)
            
            link_cmd = [
                'link',
                '/nologo',
                '/DLL',
                '/OUT:' + str(build_dir / 'parser.dll'),
                str(build_dir / 'parser.obj'),
                str(build_dir / 'scanner.obj')
            ]
            subprocess.run(link_cmd, check=True)
        else:
            raise RuntimeError(f"Scanner compilation failed for {language}")

    def _build_unix(self, language: str, parser_dir: Path, build_dir: Path, src_files: List[Path]):
        c_sources = [f for f in src_files if f.suffix == '.c']
        cpp_sources = [f for f in src_files if f.suffix in ['.cc', '.cpp']]
        object_files = []

        for src in set(c_sources):
            obj_file = build_dir / (src.stem + '.o')
            cmd = [
                'cc',
                '-fPIC',
                '-O2',
                '-g',
                '-Wall',
                '-Wextra',
                '-std=gnu11',
                '-Wno-implicit-fallthrough',
                '-c',
                '-I', str(parser_dir / 'src'),
                str(src),
                '-o', str(obj_file)
            ]
            if language == 'typescript':
                cmd.extend(['-I', str(parser_dir / 'typescript' / 'src')])
            elif language in ['yaml', 'markdown']:
                cmd.extend(['-I', str(parser_dir)])
            elif language == 'php':
                cmd.extend(['-I', str(parser_dir / 'php_only' / 'src')])
            subprocess.run(cmd, check=True)
            object_files.append(obj_file)

        for src in set(cpp_sources):
            obj_file = build_dir / (src.stem + '.o')
            cmd = [
                'c++',
                '-fPIC',
                '-O2',
                '-g',
                '-Wall',
                '-Wextra',
                '-std=c++11',
                '-Wno-implicit-fallthrough',
                '-c',
                '-I', str(parser_dir / 'src'),
                str(src),
                '-o', str(obj_file)
            ]
            if language == 'typescript':
                cmd.extend(['-I', str(parser_dir / 'typescript' / 'src')])
            elif language in ['yaml', 'markdown']:
                cmd.extend(['-I', str(parser_dir)])
            elif language == 'php':
                cmd.extend(['-I', str(parser_dir / 'php_only' / 'src')])
            subprocess.run(cmd, check=True)
            object_files.append(obj_file)

        link_cmd = [
            'c++',
            '-shared',
            '-O2',
            '-g',
            '-o', str(build_dir / 'parser.so')
        ] + [str(obj) for obj in object_files]
        subprocess.run(link_cmd, check=True)

    def _cleanup_build_artifacts(self, build_dir: Path):
        for ext in ['.exp', '.lib', '.obj', '.pdb', '.ilk', '.o']:
            try:
                for f in build_dir.glob(f'*{ext}'):
                    f.unlink()
            except:
                pass

    def install_language(self, language: str):
        if language not in LANGUAGE_CONFIGS:
            raise ValueError(f"Unsupported language: {language}")

        if language in self.installed_languages:
            print(f"{language} parser already installed")
            return

        config = LANGUAGE_CONFIGS[language]
        parser_dir = self._clone_parser(language, config['url'])
        self._build_parser(language, parser_dir)
        
        self.installed_languages.add(language)
        self._save_installed_languages()
        print(f"Successfully installed {language} parser")

    def install_all_languages(self):
        self._check_dependencies()
        self.install_dir.mkdir(parents=True, exist_ok=True)
        self.parsers_dir.mkdir(parents=True, exist_ok=True)
        self.build_dir.mkdir(parents=True, exist_ok=True)

        for language in LANGUAGE_CONFIGS:
            try:
                self.install_language(language)
            except Exception as e:
                print(f"Failed to install {language}: {str(e)}")

    def get_parser(self, language: str):
        if language not in self.installed_languages:
            self.install_language(language)

        from tree_sitter import Language, Parser
        parser = Parser()
        if not hasattr(parser, "set_language"):
            raise RuntimeError("tree-sitter package outdated: please update using pip install --upgrade tree-sitter")
        parser.set_language(Language(
            str(self.build_dir / language / ('parser.dll' if platform.system() == 'Windows' else 'parser.so')),
            language
        ))
        return parser

    def parse_file(self, file_path: str, language: str = None):
        if language is None:
            language = self._detect_language(file_path)
            
        if language is None:
            raise ValueError(f"Could not detect language for {file_path}")
            
        parser = self.get_parser(language)
        with open(file_path, 'rb') as f:
            tree = parser.parse(f.read())
        return tree

    def _detect_language(self, file_path: str) -> Optional[str]:
        ext = Path(file_path).suffix.lower()
        ext_to_lang = {
            '.py'   : 'python',
            '.js'   : 'javascript',
            '.ts'   : 'typescript',
            '.rs'   : 'rust',
            '.go'   : 'go',
            '.cpp'  : 'cpp',
            '.hpp'  : 'cpp',
            '.c'    : 'c',
            '.h'    : 'c',
            '.java' : 'java',
            '.rb'   : 'ruby',
            '.php'  : 'php',
            '.cs'   : 'c_sharp',
            '.html' : 'html',
            '.css'  : 'css',
            '.sh'   : 'bash',
            '.yaml' : 'yaml',
            '.yml'  : 'yaml',
            '.json' : 'json',
            '.toml' : 'toml',
            '.md'   : 'markdown'
        }
        return ext_to_lang.get(ext)

    def show_installation_info(self):
        print("\nTreeSitter Installation Information:")
        print("=" * 40)
        print(f"Installation Directory: {self.install_dir}")
        print(f"Parsers Directory: {self.parsers_dir}")
        print(f"Build Directory: {self.build_dir}")
        print("\nInstalled Languages:")
        print("-" * 20)
        
        for language in sorted(self.installed_languages):
            parser_dir = self.parsers_dir / language
            build_file = self.build_dir / language / ('parser.dll' if platform.system() == 'Windows' else 'parser.so')
            
            status = []
            if parser_dir.exists():
                status.append("Source✓")
            if build_file.exists():
                status.append("Binary✓")
            
            status_str = ", ".join(status) if status else "Incomplete!"
            print(f"{language:15} - {status_str}")

if __name__ == "__main__":
    setup = TreeSitterSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        setup.show_installation_info()
    else:
        setup.install_all_languages()

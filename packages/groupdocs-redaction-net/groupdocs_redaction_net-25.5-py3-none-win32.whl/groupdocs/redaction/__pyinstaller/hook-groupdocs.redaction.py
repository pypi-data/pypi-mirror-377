from PyInstaller.utils.hooks import get_package_paths
import os.path

(_, root) = get_package_paths('groupdocs')

datas = [(os.path.join(root, 'assemblies', 'redaction'), os.path.join('groupdocs', 'assemblies', 'redaction'))]

hiddenimports = [ 'groupdocs', 'groupdocs.pydrawing', 'groupdocs.pyreflection', 'groupdocs.pygc', 'groupdocs.pycore' ]


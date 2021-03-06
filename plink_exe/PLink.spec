# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

options = [('v', None, 'OPTION')]

imports = collect_submodules('plink')

a = Analysis(['PLink.py'],
             binaries=None,
             data_files=[(r'C:\Python27\lib\lib2to3\Grammar.txt', 'lib2to3'),
                         (r'C:\Python27\lib\lib2to3\PatternGrammar.txt', 'lib2to3')],
             hiddenimports=imports + ['linecache', 'pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['gi', 'pytz', 'td', 'sphinx', 'alabaster', 'babel',
                       'idlelib', 'bsddb'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='PLink',
          debug=False,
          strip=False,
          upx=True,
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.data_files,
               strip=False,
               upx=True,
               name='PLink')

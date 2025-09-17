import zipfile, glob, sys

whls = glob.glob('dist/*.whl')
assert whls, 'No wheels in dist/'
with zipfile.ZipFile(whls[0]) as z:
    meta = [n for n in z.namelist() if n.endswith('.dist-info/METADATA')][0]
    print(z.read(meta).decode().splitlines()[:12])

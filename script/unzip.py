import zipfile
import sys

archive_name = sys.argv[1]
extract_path = sys.argv[2]

print 'extracting archive'

with zipfile.ZipFile(archive_name) as zf:
    zf.extractall(extract_path)

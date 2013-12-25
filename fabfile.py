from os.path import join, dirname
from glob import glob


for f in glob(join(dirname(__file__), 'fabtasks', '*.py')):
    execfile(f)
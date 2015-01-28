from os.path import join, dirname
from glob import glob
from fabric.api import env

env.ignored_authors = frozenset([
    'jonathan.stoppani@wsfcomp.com',
    'support@requires.io',
])

for f in glob(join(dirname(__file__), 'fabtasks', '*.py')):
    execfile(f)

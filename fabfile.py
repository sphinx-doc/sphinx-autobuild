from glob import glob
from os.path import dirname, join

from fabric.api import env

env.ignored_authors = frozenset(
    ["jonathan.stoppani@wsfcomp.com", "support@requires.io",]
)

for f in glob(join(dirname(__file__), "fabtasks", "*.py")):
    execfile(f)

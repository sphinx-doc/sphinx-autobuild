import pipes

from fabric.api import settings, task, local, hide
from fabric.contrib.console import confirm


def is_working_tree_clean():
    with settings(hide('everything'), warn_only=True):
        local('git update-index -q --ignore-submodules --refresh')
        unstaged = local('git diff-files --quiet --ignore-submodules --',
                         capture=True)
        uncommitted = local('git diff-index --cached --quiet HEAD '
                            '--ignore-submodules --', capture=True)
    return unstaged.succeeded and uncommitted.succeeded


@task
def lint():
    """
    Checks the source code using flake8.
    """
    local('flake8 --statistics --exit-zero --max-complexity=10 '
          '--exclude=\'*/migrations/*,build,dist,docs\' .')


@task
def authors():
    """
    Updates the AUTHORS file with a list of committers from GIT.
    """
    local('git shortlog -s -e -n | cut -f 2- > AUTHORS')


@task
def release():
    """
    Create a new release and upload it to PyPI.
    """

    if not is_working_tree_clean():
        print 'Your working tree is not clean. Refusing to create a release.'
        return

    print 'Rebuilding the AUTHORS file to check for modifications...'
    authors()

    if not is_working_tree_clean():
        print (
            'Your working tree is not clean after the AUTHORS file was '
            'rebuilt.'
        )
        print 'Please commit the changes before continuing.'
        return

    # Get version
    version = 'v{}'.format(local('python setup.py --version', capture=True))
    name = local('python setup.py --name', capture=True)

    # Tag
    tag_message = '{} release version {}.'.format(name, version)

    print '----------------------'
    print 'Proceeding will tag the release, push the repository upstream,'
    print 'and release a new version on PyPI.'
    print
    print 'Version: {}'.format(version)
    print 'Tag message: {}'.format(tag_message)
    print
    if not confirm('Continue?', default=True):
        print 'Aborting.'
        return

    local('git tag -a {} -m {}'.format(pipes.quote(version),
                                       pipes.quote(tag_message)))

    # Push
    local('git push --tags origin master')

    # Package and upload to pypi
    local('python setup.py sdist bdist_wheel upload')
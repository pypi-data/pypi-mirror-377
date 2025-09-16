import shlex
from pathlib import Path

import nox


def run_hook(name, *args, **kwargs):
    for file in [Path(__name__).parent / '.nox-hooks.py', Path('~/.config/nox/eo-hooks.py').expanduser()]:
        if not file.exists():
            continue

        globals_ = {}
        exec(file.read_text(), globals_)
        hook = globals_.get(name, None)
        if hook:
            hook(*args, **kwargs)


def setup_venv(session, *packages, django_version='>=4.2,<4.3'):
    packages = [
        f'django{django_version}',
        'pytest',
        'pyquery',
        *packages,
    ]
    run_hook('setup_venv', session, packages)
    session.install('-e', '.', *packages, silent=False)


def hookable_run(session, *args, **kwargs):
    args = list(args)
    run_hook('run', session, args, kwargs)
    session.run(*args, **kwargs)


@nox.session()
@nox.parametrize('django', ['>=4.2,<4.3'])
def tests(session, django):
    setup_venv(
        session,
        'pytest-cov',
        'pytest-django',
        'psycopg2-binary',
        'psycopg2',
        django_version=django,
    )

    args = ['py.test']
    if '--coverage' in session.posargs or not session.interactive:
        while '--coverage' in session.posargs:
            session.posargs.remove('--coverage')
        args += [
            '-v',
            '--cov=gadjo/',
            '--cov=tests/',
            '--cov-report=term-missing',
            '--cov-config=.coveragerc',
        ]
        if not session.interactive:
            args += [
                '--cov-report=xml',
                '--cov-report=html',
                f'--junitxml=junit-coverage.django-{django}.xml',
            ]

    if not session.interactive:
        args += ['-v']

    args += session.posargs + ['tests/']

    hookable_run(
        session,
        *args,
    )


@nox.session
def pylint(session):
    setup_venv(session, 'pylint', 'astroid<3', 'pylint-django', 'nox')
    pylint_command = ['pylint', '--jobs', '12', '-f', 'parseable', '--rcfile', 'pylint.rc']

    if not session.posargs:
        pylint_command += ['gadjo/', 'tests/', 'noxfile.py']
    else:
        pylint_command += session.posargs

    if not session.interactive:
        session.run(
            'bash',
            '-c',
            f'{shlex.join(pylint_command)} | tee pylint.out ; test $PIPESTATUS -eq 0',
            external=True,
        )
    else:
        session.run(*pylint_command)


@nox.session
def codestyle(session):
    session.install('pre-commit')
    session.run('pre-commit', 'run', '--all-files', '--show-diff-on-failure')


@nox.session
def check_manifest(session):
    # django is only required to compile messages
    session.install('django', 'check-manifest')
    # compile messages and css
    ignores = [
        'VERSION',
        'gadjo/static/css/*.css',
        'gadjo/static/css/icons/*.png',
        'merge-junit-results.py',
    ]
    session.run('check-manifest', '--ignore', ','.join(ignores))

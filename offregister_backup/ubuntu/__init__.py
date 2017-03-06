from itertools import imap
from os import path
from tempfile import gettempdir

from fabric.operations import put, get, sudo, run


def gen_local_path(kwargs):
    if kwargs['LOCAL_PATH'] == '$TMPDIR':
        kwargs['LOCAL_PATH'] = gettempdir()  # e.g.: for Windows
    if kwargs.get('LOCAL_PATH.append'):
        print 'kwargs =', kwargs
        for p in kwargs['LOCAL_PATH.append']:
            if p == '$DNS_NAME':
                p = kwargs['dns_name']
            kwargs['LOCAL_PATH'] = path.join(kwargs['LOCAL_PATH'], p)


def backup0(*args, **kwargs):
    gen_local_path(kwargs)
    backup_out, run_out = process(get, kwargs)
    return {kwargs['LOCAL_PATH']: (run_out, backup_out)}


# TODO: Make this a decorator
def process(run_cmd, kwargs):
    run_out = map(sudo, kwargs['sudo']['before']) if 'sudo' in kwargs and 'before' in kwargs['sudo'] else []
    if 'run' in kwargs and 'before' in kwargs['run']:
        run_out += map(run, kwargs['run']['before'])
    backup_out = tuple(imap(lambda remote_path: run_cmd(remote_path=remote_path,
                                                        local_path=kwargs['LOCAL_PATH'],
                                                        use_sudo=kwargs.get('use_sudo', False),
                                                        temp_dir=kwargs.get('temp_dir', '')),
                            kwargs['REMOTE_PATHS']))
    for k in 'run', 'sudo':
        if k in kwargs and 'after' in kwargs[k]:
            run_out += map(sudo if k == 'sudo' else run, kwargs[k]['after'])
    return backup_out, run_out


def restore1(*args, **kwargs):
    gen_local_path(kwargs)
    put(remote_path=kwargs['REMOTE_PATH'], local_path=kwargs['LOCAL_PATH'], use_sudo=kwargs.get('use_sudo', False),
        temp_dir=kwargs.get('temp_dir', ''), mirror_local_mode=kwargs.get('mirror_local_mode', False),
        mode=kwargs.get('mode'), use_glob=kwargs.get('use_glob', True))
    return kwargs['LOCAL_PATH']

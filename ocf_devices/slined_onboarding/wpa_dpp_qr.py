import subprocess
import re
import logging

logger = logging.getLogger('slined_onboarding.wpa_dpp_qr')

def get_dpp_uri(iface_name):
    logger.info('Trying to fetch DPP URI for interface {}'.format(iface_name))
    try:
        return _fetch_dpp_uri(iface_name)
    except:
        logger.warn('Failed to fetch URI; trying to generate instead')

    return _gen_dpp_uri(iface_name)

def _fetch_dpp_uri(iface_name):
    fetch_args = ['dpp_bootstrap_get_uri', '1']
    cmd_output = _call_wpa_cli(iface_name, fetch_args)
    if re.match('^DPP:C:[\d]+/[\d]+;M:[\d\w]+;K:[\d\w+=/]+;;$', cmd_output) is None:
        raise Exception
    return cmd_output

def _gen_dpp_uri(iface_name):
    with open('/sys/class/net/{}/address'.format(iface_name), 'r') as f:
        mac_addr = f.read().strip().replace(':', '')
    gen_args = ['dpp_bootstrap_gen', 'type=qrcode', 'mac={}'.format(mac_addr), 'chan=81/1']
    cmd_output = _call_wpa_cli(iface_name, gen_args)
    if re.match('^[\d]+$', cmd_output) is None:
        raise Exception
    return _fetch_dpp_uri(iface_name)

def _call_wpa_cli(iface_name, cmd_args):
    base_args = ['wpa_cli', '-i', iface_name]
    full_args = base_args + cmd_args
    result = subprocess.run(full_args, capture_output=True)
    if result.returncode != 0:
        raise Exception
    cmd_output = result.stdout.strip().decode('ascii')
    logger.debug('wpa_cli output: {}'.format(cmd_output))
    return cmd_output

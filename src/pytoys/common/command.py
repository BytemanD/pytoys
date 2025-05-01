import subprocess

from loguru import logger


def execute(cmd, check=True, success_codes=None):
    logger.debug("RUN: {}", cmd)
    status, output = subprocess.getstatusoutput(cmd)
    if check and status not in (success_codes or [0]):
        raise subprocess.CalledProcessError(status, cmd=cmd, output=output)
    return status, output

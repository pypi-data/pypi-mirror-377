

def getHomeDir():
    import os
    p = os.path.expanduser('~')
    return p


def getDataDir(app_name=None):
    import os
    p = os.path.join(getHomeDir(), 'zldata')
    if app_name is not None:
        p = os.path.join(p, app_name)
    os.makedirs(p, exist_ok=True)
    return p

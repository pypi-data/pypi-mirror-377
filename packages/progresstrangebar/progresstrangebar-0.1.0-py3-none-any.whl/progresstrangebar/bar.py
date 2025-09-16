class PipNotInstall(ModuleNotFoundError):
    pass
def trange(total: int, desc="Loading", unit="B"):
    try:
        from tqdm import trange
        return trange(total, desc, unit)
    except:
        raise PipNotInstall("'tqdm' pip is isn't install, enter 'pip install tqdm' in cmd or powershell to install.")

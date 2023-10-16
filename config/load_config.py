import os
from hydra import compose, initialize
# import hydra
from hydra.core.config_store import ConfigStore
from config.config_property import default_config
from hydra.initialize import GlobalHydra

cs = ConfigStore.instance()
cs.store(name="default_config",node=default_config)
os.environ["HYDRA_FULL_ERROR"] = "1"

# try:
#     initialize(config_path="../conf", version_base="1.1")
# except:
#     GlobalHydra.instance().clear()
# finally:
#     initialize(config_path="../conf", version_base="1.1")

if not GlobalHydra().is_initialized():
    initialize(config_path="../conf", version_base="1.1")


def get_config(config_name="default",account:str=None):
    '''
    overrides should be mentioned like the below
    overrides = ["accounts=ferrero"]
    '''
    if account:
        overrides = [f"accounts={account}"]
    else:
        overrides = ()
    cfg:default_config = compose(config_name=config_name, overrides=overrides).accounts
    return cfg



# def config_override(overrides:list):
#     '''["db=mysql", "db.user=me"]'''
#     initialize(config_path="conf")
#     cfg = compose(config_name="config.yaml", overrides=overrides,strict=True)
#     return cfg


# cfg = get_config()
# print("before_overide---->",cfg.Extraction_settings)
# override_list = ["Extraction_settings.horizontal_buffer=200"]
# cfg = config_override(override_list)
# print("after_overide------>",cfg.Extraction_settings)




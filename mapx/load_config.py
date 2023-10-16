import hydra


@hydra.main(config_path="conf",config_name="default",version_base="1.1")
def get_config(cfg):
    return cfg
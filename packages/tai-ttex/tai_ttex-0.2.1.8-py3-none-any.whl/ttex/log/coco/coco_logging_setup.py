import logging
import os.path as osp

from ttex.log.handler import ManualRotatingFileHandler
from ttex.log.formatter import KeyFormatter
from ttex.log.filter import KeyFilter, EventKeysplitFilter


def setup_coco_logger(trigger_nth: int, name: str = "coco_logger"):
    # TODO: make this into a default setup to make it easier
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    splitter_args = {
        "trigger_nth": trigger_nth,
    }
    coco_filter = EventKeysplitFilter(
        key_splitter_cls="ttex.log.coco.COCOKeySplitter",
        key_splitter_args=splitter_args,
    )
    logger.addFilter(coco_filter)

    # Create a ManualRotatingFileHandler instance for log and info
    for type_str in ["info", "log_dat", "log_tdat"]:
        # Make some dummy files that should be deleted after
        filepath = osp.join("test_dir", f"coco_{type_str}.txt")
        handler = ManualRotatingFileHandler(filepath=filepath, key=type_str, mode="a")
        formatter = KeyFormatter(key=type_str)
        handler.setFormatter(formatter)
        filter = KeyFilter(key=type_str)
        handler.addFilter(filter)
        logger.addHandler(handler)
    return logger

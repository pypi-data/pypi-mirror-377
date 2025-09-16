from src.loss.store import get_loss_function_cfgs_type
from src.misc.stores import import_all_siblings

import_all_siblings(__name__, __file__)
LossConfig = get_loss_function_cfgs_type()

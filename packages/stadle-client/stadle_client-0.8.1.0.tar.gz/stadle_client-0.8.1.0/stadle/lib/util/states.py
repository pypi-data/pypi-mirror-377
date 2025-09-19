from enum import Enum, IntEnum


# --- STATE ENUM --- #

class BaseModelConvFormat:
    """
    The original format of the model (ex. pytorch, keras), or the desired training format
    Used to convert model during training
    """
    pytorch_format = 0
    tensorflow_format = 1
    keras_format = 2
    numpy_format = 3

    formats = [pytorch_format, tensorflow_format, keras_format, numpy_format]

class ClientState(IntEnum):
    """
    Client states defined in the STADLE Agent specification
    """
    waiting_sgm = 0
    training = 1
    sending = 2
    sg_ready = 3


class DBName:
    local = 'local_models'
    cluster = 'cluster_models'
    sg = 'sg_models'
    sg_performance = 'sg_performance'


class ModelType(Enum):
    """
    Types of models
    """
    local = 0
    cluster = 1
    semi_global = 2


class ComponentState(IntEnum):
    """
    index indicator for system state
    """
    inactive = 0
    active = 1
    suspended = 2
    timeout = 3

class OptStatus(IntEnum):
    inactive = 0
    active = 1
    force_aggregation = 2

class AggMethod(IntEnum):
    fed_avg = 0
    itr_fed_avg = 1
    geo_med = 2
    crd_med = 3
    krum = 4
    krum_avg = 5

class IDPrefix:
    agent = 'agent'
    aggregator = 'aggregator'
    db = 'database'

# --- MESSAGE PROTOCOL --- #

# MESSAGE TYPES

class DBMsgType(Enum):
    """
    Message types defined in the STADLE AGG-DB protocol
    """
    push = 0
    aggr_poll = 1
    get_list = 2
    get_models = 3
    get_num_aggregators = 4
    aggr_register = 5
    agent_register = 6
    base_model_register = 7
    base_model_request = 8
    agg_bm_update = 9
    agent_status_update = 10
    opt_status_poll = 11
    push_metrics = 12
    clear_old_models = 13
    ack = 14
    update = 15
    registration_failed = 16


class AgentMsgType(Enum):
    """
    Message types defined in the STADLE protocol sent from an agent to an aggregator
    """
    participate = 0
    update = 1
    initialize_model = 2
    waiting_sgm = 3
    send_metrics = 4


class AggMsgType(Enum):
    """
    Message types defined in the STADLE protocol sent from an aggregator to an agent
    """
    welcome = 0
    update = 1
    registration_failed = 2
    ack = 3
    not_opt = 4
    max_agents_reached = 5
    max_size_reached = 6
    max_round_reached = 7


# MESSAGE HEADER LOCATION INFO

# AGT <-> AGGR
class ParticipateMSGLocation(IntEnum):
    """
    index indicator to read a participate message
    """
    msg_type = 0
    rep = 1


# AGGR <-> DB
class DBPushMsgLocation(IntEnum):
    """
    index indicator to read a push message
    """
    msg_type = 0
    push_rep = 1
    aggregator_info = 2
    state_manager_info = 3
    agent_info = 4


# AGGR <-> AGT
class SGMDistributionMsgLocation(IntEnum):
    """
    index indicator to read a sg_model distribution message
    """
    msg_type = 0
    aggregator_id = 1
    model_id = 2
    round = 3
    sg_models = 4
    base_model = 5
from .dict_metadata_manager import DictMetadataManager
from .id_generator import next_id
try:
    from .dataframe_metadata_manager import DataframeMetadataManager
except ImportError:
    import warnings
    warnings.warn('Unable to import DataframeMetadataManager - please ensure pandas is installed', ImportWarning)

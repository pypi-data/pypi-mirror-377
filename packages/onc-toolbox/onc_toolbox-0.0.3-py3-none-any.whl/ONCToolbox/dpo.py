from typing import NamedTuple

class DataProcessingOptions(NamedTuple):
    class ADCP:
        beam3: str = 'On'

    class HF_RADAR:
        include_radials: bool = False

    class LISST:
        text_file_format: int = 1

    class BIOACOUSTIC:
        binary_source: int = 0


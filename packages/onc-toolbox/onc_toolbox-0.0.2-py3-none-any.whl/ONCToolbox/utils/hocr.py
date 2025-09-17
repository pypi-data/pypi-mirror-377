from typing import NamedTuple

class SynchronizedFrame(NamedTuple):
    frame_type: str
    serial_number: str
    intergration_time: int
    sample_delay: int
    spectrometer_counts: list[int]
    dark_sample_channels: int
    dark_sample_average: int
    spectrometer_temperature: float
    frame_counter: int
    timer: float
    checksum: int
    terminator: str


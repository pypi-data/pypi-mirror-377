from enum import Enum


class GetApiV1VideosIdStatsTimeseriesMetricMetric(str, Enum):
    """GetApiV1VideosIdStatsTimeseriesMetricMetric enumeration."""

    AGGREGATEWATCHTIME = "aggregateWatchTime"
    VIEWERS = "viewers"

    def __str__(self) -> str:
        return str(self.value)

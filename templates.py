from dataclasses import dataclass


@dataclass
class Zones:
    core = 'ru-central1-a'
    test = 'ru-central1-b'
    draft = 'ru-central1-c'


# About platforms see more:
# https://cloud.yandex.com/en-ru/docs/compute/concepts/vm-platforms
# https://cloud.yandex.com/en-ru/docs/compute/concepts/performance-levels
@dataclass(frozen=True)
class Platforms:
    v1 = 'standard-v1'
    v2 = 'standard-v2'
    v3 = 'standard-v3'
    highperformance = 'highfreq-v3'


@dataclass(frozen=True)
class Template:
    simple = dict()
    medium = dict()
    large = dict()
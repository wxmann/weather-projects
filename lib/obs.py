import pandas as pd
from config import get_resource

ASOS_SERVICE = 'http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?'
HR_PRECIP_SERVICE = 'https://mesonet.agron.iastate.edu/cgi-bin/request/hourlyprecip.py?'

DEBUG = False


def _parse_args(station, startts, endts):
    station_result = station
    if isinstance(station, str):
        station_result = [station]
    elif isinstance(station, (list, tuple, set)):
        pass
    else:
        raise ValueError("Station argument must be a single ASOS station or a list of stations")

    return station_result, pd.Timestamp(startts), pd.Timestamp(endts)


def asos_raw(station, startts, endts):
    stations, startts, endts = _parse_args(station, startts, endts)

    url = ASOS_SERVICE + 'data=all&tz=Etc/UTC&format=onlycomma&latlon=yes&'
    url += f'year1={startts:%Y}&month1={startts:%-m}&day1={startts:%-d}&'
    url += f'year2={endts:%Y}&month2={endts:%-m}&day2={endts:%-d}&'
    url += '&'.join([f'station={st}' for st in stations])

    _print_if_debug(f'Getting data from url: {url}')
    return pd.read_csv(url, parse_dates=['valid'], na_values='M')


def hourly_precip(station, startts, endts, filter_measurable=True):
    stations, startts, endts = _parse_args(station, startts, endts)
    metadata = station_metadata(stations)
    data_by_network = []

    for network in metadata.iem_network.unique():
        stations_for_ntwk = metadata[metadata.iem_network == network].stid.unique()
        data_by_network.append(_retrieve_hourly_precip(stations_for_ntwk, startts, endts, network))

    result = pd.concat(data_by_network)
    if not filter_measurable:
        return result

    return result[result.precip_in >= 0.01]


def _retrieve_hourly_precip(stations, startts, endts, network):
    url = HR_PRECIP_SERVICE + f'network={network}&tz=Etc/UTC&'
    url += startts.strftime('year1=%Y&month1=%m&day1=%d&')
    url += endts.strftime('year2=%Y&month2=%m&day2=%d&')
    url += '&'.join([f'station={st}' for st in stations])

    _print_if_debug(f'Getting data from url: {url}')
    return pd.read_csv(url, parse_dates=['valid'])


def station_metadata(stations):
    network_file = get_resource('asos_networks')
    station_mapping = pd.read_csv(network_file)
    network_query = (station_mapping.iem_network.str.contains('ASOS')) | (station_mapping.iem_network == 'AWOS')
    query = (station_mapping.stid.isin(stations)) & network_query
    return station_mapping[query]


def _print_if_debug(thing):
    if DEBUG:
        print(thing)

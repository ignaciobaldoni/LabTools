# -*- coding: utf-8 -*-
"""
Created on 14.04.2021

@author: akordts
"""

from kklib import NativeLib, NativeLibError
from kklib import ErrorCode
import datetime
import time
import logging
logger = logging.getLogger(__name__)


class KKMesstechnikFXE:

    # region class initialization and device connection functions
    def __init__(self):
        self._kknative = None
        self._source_id = None
        self._time_format = "YYYYMMDD_HH:NN:SS.ZZZ"
        self._datetime_format = '%Y%m%d_%H:%M:%S.%f'
        self._pause_time_s = 0.01

        try:
            # load K+K library
            self._kknative = NativeLib()
            logger.info("K+K library version " + self._kknative.get_version())
            self._source_id = self._kknative.get_source_id()
        except NativeLibError as exc:
            logger.exception(exc)
            raise exc

    def connect(self,
                server_ip: str = '10.0.3.185',
                port_nr_str: str = '48896',
                log_mode: str = 'FREQLOG'):

        connection_str = server_ip + ':' + port_nr_str

        try:
            kk_res = self._kknative.open_TCP_log_time(
                                    self._source_id,
                                    connection_str,
                                    log_mode,
                                    self._time_format)
            if kk_res.result_code != ErrorCode.KK_NO_ERR:
                raise Exception('open_TCP_log failed')
        except Exception as exc:
            logger.exception(exc)
            raise exc

    def disconnect(self):
        self._kknative.close_TCP_log(self._source_id)
        logger.info('disconnected from local KK server')
    # endregion

    def read_report(self):
        report_result = None

        kk_res = self._kknative.get_TCP_log(self._source_id)
        # examine result code
        if kk_res.result_code == ErrorCode.KK_ERR_BUFFER_OVERFLOW:
            logger.error("get_Tcp_log reports overflow error")
        elif kk_res.result_code == ErrorCode.KK_ERR_SERVER_DOWN:
            logger.error("get_Tcp_log reports no connection to TCP server")
        elif ((kk_res.result_code != ErrorCode.KK_NO_ERR) and
              (kk_res.result_code != ErrorCode.KK_ERR_BUFFER_TOO_SMALL)):
            logger.error("get_Tcp_log failed: " + kk_res.data)
        elif kk_res.data is None:
            logger.debug("no data read")
            time.sleep(self._pause_time_s)
        else:
            data_str = kk_res.data
            data_cols = data_str.split()

            timestamp = data_cols[0]
            timestamp = datetime.datetime.strptime(
                                                timestamp,
                                                self._datetime_format
                                                )
            timestamp = timestamp.timestamp()

            channel_data: list[float] = [float(col_data.replace(',', '.')) for col_data in data_cols[2:6]]
            report_result = [timestamp] + channel_data

        return report_result


if __name__ == '__main__':

    import sys

    log_formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] [%(name)s]   %(message)s")
    logger = logging.getLogger('root')
    logger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(log_formatter)
    logger.addHandler(consoleHandler)

    fxe = KKMesstechnikFXE()
    fxe.connect()
    for i in range(10):
        print(fxe.read_report())
        time.sleep(1)

    fxe.disconnect()

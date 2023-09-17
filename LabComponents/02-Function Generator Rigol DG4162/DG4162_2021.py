'''
Created on 08.07.2021

@author: akordts
'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020-2021 Menlo Systems GmbH <a.thaller@menlosystems.com>
#
#

__author__ = 'a.thaller@menlosystems.com'

import typing as t
import time
import pyvisa
import logging
import numpy as np

log = logging.getLogger(__name__)


class DG4162(object):
    device: t.Union[pyvisa.resources.tcpip.TCPIPInstrument, pyvisa.resources.Resource] = None
    name: str
    identity: str
    serial: str
    manufacturer: str
    model: str
    version: str
    card_identity: str
    address: str

    MAX_BURST_SAMPLES = 16384

    def connectUSB(self, address: str):
        rm = pyvisa.ResourceManager()
        try:
            self.device = rm.open_resource(address, encoding='utf8')
            self.address = address
            log.info("DMM is {}".format(type(self.device)))

        except Exception as e:
            log.fatal("Error during connection attempt: {}".format(e))
            raise ConnectionError("Error: Could not connect to DG1000Z at {}. Bailing out.".format(address))

        self.name = "DG1000Z"
        self.identity = self.cmd('*IDN?')
        self.manufacturer, self.model, self.serial, self.version = self.identity.split(',')
        self.name += "_{}".format(self.serial)

    def connect(self, address: str):
        rm = pyvisa.ResourceManager()
        try:
            self.device = rm.open_resource("TCPIP::{}".format(address), encoding='utf8')
            self.address = address
            log.info("DMM is {}".format(type(self.device)))

        except Exception as e:
            log.fatal("Error during connection attempt: {}".format(e))
            raise ConnectionError("Error: Could not connect to DG1000Z at {}. Bailing out.".format(address))

        self.name = "DG1000Z"
        self.identity = self.cmd('*IDN?')
        self.manufacturer, self.model, self.serial, self.version = self.identity.split(',')
        self.name += "_{}".format(self.serial)
        # self.cmd(':LXI:IDEN?')
        # self.cmd(':LXI:MDNS:ENAB ON')
        # self.cmd(':LXI:MDNS:ENAB?')
        # self.cmd(':LXI:MDNS:HNAM CARLAAWG')
        # self.cmd(':LXI:MDNS:SNAM:DES CARLAAWG')
        # self.cmd(':LXI:MDNS:HNAM?')
        # self.cmd(':LXI:MDNS:SNAM:DES?')
        # self.cmd(':OUTP1:IMP?')
        # self.cmd(':OUTP1:LOAD?')
        # self.cmd(':SOUR1:TRAC:DATA:CATalog?')

    @classmethod
    def get_addr_by_serial(cls, serial: str) -> (str, None):
        """
        :param serial:
        :return:
        """
        for timeout in (1, 5, 10, ):
            for address, info in cls.find_devices(timeout):
                if info.get('SerialNumber', '') == serial:
                    return address
        return None

    @staticmethod
    def find_devices(timeout: float = 6.0, callback: t.Callable[[str, t.Dict], None] = None) -> t.List[str]:

        import zeroconf
        import socket

        class MyListener(zeroconf.ServiceListener):
            def __init__(self):
                self.scan_results = {}
                self.start = time.time()

            def update_service(self, zc_: zeroconf.Zeroconf, type_: str, name: str) -> None:
                pass

            def remove_service(self, zc_: zeroconf.Zeroconf, type_: str, name: str) -> None:
                pass

            def add_service(self, zc_: zeroconf.Zeroconf, type_: str, name: str):
                def convert(data):
                    if isinstance(data, bytes):
                        try:
                            return data.decode('utf8')
                        except UnicodeDecodeError:
                            return data
                    if isinstance(data, dict):
                        return dict(map(convert, data.items()))
                    if isinstance(data, tuple):
                        return map(convert, data)
                    return data

                try:
                    log.debug('Got mDNS packet: {}'.format(name))
                    info: zeroconf.ServiceInfo = zc.get_service_info(type_, name)
                    if info and info.properties:
                        address = ["{}".format(socket.inet_ntoa(a)) for a in info.addresses][0]
                        properties = convert(info.properties)
                        if 'rigol' in properties.get('Manufacturer', '').lower():
                            if properties.get('Model', '').startswith('DG10'):
                                properties['ts'] = time.time() - self.start
                                self.scan_results[address] = properties
                                if callback is not None:
                                    try:
                                        callback(address, properties)
                                    except BaseException as e:
                                        log.error("Callback yielded {}".format(e))
                except (KeyError, zeroconf.Error):
                    pass

        # ServiceBrowser(zeroconf, "_services._dns-sd._udp.local.", listener)
        zc = zeroconf.Zeroconf()
        listener = MyListener()
        zeroconf.ServiceBrowser(zc, "_vxi-11._tcp.local.", listener)
        try:
            time.sleep(timeout)
        finally:
            zc.close()
        # future solution with a callable check:
        # start = time.time()
        # while len(listener.scan_results) == 0 and time.time() - start < timeout:
        #     time.sleep(0.1)
        # zc.close()

        return sorted(list(listener.scan_results.items()))

    cmd_debug = True
    cmd_profile = False
    cmd_pause = False

    def cmd(self, req, data: t.Optional[t.List[int]] = None, wait_completion=False, log_me=True):
        """ Simple wrapper to write commands and queries to a device resource.

        :param req: the request as a string
        :param data: raw binary data appended to the command
        :param wait_completion: Add an *OPC? after the command to confirm completion
        :param log_me: to log or not to log the command via log.debug()
        :return:
        """
        if req == '':
            return
        short_req = req + ':'.join(['{}'.format(a) for a in data]) if data else req
        short_req = short_req if len(short_req) < 150 else short_req[0:150]+"[...]"
        if "?" in req:
            if data is not None:
                raise ValueError('Binary data not allowed with queries!')
            result = self.device.query(req)
            try:
                result = result.strip()
            except UnicodeDecodeError:
                pass
            if log_me:
                log.debug('{}: "{}" -> "{}"'.format(self.name, short_req, result))
            return result
        else:
            if log_me or self.cmd_pause:
                log.debug('{}: "{}"'.format(self.name, short_req))
            if self.cmd_pause:
                import inspect
                import sys
                sys.stderr.flush()
                fi = inspect.stack()[1]
                print('{}:{}():{}'.format(fi.filename.split('/')[-1], fi.function, fi.lineno))
                c = input('ENTER for cmd: {}'.format(short_req))
                if c == 'q':
                    self.cmd_pause = False
            t0 = time.time()
            if data is None:
                self.device.write(req)
            else:
                self.device.write_binary_values(req, data, "H", is_big_endian=False)
            if '*rst' in req.lower():
                log.debug('Sleep after reset.')
                time.sleep(2)
            if wait_completion or self.cmd_profile:
                self.device.query('*OPC?')
            dt = time.time() - t0
            if self.cmd_profile:
                if dt > 0.05:
                    if log_me:
                        log.debug('* took {:.6}s'.format(dt))

    def reset(self):
        self.cmd('*RST')

    def choose_arbitrary_waveform(self, source: int, sample_rate,
                                  amplitude: t.Optional[float] = None,
                                  offset: t.Optional[float] = None,
                                  fixed_pp: t.Optional[float] = None):
        """ Implements [:SOURce[<n>]]:APPLy:ARBitrary

        See section 2-73 (p85)

        :param source:
        :param sample_rate:
        :param amplitude:
        :param offset:
        :param fixed_pp: Apply this amplitude (with offset zero) and hold amplifier to avoid glitches
        :return:
        """
        if fixed_pp is not None:
            self.cmd(':SOUR{}:VOLT:RANG:AUTO ON'.format(source), wait_completion=True)
            self.cmd(':SOUR{}:APPL:ARB {},{},{}'.format(
                source, sample_rate, fixed_pp,
                offset if offset is not None else 'DEF'
            ), wait_completion=True)
            self.cmd(':SOUR{}:VOLT:RANG:AUTO OFF'.format(source), wait_completion=True)
        else:
            self.cmd(':SOUR{}:APPL:ARB {},{},{}'.format(
                source, sample_rate,
                amplitude if amplitude is not None else 'DEF',
                offset if offset is not None else 'DEF'
            ), wait_completion=True)

    def burst_prepare(self, source, positive_flank: bool = True):
        self.cmd(':SOUR{}:BURS ON'.format(source))

        self.cmd(':SOUR{}:BURS:MODE TRIG'.format(source))
        self.cmd(':SOUR{}:BURS:NCYC 1'.format(source))  # Wiederholungen innerhalb des bursts
        self.cmd(':SOUR{}:BURS:INT:PER 5'.format(source))  # Wiederholt den Burst alle 0.2 sec, wenn INT trigger
        self.cmd(':SOUR{}:BURS:TRIG:TRIGO {}'.format(source, 'POS' if positive_flank else 'NEG'))
        self.cmd(':SOUR{}:BURS:TRIG:SOUR MAN'.format(source))
        self.cmd(':SOUR{}:BURS:TDEL 0.0'.format(source))

        self.cmd('*OPC?')

    def burst_trigger(self, source, delay: float = 0.0):
        # apparently, the trigger source needs to be re-applied after a burst is triggered,
        # otherwise there might be a time-shift in the trigger signal (we observed this, but why?)
        self.cmd(':SOUR{}:BURS:TRIG:SOUR MAN'.format(source))
        self.cmd(':SOUR{}:BURS:TDEL {}'.format(source, max(delay, 0.0)))
        self.cmd(':SOUR{}:BURS:TRIG'.format(source))
        self.cmd('*OPC?')

    def download_normalized_trace_data(self, source: int, data: t.Union[t.List[float], t.List[int]]):
        """ Implements [:SOURce[<n>]][:TRACe]:DATA:DAC and [:SOURce[<n>]][:TRACe]:DATA[:DATA]

        See section 2-175 (p185)

        :param data: Sequence of float values (-1. .. 1.) or uint16 values (0x0000 .. 0x3FFF)
        :param source:
        :return:
        """
        if len(data) > self.MAX_BURST_SAMPLES:
            raise TypeError('Data length exceeds rigol capabilities.')
        np_data = np.array(data)
        if np.min(np_data) < -1. or 1. < np.max(np_data):
            raise ValueError('Data outside valid range (-1. .. 1.)')

        # DG1000Z vertical resolution is 14 Bits (bipolar) or 1V/e^13 = 122�V
        self.cmd(':SOUR{}:TRAC:DATA:DATA VOLATILE,{}'.format(source, ','.join(['{:.5f}'.format(d) for d in data])),
                 wait_completion=True)
        self.cmd(':SOUR{}:TRAC:DATA:POIN VOLATILE,{}'.format(source, len(data)), wait_completion=True)
        return len(data)

    def download_normalized_trace_dac16(self, source: int, data: t.Union[t.List[float], t.List[int]]):
        """ Implements [:SOURce[<n>]][:TRACe]:DATA:DAC and [:SOURce[<n>]][:TRACe]:DATA[:DATA]

        See section 2-173 (p185)

        :param data: Sequence of float values (-1. .. 1.) or uint16 values (0x0000 .. 0x3FFF)
        :param source:
        :return:
        """
        if any(isinstance(x, float) for x in data):
            log.debug('Converting float input data to DAC values')
            data = [max(0, min(int((a + 1.) / 2. * 16383 + 0.5), 0x3fff)) for a in data]

        if all(isinstance(x, int) for x in data):
            if not all(0 <= x <= 0x3fff for x in data):
                raise ValueError('Data outside valid range (0x000� .. 0x3FFF)')

        buffer = data

        # DG1000Z vertical resolution is 14 Bits (bipolar) or 1V/e^13 = 122�V
        # self.cmd(':SOURCE1:FUNC:ARB:MODE SRATE')  # rigol does this for us
        start = time.time()
        while len(buffer):
            chunk_size = min(len(buffer), 8192)  # in contrast to the docs, 16384 seems to not work
            remain = len(buffer) - chunk_size
            if 0 < remain < 8:
                chunk_size -= 8
                remain = len(buffer) - chunk_size
            # log.debug("{} pts remaining, next chunk has {} pts.".format(len(buffer), chunk_size))
            # log.debug('{}'.format(buffer[:chunk_size]))
            self.cmd(':SOUR{}:TRAC:DATA:DAC16 VOLATILE,{},'.format(  # the '#{}{}' is part of the ieee-block
                source, 'CON' if remain > 0 else 'END'),
                data=buffer[:chunk_size], wait_completion=True)
            buffer = buffer[chunk_size:]
        log.debug('Transferred {} pts in {:.1f}s.'.format(len(data), time.time()-start))

        return len(data)

    def set_arbitrary_waveform(self, channel: int, x: t.List[float], y: t.List[float],
                               relax: bool = False, amplification: float = 1.0,
                               offset: float = 0.0, apply_offset: bool = False,
                               use_full_range: bool = False, fixed_pp: float = None):
        """ Provide really arbitrary data.

        The peak-to-peak amplitude and offset are extracted from [x, y] data and
        applied, normalized data is downloaded to the device.

        Incidentally, the output waveform will appear to be offset by one index and the
        output will yield the first given voltage after the burst is complete.

        The option use_full_range shall be used with care, since an offset other tha 0.0 may result
        in a surge at t=0 (when the burst is triggered)

        :param channel: 1 or 2
        :param x: Either [t0, tmax] or equidistant timestamps for each y
        :param y: array of voltages to output
        :param relax: If true, just assume that all timestamps are monotonic and equally spaced
        :param amplification: Optional external amplification, values > 1 effectively reduce the rigol output amplitude
        :param use_full_range: If true, choose offset between y_min and y_max and use full range -1.0..1.0
        :param offset: Choose this offset for remapping of all y data
        :param apply_offset: If false, do not apply the signal offset immediately
        :param fixed_pp: Apply this amplitude (with offset zero) and hold amplifier to avoid glitches
        :return:
        """
        if not isinstance(x, (list, )):
            raise TypeError('Argument x must be list of floats - got {} instead.'.format(type(x)))
        if not isinstance(y, (list, )):
            raise TypeError('Argument y must be list of floats - got {} instead.'.format(type(x)))
        if not len(x) == 2 and not len(x) == len(y):
            raise TypeError('Length of x must be 2 or equal to length of y. Got {} instead.'.format(len(x)))
        if len(y) < 2:
            raise TypeError('Argument y must comprise at least 2 values.')
        span = x[-1] - x[0]
        dx = span / (len(y) - 1)
        if len(x) == len(y):
            diffs = np.diff(x)
            lo = abs(1 - abs(np.min(diffs)) / dx)
            hi = abs(1 - abs(np.max(diffs)) / dx)
            log.info("x values: dx={}, lo={}, hi={}".format(dx, lo, hi))
            if max(lo, hi) > 1e-4 and not relax:
                log.error('Time series spacing is min_diffs={}, max_diffs={}'.format(np.min(diffs), np.max(diffs)))
                raise ValueError('Time series is not equally spaced or not monotonic')
        if amplification <= 0:
            amplification = 1.0

        y_min = np.min(y)
        y_max = np.max(y)
        if use_full_range:
            y_offs = (y_min + y_max) / 2.
            y_pp = (y_max - y_min) or 1.0
        else:
            y_offs = offset
            y_pp = 2 * max(abs(y_min-y_offs), abs(y_max-y_offs)) or 2.0
        if fixed_pp is not None:
            y_pp = fixed_pp
            fixed_pp /= amplification

        freq = len(y) / span
        waveform = 2. * (np.array(y) - y_offs) / y_pp
        log.debug("Waveform w/ PP={} and O={} is {}".format(y_pp, y_offs, waveform))

        # if we use fixed_pp, make sure to set the same amplitude
        self.download_normalized_trace_dac16(channel, waveform)
        self.choose_arbitrary_waveform(channel, freq, y_pp/amplification,
                                       y_offs/amplification if apply_offset else 0.0, fixed_pp=fixed_pp)

        return freq, y_pp/amplification, y_offs/amplification if apply_offset else 0.0

    def set_output_state(self, output, state: bool, wait_completion=True):
        """ Implements :OUTPut[<n>][:STATe]

        See section 2-58 (p70)

        :param output:
        :param state:
        :param wait_completion:
        :return:
        """
        self.cmd(':OUTP{}:STAT {}'.format(output, 'ON' if state else 'OFF'), wait_completion=wait_completion)

    def get_output_state(self, output):
        return True if self.cmd(":OUTP{}:STAT?".format(output)) == "ON" else False

    def set_fixed_range(self, source, max_amplitude, return_to=None):
        """ To fix the signal range, """
        self.cmd(':SOUR{}:VOLT:RANG:AUTO ON'.format(source), wait_completion=True)
        self.set_dc(source, max_amplitude)
        # self.set_offset(source, max_amplitude)
        self.cmd(':SOUR{}:VOLT:RANG:AUTO OFF'.format(source), wait_completion=True)
        if return_to is not None:
            self.set_offset(source, return_to)
        self.set_output_state(source, False)

    def set_dc(self, source, level):
        self.cmd(':SOUR{}:APPL:DC 1,1,{}'.format(source, level), wait_completion=True)

    def set_sin(self, source, amplitude, offset):
        self.cmd(':SOUR{}:APPL:SIN 10,{},{}'.format(source, amplitude, offset), wait_completion=True)

    def set_offset(self, source, offset):
        self.cmd(':SOUR{}:VOLT:OFFS {}'.format(source, offset), wait_completion=True)


def arb_waveform_test1(dev: DG4162):
    # waveform1 = [-0.6, -0.4, -0.3, -0.1, 0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.0]
    waveform2 = [0.6, 0.4, 0.3, 0.1, 0, -0.1, -0.2, -0.3, -0.5, -0.7, 1.0]
    # Set CH1 to output arbitrary waveform (sample rate output mode) and the waveform frequency to 500Hz
    # :SOUR1:APPL:ARB 500
    dev.choose_arbitrary_waveform(1, 500000, 5, 2.5)  # 500kHz -> 20�s (2�s = 1/500kHz per point)
    # Download the floating voltages to the volatile memory of CH1
    # :SOUR1:DATA VOLATILE,-0.6,-0.4,-0.3,-0.1,0,0.1,0.2,0.3,0.5,0.7
    # dev.download(1, waveform1)  # , save_to=1)
    dev.download_normalized_trace_data(1, waveform2)  # , save_to=2)
    # dev.cmd(':SOUR1:FUNC?')
    dev.cmd(':SOUR1:DATA:POIN? VOLATILE')
    # Turn on the output of CH1
    # :OUTP1 ON

    # dev.cmd(':SOUR1:TRAC:DATA:CATalog?')
    # dev.cmd(':SOUR2:TRAC:DATA:CATalog?')

    # Turn on the burst function of CH1
    dev.cmd(':SOUR1:BURS ON')
    # Set the burst type of CH1 to N cycle
    dev.cmd(':SOUR1:BURS:MODE TRIG')
    # Set the number of cycles of the N cycle burst of CH1 to 10
    dev.cmd(':SOUR1:BURS:NCYC 10')  # Wiederholungen innerhalb des bursts
    dev.cmd(':SOUR1:BURS:NCYC?')
    # Set the internal burst period of the N cycle burst of CH1 to 0.1s
    dev.cmd(':SOUR1:BURS:INT:PER 5')  # Wiederholt den Burst alle 0.2 sec, wenn INT trigger
    # Set the trigger source of the burst mode of CH1 to internal
    # dev.cmd(':SOUR1:BURS:TRIG:SOUR INT')
    dev.cmd(':SOUR1:BURS:TRIG:SOUR MAN')
    # Set the edge type of the trigger output signal of the burst mode of CH1 to falling edge
    dev.cmd(':SOUR1:BURS:TRIG:TRIGO POS')
    # Set the trigger delay of the N cycle burst of CH1 to 0.01s
    dev.cmd(':SOUR1:BURS:TDEL 0.01')

    # // Erste Waveform vorbereiten:
    # dev.choose_arbitrary_waveform(1, 500000, 5, 2.5)
    # dev.cmd('*CLS')
    # dev.cmd(':SOUR1:TRAC:DATA:COPY ARB1,VOLATILE')  # even if the catalog names Scpi1.RAF etc, use ARB<n>
    # dev.cmd('*RCL ARB1')
    dev.cmd(':SYSTem:ERRor?')
    dev.cmd('*OPC?')
    dev.cmd(':SOUR1:TRAC:DATA:LOAD? VOLATILE')
    # :OUTP1 ON                   /*Turn on the output off CH1*/
    dev.set_output_state(1, True)
    # :SOUR1:BURS:TRIG            /*Trigger a burst output in CH1 immediately*/
    dev.cmd(':SOUR1:BURS:TRIG')
    # dev.cmd('*TRG')


def arb_waveform_test2(dev: DG4162):
    waveform1 = [0.0, 0.0, 0.0, -0.6, -0.4, -0.3, -0.1, 0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.0]
    waveform2 = [0.0, 0.0, 0.0, 0.6, 0.4, 0.3, 0.1, 0, -0.1, -0.2, -0.3, -0.5, -0.7, 0.0]

    dev.choose_arbitrary_waveform(1, 50, 4, 0)  # 1/500Hz = 2ms/sample -> 22ms pro form, 220ms pro burst
    dev.download_normalized_trace_data(1, waveform1)

    dev.cmd(':SOUR1:BURS ON')
    dev.cmd(':SOUR1:BURS:MODE TRIG')
    dev.cmd(':SOUR1:BURS:NCYC 3')  # Wiederholungen innerhalb des bursts
    dev.cmd(':SOUR1:BURS:NCYC?')
    dev.cmd(':SOUR1:BURS:INT:PER 5')  # Wiederholt den Burst alle 0.2 sec, wenn INT trigger
    dev.cmd(':SOUR1:BURS:TRIG:SOUR MAN')
    dev.cmd(':SOUR1:BURS:TRIG:TRIGO POS')
    dev.cmd(':SOUR1:BURS:TDEL 0.01')

    # dev.choose_arbitrary_waveform(1, 5000, 4, 2)  # 1/500Hz = 2ms/sample -> 22ms pro form, 220ms pro burst

    dev.download_normalized_trace_data(1, waveform1)
    dev.cmd(':SOUR1:BURS ON')
    dev.set_output_state(1, True)
    # dev.cmd(':SOUR1:BURS:TRIG')
    dev.cmd('*OPC?')

    start = time.time()
    # dev.cmd('*TRG')
    dev.cmd(':SOUR1:BURS:TRIG')
    dev.cmd('*OPC?')
    delay = time.time() - start
    log.debug('delay = {}'.format(delay))

    time.sleep(1.5 - delay)

    # dev.cmd(':SOUR1:BURS OFF')  # switching off burst means returning to continuous output!
    dev.cmd('*TRG')
    dev.cmd('*OPC?')

    time.sleep(1.5 - delay)

    dev.set_output_state(1, False)
    dev.download_normalized_trace_data(1, waveform2)
    dev.cmd(':SOUR1:BURS ON')
    dev.cmd(':SOUR1:BURS:NCYC 2')
    dev.set_output_state(1, True)

    dev.cmd('*TRG')


def arb_waveform_test3(dev: DG4162):
    waveform1 = [0.0, 0.0, 0.0, -0.6, -0.4, -0.3, -0.1, 0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.0]

    dev.choose_arbitrary_waveform(1, 50, 4, 0)  # 1/500Hz = 2ms/sample -> 22ms pro form, 220ms pro burst
    dev.download_normalized_trace_data(1, waveform1)

    dev.cmd(':SOUR1:BURS ON')
    dev.cmd(':SOUR1:BURS:MODE TRIG')
    dev.cmd(':SOUR1:BURS:NCYC 3')  # Wiederholungen innerhalb des bursts
    dev.cmd(':SOUR1:BURS:NCYC?')
    dev.cmd(':SOUR1:BURS:INT:PER 5')  # Wiederholt den Burst alle 0.2 sec, wenn INT trigger
    dev.cmd(':SOUR1:BURS:TRIG:SOUR MAN')
    dev.cmd(':SOUR1:BURS:TRIG:TRIGO POS')
    dev.cmd(':SOUR1:BURS:TDEL 0.01')

    dev.cmd(':OUTP1:SYNC?')
    dev.download_normalized_trace_data(1, waveform1)
    dev.cmd(':SOUR1:BURS ON')
    dev.set_output_state(1, True)
    dev.cmd('*OPC?')

    dev.cmd(':SOUR1:BURS:TRIG')
    dev.cmd('*OPC?')


# def arb_waveform_carla(dev: DG4162, repeat_after: float = None):
#     from base_char import calc
#     x_time, y_data, info = calc(amp=50, offs=40, freq=48, periods=23, max_samples=50000,
#                                 v_max=80000, a_max=None,
#                                 auto_limit_amp=False)
#     dev.set_arbitrary_waveform(1, x_time, y_data, amplification=10)
# 
#     log.info("Output carla test signal with {:.2f}s duration ".format(x_time[-1]))
#     dev.burst_prepare(1)
#     dev.set_output_state(1, True, wait_completion=True)
#     while True:
#         dev.burst_trigger(1)
#         log.info("Ooops - I did it again")
#         if repeat_after:
#             time.sleep(repeat_after)
#         else:
#             break


# def arb_waveform_test4(dev: DG4162, filename=None, span=None):
#     """ Demonstrate how to output a waveform around an offset
#         with arbitrary hold time before the waveform is triggered.
#     """
#     dev.reset()
# 
#     waveform1 = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2, 0.5, 0.8]
#     if filename:
#         from carla.experiment import Experiment
#         xp = Experiment()
#         xp.load(filename)
#         # x_time, y_data = [0.0, 1.0], [35, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]
#         # xp.set_data(x_time, [y_data] * 10)
# 
#         x_time, y_data = xp.get_data(0, v_max=8000, a_max=1e7, start_at_offset=True)
#         if span is not None and span > 0:
#             x_time = [0.0, float(span)]
#         span = x_time[-1] - x_time[0]
#         log.info('arb_waveform_test4: span={} y= [{} .. {}]'.format(span, y_data[0], y_data[-1]))
# 
#         dev.set_arbitrary_waveform(1, x_time, y_data, amplification=10, offset=y_data[0], fixed_pp=10.)
# 
#         y0 = y_data[0]/10.  # amplification!
#     else:
#         # prepare the waveform with offset
#         s_rate, amp, offs = 50, 4, 0
#         dev.choose_arbitrary_waveform(1, s_rate, amp, offs)  # 1/500Hz = 2ms/sample -> 22ms pro form, 220ms pro burst
#         dev.download_normalized_trace_data(1, waveform1)
#         span = 0.1
#         y0 = 5.
# 
#     dev.burst_prepare(1)
# 
#     # the offset is applied as soon as we enable the output
# 
#     dev.cmd(':SOUR1:VOLT:OFFS 0', wait_completion=True)
#     dev.set_output_state(1, True)
#     # dev.cmd(':SOUR1:VOLT:OFFS 0', wait_completion=True)
#     time.sleep(3)
# 
#     for v in np.linspace(0., y0, int(y0/0.25)):
#         dev.cmd(':SOUR1:VOLT:OFFS {}'.format(v), wait_completion=True)
#         # time.sleep(0.5)
# 
#     # take your time to linger at this offset
#     time.sleep(5)
# 
#     # now trigger the waveform, then wait some time before disabling the output
#     dev.cmd(':SOUR1:BURS:TRIG', wait_completion=True)
#     time.sleep(span)
#     time.sleep(2)
#     for v in np.linspace(y0, 0., int(y0/0.25)):
#         dev.cmd(':SOUR1:VOLT:OFFS {}'.format(v), wait_completion=True)
#         # time.sleep(0.5)
# 
#     dev.set_output_state(1, False)


# def arb_waveform_test5(dev: DG4162, filename, span=3.5, traces=None):
#     """ Demonstrate how to output a two waveforms in a row around the same offset
#         with arbitrary hold time before the waveform is triggered.
#     """
#     dev.reset()
#     if traces is None:
#         traces = [0, 1, 2, 3]
# 
#     ch_sig, ch_offs = 1, 2
# 
#     from carla.experiment import Experiment
#     xp = Experiment()
#     xp.load(filename)
# 
#     last_offset = 0.0
# 
#     dev.set_output_state(ch_offs, False)
#     dev.set_dc(ch_offs, 0.0)
# 
#     dev.set_offset(ch_sig, 0.0)
#     dev.set_offset(ch_offs, 0.0)
# 
#     dev.burst_prepare(ch_sig)
# 
#     dev.cmd(':OUTP1:IMP 1000')
#     dev.cmd(':OUTP2:IMP 1000')
# 
#     dev.set_output_state(ch_sig, True)
#     dev.set_output_state(ch_offs, True)
# 
#     for num in traces:
#         log.info('arb_waveform_test5: Getting new trace data #{}'.format(num))
#         x_time, y_data = xp.get_data(num_or_dataset=num, v_max=8000, a_max=1e7, start_at_offset=True)
#         if span is not None and span > 0:
#             x_time = [0.0, float(span)]
#         span = x_time[-1] - x_time[0]
#         log.info('span={} y= [{} .. {}]'.format(span, y_data[0], y_data[-1]))
# 
#         y0 = y_data[0]/10.  # amplification!
# 
#         # the offset is applied as soon as we enable the output
# 
#         if y0 != last_offset:
#             log.info('*** ramping from {} to {}'.format(last_offset, y0))
#             for v in np.linspace(last_offset, y0, int((y0-last_offset)/0.25)):
#                 dev.set_dc(ch_offs, v)
# 
#         # sleep time between two traces
#         time.sleep(3)
# 
#         dev.set_dc(ch_sig, 0.0)  # otherwise, the level will drop to -amp/2
#         dev.set_output_state(ch_sig, False)
#         dev.set_arbitrary_waveform(ch_sig, x_time, y_data, amplification=10, fixed_pp=100.,
#                                    offset=y_data[0], apply_offset=False)
#         dev.set_output_state(ch_sig, True)
#         dev.burst_trigger(ch_sig)
# 
#         time.sleep(span)
#         time.sleep(1)
#         last_offset = y_data[-1]/10.
# 
#     log.info('*** ramping from {} to zero'.format(last_offset))
#     for v in np.linspace(last_offset, 0., int(last_offset/0.25)):
#         dev.set_offset(ch_offs, v)
# 
#     dev.set_output_state(ch_sig, False)
#     dev.set_output_state(ch_offs, False)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)

    logging.getLogger('pyvisa').setLevel(logging.ERROR)
    logging.getLogger('pyvisa').setLevel(logging.WARN)

    # import pprint
    # pprint.pprint(DG4162.find_devices())
#    
#    serialStr = 'DG1ZA160100016'
#    
#    addr = DG4162.get_addr_by_serial(serialStr)
##     addr = '10.0.3.79'
#    print(addr)
    
    visaAddrStr = 'USB0::0x1AB1::0x0641::DG4E225002250::INSTR'
    visaAddrStr = 'TCPIP::169.254.187.139::INSTR'
    
# 
    dg = DG4162()
    dg.connectUSB(visaAddrStr)  # 00:19:AF:04:04:3B
    dg.reset()
    dg.timeout = 5000
    
    
    time.sleep(1)
    arb_waveform_test1(dg)
    # arb_waveform_test3(dg)
    # dg.burst_purge()
#     arb_waveform_carla(dg, repeat_after=0.6)
    # arb_waveform_test4(dg, 'zeiss-format-trace.dat')
    # arb_waveform_test5(dg, 'zeiss-format-trace.dat', traces=[0, 1, 2, 3])
    # arb_waveform_test5(dg, 'carla-exp.carla', traces=[0, 1, 2, 3])
    # arb_waveform_test4(dg)
    # check waveform at 10.0.

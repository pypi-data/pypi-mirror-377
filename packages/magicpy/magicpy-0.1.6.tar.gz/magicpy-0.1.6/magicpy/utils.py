import time
import serial.tools.list_ports
import warnings


def list_ports():
    warnings.warn('Depreceated: Use magicpy.list_serial_ports() instead of magicpy.list_ports() to list serial ports.',
                  DeprecationWarning, stacklevel=2)
    return list_serial_ports()


def list_serial_ports():
    """
    Prints available serial ports on the machine.

    Returns
    -------
    list : List of available ports.
    """
    ports = serial.tools.list_ports.comports()
    print(f"{'port': <13}|{'description': <22}| {'hwid': <34} | subsystem")
    print('-' * 84)
    for p in sorted(ports):
        port, desc, hwid = p
        subsys = p.subsystem if hasattr(p, "subsystem") else "n/a"
        print(f"{port: <13}| {desc: <20} | {hwid: <34} | {subsys}")
    return ports


class TriggerPort:
    """
    Just a wrapper to pyparallel port to send a TTL pulse.
    """

    def __init__(self, port=0, pulse_duration=0.01):
        import parallel
        self.port = parallel.Parallel(port)
        self.pulse_duration = pulse_duration

        self.value_high = 1
        self.value_low = 0

    def trigger(self):
        """
        Send a TTL pulse over the parallel port.

        You should set stimulator trigger in setting to 'Raising Edge'.
        """
        self.port.setData(self.value_high)
        time.sleep(self.pulse_duration)
        self.port.setData(self.value_low)


def hexlm(val, fac=1, z=4):
    """
    Get LSB and MSB from hexified, zero-padded value.

    Parameters
    ----------
    val : float
        Value to get LSB and MSB for.
    fac : int, default: 1
        Multiplication factor.
    z : int, default: 4
        Zero padding to z.

    Returns
    -------
    LSB : str
        The least significant bit.
    MSB : str
        The most significant bit.
    """
    val *= fac
    val = int(val)
    val = hex(val)[2:].zfill(z)  # zero padded to n digits, 0x removed
    return val[2:4], val[0:2]  # LSB

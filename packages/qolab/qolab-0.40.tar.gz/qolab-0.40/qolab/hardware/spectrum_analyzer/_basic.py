"""Basic Spectrum Analyzer classes intended for expansion with hardware aware classes."""

from qolab.hardware.scpi import SCPIinstr
from qolab.hardware.basic import BasicInstrument
from qolab.data.trace import TraceSetSameX


class SpectrumAnalyzer(BasicInstrument):
    """Basic Spectrum Analyzer class.
    Intended to be expanded in hardware specific classes.
    """

    def __init__(self, *args, **kwds):
        BasicInstrument.__init__(self, *args, **kwds)
        self.config["Device type"] = "Spectrum Analyzer"
        self.config["Device model"] = (
            "Generic Spectrum Analyzer Without Hardware interface"
        )
        self.config["FnamePrefix"] = "spectrum_analyzer"
        self.numberOfChannels = 0
        self.deviceProperties.update(
            {
                "FreqCenter",
                "FreqSpan",
                "FreqStart",
                "FreqStop",
                "RBW",
                "VBW",
                "SweepTime",
            }
        )
        self.channelProperties = {
        }

    # Minimal set of methods to be implemented.
    def getTrace(
        self,
        chNum,
        **kwargs,
    ):
        """Get scope trace with time axis set."""
        raise NotImplementedError("getTrace function is not implemented")

    def getAllTraces(self, channelsList=None, **kwargs):
        """
        Get all traces channels in the channelsList.

        If channelsList is None, go over all physical channels: 1, 2, ...
        channelsList can contain non hardware channels, i.e. functional one
        then they should be called F1, F2, ... etc
        or have hardware scope dependent names to be deciphered in a particular scope class.
        """
        if channelsList is None:
            channelsList = range(1, self.numberOfChannels + 1)
        allTraces = TraceSetSameX("spectrum analyzer traces")
        allTraces.config["tags"]["DAQ"] = self.getConfig()
        for chNum in channelsList:
            allTraces.addTrace(
                self.getTrace(
                    chNum,
                    **kwargs
                )
            )
        return allTraces

    def save(
        self,
        fname=None,
        item_format="e",
        channelsList=None,
        extension="dat.gz",
    ):
        allTraces = self.getAllTraces(
            channelsList=channelsList,
        )
        allTraces.config["item_format"] = item_format
        if fname is None:
            fname = self.getNextDataFile(extension=extension)
        allTraces.save(fname)
        print(f"Data saved to: {fname}")
        return fname

class SpectrumAnalyzerSCPI(SCPIinstr, SpectrumAnalyzer):
    """Basic Spectrum Analyzer class with SCPI interface.
    Intended to be expanded in hardware specific classes.

    Example
    -------
    >>> rm = pyvisa.ResourceManager()
    >>> SpectrumAnalyzerSCPI(rm.open_resource('TCPIP::192.168.0.2::INSTR'))
    """

    pass

    def __init__(self, resource, *args, **kwds):
        SCPIinstr.__init__(self, resource)
        SpectrumAnalyzer.__init__(self, *args, **kwds)
        self.config["DeviceId"] = str.strip(self.idn)

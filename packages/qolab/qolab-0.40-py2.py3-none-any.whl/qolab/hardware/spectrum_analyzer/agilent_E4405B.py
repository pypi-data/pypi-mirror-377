from qolab.hardware.spectrum_analyzer._basic import SpectrumAnalyzerSCPI
from qolab.hardware.scpi import SCPI_PROPERTY
from qolab.data.trace import Trace, TraceXY
import numpy as np


class Agilent_E4405B(SpectrumAnalyzerSCPI):
    """Agilent E4405B Spectrum Analyzer"""

    def __init__(self, resource, *args, **kwds):
        super().__init__(resource, *args, **kwds)
        self.config["Device model"] = "Agilent E4405B"
        self.resource.read_termination = "\n"
        self.numberOfChannels = 3
        self.deviceProperties.update(
            {
                "YAxisScale",
                "YAxisUnit",
                "ReferenceLevel",
                "Attenuation",
                "TraceDataExchangeFromat",
                "SweepNpoints",
            }
        )

    @property
    def idn(self):
        """Agilent E4405B  has non standard call of idn"""
        return self.query("ID?")

    FreqCenter = SCPI_PROPERTY(
        scpi_prfx="SENSE:FREQUENCY:CENTER", ptype=float, doc="Central frequency"
    )
    FreqSpan = SCPI_PROPERTY(
        scpi_prfx="SENSE:FREQUENCY:SPAN", ptype=float, doc="Frequency span"
    )
    FreqStart = SCPI_PROPERTY(
        scpi_prfx="SENSE:FREQUENCY:START",
        ptype=float,
        doc="Start frequency of the span",
    )
    FreqStop = SCPI_PROPERTY(
        scpi_prfx="SENSE:FREQUENCY:STOP", ptype=float, doc="Stop frequency of the span"
    )
    RBW = SCPI_PROPERTY(
        scpi_prfx="SENSE:BANDWIDTH:RESOLUTION", ptype=float, doc="Resolution bandwidth"
    )
    VBW = SCPI_PROPERTY(
        scpi_prfx="SENSE:BANDWIDTH:VIDEO", ptype=float, doc="Video bandwidth"
    )
    SweepTime = SCPI_PROPERTY(
        scpi_prfx="SENSE:SWEEP:TIME", ptype=float, doc="Video bandwidth"
    )
    YAxisScale = SCPI_PROPERTY(
        scpi_prfx=":DISPlAY:WINDOW:TRACE:Y:SCALE:PDIVISION",
        ptype=float,
        doc="Vertical axis scale per division",
    )
    YAxisUnit = SCPI_PROPERTY(
        scpi_prfx=":UNIT:POWER",
        ptype=str,
        doc="Vertical axis unit (DBM|DBMV|DBUV|DBUA|V|W|A)",
    )
    ReferenceLevel = SCPI_PROPERTY(
        scpi_prfx="DISPLAY:WINDOW:TRACE:Y:SCALE:RLEVEL",
        ptype=float,
        doc="Reference level",
    )
    Attenuation = SCPI_PROPERTY(
        scpi_prfx=":SENSE:POWER:RF:ATTenuation",
        ptype=float,
        doc="Attenuation level, default setting is 10 and unit dB",
    )
    TraceDataExchangeFromat = SCPI_PROPERTY(
        scpi_prfx=":FORMAT:TRACE:DATA",
        ptype=str,
        doc="""
        Trace data exchange format (ASCii|INTeger,32|REAL,32|REAL,64|UINTeger,16),
        defalult is ASCII - human readable in the units of the Yscale
        fastest INTEGER,32 which report mdBm units (internal to the spectrum analyzer),
        """,
    )
    SweepNpoints = SCPI_PROPERTY(
        scpi_prfx=":SENSe:SWEep:POINts",
        ptype=int,
        doc="Number of points per sweep trace. Default 401, can be as large as 8192",
    )

    def getXTrace(self):
        # return X trace, default is frequency space
        # but for zero span it is better to use time space
        Npnts = self.SweepNpoints
        # de
        x = Trace("ToBeRedefined")
        x.config["tags"]["Npnts"] = Npnts
        x.config["tags"]["FreqCenter"] = self.FreqCenter
        x.config["tags"]["FreqSpan"] = self.FreqSpan
        x.config["tags"]["SweepTime"] = self.SweepTime
        if 0 != x.config["tags"]["FreqSpan"]:
            x.config["label"] = "Frequency"
            x.config["unit"] = "Hz"
            xval = np.linspace(self.FreqStart, self.FreqStop, Npnts)
        else:
            x.config["label"] = "Time"
            x.config["unit"] = "s"
            xval = np.linspace(0, x.config["tags"]["SweepTime"], Npnts)
        x.values = xval.reshape(xval.size, 1)
        return x

    def getTrace(
        self,
        chNum,
        **kwargs,
    ):
        chName = "Ch"+str(chNum)
        qstr = f':TRACE:DATA? TRACE{chNum};'
        fmt = self.TraceDataExchangeFromat
        if 'ASC,+8' == fmt:
            rstr = self.query(qstr)
            lstr = rstr.split(',')
            n=np.array([float(i) for i in lstr])
        else:
            raise(RuntimeError(f"Do not know how to exchange data formatted as '{fmt}'"))
        tr = TraceXY(chName)
        x = self.getXTrace()
        tr.x = x
        y = Trace("Amplitude")
        y.config["unit"] = self.YAxisUnit
        y.config["tags"]["ReferenceLevel"] = self.ReferenceLevel
        y.config["tags"]["Attenuation"] = self.Attenuation
        y.values = n.reshape(n.size,1)
        tr.y = y
            
        return tr

if __name__ == "__main__":
    import pyvisa

    print("testing")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    instr = rm.open_resource("visa://10.160.137.40/GPIB0::21::INSTR")

    sa = Agilent_E4405B(instr)
    print("------ Header start -------------")
    print(str.join("\n", sa.getHeader()))
    print("------ Header ends  -------------")

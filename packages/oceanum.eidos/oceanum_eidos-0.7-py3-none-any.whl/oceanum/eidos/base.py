import json
import re
import os
import time
import tempfile
import webbrowser
import jinja2
import altair
from jsonpatch import JsonPatch
from pandas import DataFrame, Timestamp
from geopandas import GeoDataFrame
from xarray import Dataset
from oceanum.datamesh import Query

from .version import __version__
from .root import EidosSpecification
from .data import EidosData
from .vegaspec import TopLevelSpec
from .exceptions import EidosError

EIDOS_RENDERER = os.environ.get("EIDOS_RENDERER", "https://render.eidos.oceanum.io")
TEMPLATES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "./_templates/"
)
j2_loader = jinja2.FileSystemLoader(TEMPLATES_PATH)
j2_env = jinja2.Environment(loader=j2_loader, trim_blocks=True)


class EidosError(Exception):
    """Base class for Eidos exceptions."""


class Eidos(EidosSpecification):
    """Eidos base class. This is the EIDOS base specification."""

    _checkpoint = None

    @classmethod
    def from_dict(cls, spec: dict):
        """Initialize Eidos class."""
        return cls(**spec)

    @classmethod
    def from_json(cls, spec: str):
        """Initialize Eidos class from json."""
        return cls.from_dict(json.loads(spec))

    def __init__(self, **spec):
        """Initialize Eidos class."""
        super().__init__(**spec)
        self._checkpoint = self.model_dump()

    def __str__(self):
        """Return string representation of Eidos class."""
        return self.model_dump_json(indent=2)

    def _change(self):
        """Change."""
        pass
        # print(f"EIDOS spec changed: {update}")

    def model_dump(self, **kwargs):
        """Dump model as dictionary."""
        return super().model_dump(**{**kwargs, "exclude_none": True})

    def diff(self):
        """Get diff since last checkpoint and reset checkpoint"""
        old = self._checkpoint
        self._checkpoint = self.model_dump()
        return (old, self._checkpoint)

    def patch(self):
        """Diff as JSON patch"""
        old, new = self.diff()
        return JsonPatch.from_diff(old, new).patch

    def spec(self):
        """Return the full EIDOS specification."""
        return self.model_dump()

    def html(self, title=None, renderer=EIDOS_RENDERER, height="99vh", width="99vw"):
        """Return the EIDOS specification as a displayable HTML page."""
        template = j2_env.get_template("index.j2")
        return template.render(
            spec=self.model_dump_json(exclude_none=True),
            title=title or self.name or "EIDOS",
            renderer=renderer,
            height=height,
            width=width,
        )

    def show(self, renderer=EIDOS_RENDERER):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            f.write(self.html(renderer).encode())
            f.close()
            url = "file://{}".format(f.name)
            time.sleep(1.0)
            return webbrowser.open_new_tab(url)


def isotime(x):
    t = Timestamp(x)
    if not t.tz:
        t = t.tz_localize("UTC")
    return t.isoformat()


class EidosDatasource(EidosData):
    """Convenience class to create Eidos :class:`eidos.Datasource` from python data objects. Use these objects in the root level data field of the Eidos spec.

    Args:
        id (str): The ID of the datasource.
        data (DataFrame, GeoDataFrame, Dataset, OceanQL Query): The data to be used for the datasource.
        coordkeys (dict): The coordinate keys for the data. Default is empty dict.

    Raises:
        EidosError: If an invalid inline data type is provided.

    """

    def __init__(self, id, data, coordkeys={}):
        if isinstance(data, GeoDataFrame):
            data = data.__geo_interface__
            data["coordkeys"] = {**coordkeys, "g": "geometry"}
            dstype = "geojson"
        elif isinstance(data, DataFrame):
            data = data.to_xarray()
            dstype = "dataset"
        elif isinstance(data, Dataset):
            dstype = "dataset"
        elif isinstance(data, Query):
            dstype = "oceanumDatamesh"
        else:
            raise EidosError("Invalid inline data type")
        if dstype == "dataset":
            rename = {v: re.sub(r"[^a-zA-Z0-9_]", "_", v) for v in data.variables}
            _data = data.rename(rename)
            data = {
                "attributes": _data.attrs,
                "dimensions": dict(_data.sizes),
                "coordkeys": coordkeys,
            }
            data["variables"] = {}
            for v in _data.variables:
                dtype = str(_data.variables[v].dtype)
                values = _data.variables[v].to_dict()["data"]
                if dtype == "object":
                    if len(_data.variables[v].dims) > 1:
                        raise EidosError(
                            "Multi-dimensional object variables not supported"
                        )
                    values = [str(x) for x in values]
                    dtype = "string"
                data["variables"][v] = {
                    "data": values,
                    "dimensions": _data.variables[v].dims,
                    "attributes": _data.variables[v].attrs,
                    "dtype": dtype,
                }
            if "t" in coordkeys:  # Sanitize time data to iso8601 strings
                if coordkeys["t"] in data["variables"]:
                    data["variables"][coordkeys["t"]]["data"] = [
                        isotime(x) for x in data["variables"][coordkeys["t"]]["data"]
                    ]
                    data["variables"][coordkeys["t"]]["dtype"] = "string"

        super().__init__(id=id, dataType=dstype, dataSpec=data)


class EidosChart(TopLevelSpec):
    """Convenience class to create :class:`eidos.TopLevelSpec` for a :class:`eidos.PlotView` node from Altair Chart. Use this object for the plotSpec field.
    To use one of the defined EIDOS datasources in the Altair Chart, use a :class:`altair.NamedData` object with the id of the :class:`eidos.Datasource`.

    Args:
        chart (altair.Chart): The Altair Chart to be used for the plot.
    Raises:
        EidosError: If an invalid chart type is provided.
    """

    def __init__(self, chart):
        if not isinstance(chart, altair.Chart):
            raise EidosError("Invalid chart type - must be an Altair Chart object")
        super().__init__(chart)

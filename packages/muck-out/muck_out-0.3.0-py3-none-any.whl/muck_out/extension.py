from cattle_grid.extensions import Extension

from . import normalize_data

extension = Extension(name="muck out", module=__name__)


@extension.transform(inputs=["raw"], outputs=["parsed"])
async def muck_out(data: dict):
    return {"parsed": normalize_data(data["raw"]).model_dump(by_alias=True)}

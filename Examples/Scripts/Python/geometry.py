#!/usr/bin/env python3
import os
from common import getOpenDataDetectorDirectory
from acts.examples.odd import getOpenDataDetector
from acts.examples import (
    GenericDetector,
    AlignedDetector,
    WhiteBoard,
    AlgorithmContext,
    ProcessCode,
    CsvTrackingGeometryWriter,
    ObjTrackingGeometryWriter,
    JsonSurfacesWriter,
    JsonMaterialWriter,
    JsonFormat,
)

import acts

from acts import MaterialMapJsonConverter

u = acts.UnitConstants

def runGeometry(
    trackingGeometry,
    decorators,
    outputDir,
    events=1,
    outputObj=False,
    outputCsv=False,
    outputJson=True,
    outputRoot=False,
):

    for ievt in range(events):
        eventStore = WhiteBoard(name=f"EventStore#{ievt}", level=acts.logging.INFO)
        ialg = 0

        context = AlgorithmContext(ialg, ievt, eventStore)

        for cdr in decorators:
            r = cdr.decorate(context)
            if r != ProcessCode.SUCCESS:
                raise RuntimeError("Failed to decorate event context")

        if outputCsv:
            writer = CsvTrackingGeometryWriter(
                level=acts.logging.INFO,
                trackingGeometry=trackingGeometry,
                outputDir=os.path.join(outputDir, "csv"),
                writePerEvent=True,
            )
            writer.write(context)

        if outputObj:
            writer = ObjTrackingGeometryWriter(
                level=acts.logging.INFO, outputDir=os.path.join(outputDir, "obj")
            )
            writer.write(context, trackingGeometry)

        if outputJson:
            writer = JsonSurfacesWriter(
                level=acts.logging.INFO,
                trackingGeometry=trackingGeometry,
                outputDir=os.path.join(outputDir, "json"),
                writePerEvent=True,
                writeSensitive=True,
            )
            writer.write(context)

            jmConverterCfg = MaterialMapJsonConverter.Config(
                processSensitives=True,
                processApproaches=True,
                processRepresenting=True,
                processBoundaries=True,
                processVolumes=True,
                processNonMaterial=True,
                context=context.geoContext,
            )

            jmw = JsonMaterialWriter(
                level=acts.logging.VERBOSE,
                converterCfg=jmConverterCfg,
                fileName=os.path.join(outputDir, "geometry-map"),
                writeFormat=JsonFormat.Json,
            )

            jmw.write(trackingGeometry)


if "__main__" == __name__:
    # detector, trackingGeometry, decorators = AlignedDetector.create()
    # detector, trackingGeometry, decorators = GenericDetector.create()
    # detector, trackingGeometry, decorators = getOpenDataDetector(getOpenDataDetectorDirectory())
    detector, trackingGeometry, decorators = acts.examples.TelescopeDetector.create(
        positions=[7.905, 22.905, 38.905, 53.905, 89.905, 180.405],
        stereos=[-0.05, 0.05, -0.05, 0.05, -0.05, 0.05],
        offsets=[0, 0],
        bounds=[255, 255],
        thickness=0.15 * u.mm,
        surfaceType=0,  # 0 for plane surface or 1 for disc surface.
        binValue=2,
    )

    runGeometry(trackingGeometry, decorators,
                # outputDir=os.getcwd()
                outputDir="/lustre/collider/zhangjunhua/Software/acts/source/Examples/Scripts/Python/x.json"
                )

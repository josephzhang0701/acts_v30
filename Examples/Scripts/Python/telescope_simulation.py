#!/usr/bin/env python3

from pathlib import Path

import acts
import acts.examples
from acts.examples.simulation import (
    addParticleGun,
    EtaConfig,
    PhiConfig,
    ParticleConfig,
    addFatras,
    addGeant4,
)

u = acts.UnitConstants

if "__main__" == __name__:
    detector, trackingGeometry, decorators = acts.examples.TelescopeDetector.create(
        bounds=[2000, 2000],
        positions=[0, 130, 260, 390, 520, 650],
		stereos=[0.05 * u.rad] * 6,
        binValue=2,
    )

    field = acts.ConstantBField(acts.Vector3(0, 4 * u.T, 0))

    outputDir = Path.cwd() / "telescope_simulation"
    if not outputDir.exists():
        outputDir.mkdir()

    for geant, postfix in [(False, "fatras")]:
        rnd = acts.examples.RandomNumbers(seed=42)

        s = acts.examples.Sequencer(events=100, numThreads=-1, logLevel=acts.logging.INFO)

        addParticleGun(
            s,
            EtaConfig(10.0, 10.1),
            PhiConfig(0.0, 360.0 * u.degree),
            ParticleConfig(2, acts.PdgParticle.eElectron, False),
            multiplicity=1,
            rnd=rnd,
            outputDirRoot=outputDir / postfix,
        )

        if geant:
            addGeant4(
                s,
                detector,
                trackingGeometry,
                field,
                rnd=rnd,
                outputDirRoot=outputDir / postfix,
                outputDirCsv=outputDir / postfix,
                logLevel=acts.logging.VERBOSE,
            )
        else:
            addFatras(
                s,
                trackingGeometry,
                field,
                rnd=rnd,
                outputDirRoot=outputDir / postfix,
                outputDirCsv=outputDir / postfix,
            )

        s.run()

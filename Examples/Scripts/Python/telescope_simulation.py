#!/usr/bin/env python3

from pathlib import Path

import acts
import acts.examples
from acts.examples.simulation import (
    addParticleGun,
    MomentumConfig,
    EtaConfig,
    PhiConfig,
    ParticleConfig,
    addFatras,
    addGeant4,
)

u = acts.UnitConstants

if "__main__" == __name__:
    detector, trackingGeometry, decorators = acts.examples.TelescopeDetector.create(
        # bounds=[268, 268],
        # positions=[5.33, 10.33, 15.33, 20.33, 55.33, 125.33, 235.33],
        # stereos=[-0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05],
        bounds=[200, 200],
        positions=[7.73, 22.73, 38.73, 53.73, 89.73, 180.23],
        stereos=[-0.05, 0.05, -0.05, 0.05,-0.05, 0.05],
        binValue=2,
    )

    field = acts.ConstantBField(acts.Vector3(0, -1.5 * u.T, 0))
    vertex_generator = acts.examples.GaussianVertexGenerator(
        mean=acts.Vector4(0, 0, -1, 0),
        stddev=acts.Vector4(15, 15, 0, 0),  # 你可以设置适当的均值和标准差
    )
    outputDir = Path.cwd()
    # if not outputDir.exists():
    #     outputDir.mkdir()

    for geant, postfix in [(False, "fatras")]:
        rnd = acts.examples.RandomNumbers(seed=42)

        s = acts.examples.Sequencer(events=500, numThreads=-1, logLevel=acts.logging.INFO)

        addParticleGun(
            s,
            MomentumConfig(7.999 * u.GeV, 8.001 * u.GeV),
            EtaConfig(5.0, 6.0),
            PhiConfig(0.0, 360.0 * u.degree),
            ParticleConfig(1, acts.PdgParticle.eElectron, False),
            multiplicity=1,
            rnd=rnd,
            vtxGen=vertex_generator,
            outputDirRoot=outputDir,
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
                outputDirRoot=outputDir,
                # outputDirCsv=outputDir / postfix,
            )

        s.run()

#!/usr/bin/env python3

from pathlib import Path

import acts
import acts.examples

import math

from truth_tracking_kalman import runTruthTrackingKalman

from acts.examples.reconstruction import (
    addSeeding,
    SeedingAlgorithm,
    TruthSeedRanges,
    addKalmanTracks,
)

u = acts.UnitConstants

if "__main__" == __name__:
    detector, trackingGeometry, decorators = acts.examples.TelescopeDetector.create(
        bounds=[251, 251],
        positions=[5.33, 10.33, 15.33, 20.33, 55.33, 125.33, 235.33],
        stereos=[-0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05],
        binValue=2,
    )

    srcdir = Path(__file__).resolve().parent.parent.parent.parent

    field = acts.ConstantBField(acts.Vector3(0, -1.5 * u.T, 0))

    outputDir = Path.cwd() / "Nov28telescope_simulation"
    if not outputDir.exists():
        outputDir.mkdir()

    ##rnd = acts.examples.RandomNumbers(seed=42)
    from acts.examples import (
        RootSimHitReader,
        RootParticleReader,
    )
    s = acts.examples.Sequencer(
        numThreads=-1, logLevel=acts.logging.INFO
    )
    s.addReader(
        RootSimHitReader(
            level=acts.logging.INFO,
            # filePath="Nov14Reco/dp_hits.root",
            filePath="Nov28telescope_simulation/hits.root",
            treeName="hits",
            simHitCollection="simhits",
        )
    )
    s.addReader(
        RootParticleReader(
            level=acts.logging.INFO,
            # filePath="Nov14Reco/dp_particles.root",
            filePath="Nov28telescope_simulation/particles.root",
            particleCollection="particles",
            orderedEvents=False,
        )
    )

    seedingConfig = {
        "algorithm": SeedingAlgorithm.TruthSmeared,
        "pt": (100 * u.MeV, None),
        "nHits": (7, None),
        "eta": (0, 7.0),
        "rho": (0, 380 * u.mm),
        "z": (0, 240 * u.mm),
        "phi": (-math.pi, math.pi),
    }


    runTruthTrackingKalman(
        seedingConfig,
        trackingGeometry,
        field,
        digiConfigFile=srcdir
                       / "Examples/Algorithms/Digitization/share/default-smearing-config-telescope.json",
        # outputDir=Path.cwd(),
        outputDir=outputDir,
        s=s,
        inputParticlePath=srcdir
                          / "Examples/Scripts/Python/Nov28telescope_simulation/particles.root",
                          # / "Examples/Scripts/Python/Nov14Reco/dp_particles.root"
    ).run()

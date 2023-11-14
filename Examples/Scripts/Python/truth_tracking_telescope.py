#!/usr/bin/env python3

from pathlib import Path

import math
import acts
import acts.examples

from truth_tracking_kalman import runTruthTrackingKalman

u = acts.UnitConstants

if "__main__" == __name__:
    detector, trackingGeometry, decorators = acts.examples.TelescopeDetector.create(
        bounds=[268, 268],
        positions=[5.33, 10.33, 15.33, 20.33, 55.33, 125.33, 235.33],
        stereos=[-0.05, 0.05, -0.05, 0.05,-0.05, 0.05, -0.05],
    )

    srcdir = Path(__file__).resolve().parent.parent.parent.parent

    field = acts.ConstantBField(acts.Vector3(0, -1.5 * u.T, 0))

    rnd = acts.examples.RandomNumbers()

    from acts.examples import (
        RootSimHitReader,
        RootParticleReader,
    )

    from acts.examples.reconstruction import (
        addSeeding,
        SeedingAlgorithm,
        TruthSeedRanges,
        addKalmanTracks,
    )

    s = acts.examples.Sequencer(
        numThreads=-1, logLevel=acts.logging.INFO
    )

    s.addReader(
        RootSimHitReader(
            level=acts.logging.INFO,
            filePath="Nov14Reco/dp_hits.root",
            treeName="hits",
            simHitCollection="simhits",
        )
    )
    s.addReader(
        RootParticleReader(
            level=acts.logging.INFO,
            filePath="Nov14Reco/dp_particles.root",
            particleCollection="particles",
            orderedEvents=False,
        )
    )

    addSeeding(
        trackingGeometry,
        field,
        seedingAlgorithm=SeedingAlgorithm.TruthSmeared,
        rnd=rnd,
        truthSeedRanges=TruthSeedRanges(
            pt=(20 * u.MeV, None),
            nHits=(4, None),
            eta=(-15.0, 15.0),
            rho=(0, 1000 * u.mm),
            z=(0, 300 * u.mm),
            phi=(-math.pi, math.pi),
        ),
    )

    runTruthTrackingKalman(
        trackingGeometry,
        field,
        digiConfigFile=srcdir
                       / "Examples/Algorithms/Digitization/share/default-smearing-config-telescope.json",
        outputDir=srcdir / "Nov14Reco",
        s=s,
        inputParticlePath=srcdir / "Nov14Reco/dp_particles.root"
    ).run()

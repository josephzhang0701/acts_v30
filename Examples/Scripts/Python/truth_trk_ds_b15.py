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
    addAmbiguityResolution,
    AmbiguityResolutionConfig,
)

u = acts.UnitConstants

if "__main__" == __name__:
    detector, trackingGeometry, decorators = acts.examples.TelescopeDetector.create(
        # positions=[-607.7550, -507.7550, -407.7550, -307.7550, -207.7550, -107.7550, -7.7550],
        # stereos=[0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05],
        positions=[7.905, 22.905, 38.905, 53.905, 89.905, 180.405],
        stereos=[-0.05, 0.05, -0.05, 0.05, -0.05, 0.05],
        offsets=[0, 0],
        bounds=[255, 255],
        thickness=0.15 * u.mm,
        surfaceType=0,  # 0 for plane surface, 1 for disc surface.
        binValue=0, # 0: along x-axis, 1y, 2z
    )

    srcdir = Path(__file__).resolve().parent.parent.parent.parent       # print(srcdir)     # is /lustre/collider/zhangjunhua/Software/acts/source

    field = acts.ConstantBField(acts.Vector3(0, 0, 1.5 * u.T))

    inputDir = Path("/lustre/collider/zhangjunhua/Software/acts/run/TruthSeedJan17/rotateCoord")
    outputDir = Path("/lustre/collider/zhangjunhua/Software/acts/run/TruthSeedJan17/rotateCoord/2GeV")
    flpt = inputDir / Path("rcl_2GeV_Mar7Particles.root")
    # outputDir = Path.cwd() / "Nov28telescope_simulation"

    if not outputDir.exists():
        outputDir.mkdir()

    ##rnd = acts.examples.RandomNumbers(seed=42)
    from acts.examples import (
        RootSimHitReader,
        RootParticleReader,
    )
    s = acts.examples.Sequencer(
        events=15000,
        numThreads=1, logLevel=acts.logging.INFO
    )
    s.addReader(
        RootSimHitReader(
            level=acts.logging.INFO,
            filePath=inputDir / "rcl_2GeV_Mar7Hits.root",
            treeName="hits",
            simHitCollection="simhits",
        )
    )
    s.addReader(
        RootParticleReader(
            level=acts.logging.INFO,
            filePath=flpt,
            particleCollection="particles",
            orderedEvents=False,
        )
    )

    seedingConfig = {
        "algorithm": SeedingAlgorithm.TruthSmeared,
        "pt": (0.0 * u.keV, None),
        "nHits": (3, 100),
        "eta": (-7.0, 7.0),
        "rho": (-10.0 * u.m, 10.0 * u.m),
        "z": (-10.0 * u.m, 10.0 * u.m),
        "phi": (-math.pi, math.pi),
    }

    particleSmearingSigmasConfig = {
        "d0": 0.01 * u.mm,
        "d0PtA": 0.001 * u.mm,
        "d0PtB": 0.001,
        "z0": 0.01 * u.mm,
        "z0PtA": 0.001,
        "z0PtB": 0.001,
        "t0": 0,
        "phi": 0.005 * u.degree,
        "theta": 0.005 * u.degree,
        "pRel": 0.02,
    }

    runTruthTrackingKalman(
        seedingConfig,
        particleSmearingSigmasConfig,
        trackingGeometry,
        field,
        digiConfigFile=srcdir / "Examples/Algorithms/Digitization/share/default-smearing-config-telescope.json",
        outputDir=outputDir,
        directNavigation=False,
        reverseFilteringMomThreshold=0 * u.MeV,
        s=s,
        inputParticlePath=flpt,
    ).run()

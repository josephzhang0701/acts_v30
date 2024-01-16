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
        # positions=[-607.73, -507.73, -407.73, -307.73, -207.73, -107.73, -7.73],
        # stereos=[0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05],
        positions=[7.905, 22.905, 38.905, 53.905, 89.905, 180.405],
        stereos=[-0.05, 0.05, -0.05, 0.05, -0.05, 0.05],
        offsets=[0, 0],
        bounds=[255, 255],
        thickness=0.15 * u.mm,
        surfaceType=0,  # 0 for plane surface or 1 for disc surface.
        binValue=2,
    )

    srcdir = Path(__file__).resolve().parent.parent.parent.parent       # print(srcdir)     # is /lustre/collider/zhangjunhua/Software/acts/source

    field = acts.ConstantBField(acts.Vector3(0, -1.5 * u.T, 0))

    outputDir = Path("/lustre/collider/zhangjunhua/Software/acts/run/Jan_2_DS15e3")
    # outputDir = Path.cwd() / "Nov28telescope_simulation"
    # if not outputDir.exists():
    #     outputDir.mkdir()

    ##rnd = acts.examples.RandomNumbers(seed=42)
    from acts.examples import (
        RootSimHitReader,
        RootParticleReader,
    )
    s = acts.examples.Sequencer(
        # events=1000,
        numThreads=1, logLevel=acts.logging.INFO
    )
    s.addReader(
        RootSimHitReader(
            level=acts.logging.INFO,
            filePath=outputDir / "trk1X_DigY_hits.root",
            treeName="hits",
            simHitCollection="simhits",
        )
    )
    s.addReader(
        RootParticleReader(
            level=acts.logging.INFO,
            filePath=outputDir / "Jan09_particles.root",
            particleCollection="particles",
            orderedEvents=False,
        )
    )

    seedingConfig = {
        "algorithm": SeedingAlgorithm.Default,
        "pt": (30 * u.keV, None),
        "nHits": (3, None),
        "eta": (-7.0, 7.0),
        "rho": (0 * u.mm, 400 * u.mm),
        "z": (0, 200 * u.mm),
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
        inputParticlePath=outputDir / "Jan09_particles.root",
    ).run()

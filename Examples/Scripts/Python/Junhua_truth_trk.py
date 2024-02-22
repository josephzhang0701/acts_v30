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
        positions=[-607.7550, -507.7550, -407.7550, -307.7550, -207.7550, -107.7550, -7.7550],
        stereos=[0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05],
        offsets=[0, 0],
        bounds=[255, 255],
        thickness=0.15 * u.mm,
        surfaceType=0,  # 0 for plane surface or 1 for disc surface.
        binValue=2,
    )

    srcdir = Path(__file__).resolve().parent.parent.parent.parent       # print(srcdir)     # is /lustre/collider/zhangjunhua/Software/acts/source

    field = acts.ConstantBField(acts.Vector3(0, -1.5 * u.T, 0))

##########
    inputDir = Path("/lustre/collider/zhangjunhua/Software/acts/run/TruthSeedJan17")
    outputDir = Path("") #you can define

    if not outputDir.exists():
        outputDir.mkdir()

    ##rnd = acts.examples.RandomNumbers(seed=42)
    from acts.examples import (
        RootSimHitReader,
        RootParticleReader,
    )
    s = acts.examples.Sequencer(
        events=100,
        numThreads=1, logLevel=acts.logging.INFO
    )
    s.addReader(
        RootSimHitReader(
            level=acts.logging.INFO,
            filePath=inputDir / "dp_tag_hits.root",
            treeName="hits",
            simHitCollection="simhits",
        )
    )
    s.addReader(
        RootParticleReader(
            level=acts.logging.INFO,
            #filePath=inputDir / "tag_ptl_28MeV/dp_tag_particles.root", #px, py, pT are in unit of MeV
            filePath=inputDir / "tag_jan23/GeV_dp_tag_ptl.root", #px, py, pT are in unit of GeV
            particleCollection="particles",
            orderedEvents=False,
        )
    )

    seedingConfig = {
        "algorithm": SeedingAlgorithm.TruthSmeared,
        "pt": (0.0 * u.keV, 4.0 * u.GeV),
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
        #inputParticlePath=inputDir / "tag_ptl_28MeV/dp_tag_particles.root", #px, py, pT are in unit of MeV
        inputParticlePath=inputDir / "tag_jan23/GeV_dp_tag_ptl.root", #px, py, pT are in unit of GeV
    ).run()

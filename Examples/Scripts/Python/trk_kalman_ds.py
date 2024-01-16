#!/usr/bin/env python3

from pathlib import Path
from typing import Optional

import acts
import acts.examples
import math

from acts.examples.simulation import addDigitization

from acts.examples.reconstruction import (
    addSeeding,
    SeedingAlgorithm,
    addKalmanTracks,
    addAmbiguityResolution,
    AmbiguityResolutionConfig,
    addStandardSeeding,
    SeedFinderConfigArg,
    SeedFinderOptionsArg,
    SeedFilterConfigArg,
    SpacePointGridConfigArg,
    SeedingAlgorithmConfigArg,
    TrackSelectorConfig,
)

u = acts.UnitConstants

def runKalmanTrk(
    trackingGeometry: acts.TrackingGeometry,
    field: acts.MagneticFieldProvider,
    geoSelectionConfigFile: Path,
    outputDir: Path,
    digiConfigFile: Path,
    directNavigation=False,
    reverseFilteringMomThreshold=0 * u.MeV,
    s: acts.examples.Sequencer = None,
    inputParticlePath=None,
):

    s = s or acts.examples.Sequencer(
        events=10, numThreads=1, logLevel=acts.logging.DEBUG
    )

    rnd = acts.examples.RandomNumbers(seed=42)

    outputDir = Path(outputDir)

    s.addReader(
        acts.examples.RootSimHitReader(
            level=acts.logging.INFO,
            filePath=outputDir / "trk1X_DigY_hits.root",
            treeName="hits",
            simHitCollection="simhits",
        )
    )

    s.addReader(
        acts.examples.RootParticleReader(
            level=acts.logging.INFO,
            filePath=str(inputParticlePath.resolve()),
            particleCollection="particles_input",
            orderedEvents=False,
        )
    )

    addDigitization(
        s,
        trackingGeometry,
        field,
        digiConfigFile=digiConfigFile,
        rnd=rnd,
    )

    # variables that do not change for strip SPs:# 不知道怎么写的参数一律写9um
    rMax=350 * u.mm
    deltaRMax = 350 * u.mm
    impactMax=9 * u.um      #It has to be: rMin > impactMax
    deltaRMin=9 * u.um

    allowSeparateRMax = True
    # zBinNeighborsTop=
    # zBinNeighborsBottom=
    numPhiNeighbors=1

    # Run the seeding algorithm
    addSeeding(
        s,
        # spacePoints="spacepoints",
        trackingGeometry,
        field,
        geoSelectionConfigFile=geoSelectionConfigFile,
        seedingAlgorithm=SeedingAlgorithm.Default,
        seedFinderConfigArg=SeedFinderConfigArg(
            maxSeedsPerSpM=10,   # for how many seeds can one SpacePoint be the middle SpacePoint?
            cotThetaMax=10000,
            sigmaScattering=5, # how many sigmas of scattering angle should be considered?
            radLengthPerSeed=0.01, # average radiation lengths of material on the length of a seed. used for scattering
            minPt=80 * u.MeV,
            impactMax=impactMax,
            rRangeMiddleSP=[[9 * u.um, 350 * u.mm]],
            deltaR=(deltaRMin, deltaRMax),
            collisionRegion=(0 * u.mm, 200 * u.mm), # limiting location of collision region in z
            r=(None, rMax),  # rMin=default, 33mm
            z=(0 * u.mm, 200 * u.mm),
            #deltaRMiddleMinSPRange  #deltaRMiddleMaxSPRange
        ),  # Set SeedFinderConfigArg parameters

        seedFinderOptionsArg=SeedFinderOptionsArg(
            bFieldInZ=1.5 * u.T,
        ),  # Set SeedFinderOptionsArg parameters

        seedFilterConfigArg=SeedFilterConfigArg(
            deltaRMin=deltaRMin,
            #SeedFilterConfigArg( compatSeedWeight, compatSeedLimit, numSeedIncrement,
                                # seedWeightIncrement, seedConfirmation, maxSeedsPerSpMConf,
                                # maxQualitySeedsPerSpMConf, useDeltaRorTopRadius)
            #Defaults specified in Core/include/Acts/Seeding/SeedFilterConfig.hpp
        ),
        spacePointGridConfigArg=SpacePointGridConfigArg(
            # SpacePointGridConfigArg(rMax, zBinEdges, phiBinDeflectionCoverage, phi, maxPhiBins, impactMax)
            rMax=rMax,
            phiBinDeflectionCoverage=2,
            deltaRMax=deltaRMax,
            impactMax=impactMax,
        ),
            # Defaults specified in Core/include/Acts/Seeding/SpacePointGrid.hpp
        seedingAlgorithmConfigArg=SeedingAlgorithmConfigArg(
            allowSeparateRMax=allowSeparateRMax,
            # zBinNeighborsTop=zBinNeighborsTop,
            # zBinNeighborsBottom=zBinNeighborsBottom,
            numPhiNeighbors=numPhiNeighbors,
        ),
            # SeedingAlgorithmConfigArg(allowSeparateRMax, zBinNeighborsTop, zBinNeighborsBottom, numPhiNeighbors)
            # Defaults specified in Examples/Algorithms/TrackFinding/include/ActsExamples/TrackFinding/SeedingAlgorithm.hpp
        # outputDirRoot=outputDir,
    )

    addKalmanTracks(
        s,
        trackingGeometry,
        field,
        directNavigation,
        reverseFilteringMomThreshold,
        inputProtoTracks="seed-prototracks",
    )

    # addAmbiguityResolution(
    #     s,
    #     AmbiguityResolutionConfig(
    #         maximumSharedHits=2,
    #         nMeasurementsMin=3,
    #         maximumIterations=1000,
    #     ),
    # )

    # Output
    s.addWriter(
        acts.examples.RootTrajectoryStatesWriter(
            level=acts.logging.INFO,
            inputTrajectories="trajectories",
            inputParticles="particles_input",
            inputSimHits="simhits",
            inputMeasurementParticlesMap="measurement_particles_map",
            inputMeasurementSimHitsMap="measurement_simhits_map",
            filePath=str(outputDir / "stdSeed_trackstates_fitter.root"),
        )
    )

    s.addWriter(
        acts.examples.RootTrajectorySummaryWriter(
            level=acts.logging.INFO,
            inputTrajectories="trajectories",
            inputParticles="particles_input",
            inputMeasurementParticlesMap="measurement_particles_map",
            filePath=str(outputDir / "stdSeed_tracksummary_fitter.root"),
        )
    )

    return s


if "__main__" == __name__:
    detector, trackingGeometry, decorators = acts.examples.TelescopeDetector.create(
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
    outputDir=Path("/lustre/collider/zhangjunhua/Software/acts/run/Jan12DefaultSeed")

    runKalmanTrk(
        trackingGeometry,
        field,
        geoSelectionConfigFile=srcdir / "Examples/Scripts/Python/geoSelection-telescope.json",
        digiConfigFile=srcdir / "Examples/Algorithms/Digitization/share/default-smearing-config-telescope.json",
        outputDir=outputDir,
        directNavigation=True,
        reverseFilteringMomThreshold=0 * u.MeV,
        inputParticlePath=outputDir / "Jan09_particles.root",
    ).run()

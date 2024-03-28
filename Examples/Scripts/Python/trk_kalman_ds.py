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
    inputParticlePath: Optional[Path] = None,
):

    s = s or acts.examples.Sequencer(
        events=10, numThreads=1, logLevel=acts.logging.INFO
    )

    rnd = acts.examples.RandomNumbers(seed=42)

    outputDir = Path(outputDir)

    s.addReader(
        acts.examples.RootSimHitReader(
            level=acts.logging.INFO,
            # filePath=inputDir / "rcl_8GeV_Mar7Hits.root",
            filePath=inputDir / "ATLAS_tag_hits.root",
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
        logLevel=acts.logging.DEBUG
    )

    # variables that do not change for strip SPs:
    rMin=0 * u.mm
    rMax=620.00 * u.mm
    deltaRMin=1 * u.mm
    deltaRMax=150 * u.mm
    zMin=-10 * u.mm
    zMax=10 * u.mm
    impactMax=200.0 * u.mm
    rRangeMiddleSP=[[0 * u.mm, 230 * u.mm], [0 * u.mm, 230 * u.mm],
                    [0 * u.mm, 230 * u.mm], [0 * u.mm, 230 * u.mm],
                    [0 * u.mm, 230 * u.mm], [0 * u.mm, 230 * u.mm],
                    [0 * u.mm, 230 * u.mm], [0 * u.mm, 230 * u.mm],
                    [0 * u.mm, 230 * u.mm], [0 * u.mm, 230 * u.mm],
                    [0 * u.mm, 230 * u.mm], [0 * u.mm, 230 * u.mm],
                    [0 * u.mm, 230 * u.mm], [0 * u.mm, 230 * u.mm]]
    zBinEdges=[-10.0, -2.5,
               -1.0, -0.6, -0.4, -0.2, -0.1,
               0.0,
               0.1, 0.2, 0.4, 0.6, 1.0,
               2.5, 10.0]
    deltaRMiddleMinSPRange = 10 * u.mm
    deltaRMiddleMaxSPRange = 10 * u.mm
    seedConfirmation=True

    # Run the seeding algorithm
    addSeeding(
        s,
        trackingGeometry,
        field,
        acts.logging.VERBOSE,
        geoSelectionConfigFile=geoSelectionConfigFile,
        seedingAlgorithm=SeedingAlgorithm.Default,
        truthSeedRanges=None,
        seedFinderConfigArg=SeedFinderConfigArg(
            # SeedFinderConfigArg(maxSeedsPerSpM, cotThetaMax, sigmaScattering, radLengthPerSeed, minPt,
            #       impactMax, deltaPhiMax, interactionPointCut, deltaZMax, maxPtScattering, zBinEdges, zBinsCustomLooping, rRangeMiddleSP,
            #       useVariableMiddleSPRange, binSizeR, seedConfirmation, centralSeedConfirmationRange, forwardSeedConfirmationRange,
            #       deltaR, deltaRBottomSP, deltaRTopSP, deltaRMiddleSPRange, collisionRegion, r, z, zOutermostLayers)
            #   Defaults specified in Examples/Algorithms/TrackFinding/include/ActsExamples/TrackFinding/TrackParamsEstimationAlgorithm.hpp

            # SeedFinderConfigArg(maxSeedsPerSpM, cotThetaMax, sigmaScattering, radLengthPerSeed, minPt,
            #       impactMax, deltaPhiMax, interactionPointCut, deltaZMax, maxPtScattering, zBinEdges, zBinsCustomLooping,
            #       skipZMiddleBinSearch, rRangeMiddleSP, useVariableMiddleSPRange, binSizeR, seedConfirmation,
            #       centralSeedConfirmationRange, forwardSeedConfirmationRange, deltaR, deltaRBottomSP, deltaRTopSP,
            #       deltaRMiddleSPRange, collisionRegion, r, z, zOutermostLayers)
            #   SeedFinderConfig settings. deltaR, deltaRBottomSP, deltaRTopSP, deltaRMiddleSPRange, collisionRegion,
            #       r, z, zOutermostLayers are ranges specified as a tuple of (min,max). beamPos is specified as (x,y).
            #       Defaults specified in Core/include/Acts/Seeding/SeedFinderConfig.hpp
            maxSeedsPerSpM=1,   # for how many seeds can one SpacePoint be the middle SpacePoint?
            cotThetaMax=100,
            sigmaScattering=3, # how many sigmas of scattering angle should be considered?
            radLengthPerSeed=0.1, # average radiation lengths of material on the length of a seed. used for scattering
            minPt=150 * u.MeV,
            impactMax=impactMax,
            rRangeMiddleSP=rRangeMiddleSP,
            deltaR=(deltaRMin, deltaRMax),
            collisionRegion=(zMin/5, zMax/5), # limiting location of collision region in z
            r=(rMin, rMax),
            z=(zMin, zMax),
            deltaRMiddleSPRange=(deltaRMiddleMinSPRange, deltaRMiddleMaxSPRange),
            binSizeR=0.01 * u.mm,
            deltaZMax=5 * u.m,
            useVariableMiddleSPRange=False,
            deltaRBottomSP=(deltaRMin, deltaRMax),
            deltaRTopSP=(deltaRMin, deltaRMax),
            zOutermostLayers=(-150 * u.mm, 150 * u.mm),
            interactionPointCut=True,
            maxPtScattering = float("inf") * u.GeV,

        ),  # Set SeedFinderConfigArg parameters

        seedFinderOptionsArg=SeedFinderOptionsArg(
            bFieldInZ=1.5 * u.T, beamPos=(0.0, 0.0)
            # Set SeedFinderOptionsArg parameters
        ),

        seedFilterConfigArg=SeedFilterConfigArg(
            impactWeightFactor=100,
            zOriginWeightFactor=None,
            compatSeedWeight=None,
            compatSeedLimit=3,
            numSeedIncrement=100,
            seedWeightIncrement=0,
            seedConfirmation=seedConfirmation,
            maxSeedsPerSpMConf=5,
            maxQualitySeedsPerSpMConf=5,
            useDeltaRorTopRadius=True,
        ),
        # seedFilterConfigArg : SeedFilterConfigArg(compatSeedWeight, compatSeedLimit, numSeedIncrement,
        #     seedWeightIncrement, seedConfirmation, maxSeedsPerSpMConf, maxQualitySeedsPerSpMConf, useDeltaRorTopRadius)
        # Defaults specified in Core/include/Acts/Seeding/SeedFilterConfig.hpp

        # SpacePointGridConfigArg(rMax, zBinEdges, phiBinDeflectionCoverage, phi, maxPhiBins, impactMax)
            # Defaults specified in Core/include/Acts/Seeding/SpacePointGrid.hpp
        spacePointGridConfigArg = SpacePointGridConfigArg(
            rMax=rMax,
            deltaRMax=deltaRMax,
            zBinEdges=zBinEdges,
            phiBinDeflectionCoverage=10,
            phi=(-0.5 * math.pi, 0.5 * math.pi),
            # impactMax=impactMax,
            maxPhiBins=300,
        ),

        # SeedingAlgorithmConfigArg(allowSeparateRMax, zBinNeighborsTop, zBinNeighborsBottom, numPhiNeighbors)
            # Defaults specified in Examples/Algorithms/TrackFinding/include/ActsExamples/TrackFinding/SeedingAlgorithm.hpp
        seedingAlgorithmConfigArg = SeedingAlgorithmConfigArg(
            allowSeparateRMax=False,
            # zBinNeighborsTop=zBinNeighborsTop,
            # zBinNeighborsBottom=zBinNeighborsBottom,
            numPhiNeighbors=1,
        ),
        outputDirRoot=outputDir,
        inputParticles="particles_input",
    )

    addKalmanTracks(
        s,
        trackingGeometry,
        field,
        directNavigation,
        reverseFilteringMomThreshold,
        inputProtoTracks="seed-prototracks",
        logLevel=acts.logging.INFO,
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
            filePath=str(outputDir / "tagStdSeed_trackstates.root"),
        )
    )

    s.addWriter(
        acts.examples.RootTrajectorySummaryWriter(
            level=acts.logging.INFO,
            inputTrajectories="trajectories",
            inputParticles="particles_input",
            inputMeasurementParticlesMap="measurement_particles_map",
            filePath=str(outputDir / "tagStdSeed_tracksummary.root"),
        )
    )

    return s

if "__main__" == __name__:
    detector, trackingGeometry, decorators = acts.examples.TelescopeDetector.create(
        # positions=[7.905, 22.905, 38.905, 53.905, 89.905, 180.405],
        # stereos=[-0.05, 0.05, -0.05, 0.05, -0.05, 0.05],
        positions=[0, 100, 200, 300, 400, 500, 600],
        stereos=[0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05],
        offsets=[0, 0],
        bounds=[255, 255],
        thickness=0.15 * u.mm,
        surfaceType=0,  # 0 for plane surface, 1 for disc surface.
        binValue=0, # 0: along x-axis, 1y, 2z
    )

    srcdir = Path(__file__).resolve().parent.parent.parent.parent       # print(srcdir)     # is /lustre/collider/zhangjunhua/Software/acts/source
    field = acts.ConstantBField(acts.Vector3(0, 0, 1.5 * u.T))
    inputDir=Path("/lustre/collider/zhangjunhua/Software/acts/run/StdSeed_Rot")
    outputDir=Path("/lustre/collider/zhangjunhua/Software/acts/run/StdSeed_Rot/Mar28")
    if not outputDir.exists():
        outputDir.mkdir()

    runKalmanTrk(
        trackingGeometry,
        field,
        geoSelectionConfigFile=srcdir / "Examples/Scripts/Python/geoSelection-telescope.json",
        digiConfigFile=srcdir / "Examples/Algorithms/Digitization/share/default-smearing-config-telescope.json",
        outputDir=outputDir,
        directNavigation=True,
        reverseFilteringMomThreshold=1000 * u.MeV,
        inputParticlePath=inputDir / "rcl_8GeV_Mar18Particles.root",
    ).run()

#!/usr/bin/env python3

from pathlib import Path
from typing import Optional

import acts
import acts.examples

u = acts.UnitConstants

def runTruthTrackingKalman(
    seedingConfig: dict,
    particleSmearingSigmasConfig:dict,
    trackingGeometry: acts.TrackingGeometry,
    field: acts.MagneticFieldProvider,
    outputDir: Path,
    digiConfigFile: Path,
    directNavigation=False,
    reverseFilteringMomThreshold=0 * u.MeV,
    s: acts.examples.Sequencer = None,
    inputParticlePath: Optional[Path] = None,
):
    from acts.examples.simulation import (
        addParticleGun,
        EtaConfig,
        ParticleConfig,
        addFatras,
        addDigitization,
    )
    from acts.examples.reconstruction import (
        addSeeding,
        SeedingAlgorithm,
        TruthSeedRanges,
        addKalmanTracks,
        ParticleSmearingSigmas,
        SeedFinderConfigArg,
        SeedFinderOptionsArg,
        TruthEstimatedSeedingAlgorithmConfigArg,
        addAmbiguityResolution,
        AmbiguityResolutionConfig,
        addVertexFitting,
        VertexFinder,
        TrackSelectorConfig,
    )

    s = s or acts.examples.Sequencer(
        events=100, numThreads=-1, logLevel=acts.logging.INFO
    )

    rnd = acts.examples.RandomNumbers()
    outputDir = Path(outputDir)

    if inputParticlePath is None:
        addParticleGun(
            s,
            EtaConfig(-2.0, 2.0),
            ParticleConfig(2, acts.PdgParticle.eMuon, False),
            multiplicity=1,
            rnd=rnd,
            outputDirRoot=outputDir,
        )
    else:
        acts.logging.getLogger("Truth tracking example").info(
            "Reading particles from %s", inputParticlePath.resolve()
        )
        assert inputParticlePath.exists()
        s.addReader(
            acts.examples.RootParticleReader(
                level=acts.logging.INFO,
                filePath=str(inputParticlePath.resolve()),
                particleCollection="particles_input",
                orderedEvents=False,
            )
        )

    # addFatras(
    #     s,
    #     trackingGeometry,
    #     field,
    #     rnd=rnd,
    #     enableInteractions=True,
    # )

    addDigitization(
        s,
        trackingGeometry,
        field,
        digiConfigFile=digiConfigFile,
        rnd=rnd,
    )

    addSeeding(
        s,
        trackingGeometry,
        field,
        # seedingAlgorithm=SeedingAlgorithm.TruthSmeared,
        seedingAlgorithm=seedingConfig.get("algorithm", SeedingAlgorithm.TruthSmeared),
        rnd=rnd,
        particleSmearingSigmas=ParticleSmearingSigmas(
            d0=particleSmearingSigmasConfig.get("d0"),                             
            d0PtA=particleSmearingSigmasConfig.get("d0PtA", 0),                    
            d0PtB=particleSmearingSigmasConfig.get("d0PtB", 0),                    
            z0=particleSmearingSigmasConfig.get("z0"),                             
            z0PtA=particleSmearingSigmasConfig.get("z0PtA", 0),                    
            z0PtB=particleSmearingSigmasConfig.get("z0PtB", 0),                    
            t0=particleSmearingSigmasConfig.get("t0", 0),                          
            phi=particleSmearingSigmasConfig.get("phi"),                           
            theta=particleSmearingSigmasConfig.get("theta"),                       
            pRel=particleSmearingSigmasConfig.get("pRel"),                         
        ),
        truthSeedRanges=TruthSeedRanges(                 # truthSeedRanges=TruthSeedRanges(
            pt=seedingConfig.get("pt"),                  #     pt=(30 * u.MeV, None),
            nHits=seedingConfig.get("nHits"),            #     nHits=(6, None),
            eta=seedingConfig.get("eta"),                #     eta=(0, 7.0),
            rho=seedingConfig.get("rho"),                #     rho=(0, 380 * u.mm),
            z=seedingConfig.get("z"),                    #     z=(0, 290 * u.mm),
            phi=seedingConfig.get("phi")                 #     phi=(-math.pi, math.pi)
        ),                                               # ),
        logLevel=acts.logging.VERBOSE,
    )

    addKalmanTracks(
        s,
        trackingGeometry,
        field,
        directNavigation,
        reverseFilteringMomThreshold,
        logLevel=acts.logging.DEBUG,
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
            # inputParticles="truth_seeds_selected",
            inputParticles="particles_input",
            inputSimHits="simhits",
            inputMeasurementParticlesMap="measurement_particles_map",
            inputMeasurementSimHitsMap="measurement_simhits_map",
            filePath=str(outputDir / "trackstates_fitter.root"),
        )
    )

    s.addWriter(
        acts.examples.RootTrajectorySummaryWriter(
            level=acts.logging.INFO,
            inputTrajectories="trajectories",
            inputParticles="truth_seeds_selected",
            inputMeasurementParticlesMap="measurement_particles_map",
            filePath=str(outputDir / "tracksummary_fitter.root"),
        )
    )

    # s.addWriter(
    #     acts.examples.TrackFinderPerformanceWriter(
    #         level=acts.logging.INFO,
    #         inputProtoTracks="sorted_truth_particle_tracks"
    #         if directNavigation
    #         else "truth_particle_tracks",
    #         inputParticles="truth_seeds_selected",
    #         inputMeasurementParticlesMap="measurement_particles_map",
    #         filePath=str(outputDir / "performance_track_finder.root"),
    #     )
    # )
    #
    # s.addWriter(
    #     acts.examples.TrackFitterPerformanceWriter(
    #         level=acts.logging.INFO,
    #         inputTrajectories="trajectories",
    #         inputParticles="truth_seeds_selected",
    #         inputMeasurementParticlesMap="measurement_particles_map",
    #         filePath=str(outputDir / "performance_track_fitter.root"),
    #     )
    # )

    return s


if "__main__" == __name__:

    srcdir = Path(__file__).resolve().parent.parent.parent.parent

    # detector, trackingGeometry, _ = getOpenDataDetector()
    detector, trackingGeometry, decorators = acts.examples.GenericDetector.create()

    field = acts.ConstantBField(acts.Vector3(0, 0, 2 * u.T))

    runTruthTrackingKalman(
        trackingGeometry,
        field,
        digiConfigFile=srcdir
        / "Examples/Algorithms/Digitization/share/default-smearing-config-generic.json",
        # "thirdparty/OpenDataDetector/config/odd-digi-smearing-config.json",
        outputDir=Path.cwd(),
    ).run()

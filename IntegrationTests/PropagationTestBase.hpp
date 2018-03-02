// This file is part of the ACTS project.
//
// Copyright (C) 2017-2018 ACTS project team
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

// Boost include(s)
#define BOOST_TEST_MODULE Propagator Tests

#include <boost/test/included/unit_test.hpp>
// leave blank
#include <boost/test/data/test_case.hpp>
#include <cmath>

/// test consistency of forward-backward propagation
BOOST_DATA_TEST_CASE(
    forward_backward_propagation_,
    bdata::random((bdata::seed = 0,
                   bdata::distribution
                   = std::uniform_real_distribution<>(0.4 * units::_GeV,
                                                      10. * units::_GeV)))
        ^ bdata::random((bdata::seed = 1,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-M_PI, M_PI)))
        ^ bdata::random((bdata::seed = 2,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.1, M_PI - 0.1)))
        ^ bdata::random((bdata::seed = 3,
                         bdata::distribution
                         = std::uniform_int_distribution<>(0, 1)))
        ^ bdata::random((bdata::seed = 4,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0, 1. * units::_m)))
        ^ bdata::xrange(ntests),
    pT,
    phi,
    theta,
    charge,
    plimit,
    index)
{
  double dcharge = -1 + 2 * charge;
  // foward backward check atlas stepper
  foward_backward(apropagator, pT, phi, theta, dcharge, plimit, index, 1e-3);
  // foward backward check eigen stepper
  foward_backward(epropagator, pT, phi, theta, dcharge, plimit, index, 1e-3);
  // foward backward runge kutta engine
  foward_backward(wpropagator, pT, phi, theta, dcharge, plimit, index, 1e-3);
}

/// test consistency of propgators when approaching a cylinder
BOOST_DATA_TEST_CASE(
    propagation_to_cylinder_,
    bdata::random((bdata::seed = 1010,
                   bdata::distribution
                   = std::uniform_real_distribution<>(0.4 * units::_GeV,
                                                      10. * units::_GeV)))
        ^ bdata::random((bdata::seed = 1111,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-M_PI, M_PI)))
        ^ bdata::random((bdata::seed = 1212,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.1, 0.9 * M_PI)))
        ^ bdata::random((bdata::seed = 1313,
                         bdata::distribution
                         = std::uniform_int_distribution<>(0, 1)))
        ^ bdata::random((bdata::seed = 1414,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.5, 1.)))
        ^ bdata::random((bdata::seed = 1515,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 1616,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 1717,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::xrange(ntests),
    pT,
    phi,
    theta,
    charge,
    rfrac,
    rand1,
    rand2,
    rand3,
    index)
{
  (void)index;

  double dcharge = -1 + 2 * charge;
  // just make sure we can reach it
  double r = rfrac * std::abs(Nat2SI<units::MOMENTUM>(pT) / (1. * Bz));
  r        = (r > 2.5 * Acts::units::_m) ? 2.5 * Acts::units::_m : r;

  // check atlas stepper
  auto a_at_cylinder = to_cylinder(
      apropagator, pT, phi, theta, dcharge, r, rand1, rand2, rand3, covtpr);
  // check eigen stepper
  auto e_at_cylinder = to_cylinder(
      epropagator, pT, phi, theta, dcharge, r, rand1, rand2, rand3, covtpr);
  // the runge kutta engine
  auto w_at_cylinder = to_cylinder(
      wpropagator, pT, phi, theta, dcharge, r, rand1, rand2, rand3, covtpr);
  BOOST_CHECK(
      e_at_cylinder.first.isApprox(a_at_cylinder.first, 1 * units::_um));
  BOOST_CHECK(
      e_at_cylinder.first.isApprox(w_at_cylinder.first, 1 * units::_um));
}

/// test consistency of propagators to a plane
BOOST_DATA_TEST_CASE(
    propagation_to_plane_,
    bdata::random((bdata::seed = 0,
                   bdata::distribution
                   = std::uniform_real_distribution<>(0.4 * units::_GeV,
                                                      10. * units::_GeV)))
        ^ bdata::random((bdata::seed = 1,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-M_PI, M_PI)))
        ^ bdata::random((bdata::seed = 2,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0., M_PI)))
        ^ bdata::random((bdata::seed = 3,
                         bdata::distribution
                         = std::uniform_int_distribution<>(0, 1)))
        ^ bdata::random((bdata::seed = 4,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.5, 1.)))
        ^ bdata::random((bdata::seed = 5,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 6,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 7,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::xrange(ntests),
    pT,
    phi,
    theta,
    charge,
    pfrac,
    rand1,
    rand2,
    rand3,
    index)
{
  (void)index;
  double dcharge = -1 + 2 * charge;
  // to a plane with the atlas stepper
  auto a_at_plane
      = to_surface<AtlasPropagator_type, PlaneSurface>(apropagator,
                                                       pT,
                                                       phi,
                                                       theta,
                                                       dcharge,
                                                       pfrac * Acts::units::_m,
                                                       rand1,
                                                       rand2,
                                                       rand3,
                                                       true,
                                                       covtpr);
  // to a plane with the eigen stepper
  auto e_at_plane
      = to_surface<EigenPropagator_type, PlaneSurface>(epropagator,
                                                       pT,
                                                       phi,
                                                       theta,
                                                       dcharge,
                                                       pfrac * Acts::units::_m,
                                                       rand1,
                                                       rand2,
                                                       rand3,
                                                       true,
                                                       covtpr);
  // foward backward runge kutta engine
  // to a plane with the runge kutta engine
  auto w_at_plane = to_surface<WrappedPropagator_type, PlaneSurface>(
      wpropagator,
      pT,
      phi,
      theta,
      dcharge,
      pfrac * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      true,
      covtpr);

  BOOST_CHECK(e_at_plane.first.isApprox(a_at_plane.first, 1 * units::_um));
  BOOST_CHECK(e_at_plane.first.isApprox(w_at_plane.first, 1 * units::_um));
}
/// test consistency of propagators to a disc
BOOST_DATA_TEST_CASE(
    propagation_to_disc_,
    bdata::random((bdata::seed = 0,
                   bdata::distribution
                   = std::uniform_real_distribution<>(0.4 * units::_GeV,
                                                      10. * units::_GeV)))
        ^ bdata::random((bdata::seed = 1,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-M_PI, M_PI)))
        ^ bdata::random((bdata::seed = 2,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.1, M_PI - 0.1)))
        ^ bdata::random((bdata::seed = 3,
                         bdata::distribution
                         = std::uniform_int_distribution<>(0, 1)))
        ^ bdata::random((bdata::seed = 4,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.5, 1.)))
        ^ bdata::random((bdata::seed = 5,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 6,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 7,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::xrange(ntests),
    pT,
    phi,
    theta,
    charge,
    pfrac,
    rand1,
    rand2,
    rand3,
    index)
{
  (void)index;
  double dcharge = -1 + 2 * charge;
  // to a disc with the  atlas stepper
  auto a_at_disc
      = to_surface<AtlasPropagator_type, DiscSurface>(apropagator,
                                                      pT,
                                                      phi,
                                                      theta,
                                                      dcharge,
                                                      pfrac * Acts::units::_m,
                                                      rand1,
                                                      rand2,
                                                      rand3,
                                                      true,
                                                      covtpr);
  // to a disc with the eigen stepper
  auto e_at_disc
      = to_surface<EigenPropagator_type, DiscSurface>(epropagator,
                                                      pT,
                                                      phi,
                                                      theta,
                                                      dcharge,
                                                      pfrac * Acts::units::_m,
                                                      rand1,
                                                      rand2,
                                                      rand3,
                                                      true,
                                                      covtpr);
  // foward backward runge kutta engine
  // to a disc with the runge kutta engine
  auto w_at_disc
      = to_surface<WrappedPropagator_type, DiscSurface>(wpropagator,
                                                        pT,
                                                        phi,
                                                        theta,
                                                        dcharge,
                                                        pfrac * Acts::units::_m,
                                                        rand1,
                                                        rand2,
                                                        rand3,
                                                        true,
                                                        covtpr);

  BOOST_CHECK(e_at_disc.first.isApprox(a_at_disc.first, 1 * units::_um));
  BOOST_CHECK(e_at_disc.first.isApprox(w_at_disc.first, 1 * units::_um));
}
/// test consistency of propagators to a line
BOOST_DATA_TEST_CASE(
    propagation_to_line_,
    bdata::random((bdata::seed = 1000,
                   bdata::distribution
                   = std::uniform_real_distribution<>(0.4 * units::_GeV,
                                                      10. * units::_GeV)))
        ^ bdata::random((bdata::seed = 1001,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-M_PI, M_PI)))
        ^ bdata::random((bdata::seed = 1002,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.1, M_PI - 0.1)))
        ^ bdata::random((bdata::seed = 1003,
                         bdata::distribution
                         = std::uniform_int_distribution<>(0, 1)))
        ^ bdata::random((bdata::seed = 1004,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.5, 1.)))
        ^ bdata::random((bdata::seed = 1005,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 1006,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 1007,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::xrange(ntests),
    pT,
    phi,
    theta,
    charge,
    pfrac,
    rand1,
    rand2,
    rand3,
    index)
{
  (void)index;
  double dcharge = -1 + 2 * charge;
  // to a line with the atlas stepper
  auto a_at_line
      = to_surface<AtlasPropagator_type, StrawSurface>(apropagator,
                                                       pT,
                                                       phi,
                                                       theta,
                                                       dcharge,
                                                       pfrac * Acts::units::_m,
                                                       rand1,
                                                       rand2,
                                                       rand3,
                                                       false,
                                                       covtpr);
  // to a line with the eigen stepper
  auto e_at_line
      = to_surface<EigenPropagator_type, StrawSurface>(epropagator,
                                                       pT,
                                                       phi,
                                                       theta,
                                                       dcharge,
                                                       pfrac * Acts::units::_m,
                                                       rand1,
                                                       rand2,
                                                       rand3,
                                                       false,
                                                       covtpr);
  // to a line with the runge kutta engine
  auto w_at_line = to_surface<WrappedPropagator_type, StrawSurface>(
      wpropagator,
      pT,
      phi,
      theta,
      dcharge,
      pfrac * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      false,
      covtpr);

  BOOST_CHECK(e_at_line.first.isApprox(a_at_line.first, 1 * units::_um));
  BOOST_CHECK(e_at_line.first.isApprox(w_at_line.first, 1 * units::_um));
}
/// test correct covariance transport for curvilinear parameters
/// this test only works within the
/// s_curvilinearProjTolerance (in: Definitions.hpp)
BOOST_DATA_TEST_CASE(
    covariance_transport_curvilinear_curvilinear_,
    bdata::random((bdata::seed = 2000,
                   bdata::distribution
                   = std::uniform_real_distribution<>(0.4 * units::_GeV,
                                                      10. * units::_GeV)))
        ^ bdata::random((bdata::seed = 2001,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-M_PI, M_PI)))
        ^ bdata::random((bdata::seed = 2002,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.10, M_PI - 0.10)))
        ^ bdata::random((bdata::seed = 2003,
                         bdata::distribution
                         = std::uniform_int_distribution<>(0, 1)))
        ^ bdata::random((bdata::seed = 2004,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.5, 1.)))
        ^ bdata::xrange(ntests),
    pT,
    phi,
    theta,
    charge,
    plimit,
    index)
{
  double dcharge = -1 + 2 * charge;
  // covariance check for eigen stepper
  covariance_curvilinear(
      epropagator, pT, phi, theta, dcharge, plimit * Acts::units::_m, index);
  // covariance check fo atlas stepper
  covariance_curvilinear(
      apropagator, pT, phi, theta, dcharge, plimit * Acts::units::_m, index);
  // covariance check for wrapped engine
  covariance_curvilinear(
      wpropagator, pT, phi, theta, dcharge, plimit * Acts::units::_m, index);
}

// test correct covariance transport from disc to disc
BOOST_DATA_TEST_CASE(
    covariance_transport_disc_disc_,
    bdata::random((bdata::seed = 3000,
                   bdata::distribution
                   = std::uniform_real_distribution<>(0.4 * units::_GeV,
                                                      10. * units::_GeV)))
        ^ bdata::random((bdata::seed = 3001,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-M_PI, M_PI)))
        ^ bdata::random((bdata::seed = 3002,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.1, M_PI - 0.1)))
        ^ bdata::random((bdata::seed = 3003,
                         bdata::distribution
                         = std::uniform_int_distribution<>(0, 1)))
        ^ bdata::random((bdata::seed = 3004,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.5, 1.)))
        ^ bdata::random((bdata::seed = 3005,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 3006,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 3007,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::xrange(ntests),
    pT,
    phi,
    theta,
    charge,
    plimit,
    rand1,
    rand2,
    rand3,
    index)
{
  double dcharge = -1 + 2 * charge;
  // covariance check for atlas stepper
  covariance_bound<AtlasPropagator_type, DiscSurface, DiscSurface>(
      apropagator,
      pT,
      phi,
      theta,
      dcharge,
      plimit * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      index,
      true,
      true,
      1e-1);

  // covariance check for eigen stepper
  covariance_bound<EigenPropagator_type, DiscSurface, DiscSurface>(
      epropagator,
      pT,
      phi,
      theta,
      dcharge,
      plimit * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      index,
      true,
      true,
      1e-1);

  // covariance check fo the runge kutta engine
  covariance_bound<WrappedPropagator_type, DiscSurface, DiscSurface>(
      wpropagator,
      pT,
      phi,
      theta,
      dcharge,
      plimit * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      index,
      true,
      true,
      1e-1);
}

// test correct covariance transport from plane to plane
BOOST_DATA_TEST_CASE(
    covariance_transport_plane_plane_,
    bdata::random((bdata::seed = 4000,
                   bdata::distribution
                   = std::uniform_real_distribution<>(0.4 * units::_GeV,
                                                      10. * units::_GeV)))
        ^ bdata::random((bdata::seed = 4001,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-M_PI, M_PI)))
        ^ bdata::random((bdata::seed = 4002,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.1, M_PI - 0.1)))
        ^ bdata::random((bdata::seed = 4003,
                         bdata::distribution
                         = std::uniform_int_distribution<>(0, 1)))
        ^ bdata::random((bdata::seed = 4004,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.5, 1.)))
        ^ bdata::random((bdata::seed = 4005,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 4006,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::random((bdata::seed = 4007,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-1., 1.)))
        ^ bdata::xrange(ntests),
    pT,
    phi,
    theta,
    charge,
    plimit,
    rand1,
    rand2,
    rand3,
    index)
{
  double dcharge = -1 + 2 * charge;
  // covariance check for atlas stepper
  covariance_bound<AtlasPropagator_type, PlaneSurface, PlaneSurface>(
      apropagator,
      pT,
      phi,
      theta,
      dcharge,
      plimit * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      index);

  // covariance check for eigen stepper
  covariance_bound<EigenPropagator_type, PlaneSurface, PlaneSurface>(
      epropagator,
      pT,
      phi,
      theta,
      dcharge,
      plimit * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      index);

  // covariance check fo the runge kutta engine
  covariance_bound<WrappedPropagator_type, PlaneSurface, PlaneSurface>(
      wpropagator,
      pT,
      phi,
      theta,
      dcharge,
      plimit * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      index);
}

// test correct covariance transport from straw to straw
// for straw surfaces the numerical fixture is actually more difficult
// to calculate
BOOST_DATA_TEST_CASE(
    covariance_transport_line_line_,
    bdata::random((bdata::seed = 1000,
                   bdata::distribution
                   = std::uniform_real_distribution<>(0.4 * units::_GeV,
                                                      10. * units::_GeV)))
        ^ bdata::random((bdata::seed = 1001,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-M_PI, M_PI)))
        ^ bdata::random((bdata::seed = 1002,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.15, M_PI - 0.15)))
        ^ bdata::random((bdata::seed = 1003,
                         bdata::distribution
                         = std::uniform_int_distribution<>(0, 1)))
        ^ bdata::random((bdata::seed = 1004,
                         bdata::distribution
                         = std::uniform_real_distribution<>(0.1, 0.2)))
        ^ bdata::random((bdata::seed = 1005,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-0.25, 0.25)))
        ^ bdata::random((bdata::seed = 1006,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-0.25, 0.25)))
        ^ bdata::random((bdata::seed = 1007,
                         bdata::distribution
                         = std::uniform_real_distribution<>(-0.25, 0.25)))
        ^ bdata::xrange(ntests),
    pT,
    phi,
    theta,
    charge,
    plimit,
    rand1,
    rand2,
    rand3,
    index)
{
  double dcharge = -1 + 2 * charge;

  // covariance check for atlas stepper
  covariance_bound<AtlasPropagator_type, StrawSurface, StrawSurface>(
      apropagator,
      pT,
      phi,
      theta,
      dcharge,
      plimit * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      index,
      false,
      false,
      1e-1);

  // covariance check for eigen stepper
  covariance_bound<EigenPropagator_type, StrawSurface, StrawSurface>(
      epropagator,
      pT,
      phi,
      theta,
      dcharge,
      plimit * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      index,
      false,
      false,
      1e-1);

  // covariance check fo the runge kutta engine
  covariance_bound<WrappedPropagator_type, StrawSurface, StrawSurface>(
      wpropagator,
      pT,
      phi,
      theta,
      dcharge,
      plimit * Acts::units::_m,
      rand1,
      rand2,
      rand3,
      index,
      false,
      false,
      1e-1);
}
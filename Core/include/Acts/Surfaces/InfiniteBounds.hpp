// This file is part of the Acts project.
//
// Copyright (C) 2016-2018 Acts project team
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

///////////////////////////////////////////////////////////////////
// InfiniteBounds.h, Acts project
///////////////////////////////////////////////////////////////////

#pragma once
#include "Acts/Surfaces/SurfaceBounds.hpp"
#include "Acts/Utilities/Definitions.hpp"
#include "Acts/Utilities/VariantDataFwd.hpp"

namespace Acts {

/// @class InfiniteBounds
///
/// templated boundless extension to forward the interface
/// Returns all inside checks to true and can templated for all bounds

class InfiniteBounds : public SurfaceBounds
{
public:
  InfiniteBounds() = default;
  ~InfiniteBounds() {}

  virtual InfiniteBounds*
  clone() const final override
  {
    return new InfiniteBounds();
  }

  virtual SurfaceBounds::BoundsType
  type() const final override
  {
    return SurfaceBounds::Boundless;
  }

  virtual std::vector<TDD_real_t>
  valueStore() const final override
  {
    return {};
  }

  /// Method inside() returns true for any case
  ///
  /// ignores input parameters
  ///
  /// @return always true
  virtual bool
  inside(const Vector2D&, const BoundaryCheck&) const final override
  {
    return true;
  }

  /// Minimal distance calculation
  /// ignores input parameter
  /// @return always 0. (should be -NaN)
  virtual double
  distanceToBoundary(const Vector2D& /*pos*/) const final override
  {
    return 0;
  }

  /// Output Method for std::ostream
  virtual std::ostream&
  dump(std::ostream& os) const final override
  {
    os << "Acts::InfiniteBounds ... boundless surface" << std::endl;
    return os;
  }

  /// Produce a @c variant_data representation of this object
  /// @return The representation
  variant_data
  toVariantData() const override;
};

static const InfiniteBounds s_noBounds{};

}  // namespace Acts
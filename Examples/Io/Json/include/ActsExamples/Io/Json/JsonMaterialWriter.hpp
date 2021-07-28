// This file is part of the Acts project.
//
// Copyright (C) 2017-2019 CERN for the benefit of the Acts project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

#pragma once

#include "Acts/Definitions/Algebra.hpp"
#include "Acts/Geometry/GeometryIdentifier.hpp"
#include "Acts/Material/ISurfaceMaterial.hpp"
#include "Acts/Material/IVolumeMaterial.hpp"
#include "Acts/Plugins/Json/MaterialMapJsonConverter.hpp"
#include "Acts/Utilities/EnumBitwiseOperators.hpp"
#include "Acts/Utilities/Logger.hpp"
#include "ActsExamples/Framework/ProcessCode.hpp"

#include <mutex>

namespace Acts {

class TrackingGeometry;

using SurfaceMaterialMap =
    std::map<GeometryIdentifier, std::shared_ptr<const ISurfaceMaterial>>;

using VolumeMaterialMap =
    std::map<GeometryIdentifier, std::shared_ptr<const IVolumeMaterial>>;

using DetectorMaterialMaps = std::pair<SurfaceMaterialMap, VolumeMaterialMap>;
}  // namespace Acts

namespace ActsExamples {

enum class JsonFormat : uint8_t {
  NoOutput = 0,
  Json = 1,
  Cbor = 2,
  All = std::numeric_limits<uint8_t>::max()
};

ACTS_DEFINE_ENUM_BITWISE_OPERATORS(JsonFormat)

/// @class Json Material writer
///
/// @brief Writes out Detector material maps
/// using the Json Geometry converter
class JsonMaterialWriter {
 public:
  struct Config {
    /// The config class of the converter
    Acts::MaterialMapJsonConverter::Config converterCfg;
    /// Output file name
    std::string fileName = "material";
    /// Output format of the file
    JsonFormat writeFormat = JsonFormat::Json;
  };

  /// Constructor
  ///
  /// @param cfg The configuration struct of the writer
  JsonMaterialWriter(const Config& cfg);

  /// Virtual destructor
  ~JsonMaterialWriter();

  /// Write out the material map
  ///
  /// @param detMaterial is the SurfaceMaterial and VolumeMaterial maps
  void write(const Acts::DetectorMaterialMaps& detMaterial);

  /// Write out the material map from Geometry
  ///
  /// @param tGeometry is the TrackingGeometry
  void write(const Acts::TrackingGeometry& tGeometry);

 private:
  /// The config of the writer
  Config m_cfg;

  /// Private access to the logging instance
  const Acts::Logger& logger() const { return *m_cfg.converterCfg.logger; }
};

}  // namespace ActsExamples
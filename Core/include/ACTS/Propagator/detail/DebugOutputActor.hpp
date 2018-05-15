// This file is part of the ACTS project.
//
// Copyright (C) 2018 ACTS project team
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

#ifndef ACTS_DEBUG_OUTPUT_ACTOR_HPP
#define ACTS_DEBUG_OUTPUT_ACTOR_HPP

namespace Acts {

namespace detail {

  /// This is an actor that deals with the output string
  /// It is called upon targetReached and navigationBreak
  /// of the state and then copies the debugString into
  /// the final output object (result), which leaves the propagation
  struct DebugOutputActor
  {

    /// mute the thing if you don't want any action
    bool mute = false;

    /// Simple result struct to be returned
    /// It collects the debug output string from the state
    /// into which all actors and aborters can write
    struct this_result
    {
      std::string debugString = "";
    };

    typedef this_result result_type;

    /// Debug output action for the ActionList of the Propagator
    ///
    /// @tparam propagator_state_t is the type of the Propagator state
    /// it is not used in this stepper
    ///
    /// @param state is the mutable propagator state object
    /// @param result is the mutable result state object
    template <typename propagator_state_t>
    void
    operator()(propagator_state_t& state, result_type& result) const
    {
      // move the debug output from the state to
      // to the output actor if it is not set to mute
      // only when the target is reached (or later otherwise triggered)
      if (!mute && (state.targetReached || state.navigationBreak))
        result.debugString = std::move(state.options.debugString);
    }

    /// Pure observer interface
    /// - this does not apply to the output collector
    template <typename propagator_state_t>
    void
    operator()(propagator_state_t&) const
    {
    }
  };

}  // namespace detail
}  // namespace Acts

#endif

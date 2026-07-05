# Design Summary

## Architecture

```text
Universal Bio-State Foundation
  -> Cell Belief State
  -> JEPA Transition
  -> HDF Adapter
  -> Biological Verifier
  -> Target-State Planner
  -> Demo
```

## Universal Bio-State Foundation
Defines compact biological state features and readout conventions that can later generalize beyond HDF-like data.

## Cell Belief State
Represents the current inferred state of a cell or cell population using small gene set scores, metadata, and quality signals.

## JEPA Transition
Predicts the next biological belief state from current state, action, context, and adapter state without generating a full transcriptome.

## HDF Adapter
Adds HDF-specific conditioning for aging, regeneration, and partial reprogramming scenarios.

## Biological Verifier
Checks predicted transitions for internal consistency, known limitations, and obvious overclaims.

## Target-State Planner
Searches over action sequences to move toward a desired target state under verifier constraints.

## Demo
Provides a small interactive Streamlit interface for inspecting toy states, interventions, predicted transitions, verifier output, and planner suggestions.

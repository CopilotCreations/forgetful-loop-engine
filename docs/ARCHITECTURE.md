# Lethe System Architecture

This document describes the architecture of the Lethe self-degrading cognitive system.

## Overview

Lethe is designed as a modular system where components can be composed together to create
a self-degrading program that gradually forgets its own functionality while maintaining
stability and narrating its cognitive decline.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LETHE SYSTEM                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Lethe Core (lethe.py)                        │    │
│  │                                                                      │    │
│  │   - Main loop orchestration                                          │    │
│  │   - Component coordination                                           │    │
│  │   - State management                                                 │    │
│  │   - Signal handling                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│           ┌────────────────────────┼────────────────────────┐               │
│           │                        │                        │               │
│           ▼                        ▼                        ▼               │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐            │
│  │   Capability   │    │     Decay      │    │    Safety      │            │
│  │   Registry     │◄───│    Engine      │───►│    Layer       │            │
│  │                │    │                │    │                │            │
│  │ - Registration │    │ - Decay logic  │    │ - Protection   │            │
│  │ - Metadata     │    │ - Targeting    │    │ - Intervention │            │
│  │ - Execution    │    │ - Stub/Delete  │    │ - Fallback     │            │
│  └────────────────┘    └────────────────┘    └────────────────┘            │
│           │                                           │                     │
│           │            ┌────────────────┐            │                     │
│           └───────────►│ Introspector   │◄───────────┘                     │
│                        │                │                                   │
│                        │ - Health track │                                   │
│                        │ - State history│                                   │
│                        │ - Loss records │                                   │
│                        └────────────────┘                                   │
│                                 │                                           │
│                                 ▼                                           │
│                        ┌────────────────┐                                   │
│                        │   Narrative    │                                   │
│                        │   Logger       │                                   │
│                        │                │                                   │
│                        │ - Mental state │                                   │
│                        │ - Storytelling │                                   │
│                        │ - Mood tracking│                                   │
│                        └────────────────┘                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Capability Registry (`capability.py`)

The registry is the central store for all system capabilities.

**Key Classes:**
- `Importance`: Enum defining importance levels (TRIVIAL to ESSENTIAL)
- `CapabilityMetadata`: Dataclass storing capability metadata
- `CapabilityRegistry`: Main registry class

**Responsibilities:**
- Register functions as capabilities with metadata
- Track execution counts
- Manage degradation state
- Provide dependency information

**Example:**
```python
registry = CapabilityRegistry()

@registry.register(
    name="my_function",
    importance=Importance.HIGH,
    degradation_resistance=0.7
)
def my_function():
    return "result"
```

### 2. Decay Engine (`decay_engine.py`)

The engine responsible for gradually degrading capabilities.

**Key Classes:**
- `DecayEvent`: Record of a decay occurrence
- `DecayEngine`: Main engine class

**Decay Stages:**
1. **Approximation** (Level 1): Function works but may produce slightly wrong results
2. **Stubbing** (Level 2): Function replaced with minimal stub returning defaults
3. **Deletion** (Level 3): Function marked as deleted, calls return None

**Target Selection:**
- Lower importance = higher chance of selection
- Lower resistance = higher chance of selection
- Already degraded capabilities continue to degrade

### 3. Introspector (`introspection.py`)

Monitors and reports on system health.

**Key Classes:**
- `SystemState`: Snapshot of system state
- `CapabilityLoss`: Record of a lost capability
- `Introspector`: Main introspection class

**Metrics Tracked:**
- Total/Active/Degraded/Deleted capability counts
- Health percentage (weighted by importance)
- Health trend (stable/declining/critical)
- Uptime and module information

### 4. Narrative Logger (`narrative.py`)

Generates first-person narratives describing the system's experience.

**Key Classes:**
- `MentalState`: Enum of mental states (CONFIDENT to FADING)
- `NarrativeEntry`: Single narrative log entry
- `NarrativeLogger`: Main narrative class

**Mental States by Health:**
| Health % | Mental State |
|----------|-------------|
| 80-100   | CONFIDENT   |
| 60-80    | STABLE      |
| 40-60    | UNCERTAIN   |
| 20-40    | CONFUSED    |
| 10-20    | DISORIENTED |
| 0-10     | FADING      |

### 5. Safety Layer (`safety.py`)

Prevents total system collapse.

**Key Classes:**
- `SafetyStatus`: Enum of safety statuses
- `SafetyCheck`: Result of a safety check
- `SafetyLayer`: Main safety class

**Protections:**
- ESSENTIAL capabilities cannot be degraded
- Minimum capability count is maintained
- Emergency fallback function
- Exception wrapping for safe execution

### 6. Lethe Core (`lethe.py`)

Main orchestrator tying all components together.

**Key Classes:**
- `LetheState`: System state enum
- `LoopIteration`: Record of a main loop iteration
- `Lethe`: Main orchestrator class

**Main Loop Flow:**
```
┌──────────────┐
│    Start     │
└──────┬───────┘
       ▼
┌──────────────┐
│  Execute     │
│ Capabilities │
└──────┬───────┘
       ▼
┌──────────────┐
│   Attempt    │
│    Decay     │
└──────┬───────┘
       ▼
┌──────────────┐
│   Safety     │
│    Check     │
└──────┬───────┘
       ▼
┌──────────────┐
│  Narrative   │
│   Output     │
└──────┬───────┘
       ▼
┌──────────────┐
│    Sleep     │
└──────┬───────┘
       │
       └──► Loop
```

## Data Flow

### Registration Flow
```
User Code ──► Lethe.register() ──► CapabilityRegistry ──► CapabilityMetadata
```

### Decay Flow
```
DecayEngine.tick()
       │
       ▼
select_target() ──► SafetyLayer.should_allow_decay()
       │                         │
       ▼                         ▼
apply_decay() ◄────── (if allowed)
       │
       ▼
Registry.mark_degraded() ──► Introspector.update_lost_capabilities()
       │
       ▼
NarrativeLogger.speak_loss()
```

### Health Check Flow
```
Introspector.get_current_state()
       │
       ▼
Calculate health from weighted capabilities
       │
       ▼
Determine trend from history
       │
       ▼
SafetyLayer.check() ──► Intervene if needed
       │
       ▼
NarrativeLogger determines mental state
```

## Configuration

### Decay Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `decay_interval` | Seconds between decay attempts | 5.0 |
| `decay_probability` | Chance of decay per interval | 0.4 |

### Capability Parameters

| Parameter | Description | Range |
|-----------|-------------|-------|
| `importance` | How critical the capability is | TRIVIAL-ESSENTIAL |
| `degradation_resistance` | How much it resists decay | 0.0-1.0 |
| `dependencies` | Other capabilities it depends on | List of names |

## Thread Safety

The current implementation is **not thread-safe**. The main loop runs in a single thread
with all operations occurring sequentially. If thread safety is needed:

1. Add locks around registry operations
2. Use thread-safe collections for history lists
3. Protect decay engine state with mutexes

## Extension Points

### Custom Capabilities
Register any function with appropriate metadata.

### Custom Decay Logic
Override `DecayEngine.create_approximation()` for custom approximation behavior.

### Custom Narratives
Extend `NarrativeLogger.TEMPLATES` with custom narrative templates.

### Custom Safety Rules
Subclass `SafetyLayer` and override `should_allow_decay()` for custom protection logic.

<p align="center">
  <a href="docs/images/stoa.png">
    <img src="docs/images/stoa.jpeg" alt="Stoa logo" width="30%"/>
  </a>
</p>

<div align="center">
  <a href="https://www.python.org/doc/versions/">
    <img src="https://img.shields.io/badge/python-3.10-blue" alt="Python Versions"/>
  </a>
  <a href="https://github.com/EdanToledo/Stoa/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/>
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000" alt="Code Style"/>
  </a>
  <a  href="http://mypy-lang.org/">
    <img src="https://www.mypy-lang.org/static/mypy_badge.svg" alt="MyPy" />
</a>
</div>

<h2 align="center">
  <p>A JAX-Native Interface for Reinforcement Learning Environments</p>
</h2>

## 🚀 Welcome to Stoa

Stoa provides a lightweight, JAX-native interface for reinforcement learning environments. It defines a common abstraction layer that enables different environment libraries to work together seamlessly in JAX workflows.

> ⚠️ **Early Development** – Core abstractions are in place, but the library is still growing!



## 🎯 What Stoa Provides

* **Common Interface**: A standardized `Environment` base class that defines the contract for RL environments in JAX.
* **JAX-Native Design**: Pure-functional `step` and `reset` operations compatible with JAX transformations like `jit` and `vmap`.
* **Environment Wrappers**: A flexible system for composing and extending environments with additional functionality.
* **Space Definitions**: Structured representations for observation, action, and state spaces.
* **TimeStep Protocol**: A standardized `TimeStep` structure to represent environment transitions with clear termination and truncation signals.



## 🛠️ Installation

You can install the core `stoa` library via pip:

```bash
pip install stoa-env
```

This minimal installation includes the core API and wrappers but no specific environment adapters.

### Environment Adapters

Adapters for external environment libraries are available as optional extras. You can install them individually or all at once.

**Install a specific adapter:**

```bash
# Example for Gymnax
pip install "stoa-env[gymnax]"

# Example for Brax
pip install "stoa-env[brax]"
```

**Install all available adapters:**

```bash
pip install "stoa-env[all]"
```



## 🧩 Available Adapters

Stoa currently supports the following JAX-native environment libraries:

* **Brax**
* **Gymnax**
* **Jumanji**
* **Kinetix**
* **Navix**
* **PGX** (Game environments)
* **MuJoCo Playground**
* **XMinigrid**



## ✨ Available Wrappers

Stoa provides a rich set of wrappers to modify and extend environment behavior:

* **Core Wrappers**: `AutoResetWrapper`, `RecordEpisodeMetrics`, `AddRNGKey`, `VmapWrapper`.
* **Observation Wrappers**: `FlattenObservationWrapper`, `FrameStackingWrapper`, `ObservationExtractWrapper`, `AddActionMaskWrapper`, `AddStartFlagAndPrevAction`, `AddStepCountWrapper`, `MakeChannelLast`, `ObservationTypeWrapper`.
* **Action Space Wrappers**: `MultiDiscreteToDiscreteWrapper`, `MultiBoundedToBoundedWrapper`.
* **Utility Wrappers**: `EpisodeStepLimitWrapper`, `ConsistentExtrasWrapper`.



## ⚡ Usage Example

Here's how to adapt a `gymnax` environment and compose it with several wrappers:

```python
import jax
import gymnax
from stoa import GymnaxToStoa, FlattenObservationWrapper, AutoResetWrapper, RecordEpisodeMetrics

# 1. Instantiate a base environment from a supported library
gymnax_env, env_params = gymnax.make("CartPole-v1")

# 2. Adapt the environment to the Stoa interface
env = GymnaxToStoa(gymnax_env, env_params)

# 3. Apply standard wrappers
# Note: The order of wrappers matters.
env = AutoResetWrapper(env, next_obs_in_extras=True)
env = RecordEpisodeMetrics(env)

# JIT compile the reset and step functions for performance
env.reset = jax.jit(env.reset)
env.step = jax.jit(env.step)

# 4. Interact with the environment
rng_key = jax.random.PRNGKey(0)
state, timestep = env.reset(rng_key)
total_reward = 0

for _ in range(100):
    action = env.action_space().sample(rng_key)
    state, timestep = env.step(state, action)
    total_reward += timestep.reward

    if timestep.last():
        # Access metrics recorded by the RecordEpisodeMetrics wrapper
        episode_return = timestep.extras['episode_metrics']['episode_return']
        print(f"Episode finished. Return: {episode_return}")

        # The state has been auto-reset, so we can continue the loop
        total_reward = 0
```



## 🛣️ Roadmap

* **Documentation**: Expand documentation with detailed tutorials and API references.
* **More Wrappers**: Add more common utility wrappers (e.g., observation normalization, reward clipping).
* **Integration Examples**: Provide examples of how to integrate `stoa` with popular JAX-based RL libraries.



## 🤝 Contributing

We're building Stoa to provide a common foundation for JAX-based RL research. Contributions are welcome!



### 📚 Related Projects

* **Stoix** – Distributed single-agent RL in JAX
* **Gymnax** – Classic control environments in JAX
* **Brax** – Physics-based environments in JAX
* **Jumanji** – Board games and optimization problems in JAX
* **Navix** – Grid-world environments in JAX
* **PGX** - Classic board and card game environments in JAX
* **Kinetix** - Robotics environments in JAX

## Citation
If you use Stoa, please cite it!

```
@misc{toledo2025stoa,
  author = {Edan Toledo},
  title  = {Stoa: A JAX-Native Interface for Reinforcement Learning Environments},
  year   = {2025},
  url    = {https://github.com/EdanToledo/Stoa}
}
```

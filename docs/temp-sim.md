# Temporal Simulator

In this family of classes, we want to extract temporal characteristics using execution of simulations.
We can extract average estimates by average over several executions of the simulation (sample average).

## Serverless Temporal Simulator

```eval_rst
.. autoclass:: pacssim.ServerlessTemporalSimulator.ServerlessTemporalSimulator
    :members:
    :show-inheritance:
```

## Exponential Temporal Simulator

The exponential temporal simulator assume exponential inter-event distribution for both arrival
and departure from each function instance.

```eval_rst
.. autoclass:: pacssim.ServerlessTemporalSimulator.ExponentialServerlessTemporalSimulator
    :members:
    :show-inheritance:
```

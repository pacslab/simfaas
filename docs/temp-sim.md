# Temporal Simulator

```eval_rst
In this family of classes, we want to extract temporal characteristics using execution of simulations.
We can extract average estimates by average over several executions of the simulation (sample average).
All of these classes extend the functionality provided by 
:class:`~pacssim.ServerlessSimulator.ServerlessSimulator`, you can use the same arguments
and call the same methods, with some exteded functionality provided below.
```
<!-- [ServerlessSimulator][]
[ServerlessSimulator]: <sim> -->

## Serverless Temporal Simulator

```eval_rst
.. autoclass:: pacssim.ServerlessTemporalSimulator.ServerlessTemporalSimulator
    :members:
    :undoc-members:
    :show-inheritance:
```

## Exponential Temporal Simulator

The exponential temporal simulator assume exponential inter-event distribution for both arrival
and departure from each function instance.

```eval_rst
.. autoclass:: pacssim.ServerlessTemporalSimulator.ExponentialServerlessTemporalSimulator
    :members:
    :undoc-members:
    :show-inheritance:
```

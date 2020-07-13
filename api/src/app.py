from typing import Optional
import json
import math

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Schema

from simfaas.ServerlessSimulator import ServerlessSimulator
import numpy as np

# plotly imports
from plotly.subplots import make_subplots
import plotly.graph_objs as go

app = FastAPI()

# allow cors for integrations
origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

getArrayIdxArr = lambda x, idx: np.array(x)[idx]
def sample_sim_history_idxs(sim, num_of_points=200):
    hist_idx = 0
    # go in 10 second steps
    hist_step = sim.max_time / num_of_points
    idxs = [0]
    last_hist_time = 0
    while hist_idx < (len(sim.hist_times) - 1):
        hist_idx += 1
        if sim.hist_times[hist_idx] - last_hist_time < hist_step:
            continue

        if hist_idx < (len(sim.hist_times) - 1):
            last_hist_time = sim.hist_times[hist_idx]
            idxs.append(hist_idx)
    return idxs

def generate_trace_api(data, fig=False):
    sim = ServerlessSimulator(**data)
    sim.generate_trace(debug_print=False, progress=False)
    results = sim.get_result_dict()
    # update results with inputs
    results.update(data)

    # analyze the trace for plot
    idxs = sample_sim_history_idxs(sim, 20)
    sampled_hist_times = getArrayIdxArr(sim.hist_times, idxs)
    sampled_hist_inst_counts = getArrayIdxArr(sim.hist_server_count, idxs)
    # calculate sampled instance count average so far
    sampled_hist_inst_avgs = np.cumsum(sampled_hist_inst_counts) / ( np.array(list(range(len(sampled_hist_inst_counts)))) + 1)
    results['sampled_hist_inst_counts'] = sampled_hist_inst_counts.tolist()
    results['sampled_hist_inst_avgs'] = sampled_hist_inst_avgs.tolist()
    results['sampled_hist_times'] = sampled_hist_times.tolist()

    if fig:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x = [i/60 for i in sampled_hist_times],
                y = sampled_hist_inst_counts,
                mode = 'markers+lines',
                name = "Current Value",
            ),
        )
        fig.add_trace(
            go.Scatter(
                x = [i/60 for i in sampled_hist_times],
                y = sampled_hist_inst_avgs,
                mode = 'markers+lines',
                name = "Average Estimate",
            ),
        )
        fig.update_layout(title="Instance Counts Over Time", xaxis=dict(title="Time (minutes)"), yaxis=dict(title="Instance Count"))
        results['plot1'] = json.loads(fig.to_json())

    return results


class SingleSimInput(BaseModel):
    arrival_rate: float = Schema(1, title="Arrival Rate", description="should be less than 10 reqs/sec", gt=0, lte=10)
    warm_service_time: float = Schema(1, title="Warm Service Time", description="Should be less than 1000 seconds", gt=0, lte=1000)
    cold_service_time: float = Schema(1, title="Cold Service Time", description="Should be less than 1000 seconds", gt=0, lte=1000)
    expiration_threshold: Optional[float] = Schema(600, title="Expiration Threshold", description="How long do we keep the instances?", gt=0)
    max_time: Optional[float] = Schema(1e5, title="Maximum Simulation Time", description="How long should the simulation run for?", gt=0, lte=1e6)

class OverallSimInput(BaseModel):
    warm_service_time: float = Schema(1, title="Warm Service Time", description="Should be less than 1000 seconds", gt=0, lte=1000)
    cold_service_time: float = Schema(1, title="Cold Service Time", description="Should be less than 1000 seconds", gt=0, lte=1000)
    expiration_threshold: Optional[float] = Schema(600, title="Expiration Threshold", description="How long do we keep the instances?", gt=0)
    max_time: Optional[float] = Schema(1e3, title="Maximum Simulation Time", description="How long should the simulation run for? should be less than 1000 seconds", gt=0, lte=1e3)


@app.post("/sim/single")
async def single_simulation(sim_input: SingleSimInput):
    sim_input_dict = sim_input.dict()
    sim_input_dict['warm_service_rate'] = 1/sim_input_dict['warm_service_time']
    sim_input_dict['cold_service_rate'] = 1/sim_input_dict['cold_service_time']
    # we want to return the inputs as well
    output_dict = sim_input_dict
    # remove extra parameters, and update output with simulation results
    del sim_input_dict['warm_service_time']
    del sim_input_dict['cold_service_time']

    # perform simulation
    ret = generate_trace_api(sim_input_dict, True)

    # update the output dict with return values
    output_dict.update(ret)

    return output_dict

@app.post("/sim/overall")
async def overall_plot_simulation(sim_input: OverallSimInput):
    sim_input_dict = sim_input.dict()
    sim_input_dict['warm_service_rate'] = 1/sim_input_dict['warm_service_time']
    sim_input_dict['cold_service_rate'] = 1/sim_input_dict['cold_service_time']
    # we want to return the inputs as well
    output_dict = sim_input_dict
    # remove extra parameters, and update output with simulation results
    del sim_input_dict['warm_service_time']
    del sim_input_dict['cold_service_time']

    # perform simulation
    # Plot characteristics for different arrival rates and expiration thresholds
    num_arrival_rates = 10
    exp_thresholds = [10, 60, 600, 1200, 1800]
    exp_threshold_labels = ["10 sec", "1 min", "10 min", "20 min", "30 min"]
    sim_input_dict['arrival_rate'] = list(np.repeat(np.logspace(-3,1,num_arrival_rates), len(exp_thresholds)))
    sim_input_dict['expiration_threshold'] = exp_thresholds * num_arrival_rates
    sim_input_dict['expiration_threshold_labels'] = exp_threshold_labels * num_arrival_rates

    input_dicts = []
    for i in range(len(sim_input_dict['arrival_rate'])):
        inp_dict = {}
        for k in sim_input_dict:
            if type(sim_input_dict[k]) == list:
                inp_dict[k] = sim_input_dict[k][i]
            else:
                inp_dict[k] = sim_input_dict[k]

        input_dicts.append(inp_dict)

    res = [generate_trace_api(d) for d in input_dicts]

    ret = {}
    ret['prob_cold_percent'] = [round(r['prob_cold'] * 100, 6) for r in res]
    ret['utilization_percent'] = [round(r['inst_running_count_avg'] / r['inst_count_avg'] * 100, 6) for r in res]
    for idx in range(len(ret['utilization_percent'])):
        if math.isnan(ret['utilization_percent'][idx]):
            ret['utilization_percent'][idx] = None

    # update the output dict with return values
    output_dict.update(ret)

    return output_dict

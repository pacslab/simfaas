from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Schema

from simfaas.ServerlessSimulator import ServerlessSimulator
import numpy as np

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

        last_hist_time = sim.hist_times[hist_idx]
        idxs.append(hist_idx)
    return idxs

def generate_trace_api(data):
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
    sampled_hist_inst_avgs = np.cumsum(sampled_hist_inst_counts) / np.array(list(range(len(sampled_hist_inst_counts))))
    sampled_hist_inst_avgs[0] = 0
    results['sampled_hist_inst_counts'] = sampled_hist_inst_counts.tolist()
    results['sampled_hist_inst_avgs'] = sampled_hist_inst_avgs.tolist()
    results['sampled_hist_times'] = sampled_hist_times.tolist()

    return results


class SingleSimInput(BaseModel):
    arrival_rate: float = Schema(1, title="Arrival Rate", description="should be less than 10 reqs/sec", gt=0, lte=10)
    warm_service_time: float = Schema(1, title="Warm Service Time", description="Should be less than 1000 seconds", gt=0, lte=1000)
    cold_service_time: float = Schema(1, title="Cold Service Time", description="Should be less than 1000 seconds", gt=0, lte=1000)
    expiration_threshold: Optional[float] = Schema(600, title="Expiration Threshold", description="How long do we keep the instances?", gt=0)
    max_time: Optional[float] = Schema(1e5, title="Maximum Simulation Time", description="How long should the simulation run for?", gt=0, lte=1e6)


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
    output_dict.update(generate_trace_api(sim_input_dict))

    return output_dict

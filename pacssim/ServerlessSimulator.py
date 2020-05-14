# The main simulator for serverless computing platforms

from pacssim.SimProcess import ExpSimProcess

class FunctionInstance:
    def __init__(self, t, cold_service_process, warm_service_process, expiration_threshold):
        super().__init__()

        self.cold_service_process = cold_service_process
        self.warm_service_process = warm_service_process
        self.expiration_threshold = expiration_threshold

        # life span calculations
        self.creation_time = t

        # set current state variables
        self.state = 'COLD'
        self.is_busy = True
        self.is_cold = True

        # calculate departure and expected termination on each arrival
        self.next_departure = t + self.cold_service_process.generate_trace()
        self.update_next_termination()

    def __str__(self):
        return f"State: {self.state} \t Departure: {self.next_departure:8.2f} \t Termination: {self.next_termination:8.2f}"

    def get_life_span(self):
        return self.next_termination - self.creation_time

    def update_next_termination(self):
        self.next_termination = self.next_departure + self.expiration_threshold

    def get_state(self):
        return self.state

    def arrival_transition(self, t):
        if self.state == 'COLD' or self.state == 'WARM':
            raise Exception('instance is already busy!')

        elif self.state == 'IDLE':
            self.state = 'WARM'
            self.is_busy = True
            self.next_departure = t + self.warm_service_process.generate_trace()
            self.update_next_termination()

    def make_transition(self):
        # next transition is a departure
        if self.state == 'COLD' or self.state == 'WARM':
            self.state = 'IDLE'
            self.is_busy = False
            self.is_cold = False

        # next transition is a termination
        elif self.state == 'IDLE':
            self.state = 'TERM'
            self.is_busy = False

        # if terminated
        else:
            raise Exception("Cannot make transition on terminated instance!")

    def get_next_transition_time(self, t):
        # next transition would be termination
        if self.state == 'IDLE':
            return self.get_next_termination(t)
        # next transition would be departure
        return self.get_next_departure(t)

    def get_next_departure(self, t):
        if t > self.next_departure:
            raise Exception("current time is after departure!")
        return self.next_departure - t

    def get_next_termination(self, t):
        if t > self.next_termination:
            raise Exception("current time is after termination!")
        return self.next_termination - t

class ServerlessSimulator:
    def __init__(self, arrival_process=None, warm_service_process=None, 
            cold_service_process=None, expiration_threshold=600, **kwargs):
        super().__init__()
        
        # setup arrival process
        self.arrival_process = arrival_process
        # if the user wants a exponentially distributed arrival process
        if 'arrival_rate' in kwargs:
            self.arrival_process = ExpSimProcess(rate=kwargs.get('arrival_rate'))
        # in the end, arrival process should be defined
        if self.arrival_process is None:
            raise Exception('Arrival process not defined!')

        # if both warm and cold service rate is provided (exponential distribution)
        # then, warm service rate should be larger than cold service rate
        if 'warm_service_rate' in kwargs and 'cold_service_rate' in kwargs:
            if kwargs.get('warm_service_rate') < kwargs.get('cold_service_rate'):
                raise Exception("Warm service rate cannot be smaller than cold service rate!")

        # setup warm service process
        self.warm_service_process = warm_service_process
        if 'warm_service_rate' in kwargs:
            self.warm_service_process = ExpSimProcess(rate=kwargs.get('warm_service_rate'))
        if self.warm_service_process is None:
            raise Exception('Warm Service process not defined!')

        # setup cold service process
        self.cold_service_process = cold_service_process
        if 'cold_service_rate' in kwargs:
            self.cold_service_process = ExpSimProcess(rate=kwargs.get('cold_service_rate'))
        if self.cold_service_process is None:
            raise Exception('Cold Service process not defined!')

        self.expiration_threshold = expiration_threshold

    # def generate_trace(self):



if __name__ == "__main__":
    sim = ServerlessSimulator(arrival_rate=1/0.3, warm_service_rate=1/2.05, cold_service_rate=1/2.2,
            expiration_threshold=600)
    func = FunctionInstance(100, sim.cold_service_process, sim.warm_service_process, sim.expiration_threshold)
    print(func.get_next_transition_time(100))
    print(func)
    func.make_transition()
    print(func)
    func.arrival_transition(200)
    print(func)
    func.make_transition()
    print(func)
    print(func.get_next_transition_time(300))
  
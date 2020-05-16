

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

    def get_life_span(self):
        return self.next_termination - self.creation_time

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

    def is_idle(self):
        return self.state == 'IDLE'

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

        return self.state

    def get_next_transition_time(self, t=0):
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
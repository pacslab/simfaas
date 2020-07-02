

class FunctionInstance:
    """FunctionInstance aims to simulate the behaviour of a function instance in a serverless platform, with all the internal transitions necessary.

    Parameters
    ----------
    t : float
        The time at which the instance is being created
    cold_service_process : simfaas.SimProcess.SimProcess
        The process used to sample cold start response times
    warm_service_process : simfaas.SimProcess.SimProcess
        The process used to sample warm start response times
    expiration_threshold : float
        The amount of time it takes for an instance to get expired and the resources consumed by it released after processing the last request
    """
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
        """Get the lifespan of the instance (from creation until the termination)

        Returns
        -------
        float
            The number of seconds it took the instance to be expired
        """
        return self.next_termination - self.creation_time

    def update_next_termination(self):
        """Update the next scheduled termination if no other requests are made to the instance.
        """
        self.next_termination = self.next_departure + self.expiration_threshold

    def get_life_span(self):
        return self.next_termination - self.creation_time

    def get_state(self):
        return self.state

    def arrival_transition(self, t):
        """Make an arrival transition, which causes the instance to go from IDLE to WARM

        Parameters
        ----------
        t : float
            The time at which the transition has occured, this also updates the next termination.

        Raises
        ------
        Exception
            Raises if currently process a request by being in `COLD` or `WARM` states
        """
        if self.state == 'COLD' or self.state == 'WARM':
            raise Exception('instance is already busy!')

        elif self.state == 'IDLE':
            self.state = 'WARM'
            self.is_busy = True
            self.next_departure = t + self.warm_service_process.generate_trace()
            self.update_next_termination()

    def is_idle(self):
        """Whether or not the instance is currently idle, and thus can accept new requests.

        Returns
        -------
        bool
            True if idle, false otherwise
        """
        return self.state == 'IDLE'

    def make_transition(self):
        """Make the next internal transition, either transition into `IDLE` of already processing a request, or `TERM` if scheduled termination has arrived.

        Returns
        -------
        str
            The state after making the internal transition

        Raises
        ------
        Exception
            Raises if already in `TERM` state, since no other internal transitions are possible
        """
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
        """Get how long until the next transition.

        Parameters
        ----------
        t : float, optional
            The current time, by default 0

        Returns
        -------
        float
            The seconds remaining until the next transition
        """
        # next transition would be termination
        if self.state == 'IDLE':
            return self.get_next_termination(t)
        # next transition would be departure
        return self.get_next_departure(t)

    def get_next_departure(self, t):
        """Get the time until the next departure

        Parameters
        ----------
        t : float
            Current time

        Returns
        -------
        float
            Amount of time until the next departure

        Raises
        ------
        Exception
            Raises if called after the departure
        """
        if t > self.next_departure:
            raise Exception("current time is after departure!")
        return self.next_departure - t

    def get_next_termination(self, t):
        """Get the time until the next termination

        Parameters
        ----------
        t : float
            Current time

        Returns
        -------
        float
            Amount of time until the next termination

        Raises
        ------
        Exception
            Raises if called after the termination
        """
        if t > self.next_termination:
            raise Exception("current time is after termination!")
        return self.next_termination - t
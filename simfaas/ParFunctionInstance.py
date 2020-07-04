from simfaas.FunctionInstance import FunctionInstance

class ParFunctionInstance(FunctionInstance):
    """ParFunctionInstance aims to simulate the behaviour of a function instance in a serverless platform, with all the internal transitions necessary allowing multiple requests to be parsed. For other input parameters, refer to :class:`~simfaas.FunctionInstance.FunctionInstance`.

    Parameters
    ----------
    cold_service_process : simfaas.SimProcess.SimProcess
        The process used to sample cold start `initialization` process before warm process is starting. Note that this is different from :class:`~simfaas.FunctionInstance.FunctionInstance`
    concurrency_value : int
        The number of parallel requests that a single instance can handle.
    """
    def __init__(self, concurrency_value, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # save concurrency value
        self.concurrency_value = concurrency_value

    def __str__(self):
        return f"State: {self.state} \t Cold End: {self.cold_end:8.2f} \t Next Transition: {self.get_next_transition_time():8.2f} \t Termination: {self.next_termination:8.2f} \t Departure: {','.join([f'{s:.2f}' for s in self.next_departure])}"

    def generate_cold_departure(self, t):
        # calculate departure and expected termination on each arrival
        self.cold_end = self.creation_time + self.cold_service_process.generate_trace()
        self.next_departure = [self.cold_end + self.warm_service_process.generate_trace()]

    def update_next_termination(self):
        """Update the next scheduled termination if no other requests are made to the instance.
        """
        self.next_termination = max(self.next_departure) + self.expiration_threshold

    def _get_running_reqs(self):
        return len(self.next_departure)

    def get_concurrency(self):
        """get current concurrency level

        Returns
        -------
        int
            number of requests being processed right now
        """
        return self._get_running_reqs()

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
            if not self.is_ready():
                raise Exception('instance is already at full capacity!')
            else:
                # if arrived before cold start process ends, processing starts after cold start ends
                self.next_departure += [max(t, self.cold_end) + self.warm_service_process.generate_trace()]
                self.update_next_termination()

        elif self.state == 'IDLE':
            self.state = 'WARM'
            self.is_busy = True
            self.next_departure = [t + self.warm_service_process.generate_trace()]
            self.update_next_termination()

    def is_ready(self):
        """Whether or not the instance is ready to accept new requests. Here, same as is_idle()

        Returns
        -------
        bool
            True if ready to accept new requests, False otherwise
        """
        return self._get_running_reqs() < self.concurrency_value

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
        if self.state == 'COLD':
            self.state = 'WARM'
            self.is_cold = False

        elif self.state == 'WARM':
            if self._get_running_reqs() > 1:
                idxmin = self.next_departure.index(min(self.next_departure))
                del self.next_departure[idxmin]
            elif self._get_running_reqs() == 1:
                # if only 1 request, then we go to idle mode
                del self.next_departure[0]
                self.state = 'IDLE'
                self.is_busy = False
            else:
                raise Exception("Invalid state!")

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
        elif self.state == 'COLD':
            return self.cold_end - t
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
        if t > min(self.next_departure):
            raise Exception("current time is after departure!")
        return min(self.next_departure) - t

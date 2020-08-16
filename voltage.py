   def get_voltage(self, channel_name, **kwargs):
        self.voltmeter_autorange(channel_name)
        return self.get_average_voltage(channel_name, **kwargs)

    def voltmeter_autorange(self, channel_name):
        try:
            self.oscilloscope._channels[channel_name].gain = 1
        except TypeError:  # channel_name is not CH1 or CH2.
            return 1
        V = self.get_average_voltage(channel_name)
        return self.__autoSelectRange__(channel_name, V)

    def __autoSelectRange__(self, channel_name, V):
        keys = [8, 4, 3, 2, 1.5, 1, .5, 0]
        cutoffs = {8: 1, 4: 2, 3: 4, 2: 5, 1.5: 8, 1.: 10, .5: 16, 0: 32}
        for a in keys:
            if abs(V) > a:
                g = cutoffs[a]
                break
        self.oscilloscope._channels[channel_name].gain = g
        return g

    def __autoRangeScope__(self, tg):
        x, y1, y2 = self.oscilloscope.capture(2, 1000, tg)
        self.__autoSelectRange__('CH1', max(abs(y1)))
        self.__autoSelectRange__('CH2', max(abs(y2)))

    def get_average_voltage(self, channel_name, **kwargs):
        """
		Return the voltage on the selected channel
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		+------------+-----------------------------------------------------------------------------------------+
		|Arguments   |Description                                                                              |
		+============+=========================================================================================+
		|channel_name| 'CH1','CH2','CH3', 'MIC','IN1','SEN','V+'                                               |
		+------------+-----------------------------------------------------------------------------------------+
		|sleep       | read voltage in CPU sleep mode. not particularly useful. Also, Buggy.                   |
		+------------+-----------------------------------------------------------------------------------------+
		|\*\*kwargs  | Samples to average can be specified. eg. samples=100 will average a hundred readings    |
		+------------+-----------------------------------------------------------------------------------------+
		see :ref:`stream_video`
		Example:
		>>> self.__print__(I.get_average_voltage('CH4'))
		1.002
		"""
    self.oscilloscope._channels[channel_name].resolution = 12
        scale = self.oscilloscope._channels[channel_name].scale
        vals = [self.__get_raw_average_voltage__(channel_name, **kwargs) for a in range(int(kwargs.get('samples', 1)))]
        # if vals[0]>2052:print (vals)
        val = np.average([scale(a) for a in vals])
        return val

    def __get_raw_average_voltage__(self, channel_name, **kwargs):
        """
		Return the average of 16 raw 12-bit ADC values of the voltage on the selected channel
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================================
		**Arguments**
		==============  ============================================================================================================
		channel_name    'CH1', 'CH2', 'CH3', 'MIC', '5V', 'IN1','SEN'
		sleep           read voltage in CPU sleep mode
		==============  ============================================================================================================
		"""
        chosa = self.oscilloscope._channels[channel_name].chosa
        self.H.__sendByte__(CP.ADC)
        self.H.__sendByte__(CP.GET_VOLTAGE_SUMMED)
        self.H.__sendByte__(chosa)
        V_sum = self.H.__getInt__()
        self.H.__get_ack__()
        return V_sum / 16.  # sum(V)/16.0  #

    def fetch_buffer(self, starting_position=0, total_points=100):
        """
		fetches a section of the ADC hardware buffer
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.RETRIEVE_BUFFER)
        self.H.__sendInt__(starting_position)
        self.H.__sendInt__(total_points)
        for a in range(int(total_points)): self.buff[a] = self.H.__getInt__()
        self.H.__get_ack__()

    def clear_buffer(self, starting_position, total_points):
        """
		clears a section of the ADC hardware buffer
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.CLEAR_BUFFER)
        self.H.__sendInt__(starting_position)
        self.H.__sendInt__(total_points)
        self.H.__get_ack__()

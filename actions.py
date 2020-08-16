def fill_buffer(self, starting_position, point_array):
        """
		fill a section of the ADC hardware buffer with data
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.FILL_BUFFER)
        self.H.__sendInt__(starting_position)
        self.H.__sendInt__(len(point_array))
        for a in point_array:
            self.H.__sendInt__(int(a))
        self.H.__get_ack__()

    def start_streaming(self, tg, channel='CH1'):
        """
		Instruct the ADC to start streaming 8-bit data.  use stop_streaming to stop.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		tg              timegap. 250KHz clock
		channel         channel 'CH1'... 'CH9','IN1','SEN'
		==============  ============================================================================================
		"""
        chosa = self.oscilloscope.channels[channel].chosa
        if (self.streaming): self.stop_streaming()
        self.H.__sendByte__(CP.ADC)
        self.H.__sendByte__(CP.START_ADC_STREAMING)
        self.H.__sendByte__(chosa)
        self.H.__sendInt__(tg)  # Timegap between samples.  8MHz timer clock
        self.streaming = True

    def stop_streaming(self):
        """
		Instruct the ADC to stop streaming data
		"""
        if (self.streaming):
            self.H.__sendByte__(CP.STOP_STREAMING)
            self.H.fd.read(20000)
            self.H.fd.flush()
        else:
            self.__print__('not streaming')
        self.streaming = False

    # -------------------------------------------------------------------------------------------------------------------#

    # |===============================================DIGITAL SECTION====================================================|
    # |This section has commands related to digital measurement and control. These include the Logic Analyzer, frequency |
    # |measurement calls, timing routines, digital outputs etc                               |
    # -------------------------------------------------------------------------------------------------------------------#

    def __calcDChan__(self, name):
        """
		accepts a string represention of a digital input ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		and returns a corresponding number
		"""

        if name in self.digital_channel_names:
            return self.digital_channel_names.index(name)
        else:
            self.__print__(' invalid channel', name, ' , selecting ID1 instead ')
            return 0

    def __get_high_freq__backup__(self, pin):
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.GET_HIGH_FREQUENCY)
        self.H.__sendByte__(self.__calcDChan__(pin))
        scale = self.H.__getByte__()
        val = self.H.__getLong__()
        self.H.__get_ack__()
        return scale * (val) / 1.0e-1  # 100mS sampling

    def get_high_freq(self, pin):
        """
		retrieves the frequency of the signal connected to ID1. for frequencies > 1MHz
		also good for lower frequencies, but avoid using it since
		the oscilloscope cannot be used simultaneously due to hardware limitations.
		The input frequency is fed to a 32 bit counter for a period of 100mS.
		The value of the counter at the end of 100mS is used to calculate the frequency.
		see :ref:`freq_video`
		.. seealso:: :func:`get_freq`
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		pin             The input pin to measure frequency from : ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		==============  ============================================================================================
		:return: frequency
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.GET_ALTERNATE_HIGH_FREQUENCY)
        self.H.__sendByte__(self.__calcDChan__(pin))
        scale = self.H.__getByte__()
        val = self.H.__getLong__()
        self.H.__get_ack__()
        # self.__print__(hex(val))
        return scale * (val) / 1.0e-1  # 100mS sampling

    def get_freq(self, channel='CNTR', timeout=2):
        """
		Frequency measurement on IDx.
		Measures time taken for 16 rising edges of input signal.
		returns the frequency in Hertz
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		channel         The input to measure frequency from. ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		timeout         This is a blocking call which will wait for one full wavelength before returning the
						calculated frequency.
						Use the timeout option if you're unsure of the input signal.
						returns 0 if timed out
		==============  ============================================================================================
		:return float: frequency
		.. _timing_example:
			* connect SQR1 to ID1
			>>> I.sqr1(4000,25)
			>>> self.__print__(I.get_freq('ID1'))
			4000.0
			>>> self.__print__(I.r2r_time('ID1'))
			#time between successive rising edges
			0.00025
			>>> self.__print__(I.f2f_time('ID1'))
			#time between successive falling edges
			0.00025
			>>> self.__print__(I.pulse_time('ID1'))
			#may detect a low pulse, or a high pulse. Whichever comes first
			6.25e-05
			>>> I.duty_cycle('ID1')
			#returns wavelength, high time
			(0.00025,6.25e-05)
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.GET_FREQUENCY)
        timeout_msb = int((timeout * 64e6)) >> 16
        self.H.__sendInt__(timeout_msb)
        self.H.__sendByte__(self.__calcDChan__(channel))

        self.H.waitForData(timeout)

        tmt = self.H.__getByte__()
        x = [self.H.__getLong__() for a in range(2)]
        self.H.__get_ack__()
        freq = lambda t: 16 * 64e6 / t if (t) else 0
        # self.__print__(x,tmt,timeout_msb)

        if (tmt): return 0
        return freq(x[1] - x[0])

    '''
	def r2r_time(self,channel='ID1',timeout=0.1):
		"""
		Returns the time interval between two rising edges
		of input signal on ID1
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ================================================================================================
		**Arguments**
		==============  ================================================================================================
		channel         The input to measure time between two rising edges.['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		timeout         Use the timeout option if you're unsure of the input signal time period.
						returns 0 if timed out
		==============  ================================================================================================
		:return float: time between two rising edges of input signal
		.. seealso:: timing_example_
		"""
		self.H.__sendByte__(CP.TIMING)
		self.H.__sendByte__(CP.GET_TIMING)
		timeout_msb = int((timeout*64e6))>>16
		self.H.__sendInt__(timeout_msb)
		self.H.__sendByte__( EVERY_RISING_EDGE<<2 | 2)
		self.H.__sendByte__(self.__calcDChan__(channel))
		tmt = self.H.__getInt__()
		x=[self.H.__getLong__() for a in range(2)]
		self.H.__get_ack__()
		if(tmt >= timeout_msb):return -1
		rtime = lambda t: t/64e6
		y=x[1]-x[0]
		return rtime(y)
	'''

    def r2r_time(self, channel, skip_cycle=0, timeout=5):
        """
		Return a list of rising edges that occured within the timeout period.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ==============================================================================================================
		**Arguments**
		==============  ==============================================================================================================
		channel         The input to measure time between two rising edges.['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		skip_cycle      Number of points to skip. eg. Pendulums pass through light barriers twice every cycle. SO 1 must be skipped
		timeout         Number of seconds to wait for datapoints. (Maximum 60 seconds)
		==============  ==============================================================================================================
		:return list: Array of points
		"""
        if timeout > 60: timeout = 60
        self.start_one_channel_LA(channel=channel, channel_mode=3, trigger_mode=0)  # every rising edge
        startTime = time.time()
        while time.time() - startTime < timeout:
            a, b, c, d, e = self.get_LA_initial_states()
            if a == self.MAX_SAMPLES / 4:
                a = 0
            if a >= skip_cycle + 2:
                tmp = self.fetch_long_data_from_LA(a, 1)
                self.dchans[0].load_data(e, tmp)
                # print (self.dchans[0].timestamps)
                return [1e-6 * (self.dchans[0].timestamps[skip_cycle + 1] - self.dchans[0].timestamps[0])]
            time.sleep(0.1)
        return []

    def f2f_time(self, channel, skip_cycle=0, timeout=5):
        """
		Return a list of falling edges that occured within the timeout period.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ==============================================================================================================
		**Arguments**
		==============  ==============================================================================================================
		channel         The input to measure time between two falling edges.['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		skip_cycle      Number of points to skip. eg. Pendulums pass through light barriers twice every cycle. SO 1 must be skipped
		timeout         Number of seconds to wait for datapoints. (Maximum 60 seconds)
		==============  ==============================================================================================================
		:return list: Array of points
		"""
        if timeout > 60: timeout = 60
        self.start_one_channel_LA(channel=channel, channel_mode=2, trigger_mode=0)  # every falling edge
        startTime = time.time()
        while time.time() - startTime < timeout:
            a, b, c, d, e = self.get_LA_initial_states()
            if a == self.MAX_SAMPLES / 4:
                a = 0
            if a >= skip_cycle + 2:
                tmp = self.fetch_long_data_from_LA(a, 1)
                self.dchans[0].load_data(e, tmp)
                # print (self.dchans[0].timestamps)
                return [1e-6 * (self.dchans[0].timestamps[skip_cycle + 1] - self.dchans[0].timestamps[0])]
            time.sleep(0.1)
        return []

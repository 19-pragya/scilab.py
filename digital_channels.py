self.clear_buffer(0, self.MAX_SAMPLES / 2)
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.START_ONE_CHAN_LA)
        self.H.__sendInt__(self.MAX_SAMPLES / 4)
        # trigchan bit functions
        # b0 - trigger or not
        # b1 - trigger edge . 1 => rising. 0 => falling
        # b2, b3 - channel to acquire data from. ID1,ID2,ID3,ID4,COMPARATOR
        # b4 - trigger channel ID1
        # b5 - trigger channel ID2
        # b6 - trigger channel ID3

        if ('trigger_channels' in args) and trigger & 1:
            trigchans = args.get('trigger_channels', 0)
            if 'ID1' in trigchans: trigger |= (1 << 4)
            if 'ID2' in trigchans: trigger |= (1 << 5)
            if 'ID3' in trigchans: trigger |= (1 << 6)
        else:
            trigger |= 1 << (self.__calcDChan__(
                channel) + 4)  # trigger on specified input channel if not trigger_channel argument provided

        trigger |= 2 if args.get('edge', 0) == 'rising' else 0
        trigger |= self.__calcDChan__(channel) << 2

        self.H.__sendByte__(trigger)
        self.H.__get_ack__()
        self.digital_channels_in_buffer = 1
        for a in self.dchans:
            a.prescaler = 0
            a.datatype = 'long'
            a.length = self.MAX_SAMPLES / 4
            a.maximum_time = maximum_time * 1e6  # conversion to uS
            a.mode = self.EVERY_EDGE

            # def start_one_channel_LA(self,**args):
            """
			start logging timestamps of rising/falling edges on ID1
			.. tabularcolumns:: |p{3cm}|p{11cm}|
			================== ======================================================================================================
			**Arguments**
			================== ======================================================================================================
			args
			channel             ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
			trigger_channel     ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
			channel_mode        acquisition mode\n
								default value: 1(EVERY_EDGE)
								- EVERY_SIXTEENTH_RISING_EDGE = 5
								- EVERY_FOURTH_RISING_EDGE    = 4
								- EVERY_RISING_EDGE           = 3
								- EVERY_FALLING_EDGE          = 2
								- EVERY_EDGE                  = 1
								- DISABLED                    = 0
			trigger_edge        1=Falling edge
								0=Rising Edge
								-1=Disable Trigger
			================== ======================================================================================================
			:return: Nothing
			self.clear_buffer(0,self.MAX_SAMPLES/2);
			self.H.__sendByte__(CP.TIMING)
			self.H.__sendByte__(CP.START_ONE_CHAN_LA)
			self.H.__sendInt__(self.MAX_SAMPLES/4)
			aqchan = self.__calcDChan__(args.get('channel','ID1'))
			aqmode = args.get('channel_mode',1)
			if 'trigger_channel' in args:
				trchan = self.__calcDChan__(args.get('trigger_channel','ID1'))
				tredge = args.get('trigger_edge',0)
				self.__print__('trigger chan',trchan,' trigger edge ',tredge)
				if tredge!=-1:
					self.H.__sendByte__((trchan<<4)|(tredge<<1)|1)
				else:
					self.H.__sendByte__(0)  #no triggering
			elif 'trigger_edge' in args:
				tredge = args.get('trigger_edge',0)
				if tredge!=-1:
					self.H.__sendByte__((aqchan<<4)|(tredge<<1)|1)  #trigger on acquisition channel
				else:
					self.H.__sendByte__(0)  #no triggering
			else:
				self.H.__sendByte__(0)  #no triggering
			self.H.__sendByte__((aqchan<<4)|aqmode)
			self.H.__get_ack__()
			self.digital_channels_in_buffer = 1
			a = self.dchans[0]
			a.prescaler = 0
			a.datatype='long'
			a.length = self.MAX_SAMPLES/4
			a.maximum_time = 67*1e6 #conversion to uS
			a.mode = args.get('channel_mode',1)
			a.initial_state_override=False
			'''
			if trmode in [3,4,5]:
				a.initial_state_override = 2
			elif trmode == 2:
				a.initial_state_override = 1
			'''
			"""

    def start_one_channel_LA(self, **args):
        """
		start logging timestamps of rising/falling edges on ID1
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		================== ======================================================================================================
		**Arguments**
		================== ======================================================================================================
		args
		channel            ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		channel_mode       acquisition mode.
						   default value: 1
							- EVERY_SIXTEENTH_RISING_EDGE = 5
							- EVERY_FOURTH_RISING_EDGE    = 4
							- EVERY_RISING_EDGE           = 3
							- EVERY_FALLING_EDGE          = 2
							- EVERY_EDGE                  = 1
							- DISABLED                    = 0
		================== ======================================================================================================
		:return: Nothing
		see :ref:`LA_video`
		"""
        # trigger_channel    ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
        # trigger_mode       same as channel_mode.
        #				   default_value : 3
        self.clear_buffer(0, self.MAX_SAMPLES / 2)
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.START_ALTERNATE_ONE_CHAN_LA)
        self.H.__sendInt__(self.MAX_SAMPLES / 4)
        aqchan = self.__calcDChan__(args.get('channel', 'ID1'))
        aqmode = args.get('channel_mode', 1)
        trchan = self.__calcDChan__(args.get('trigger_channel', 'ID1'))
        trmode = args.get('trigger_mode', 3)

        self.H.__sendByte__((aqchan << 4) | aqmode)
        self.H.__sendByte__((trchan << 4) | trmode)
        self.H.__get_ack__()
        self.digital_channels_in_buffer = 1

        a = self.dchans[0]
        a.prescaler = 0
        a.datatype = 'long'
        a.length = self.MAX_SAMPLES / 4
        a.maximum_time = 67 * 1e6  # conversion to uS
        a.mode = args.get('channel_mode', 1)
        a.name = args.get('channel', 'ID1')

        if trmode in [3, 4, 5]:
            a.initial_state_override = 2
        elif trmode == 2:
            a.initial_state_override = 1

    def start_two_channel_LA(self, **args):
        """
		start logging timestamps of rising/falling edges on ID1,AD2
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  =======================================================================================================
		**Arguments**
		==============  =======================================================================================================
		trigger         Bool . Enable rising edge trigger on ID1
		\*\*args
		chans			Channels to acquire data from . default ['ID1','ID2']
		modes               modes for each channel. Array .\n
							default value: [1,1]
							- EVERY_SIXTEENTH_RISING_EDGE = 5
							- EVERY_FOURTH_RISING_EDGE    = 4
							- EVERY_RISING_EDGE           = 3
							- EVERY_FALLING_EDGE          = 2
							- EVERY_EDGE                  = 1
							- DISABLED                    = 0
		maximum_time    Total time to sample. If total time exceeds 67 seconds, a prescaler will be used in the reference clock
		==============  =======================================================================================================
		::
			"fetch_long_data_from_dma(samples,1)" to get data acquired from channel 1
			"fetch_long_data_from_dma(samples,2)" to get data acquired from channel 2
			The read data can be accessed from self.dchans[0 or 1]
		"""
        # Trigger not working up to expectations. DMA keeps dumping Null values even though not triggered.

        # trigger         True/False  : Whether or not to trigger the Logic Analyzer using the first channel of the two.
        # trig_type		'rising' / 'falling' .  Type of logic change to trigger on
        # trig_chan		channel to trigger on . Any digital input. default chans[0]

        modes = args.get('modes', [1, 1])
        strchans = args.get('chans', ['ID1', 'ID2'])
        chans = [self.__calcDChan__(strchans[0]), self.__calcDChan__(strchans[1])]  # Convert strings to index
        maximum_time = args.get('maximum_time', 67)
        trigger = args.get('trigger', 0)
        if trigger:
            trigger = 1
            if args.get('edge', 'rising') == 'falling': trigger |= 2
            trigger |= (self.__calcDChan__(args.get('trig_chan', strchans[0])) << 4)
        # print (args.get('trigger',0),args.get('edge'),args.get('trig_chan',strchans[0]),hex(trigger),args)
        else:
            trigger = 0

        self.clear_buffer(0, self.MAX_SAMPLES)
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.START_TWO_CHAN_LA)
        self.H.__sendInt__(self.MAX_SAMPLES / 4)
        self.H.__sendByte__(trigger)

        self.H.__sendByte__((modes[1] << 4) | modes[0])  # Modes. four bits each
        self.H.__sendByte__((chans[1] << 4) | chans[0])  # Channels. four bits each
        self.H.__get_ack__()
        n = 0
        for a in self.dchans[:2]:
            a.prescaler = 0
            a.length = self.MAX_SAMPLES / 4
            a.datatype = 'long'
            a.maximum_time = maximum_time * 1e6  # conversion to uS
            a.mode = modes[n]
            a.channel_number = chans[n]
            a.name = strchans[n]
            n += 1
        self.digital_channels_in_buffer = 2
	
	def start_three_channel_LA(self, **args):
        """
		start logging timestamps of rising/falling edges on ID1,ID2,ID3
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		================== ======================================================================================================
		**Arguments**
		================== ======================================================================================================
		args
		trigger_channel     ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		modes               modes for each channel. Array .\n
							default value: [1,1,1]
							- EVERY_SIXTEENTH_RISING_EDGE = 5
							- EVERY_FOURTH_RISING_EDGE    = 4
							- EVERY_RISING_EDGE           = 3
							- EVERY_FALLING_EDGE          = 2
							- EVERY_EDGE                  = 1
							- DISABLED                    = 0
		trigger_mode        same as modes(previously documented keyword argument)
							default_value : 3
		================== ======================================================================================================
		:return: Nothing
		"""
        self.clear_buffer(0, self.MAX_SAMPLES)
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.START_THREE_CHAN_LA)
        self.H.__sendInt__(self.MAX_SAMPLES / 4)
        modes = args.get('modes', [1, 1, 1, 1])
        trchan = self.__calcDChan__(args.get('trigger_channel', 'ID1'))
        trmode = args.get('trigger_mode', 3)

        self.H.__sendInt__(modes[0] | (modes[1] << 4) | (modes[2] << 8))
        self.H.__sendByte__((trchan << 4) | trmode)

        self.H.__get_ack__()
        self.digital_channels_in_buffer = 3

        n = 0
        for a in self.dchans[:3]:
            a.prescaler = 0
            a.length = self.MAX_SAMPLES / 4
            a.datatype = 'int'
            a.maximum_time = 1e3  # < 1 mS between each consecutive level changes in the input signal must be ensured to prevent rollover
            a.mode = modes[n]
            a.name = a.digital_channel_names[n]
            if trmode in [3, 4, 5]:
                a.initial_state_override = 2
            elif trmode == 2:
                a.initial_state_override = 1
            n += 1

    def start_four_channel_LA(self, trigger=1, maximum_time=0.001, mode=[1, 1, 1, 1], **args):
        """
		Four channel Logic Analyzer.
		start logging timestamps from a 64MHz counter to record level changes on ID1,ID2,ID3,ID4.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		trigger         Bool . Enable rising edge trigger on ID1
		maximum_time    Maximum delay expected between two logic level changes.\n
						If total time exceeds 1 mS, a prescaler will be used in the reference clock
						However, this only refers to the maximum time between two successive level changes. If a delay larger
						than .26 S occurs, it will be truncated by modulo .26 S.\n
						If you need to record large intervals, try single channel/two channel modes which use 32 bit counters
						capable of time interval up to 67 seconds.
		mode            modes for each channel. List with four elements\n
						default values: [1,1,1,1]
						- EVERY_SIXTEENTH_RISING_EDGE = 5
						- EVERY_FOURTH_RISING_EDGE    = 4
						- EVERY_RISING_EDGE           = 3
						- EVERY_FALLING_EDGE          = 2
						- EVERY_EDGE                  = 1
						- DISABLED                    = 0
		==============  ============================================================================================
		:return: Nothing
		.. seealso::
			Use :func:`fetch_long_data_from_LA` (points to read,x) to get data acquired from channel x.
			The read data can be accessed from :class:`~ScienceLab.dchans` [x-1]
		"""
        self.clear_buffer(0, self.MAX_SAMPLES)
        prescale = 0
        """
		if(maximum_time > 0.26):
			#self.__print__('too long for 4 channel. try 2/1 channels')
			prescale = 3
		elif(maximum_time > 0.0655):
			prescale = 3
		elif(maximum_time > 0.008191):
			prescale = 2
		elif(maximum_time > 0.0010239):
			prescale = 1
		"""
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.START_FOUR_CHAN_LA)
        self.H.__sendInt__(self.MAX_SAMPLES / 4)
        self.H.__sendInt__(mode[0] | (mode[1] << 4) | (mode[2] << 8) | (mode[3] << 12))
        self.H.__sendByte__(prescale)  # prescaler
        trigopts = 0
        trigopts |= 4 if args.get('trigger_ID1', 0) else 0
        trigopts |= 8 if args.get('trigger_ID2', 0) else 0
        trigopts |= 16 if args.get('trigger_ID3', 0) else 0
        if (trigopts == 0): trigger |= 4  # select one trigger channel(ID1) if none selected
        trigopts |= 2 if args.get('edge', 0) == 'rising' else 0
        trigger |= trigopts
        self.H.__sendByte__(trigger)
        self.H.__get_ack__()
        self.digital_channels_in_buffer = 4
        n = 0
        for a in self.dchans:
            a.prescaler = prescale
            a.length = self.MAX_SAMPLES / 4
            a.datatype = 'int'
            a.name = a.digital_channel_names[n]
            a.maximum_time = maximum_time * 1e6  # conversion to uS
            a.mode = mode[n]
            n += 1

    def get_LA_initial_states(self):
        """
		fetches the initial states of digital inputs that were recorded right before the Logic analyzer was started, and the total points each channel recorded
		:return: chan1 progress,chan2 progress,chan3 progress,chan4 progress,[ID1,ID2,ID3,ID4]. eg. [1,0,1,1]
		"""
        self.H.__sendByte__(CP.TIMING)
        self.H.__sendByte__(CP.GET_INITIAL_DIGITAL_STATES)
        initial = self.H.__getInt__()
        A = (self.H.__getInt__() - initial) / 2
        B = (self.H.__getInt__() - initial) / 2 - self.MAX_SAMPLES / 4
        C = (self.H.__getInt__() - initial) / 2 - 2 * self.MAX_SAMPLES / 4
        D = (self.H.__getInt__() - initial) / 2 - 3 * self.MAX_SAMPLES / 4
        s = self.H.__getByte__()
        s_err = self.H.__getByte__()
        self.H.__get_ack__()

        if A == 0: A = self.MAX_SAMPLES / 4
        if B == 0: B = self.MAX_SAMPLES / 4
        if C == 0: C = self.MAX_SAMPLES / 4
        if D == 0: D = self.MAX_SAMPLES / 4

        if A < 0: A = 0
        if B < 0: B = 0
        if C < 0: C = 0
        if D < 0: D = 0

        return A, B, C, D, {'ID1': (s & 1 != 0), 'ID2': (s & 2 != 0), 'ID3': (s & 4 != 0), 'ID4': (s & 8 != 0),
                            'SEN': (s & 16 != 16)}  # SEN is inverted comparator output.


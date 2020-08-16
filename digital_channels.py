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

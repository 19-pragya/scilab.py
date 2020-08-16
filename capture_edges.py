 def capture_edges1(self, waiting_time=1., **args):
        """
		log timestamps of rising/falling edges on one digital input
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		=================   ======================================================================================================
		**Arguments**
		=================   ======================================================================================================
		waiting_time        Total time to allow the logic analyzer to collect data.
							This is implemented using a simple sleep routine, so if large delays will be involved,
							refer to :func:`start_one_channel_LA` to start the acquisition, and :func:`fetch_LA_channels` to
							retrieve data from the hardware after adequate time. The retrieved data is stored
							in the array self.dchans[0].timestamps.
		keyword arguments
		channel             'ID1',...,'ID4'
		trigger_channel     'ID1',...,'ID4'
		channel_mode        acquisition mode\n
							default value: 3
							- EVERY_SIXTEENTH_RISING_EDGE = 5
							- EVERY_FOURTH_RISING_EDGE    = 4
							- EVERY_RISING_EDGE           = 3
							- EVERY_FALLING_EDGE          = 2
							- EVERY_EDGE                  = 1
							- DISABLED                    = 0
		trigger_mode        same as channel_mode.
							default_value : 3
		=================   ======================================================================================================
		:return:  timestamp array in Seconds
		>>> I.capture_edges(0.2,channel='ID1',trigger_channel='ID1',channel_mode=3,trigger_mode = 3)
		#captures rising edges only. with rising edge trigger on ID1
		"""
        aqchan = args.get('channel', 'ID1')
        trchan = args.get('trigger_channel', aqchan)

        aqmode = args.get('channel_mode', 3)
        trmode = args.get('trigger_mode', 3)

        self.start_one_channel_LA(channel=aqchan, channel_mode=aqmode, trigger_channel=trchan, trigger_mode=trmode)

        time.sleep(waiting_time)

        data = self.get_LA_initial_states()
        tmp = self.fetch_long_data_from_LA(data[0], 1)
        # data[4][0] -> initial state
        return tmp / 64e6

    def start_one_channel_LA_backup__(self, trigger=1, channel='ID1', maximum_time=67, **args):
        """
		start logging timestamps of rising/falling edges on ID1
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		================== ======================================================================================================
		**Arguments**
		================== ======================================================================================================
		trigger            Bool . Enable edge trigger on ID1. use keyword argument edge='rising' or 'falling'
		channel            ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		maximum_time       Total time to sample. If total time exceeds 67 seconds, a prescaler will be used in the reference clock
		kwargs
		triggger_channels  array of digital input names that can trigger the acquisition.eg. trigger= ['ID1','ID2','ID3']
						   will triggger when a logic change specified by the keyword argument 'edge' occurs
						   on either or the three specified trigger inputs.
		edge               'rising' or 'falling' . trigger edge type for trigger_channels.
		================== ======================================================================================================
		:return: Nothing
		"""

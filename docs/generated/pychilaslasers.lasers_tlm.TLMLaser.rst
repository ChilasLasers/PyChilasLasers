pychilaslasers.lasers\_tlm.TLMLaser
===================================

.. currentmodule:: pychilaslasers.lasers_tlm
   

.. autoclass:: TLMLaser




   



   



   .. dropdown:: Methods

      .. autosummary::

      
         ~TLMLaser.__init__
         ~TLMLaser.clear_cycler_table
         ~TLMLaser.close_connection
         ~TLMLaser.get_all_cycler_entries
         ~TLMLaser.get_amount_fb
         ~TLMLaser.get_amount_meas_channels
         ~TLMLaser.get_cycler_entries_max
         ~TLMLaser.get_cycler_entry
         ~TLMLaser.get_cycler_entry_mode_hop
         ~TLMLaser.get_cycler_entry_wavelength
         ~TLMLaser.get_cycler_index
         ~TLMLaser.get_cycler_span
         ~TLMLaser.get_cycler_wavelength_count
         ~TLMLaser.get_driver_max
         ~TLMLaser.get_driver_min
         ~TLMLaser.get_driver_value
         ~TLMLaser.get_fb_destination
         ~TLMLaser.get_fb_gain
         ~TLMLaser.get_fb_loop
         ~TLMLaser.get_fb_setpoint
         ~TLMLaser.get_fb_settings
         ~TLMLaser.get_fb_source
         ~TLMLaser.get_fb_state
         ~TLMLaser.get_fb_tick_interval
         ~TLMLaser.get_meas_unit
         ~TLMLaser.get_meas_value
         ~TLMLaser.get_user_data_bool
         ~TLMLaser.get_user_data_float
         ~TLMLaser.get_user_data_int
         ~TLMLaser.initialize_cycler_table
         ~TLMLaser.list_comports
         ~TLMLaser.load_cycler_entry
         ~TLMLaser.open_connection
         ~TLMLaser.open_file_cycler_table
         ~TLMLaser.put_cycler_entry
         ~TLMLaser.query
         ~TLMLaser.reset_device
         ~TLMLaser.save_cycler_entry
         ~TLMLaser.save_file_cycler_table
         ~TLMLaser.set_cycler_entry
         ~TLMLaser.set_cycler_entry_mode_hop
         ~TLMLaser.set_cycler_entry_wavelengths
         ~TLMLaser.set_cycler_mode_hop
         ~TLMLaser.set_cycler_span
         ~TLMLaser.set_cycler_trigger
         ~TLMLaser.set_cycler_wavelength_count
         ~TLMLaser.set_driver_value
         ~TLMLaser.set_driver_value_with_antihyst
         ~TLMLaser.set_fb_destination
         ~TLMLaser.set_fb_gain
         ~TLMLaser.set_fb_loop
         ~TLMLaser.set_fb_setpoint
         ~TLMLaser.set_fb_source
         ~TLMLaser.set_fb_state
         ~TLMLaser.set_fb_tick_interval
         ~TLMLaser.set_up_temp_enclosure_fb
         ~TLMLaser.set_user_data_bool
         ~TLMLaser.set_user_data_float
         ~TLMLaser.set_user_data_int
         ~TLMLaser.store_cycler
         ~TLMLaser.store_user_data
         ~TLMLaser.turn_off_cycler
         ~TLMLaser.turn_off_diode
         ~TLMLaser.turn_off_system
         ~TLMLaser.turn_off_tec
         ~TLMLaser.turn_on_cycler
         ~TLMLaser.turn_on_diode
         ~TLMLaser.turn_on_system
         ~TLMLaser.turn_on_tec
         ~TLMLaser.write
         ~TLMLaser.write_laser_settings


   
   

   
   

   .. dropdown:: Attributes

      .. autosummary::
      
         ~TLMLaser.admin_mode
         ~TLMLaser.baudrate
         ~TLMLaser.cpu
         ~TLMLaser.cycler_interval
         ~TLMLaser.cycler_running
         ~TLMLaser.debug_info
         ~TLMLaser.diode_current
         ~TLMLaser.diode_state
         ~TLMLaser.fwv
         ~TLMLaser.hwv
         ~TLMLaser.idn
         ~TLMLaser.is_connected
         ~TLMLaser.model
         ~TLMLaser.port
         ~TLMLaser.prefix_mode
         ~TLMLaser.shutdown_reason
         ~TLMLaser.srn
         ~TLMLaser.statusCode_prefix
         ~TLMLaser.system_state
         ~TLMLaser.tec_current
         ~TLMLaser.tec_limit_max
         ~TLMLaser.tec_limit_min
         ~TLMLaser.tec_state
         ~TLMLaser.tec_target
         ~TLMLaser.tec_temp
         ~TLMLaser.temp_electronics
         ~TLMLaser.temp_enclosure
         ~TLMLaser.uptime
   
   

 
   
   
   .. automethod:: __init__
   .. automethod:: clear_cycler_table
   .. automethod:: close_connection
   .. automethod:: get_all_cycler_entries
   .. automethod:: get_amount_fb
   .. automethod:: get_amount_meas_channels
   .. automethod:: get_cycler_entries_max
   .. automethod:: get_cycler_entry
   .. automethod:: get_cycler_entry_mode_hop
   .. automethod:: get_cycler_entry_wavelength
   .. automethod:: get_cycler_index
   .. automethod:: get_cycler_span
   .. automethod:: get_cycler_wavelength_count
   .. automethod:: get_driver_max
   .. automethod:: get_driver_min
   .. automethod:: get_driver_value
   .. automethod:: get_fb_destination
   .. automethod:: get_fb_gain
   .. automethod:: get_fb_loop
   .. automethod:: get_fb_setpoint
   .. automethod:: get_fb_settings
   .. automethod:: get_fb_source
   .. automethod:: get_fb_state
   .. automethod:: get_fb_tick_interval
   .. automethod:: get_meas_unit
   .. automethod:: get_meas_value
   .. automethod:: get_user_data_bool
   .. automethod:: get_user_data_float
   .. automethod:: get_user_data_int
   .. automethod:: initialize_cycler_table
   .. automethod:: list_comports
   .. automethod:: load_cycler_entry
   .. automethod:: open_connection
   .. automethod:: open_file_cycler_table
   .. automethod:: put_cycler_entry
   .. automethod:: query
   .. automethod:: reset_device
   .. automethod:: save_cycler_entry
   .. automethod:: save_file_cycler_table
   .. automethod:: set_cycler_entry
   .. automethod:: set_cycler_entry_mode_hop
   .. automethod:: set_cycler_entry_wavelengths
   .. automethod:: set_cycler_mode_hop
   .. automethod:: set_cycler_span
   .. automethod:: set_cycler_trigger
   .. automethod:: set_cycler_wavelength_count
   .. automethod:: set_driver_value
   .. automethod:: set_driver_value_with_antihyst
   .. automethod:: set_fb_destination
   .. automethod:: set_fb_gain
   .. automethod:: set_fb_loop
   .. automethod:: set_fb_setpoint
   .. automethod:: set_fb_source
   .. automethod:: set_fb_state
   .. automethod:: set_fb_tick_interval
   .. automethod:: set_up_temp_enclosure_fb
   .. automethod:: set_user_data_bool
   .. automethod:: set_user_data_float
   .. automethod:: set_user_data_int
   .. automethod:: store_cycler
   .. automethod:: store_user_data
   .. automethod:: turn_off_cycler
   .. automethod:: turn_off_diode
   .. automethod:: turn_off_system
   .. automethod:: turn_off_tec
   .. automethod:: turn_on_cycler
   .. automethod:: turn_on_diode
   .. automethod:: turn_on_system
   .. automethod:: turn_on_tec
   .. automethod:: write
   .. automethod:: write_laser_settings
   
   ..  autoattribute:: admin_mode
   ..  autoattribute:: baudrate
   ..  autoattribute:: cpu
   ..  autoattribute:: cycler_interval
   ..  autoattribute:: cycler_running
   ..  autoattribute:: debug_info
   ..  autoattribute:: diode_current
   ..  autoattribute:: diode_state
   ..  autoattribute:: fwv
   ..  autoattribute:: hwv
   ..  autoattribute:: idn
   ..  autoattribute:: is_connected
   ..  autoattribute:: model
   ..  autoattribute:: port
   ..  autoattribute:: prefix_mode
   ..  autoattribute:: shutdown_reason
   ..  autoattribute:: srn
   ..  autoattribute:: statusCode_prefix
   ..  autoattribute:: system_state
   ..  autoattribute:: tec_current
   ..  autoattribute:: tec_limit_max
   ..  autoattribute:: tec_limit_min
   ..  autoattribute:: tec_state
   ..  autoattribute:: tec_target
   ..  autoattribute:: tec_temp
   ..  autoattribute:: temp_electronics
   ..  autoattribute:: temp_enclosure
   ..  autoattribute:: uptime

   
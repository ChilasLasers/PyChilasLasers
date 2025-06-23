pychilaslasers.lasers\_swept.SweptLaser
=======================================

.. currentmodule:: pychilaslasers.lasers_swept
   

.. autoclass:: SweptLaser




   



   



   .. dropdown:: Methods

      .. autosummary::

      
         ~SweptLaser.__init__
         ~SweptLaser.clear_cycler_table
         ~SweptLaser.close_connection
         ~SweptLaser.get_all_cycler_entries
         ~SweptLaser.get_amount_fb
         ~SweptLaser.get_amount_meas_channels
         ~SweptLaser.get_cycler_entries_max
         ~SweptLaser.get_cycler_entry
         ~SweptLaser.get_cycler_entry_mode_hop
         ~SweptLaser.get_cycler_entry_wavelength
         ~SweptLaser.get_cycler_index
         ~SweptLaser.get_cycler_span
         ~SweptLaser.get_cycler_wavelength_count
         ~SweptLaser.get_driver_max
         ~SweptLaser.get_driver_min
         ~SweptLaser.get_driver_value
         ~SweptLaser.get_fb_destination
         ~SweptLaser.get_fb_gain
         ~SweptLaser.get_fb_loop
         ~SweptLaser.get_fb_setpoint
         ~SweptLaser.get_fb_settings
         ~SweptLaser.get_fb_source
         ~SweptLaser.get_fb_state
         ~SweptLaser.get_fb_tick_interval
         ~SweptLaser.get_idx_mode_hop
         ~SweptLaser.get_idx_wavelength
         ~SweptLaser.get_meas_unit
         ~SweptLaser.get_meas_value
         ~SweptLaser.get_mode_number_idx
         ~SweptLaser.get_user_data_bool
         ~SweptLaser.get_user_data_float
         ~SweptLaser.get_user_data_int
         ~SweptLaser.get_wavelength
         ~SweptLaser.get_wavelength_idx
         ~SweptLaser.initialize_cycler_table
         ~SweptLaser.list_comports
         ~SweptLaser.load_cycler_entry
         ~SweptLaser.load_cycler_table
         ~SweptLaser.open_connection
         ~SweptLaser.open_file_cycler_table
         ~SweptLaser.phase_anti_hyst
         ~SweptLaser.phase_correction_sweep_to_steady
         ~SweptLaser.prepare_steady_mode
         ~SweptLaser.prepare_sweep_mode
         ~SweptLaser.put_cycler_entry
         ~SweptLaser.query
         ~SweptLaser.reapply_mode_settings
         ~SweptLaser.reset_device
         ~SweptLaser.save_cycler_entry
         ~SweptLaser.save_file_cycler_table
         ~SweptLaser.set_cycler_entry
         ~SweptLaser.set_cycler_entry_mode_hop
         ~SweptLaser.set_cycler_entry_wavelengths
         ~SweptLaser.set_cycler_mode_hop
         ~SweptLaser.set_cycler_span
         ~SweptLaser.set_cycler_trigger
         ~SweptLaser.set_cycler_wavelength_count
         ~SweptLaser.set_driver_value
         ~SweptLaser.set_driver_value_with_antihyst
         ~SweptLaser.set_fb_destination
         ~SweptLaser.set_fb_gain
         ~SweptLaser.set_fb_loop
         ~SweptLaser.set_fb_setpoint
         ~SweptLaser.set_fb_source
         ~SweptLaser.set_fb_state
         ~SweptLaser.set_fb_tick_interval
         ~SweptLaser.set_up_temp_enclosure_fb
         ~SweptLaser.set_user_data_bool
         ~SweptLaser.set_user_data_float
         ~SweptLaser.set_user_data_int
         ~SweptLaser.set_wavelength_abs
         ~SweptLaser.set_wavelength_abs_idx
         ~SweptLaser.set_wavelength_rel
         ~SweptLaser.set_wavelength_rel_idx
         ~SweptLaser.store_cycler
         ~SweptLaser.store_user_data
         ~SweptLaser.sweep
         ~SweptLaser.sweep_abort
         ~SweptLaser.sweep_full
         ~SweptLaser.sweep_idx
         ~SweptLaser.trigger_pulse
         ~SweptLaser.turn_off_cycler
         ~SweptLaser.turn_off_diode
         ~SweptLaser.turn_off_system
         ~SweptLaser.turn_off_tec
         ~SweptLaser.turn_on_cycler
         ~SweptLaser.turn_on_diode
         ~SweptLaser.turn_on_system
         ~SweptLaser.turn_on_tec
         ~SweptLaser.write
         ~SweptLaser.write_laser_settings


   
   

   
   

   .. dropdown:: Attributes

      .. autosummary::
      
         ~SweptLaser.admin_mode
         ~SweptLaser.baudrate
         ~SweptLaser.cpu
         ~SweptLaser.cycler_interval
         ~SweptLaser.cycler_running
         ~SweptLaser.debug_info
         ~SweptLaser.diode_current
         ~SweptLaser.diode_current_steady_mode
         ~SweptLaser.diode_current_sweep_mode
         ~SweptLaser.diode_state
         ~SweptLaser.fwv
         ~SweptLaser.hwv
         ~SweptLaser.idn
         ~SweptLaser.is_connected
         ~SweptLaser.max_wavelength
         ~SweptLaser.min_wavelength
         ~SweptLaser.model
         ~SweptLaser.operation_mode
         ~SweptLaser.port
         ~SweptLaser.prefix_mode
         ~SweptLaser.shutdown_reason
         ~SweptLaser.srn
         ~SweptLaser.statusCode_prefix
         ~SweptLaser.sweep_stepsize
         ~SweptLaser.system_state
         ~SweptLaser.tec_current
         ~SweptLaser.tec_limit_max
         ~SweptLaser.tec_limit_min
         ~SweptLaser.tec_state
         ~SweptLaser.tec_target
         ~SweptLaser.tec_target_steady_mode
         ~SweptLaser.tec_target_sweep_mode
         ~SweptLaser.tec_temp
         ~SweptLaser.temp_electronics
         ~SweptLaser.temp_enclosure
         ~SweptLaser.uptime
   
   

 
   
   
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
   .. automethod:: get_idx_mode_hop
   .. automethod:: get_idx_wavelength
   .. automethod:: get_meas_unit
   .. automethod:: get_meas_value
   .. automethod:: get_mode_number_idx
   .. automethod:: get_user_data_bool
   .. automethod:: get_user_data_float
   .. automethod:: get_user_data_int
   .. automethod:: get_wavelength
   .. automethod:: get_wavelength_idx
   .. automethod:: initialize_cycler_table
   .. automethod:: list_comports
   .. automethod:: load_cycler_entry
   .. automethod:: load_cycler_table
   .. automethod:: open_connection
   .. automethod:: open_file_cycler_table
   .. automethod:: phase_anti_hyst
   .. automethod:: phase_correction_sweep_to_steady
   .. automethod:: prepare_steady_mode
   .. automethod:: prepare_sweep_mode
   .. automethod:: put_cycler_entry
   .. automethod:: query
   .. automethod:: reapply_mode_settings
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
   .. automethod:: set_wavelength_abs
   .. automethod:: set_wavelength_abs_idx
   .. automethod:: set_wavelength_rel
   .. automethod:: set_wavelength_rel_idx
   .. automethod:: store_cycler
   .. automethod:: store_user_data
   .. automethod:: sweep
   .. automethod:: sweep_abort
   .. automethod:: sweep_full
   .. automethod:: sweep_idx
   .. automethod:: trigger_pulse
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
   ..  autoattribute:: diode_current_steady_mode
   ..  autoattribute:: diode_current_sweep_mode
   ..  autoattribute:: diode_state
   ..  autoattribute:: fwv
   ..  autoattribute:: hwv
   ..  autoattribute:: idn
   ..  autoattribute:: is_connected
   ..  autoattribute:: max_wavelength
   ..  autoattribute:: min_wavelength
   ..  autoattribute:: model
   ..  autoattribute:: operation_mode
   ..  autoattribute:: port
   ..  autoattribute:: prefix_mode
   ..  autoattribute:: shutdown_reason
   ..  autoattribute:: srn
   ..  autoattribute:: statusCode_prefix
   ..  autoattribute:: sweep_stepsize
   ..  autoattribute:: system_state
   ..  autoattribute:: tec_current
   ..  autoattribute:: tec_limit_max
   ..  autoattribute:: tec_limit_min
   ..  autoattribute:: tec_state
   ..  autoattribute:: tec_target
   ..  autoattribute:: tec_target_steady_mode
   ..  autoattribute:: tec_target_sweep_mode
   ..  autoattribute:: tec_temp
   ..  autoattribute:: temp_electronics
   ..  autoattribute:: temp_enclosure
   ..  autoattribute:: uptime

   
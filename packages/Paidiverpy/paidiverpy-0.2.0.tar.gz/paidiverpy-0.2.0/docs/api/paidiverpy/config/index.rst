paidiverpy.config
=================

.. py:module:: paidiverpy.config

.. autoapi-nested-parse::

   
   __init__.py for config module.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/paidiverpy/config/config_params/index
   /api/paidiverpy/config/configuration/index


Classes
-------

.. autoapisummary::

   paidiverpy.config.Configuration


Package Contents
----------------

.. py:class:: Configuration(config_file_path: str | None = None, add_general: dict[str, Any] | None = None, add_steps: list[dict[str, Any]] | None = None)

   
   Configuration class.

   :param config_file_path: The configuration file path. Defaults to None.
   :type config_file_path: str, optional
   :param add_general: The general configuration. Defaults to None.
   :type add_general: dict, optional
   :param add_steps: The steps configuration. Defaults to None.
   :type add_steps: list[dict], optional















   ..
       !! processed by numpydoc !!

   .. py:method:: validate_config(config: dict[str, Any] | str | pathlib.Path, local: bool = True) -> None
      :staticmethod:


      
      Validate the configuration.

      :param config: The configuration to validate.
      :type config: dict | str | Path
      :param local: Whether the schema is local. Defaults to True.
      :type local: bool, optional















      ..
          !! processed by numpydoc !!


   .. py:method:: add_general(config: dict[str, Any], validate: bool = False) -> None

      
      Add a configuration.

      :param config: The configuration.
      :type config: dict
      :param validate: Whether to validate the configuration. Defaults to False.
      :type validate: bool, optional

      :raises ValueError: Invalid configuration name.















      ..
          !! processed by numpydoc !!


   .. py:method:: add_step(config_index: int | None = None, parameters: dict[str, Any] | None = None, insert: bool = False, validate: bool = False, step_class: type[paidiverpy.colour_layer.ColourLayer] | type[paidiverpy.convert_layer.ConvertLayer] | type[paidiverpy.position_layer.PositionLayer] | type[paidiverpy.sampling_layer.SamplingLayer] | type[paidiverpy.custom_layer.CustomLayer] | type[paidiverpy.investigation_layer.InvestigationLayer] | None = None) -> int

      
      Add a step to the configuration.

      :param config_index: The configuration index. Defaults to None.
      :type config_index: int, optional
      :param parameters: The parameters for the step. Defaults to None.
      :type parameters: dict, optional
      :param insert: Whether to insert the step at the given index. Defaults to False.
      :type insert: bool, optional
      :param validate: Whether to validate the configuration. Defaults to True.
      :type validate: bool, optional
      :param step_class: The class of the step. Defaults to None.
      :type step_class: BaseModel, optional

      :raises ValueError: Invalid step index.

      :returns: The step index.
      :rtype: int















      ..
          !! processed by numpydoc !!


   .. py:method:: remove_step(config_index: int | None = None) -> int

      
      Remove a step from the configuration.

      :param config_index: The configuration index. Defaults to None, which means the last step will be removed.
      :type config_index: int, optional

      :raises ValueError: Invalid step index.

      :returns: The step index.
      :rtype: int















      ..
          !! processed by numpydoc !!


   .. py:method:: export(output_path: pathlib.Path | str | None) -> None | str

      
      Export the configuration to a file.

      :param output_path: The path to save the configuration file. If None, returns the configuration as a YAML string.
      :type output_path: str, optional

      :returns:

                If output_path is None, returns the configuration as a YAML string.
                            Otherwise, writes the configuration to the specified file.
      :rtype: None | str















      ..
          !! processed by numpydoc !!


   .. py:method:: get_output_path(output_path: str | pathlib.Path | None = None) -> tuple[pathlib.Path | str, bool]

      
      Get the output path.

      :param output_path: The output path. Defaults to None.
      :type output_path: str, optional

      :returns: The output path and whether it is remote.
      :rtype: tuple[Path | str, bool]















      ..
          !! processed by numpydoc !!


   .. py:method:: to_dict(yaml_convert: bool = False) -> dict[str, Any]

      
      Convert the configuration to a dictionary.

      :param yaml_convert: Whether to convert the configuration to a yaml format. Defaults to False.
      :type yaml_convert: bool, optional

      :returns: The configuration as a dictionary.
      :rtype: dict















      ..
          !! processed by numpydoc !!


   .. py:method:: __repr__() -> str

      
      Return the string representation of the configuration.

      :returns: The string representation of the configuration.
      :rtype: str















      ..
          !! processed by numpydoc !!



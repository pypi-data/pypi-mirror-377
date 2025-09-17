# Copyright (C) 2023-2025 SIPez LLC.  All rights reserved.

import typing
import pydantic
import pyjq
import vcon.pydantic_utils
import py_vcon_server.processor

logger = py_vcon_server.logging_utils.init_logger(__name__)

class JQInitOptions(py_vcon_server.processor.VconProcessorInitOptions):
  """
  JQInitOptions is passed to the jq processor when it is initialized.
  JQInitOptions extends VconProcessorInitOptions, but does not add any
  new fields.  
  """


class JQOptions(py_vcon_server.processor.VconProcessorOptions):
  """
  JOptions is passed to the jq processor when processing the VconProcessorIO.
  JQOptions adds the jq_queries to VconProcessorOptions which defines the
  set of querries to perform on the VconProcessorIO.
  """
  jq_queries: typing.Dict[str, str] = pydantic.Field(
      title = "dict of JQ queries to perform on VconProcessorIO input.",
      examples = [{
          "party_count": ".parties | length",
          "first_dialog_type": ".vcons[0].dialog[0].type",
          "party0_has_email_address": ".vcons[0].parties[0].email | length > 0"
        }],
      default = {}
    )


class JQProcessor(py_vcon_server.processor.VconProcessor):
  """ Processor to set VconProcessorIO parameters from JS queries on VconProcessorIO """

  def __init__(
    self,
    init_options: JQInitOptions
    ):

    super().__init__(
      "set VconProcessorIO parameter(s) from result(s) of JQ query(s) on VconPRocessorIO input",
      "For each name, value pair in jq_queries field in ProcessorOptions, save the result of the JQ query defined in value in the VconProcessorIO parameter in name.  The query is into a dict representation of the input VconProcessorIO.  At the top level this dict contains: 'vcons', an array of the zero or more input vCons and 'parameters', the dict of parameters in the input VconProcessorIO.",
      "0.0.1",
      init_options,
      JQOptions,
      False # modifies a Vcon
      )


  async def process(self,
    processor_input: py_vcon_server.processor.VconProcessorIO,
    options: JQOptions
    ) -> py_vcon_server.processor.VconProcessorIO:
    """
    Set the VconProcessorIO parameters (keys in jq_queries field) to the result of the query(s) (query defined in string value of jq_queries dict).  Does not modify the vCons.
    """

    # TODO: may want to package this up as a VconProcessorIO method

    # Create the dict into which the queries are to be done.
    # This is a dict rep for the VconProcessorIO input.
    dict_to_query = {
        "vcons": [],
        "parameters": processor_input._parameters
      }
    # Add dict form of vCons
    for mVcon in processor_input._vcons:
      # Need to use the object form so that we can get verified or locally signed dict form
      a_vcon = await mVcon.get_vcon(py_vcon_server.processor.VconTypes.OBJECT)
      logger.debug("jq processor adding vcon state={}".format(a_vcon._state))
      dict_to_query["vcons"].append(a_vcon.dumpd(signed = False, deepcopy = False))

    if(len(options.jq_queries.keys()) < 1):
      logger.warning("jq processor option 'jq_queries' is empty")

    for parameter_name in options.jq_queries.keys():
      logger.debug("parameter: \"{}\" defined by jq query: '{}'".format(
          parameter_name,
          options.jq_queries[parameter_name]
        ))

      query_result = pyjq.all(options.jq_queries[parameter_name],
        dict_to_query)[0]
      logger.debug("setting parameter: {} to {}".format(
          parameter_name,
          query_result
        ))
      processor_input.set_parameter(parameter_name, query_result)

    return(processor_input)


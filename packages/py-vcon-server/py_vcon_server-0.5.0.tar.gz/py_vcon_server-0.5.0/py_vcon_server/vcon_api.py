# Copyright (C) 2023-2025 SIPez LLC.  All rights reserved.
""" Implementation of the Vcon API entry points """

import os
import typing
import copy
import pydantic
import fastapi
import fastapi.responses
import py_vcon_server.db
import py_vcon_server.processor
import py_vcon_server.logging_utils
import vcon
import vcon.utils
import vcon.pydantic_utils

logger = py_vcon_server.logging_utils.init_logger(__name__)


def init(restapi):
  @restapi.get("/vcon/{vcon_uuid}",
    response_model = typing.Union[
        py_vcon_server.processor.VconUnsignedObject,
        py_vcon_server.processor.VconSignedObject,
        py_vcon_server.processor.VconEncryptedObject
      ],
    responses = py_vcon_server.restful_api.ERROR_RESPONSES,
    tags = [ py_vcon_server.restful_api.VCON_TAG ])
  async def get_vcon(vcon_uuid: str):
    """
    Get the vCon object identified by the given UUID.

    Returns: dict - vCon object which may be in the unencrypted, signed or encrypted JSON forms
    """

    try:
      logger.debug("getting vcon UUID: {}".format(vcon_uuid))
      vCon = await py_vcon_server.db.VCON_STORAGE.get(vcon_uuid)

    except py_vcon_server.db.VconNotFound as e:
      py_vcon_server.restful_api.log_exception(e)
      return(py_vcon_server.restful_api.NotFoundResponse("vCon UUID: {} not found".format(vcon_uuid)))

    except Exception as e:
      py_vcon_server.restful_api.log_exception(e)
      return(py_vcon_server.restful_api.InternalErrorResponse(e))

    logger.debug(
      "Returning whole vcon for {} found: {}".format(vcon_uuid, vCon is not None))

    return(fastapi.responses.JSONResponse(content=vCon.dumpd()))

  @restapi.post("/vcon",
    status_code = 204,
    responses = py_vcon_server.restful_api.ERROR_RESPONSES,
    tags = [ py_vcon_server.restful_api.VCON_TAG ])
  async def post_vcon(inbound_vcon: typing.Union[
      py_vcon_server.processor.VconUnsignedObject,
      py_vcon_server.processor.VconSignedObject,
      py_vcon_server.processor.VconEncryptedObject
    ]):
    """
    Store the given vCon in VconStorage, replace if it exists for the given UUID
    """
    try:
      vcon_dict = vcon.pydantic_utils.get_dict(inbound_vcon, exclude_none = True)

      vcon_uuid = vcon_dict.get("uuid", None)
      logger.debug("setting vcon UUID: {}".format(vcon_uuid))

      if(vcon_uuid is None or len(vcon_uuid) < 1):
        return(py_vcon_server.restful_api.ValidationError("vCon UUID: not set"))

      vcon_object = vcon.Vcon()
      vcon_object.loadd(vcon_dict)

      await py_vcon_server.db.VCON_STORAGE.set(vcon_dict)

    except Exception as e:
      py_vcon_server.restful_api.log_exception(e)
      return(py_vcon_server.restful_api.InternalErrorResponse(e))

    # No return should emmit 204, no content

  @restapi.delete("/vcon/{vcon_uuid}",
    status_code = 204,
    responses = py_vcon_server.restful_api.ERROR_RESPONSES,
    tags = [ py_vcon_server.restful_api.VCON_TAG ])
  async def delete_vcon(vcon_uuid: str):
    """
    Delete the vCon idenfied by the given UUID from VconStorage

    Returns: None
    """
    try:
      logger.debug("deleting vcon UUID: {}".format(vcon_uuid))
      await py_vcon_server.db.VCON_STORAGE.delete(vcon_uuid)

    except Exception as e:
      py_vcon_server.restful_api.log_exception(e)
      return(py_vcon_server.restful_api.InternalErrorResponse(e))

    logger.debug("Deleted vcon: UUID={}".format(vcon_uuid))

    # no return should cause 204, no content

  @restapi.get("/vcon/{vcon_uuid}/jq",
    responses = py_vcon_server.restful_api.ERROR_RESPONSES,
    tags = [ py_vcon_server.restful_api.VCON_TAG ])
  async def get_vcon_jq_transform(vcon_uuid: str, jq_transform: str):
    """
    Apply the given jq transform to the vCon identified by the given UUID and return the results.

    Returns: list - containing jq tranform of the vCon.
    """
    try:
      logger.info("vcon UID: {} jq transform string: {}".format(vcon_uuid, jq_transform))
      transform_result = await py_vcon_server.db.VCON_STORAGE.jq_query(vcon_uuid, jq_transform)
      logger.debug("jq  transform result: {}".format(transform_result))

    except Exception as e:
      py_vcon_server.restful_api.log_exception(e)
      return(py_vcon_server.restful_api.InternalErrorResponse(e))

    return(fastapi.responses.JSONResponse(content=transform_result))

  @restapi.get("/vcon/{vcon_uuid}/jsonpath",
    responses = py_vcon_server.restful_api.ERROR_RESPONSES,
    tags = [ py_vcon_server.restful_api.VCON_TAG ])
  async def get_vcon_jsonpath_query(vcon_uuid: str, path_string: str):
    """
    Apply the given JSONpath query to the vCon idntified by the given UUID.

    Returns: list - the JSONpath query results
    """

    try:
      logger.info("vcon UID: {} jsonpath query string: {}".format(vcon_uuid, path_string))
      query_result = await py_vcon_server.db.VCON_STORAGE.json_path_query(vcon_uuid, path_string)
      logger.debug("jsonpath query result: {}".format(query_result))

    except Exception as e:
      py_vcon_server.restful_api.log_exception(e)
      return(py_vcon_server.restful_api.InternalErrorResponse(e))

    return(fastapi.responses.JSONResponse(content=query_result))


  processor_names = py_vcon_server.processor.VconProcessorRegistry.get_processor_names()
  for processor_name in processor_names:
    processor_inst = py_vcon_server.processor.VconProcessorRegistry.get_processor_instance(
      processor_name)

    @restapi.post("/process/{{vcon_uuid}}/{}".format(processor_name),
      summary = processor_inst.title(),
      description = processor_inst.description(),
      response_model = py_vcon_server.processor.VconProcessorOutput,
      responses = py_vcon_server.restful_api.ERROR_RESPONSES,
      tags = [ py_vcon_server.restful_api.PROCESSOR_TAG ])
    async def run_vcon_processor(
      options: processor_inst.processor_options_class(),
      vcon_uuid: str,
      request: fastapi.Request,
      commit_changes: bool = False,
      return_whole_vcon: bool = True
      ) -> str:

      try:
        #processor_name = processor_type_dict[type(options)]
        path = request.url.path
        processor_name_from_path = os.path.basename(path)

        # Get the processor form the registry
        processor_inst = py_vcon_server.processor.VconProcessorRegistry.get_processor_instance(
          processor_name_from_path)

        # TODO: take a real lock on the vCon

        processor_input = py_vcon_server.processor.VconProcessorIO(py_vcon_server.db.VCON_STORAGE)
        await processor_input.add_vcon(vcon_uuid, "fake_lock", False)

        # format_options for dynamic options
        formatted_options_dict = processor_input.format_parameters_to_options(vcon.pydantic_utils.get_dict(options))
        processor_type_options = processor_inst.processor_options_class()(** formatted_options_dict)

        logger.debug("type: {} path: {} ({}) options: {} processor: {}".format(
            processor_name,
            path,
            type(processor_type_options),
            processor_type_options,
            processor_name_from_path
          ))

        # Run the processor
        processor_output = await processor_inst.process(
          processor_input,
          processor_type_options)

        if(commit_changes):
          # Save changed Vcons
          await py_vcon_server.db.VCON_STORAGE.commit(processor_output)

        # TODO: release vCon lock

        # Commit jobs to be queued.
        # This is done here as opposed to in the queue processor as we
        # have not yet implemented vCon locking.  It may often be expected that
        # modification to vCon(s) in a pipeline have been committed at the time
        # the pipeline queues a job for the vCon.
        await processor_output.commit_queue_jobs(py_vcon_server.queue.JOB_QUEUE)

        # Get serializable output
        # TODO: don't return whole Vcon if not return_whole_vcon
        response_output = await processor_output.get_output()

      except py_vcon_server.db.VconNotFound as e:
        py_vcon_server.restful_api.log_exception(e)
        return(py_vcon_server.restful_api.NotFoundResponse("vCon UUID: {} not found".format(vcon_uuid)))

      except Exception as e:
        # Add options to response for easier diagnostics and error reporting
        exception_error_content = py_vcon_server.restful_api.InternalErrorResponse(e,
            {
              "processor_options": vcon.pydantic_utils.get_dict(processor_type_options, exclude_none = True),
              "processor_name": processor_name_from_path
            })
        return(exception_error_content)

      return(fastapi.responses.JSONResponse(content = vcon.pydantic_utils.get_dict(response_output, exclude_none = True)))


  processor_names = py_vcon_server.processor.VconProcessorRegistry.get_processor_names()
  for processor_name in processor_names:
    processor_inst = py_vcon_server.processor.VconProcessorRegistry.get_processor_instance(
      processor_name)

    input_class_fields = {
        'processor_io': (py_vcon_server.processor.VconProcessorOutput, "processor IO"),
        'processor_options': (processor_inst.processor_options_class(), "processor options")
      }
    input_class_name = processor_inst.processor_options_class().__name__.split(".")[-1].replace("Options", "IO")
    processor_input_class = pydantic.create_model(
        input_class_name,
        __base__=pydantic.BaseModel, # need to figure how to add this: **vcon.pydantic_utils.SET_ALLOW),
        **input_class_fields
      )

    @restapi.post("/processIO/{}".format(processor_name),
      summary = processor_inst.title(),
      description = processor_inst.description(),
      response_model = py_vcon_server.processor.VconProcessorOutput,
      responses = py_vcon_server.restful_api.ERROR_RESPONSES,
      tags = [ py_vcon_server.restful_api.PROCESSOR_TAG ])
    async def run_vcon_processor_io(
      processor_input: processor_input_class,
      request: fastapi.Request,
      commit_changes: bool = False,
      ) -> str:

      try:
        #processor_name = processor_type_dict[type(options)]
        path = request.url.path
        processor_name_from_path = os.path.basename(path)

        # Get the processor form the registry
        processor_inst = py_vcon_server.processor.VconProcessorRegistry.get_processor_instance(
          processor_name_from_path)

        # TODO: take a real lock on the vCon
        processor_input_dict = vcon.pydantic_utils.get_dict(processor_input, exclude_none = True)
        processor_io = py_vcon_server.processor.VconProcessorIO(py_vcon_server.db.VCON_STORAGE)

        # Copy the vcons to the input
        if( processor_input_dict and
            "processor_io" in processor_input_dict and
            "vcons" in processor_input_dict["processor_io"]
          ):
          for aVcon in processor_input_dict["processor_io"]["vcons"]:
            await processor_io.add_vcon(aVcon, "fake_lock", False)

        # Copy the parameters to the input
        if( processor_input_dict and
            "processor_io" in processor_input_dict and
            "parameters" in processor_input_dict["processor_io"]
          ):
          for parameter_name, parameter_value in processor_input_dict["processor_io"]["parameters"].items():
            processor_io.set_parameter(parameter_name, parameter_value)

        # format_options for dynamic options
        formatted_options_dict = processor_io.format_parameters_to_options(processor_input_dict["processor_options"])
        processor_type_options = processor_inst.processor_options_class()(** formatted_options_dict)

        logger.debug("type: {} path: {} ({}) options: {} processor: {}".format(
            processor_name,
            path,
            type(processor_type_options),
            processor_type_options,
            processor_name_from_path
          ))

        # Run the processor
        processor_output = await processor_inst.process(
          processor_io,
          processor_type_options)

        if(commit_changes):
          # Save changed Vcons
          await py_vcon_server.db.VCON_STORAGE.commit(processor_output)

        # TODO: release vCon lock

        # Commit jobs to be queued.
        # This is done here as opposed to in the queue processor as we
        # have not yet implemented vCon locking.  It may often be expected that
        # modification to vCon(s) in a pipeline have been committed at the time
        # the pipeline queues a job for the vCon.
        await processor_output.commit_queue_jobs(py_vcon_server.queue.JOB_QUEUE)

        # Get serializable output
        response_output = await processor_output.get_output()

      except Exception as e:
        py_vcon_server.restful_api.log_exception(e)
        # Add options to response for easier diagnostics and error reporting
        exception_error_content = py_vcon_server.restful_api.InternalErrorResponse(e,
            {
              "processor_options": vcon.pydantic_utils.get_dict(processor_type_options, exclude_none = True),
              "processor_name": processor_name_from_path

            })
        return(exception_error_content)

      return(fastapi.responses.JSONResponse(content = vcon.pydantic_utils.get_dict(response_output, exclude_none = True)))


  async def do_run_pipeline(
      vCon: typing.Union[vcon.Vcon, str],
      vcon_in_storage: bool,
      pipeline_name: str,
      save_vcons: bool,
      return_results: bool
    ):
      # TODO: get vCon lock if this is a write pipeline
      if(vcon_in_storage):
        lock_key = "fake_lock"
      else:
        lock_key = None

      # Build the VconProcessorIO
      pipeline_input = py_vcon_server.processor.VconProcessorIO(py_vcon_server.db.VCON_STORAGE)
      await pipeline_input.add_vcon(vCon, lock_key, False)

      # Get the pipeline
      pipe_def = await py_vcon_server.pipeline.PIPELINE_DB.get_pipeline(pipeline_name)

      # Run the vCon through the pipeline
      pipeline_runner = py_vcon_server.pipeline.PipelineRunner(pipe_def, pipeline_name)
      pipeline_output = await pipeline_runner.run(pipeline_input)

      # Optionally save vCons
      if(save_vcons):
        # Save changed Vcons
        await py_vcon_server.db.VCON_STORAGE.commit(pipeline_output)

      # TODO: release the vCon lock if taken
      if(lock_key is not None):
        pass

      # Commit jobs to be queued.
      # This is done here as opposed to in the queue processor as we
      # have not yet implemented vCon locking.  It may often be expected that
      # modification to vCon(s) in a pipeline have been committed at the time
      # the pipeline queues a job for the vCon.
      await pipeline_output.commit_queue_jobs(py_vcon_server.queue.JOB_QUEUE)

      # Optionally return the pipeline output
      if(return_results):
        pipe_out = await pipeline_output.get_output()
        return(fastapi.responses.JSONResponse(content = vcon.pydantic_utils.get_dict(pipe_out, exclude_none=True)))


  pipeline_responses = copy.deepcopy(py_vcon_server.restful_api.ERROR_RESPONSES)
  pipeline_responses[200] = { "model": py_vcon_server.processor.VconProcessorOutput}
  pipeline_responses[204] = { "model": None }
  @restapi.post("/pipeline/{name}/run",
    response_model = typing.Union[py_vcon_server.processor.VconProcessorOutput, None],
    summary = "Run a pipeline of processors on the vCon given in the request body",
    tags = [ py_vcon_server.restful_api.PIPELINE_RUN_TAG ])
  async def run_pipeline(
      name: str,
      vCon: typing.Union[
          py_vcon_server.processor.VconUnsignedObject,
          py_vcon_server.processor.VconSignedObject,
          py_vcon_server.processor.VconEncryptedObject
        ],
      save_vcons: bool = False,
      return_results: bool = True
    ):
    """
    Run the given Vcon through the named pipeline.

    Note: the following **PipelineOptions** are ignored when the pipeline is run via this RESTful interface:

      **failure_queue** assumed to be None <br>
      **success_queue** assumed to be None <br>
      **save_vcons** <br>

    Parameters:

      **name** (str) - name of the pipeline defined in the pipeline DB

      **vCon** (py_vcon_server.processor.VconUnsignedObject or 
        py_vcon_server.processor.VconSignedObject or
        py_vcon_server.processor.VconEncryptObject) - 
          vCon from body, assumes vCon/UUID does NOT exist in storage

      **save_vcons** (bool) - save/update the vCon(s) to the vCon Storage after pipeline
          processing.  Ignores/overides the **PipelineOptions.save_vcons**

      **return_results** (bool) - return the VconProcessorOutput from the end of the pipeline

    Returns:

      If return_results is true, return the VconProcessorOutput, otherwise return None
    """

    logger.debug("run_pipeline( pipeline: {} vCon with UUID: {} save: {} return: {}".format(
        name,
        vcon.pydantic_utils.get_dict(vCon, exclude_none=True).get("uuid", None),
        save_vcons,
        return_results
      ))

    try:
      vcon_object = vcon.Vcon()
      vcon_object.loadd(vcon.pydantic_utils.get_dict(vCon, exclude_none=True))

      # TODO: verify the UUID for the given vCon does not exist in storage

      return(await do_run_pipeline(vcon_object, False, name, save_vcons, return_results))

    except py_vcon_server.pipeline.PipelineNotFound as nf:
      logger.info("Error: pipeline: {} not found".format(name))
      return(py_vcon_server.restful_api.NotFoundResponse("pipeline: {} not found".format(name)))

    except py_vcon_server.pipeline.PipelineTimeout as timeout_exception:
      logger.info("Error: pipeline: {} input Vcon with uuid: {} processing time exeeded timeout".format(
          name,
          vcon_object.dict
        ))
      py_vcon_server.restful_api.log_exception(timeout_exception)
      return(py_vcon_server.restful_api.ProcessingTimeout(
          "Error: pipeline: {} input Vcon with uuid: {} processing time exeeded timeout".format(
            name,
            vcon_object.uuid,
          )
        ))

    except Exception as e:
      py_vcon_server.restful_api.log_exception(e)
      return(py_vcon_server.restful_api.InternalErrorResponse(e))


  @restapi.post("/pipeline/{name}/run/{uuid}",
    response_model = typing.Union[py_vcon_server.processor.VconProcessorOutput, None],
    summary = "Run a pipeline of processors on the vCon in storage identified by UUID",
    tags = [ py_vcon_server.restful_api.PIPELINE_RUN_TAG ])
  async def run_pipeline_uuid(
      name: str,
      uuid: str,
      save_vcons: bool = False,
      return_results: bool = True
    ):
    """
    Run the vCon identified by the given UUID through the named pipeline.

    Note: the following **PipelineOptions** are ignored when the pipeline is run via this RESTful interface:

      **failure_queue** assumed to be None <br>
      **success_queue** assumed to be None <br>
      **save_vcons** <br>

    Parameters:

      **name** (str) - name of the pipeline defined in the pipeline DB

      **uuid** (str) - UUID of the vCon in the vCon Storage

      **save_vcons** (bool) - save/update the vCon(s) to the vCon Storage after pipeline
          processing.  Ignores/overides the **PipelineOptions.save_vcons**

      **return_results** (bool) - return the VconProcessorOutput from the end of the pipeline

    Returns:

      If return_results is true, return the VconProcessorOutput, otherwise return None
    """

    logger.debug("run_pipeline_uuid( pipeline: {} uuid: {} save: {} return: {}".format(
        name,
        uuid,
        save_vcons,
        return_results
      ))

    try:
      return(await do_run_pipeline(uuid, True, name, save_vcons, return_results))

    except py_vcon_server.pipeline.PipelineNotFound as nf:
      logger.info("Error: pipeline: {} not found".format(name))
      return(py_vcon_server.restful_api.NotFoundResponse("pipeline: {} not found".format(name)))

    except py_vcon_server.pipeline.PipelineTimeout as timeout_exception:
      logger.info("Error: pipeline: {} uuid: {} processing time exeeded timeout".format(
          name,
          uuid
        ))
      py_vcon_server.restful_api.log_exception(timeout_exception)
      return(py_vcon_server.restful_api.ProcessingTimeout(
          "Error: pipeline: {} uuid: {} processing time exeeded timeout".format(
            name,
            uuid,
          )
        ))

    except Exception as e:
      py_vcon_server.restful_api.log_exception(e)
      return(py_vcon_server.restful_api.InternalErrorResponse(e))



# Copyright (C) 2023-2025 SIPez LLC.  All rights reserved.
""" Unit tests for Pipeline and related data objects """
import pydantic
import pytest
import pytest_asyncio
import copy
import fastapi.testclient
import vcon
import vcon.pydantic_utils
import py_vcon_server.pipeline
from py_vcon_server.settings import PIPELINE_DB_URL
from common_setup import UUID, make_inline_audio_vcon, make_2_party_tel_vcon

PIPELINE_DB = None
TIMEOUT = 60.0

@pytest_asyncio.fixture(autouse=True)
async def pipeline_db():
  """ Setup Pipeline DB connection before test """
  print("initializing PipelineDB connection")
  pdb = py_vcon_server.pipeline.PipelineDb(PIPELINE_DB_URL)
  print("initialized PipelineDB connection")
  global PIPELINE_DB
  PIPELINE_DB = pdb

  # Turn off workers so as to not interfer with queues used in testing
  # and workers created in these unit tests.
  num_workers = py_vcon_server.settings.NUM_WORKERS
  py_vcon_server.settings.NUM_WORKERS = 0
  #do_bg = py_vcon_server.RUN_BACKGROUND_JOBS
  #py_vcon_server.RUN_BACKGROUND_JOBS = False

  # wait until teardown time
  yield pdb

  # Shutdown the Vcon storage after test
  print("shutting down PipelineDB connection")
  PIPELINE_DB = None
  await pdb.shutdown()
  print("shutdown PipelineDB connection")


  # Restore workers config
  py_vcon_server.settings.NUM_WORKERS = num_workers
  #py_vcon_server.RUN_BACKGROUND_JOBS = do_bg


def test_pipeline_objects():

  proc1 = py_vcon_server.pipeline.PipelineProcessor(processor_name = "foo", processor_options = {"a": 3, "b": "abc"})
  print("options: {}".format(proc1.processor_options))
  assert(proc1.processor_name == "foo")
  assert(proc1.processor_options.input_vcon_index == 0)
  assert(proc1.processor_options.a == 3)
  assert(proc1.processor_options.b == "abc")
  assert("b" in vcon.pydantic_utils.get_fields_set(proc1.processor_options))
  assert("c" not in vcon.pydantic_utils.get_fields_set(proc1.processor_options))

  processor_inst = py_vcon_server.processor.VconProcessorRegistry.get_processor_instance(
      "whisper_base"
    )
  whisp_opts = processor_inst.processor_options_class()(**{"output_types": ["vendor"]})
  proc2  = py_vcon_server.pipeline.PipelineProcessor(processor_name = "whisper_base", processor_options = whisp_opts)
  assert(proc2.processor_options.output_types == ["vendor"])

  pipe1_opts = py_vcon_server.pipeline.PipelineOptions(
      save_vcons = False,
      timeout = 30,
      failure_queue = "bad_jobs"
    )

  try:
    py_vcon_server.pipeline.PipelineOptions(
        timeout = "ddd"
      )
    raise Exception("Should raise validation error for timeout not an int")
  except vcon.pydantic_utils.ValidationErrorType as ve:
    # Expected
    #print("ve dir: {}".format(dir(ve)))
    errors_dict = ve.errors()
    #print("error: {}".format(errors_dict[0]))
    assert(errors_dict[0]["loc"][0] == "timeout")
    assert(errors_dict[0]["type"] == vcon.pydantic_utils.IntParseError
      or errors_dict[0]["type"] == vcon.pydantic_utils.FloatParseError)
    assert(errors_dict[1]["loc"][0] == "timeout")
    assert(errors_dict[1]["type"] == vcon.pydantic_utils.IntParseError
      or errors_dict[1]["type"] == vcon.pydantic_utils.FloatParseError)
    print("validation error: {}".format(errors_dict[0]["msg"]))

  pipe1_def = py_vcon_server.pipeline.PipelineDefinition(
      pipeline_options = pipe1_opts,
      processors = [ proc1, proc2 ]
    )

  print("pipe1: {}".format(pipe1_def))

  try:
    py_vcon_server.pipeline.PipelineDefinition(
        pipeline_options = {
            "timeout": "ddd"
          },
        processors = [ proc1, proc2 ]
      )
    raise Exception("Should raise validation error for timeout not an int")
  except vcon.pydantic_utils.ValidationErrorType as ve:
    # Expected
    #print("ve dir: {}".format(dir(ve)))
    errors_dict = ve.errors()
    #print("error: {}".format(errors_dict[0]))
    assert(errors_dict[0]["loc"][0] == "pipeline_options")
    assert(errors_dict[0]["loc"][1] == "timeout")
    assert(errors_dict[0]["type"] == vcon.pydantic_utils.IntParseError
      or errors_dict[0]["type"] == vcon.pydantic_utils.FloatParseError)
    assert(errors_dict[1]["loc"][1] == "timeout")
    assert(errors_dict[1]["type"] == vcon.pydantic_utils.IntParseError
      or errors_dict[1]["type"] == vcon.pydantic_utils.FloatParseError)
    print("validation error: {}".format(errors_dict[0]["msg"]))

  pipe_def_dict = {
    "pipeline_options": {
        "timeout": 33
      },
    "processors": [
        {
          "processor_name": "foo",
          "processor_options": {
              "a": 3,
              "b": "abc"
            }
        },
        {
          "processor_name": "whisper_base",
          "processor_options":  {
              "output_types": ["vendor"]
            }
        }
      ]
  }

  pipe3_def = py_vcon_server.pipeline.PipelineDefinition(**pipe_def_dict)

  assert(pipe3_def.pipeline_options.timeout == 33)
  assert(len(pipe3_def.processors) == 2)
  assert(pipe3_def.processors[0].processor_name == "foo")
  assert(pipe3_def.processors[0].processor_options.a == 3)
  assert(pipe3_def.processors[0].processor_options.b == "abc")
  assert(pipe3_def.processors[1].processor_name == "whisper_base")
  assert(pipe3_def.processors[1].processor_options.output_types == ["vendor"])

PIPE_DEF1_DICT = {
  "pipeline_options": {
      "timeout": 33
    },
  "processors": [
      {
        "processor_name": "foo",
        "processor_options": {
            "a": 3,
            "b": "abc"
          }
      },
      {
        "processor_name": "whisper_base",
        "processor_options":  {
            "output_types": ["vendor"]
          }
      }
    ]
}

test_timeout = 0.1
PIPE_DEF2_DICT = {
  "pipeline_options": {
      "timeout": test_timeout
    },
  "processors": [
      {
        "processor_name": "deepgram",
        "processor_options": {
          }
      },
      {
        "processor_name": "openai_chat_completion",
        "processor_options":  {
          }
      }
    ]
}

PIPE_CONDITIONAL_DICT = {
  "pipeline_options": {
      "timeout": 10.0
    },
  "processors": [
      {
        "processor_name": "jq",
        "processor_options": {
          "jq_queries": {
              "has_dialogs": ".vcons[0].dialog[0].url | length > 0",
              "party0_has_email_address": ".vcons[0].parties[0].email | length > 0"
            }
          }
        },
      {
        "processor_name": "whisper_base",
        "processor_options": {
            "format_options": {
                "should_process": "{has_dialogs}"
              }
          }
        },
      {
        "processor_name": "send_email",
        "processor_options": {
            "format_options": {
                "should_process": "{party0_has_email_address}"
              },
            "smtp_host": "foo"
          }
        },
      {
        "processor_name": "set_parameters",
        "processor_options": {
            "parameters": {
                "party0_has_email_address": "nobody@example.com"
              }
          }
        }
    ]
}

@pytest.mark.asyncio
async def test_pipeline_db():

  assert(PIPELINE_DB is not None)

  # Clean up reminents from prior runs
  try:
    await PIPELINE_DB.delete_pipeline("first_pipe")
  except py_vcon_server.pipeline.PipelineNotFound:
    # Ignore as this may have been cleaned up in prior test run
    pass

  await PIPELINE_DB.set_pipeline("first_pipe", PIPE_DEF1_DICT)

  pipe_got = await PIPELINE_DB.get_pipeline("first_pipe")
  assert(pipe_got.pipeline_options.timeout == 33)
  assert(len(pipe_got.processors) == 2)
  assert(pipe_got.processors[0].processor_name == "foo")
  assert(pipe_got.processors[0].processor_options.a == 3)
  assert(pipe_got.processors[0].processor_options.b == "abc")
  assert(pipe_got.processors[1].processor_name == "whisper_base")
  assert(pipe_got.processors[1].processor_options.output_types == ["vendor"])

  pipeline_names = await PIPELINE_DB.get_pipeline_names()
  print("name type: {}".format(type(pipeline_names)))
  # The test DB may be used for other things, so cannot assume only 1 pipeline
  assert("first_pipe" in pipeline_names)

  await PIPELINE_DB.delete_pipeline("first_pipe")

  pipeline_names = await PIPELINE_DB.get_pipeline_names()
  print("name type: {}".format(type(pipeline_names)))
  # The test DB may be used for other things, so cannot assume only 1 pipeline
  assert("first_pipe" not in pipeline_names)

  try:
    await PIPELINE_DB.delete_pipeline("first_pipe")
    raise Exception("Expected delete to fail with not found")
  except py_vcon_server.pipeline.PipelineNotFound:
    # expected as it was already deleted
    pass

  try:
    pipe_got = await PIPELINE_DB.get_pipeline("first_pipe")
    raise Exception("Expected get to fail with not found")
  except py_vcon_server.pipeline.PipelineNotFound:
    # expected as it was already deleted
    pass


@pytest.mark.asyncio
async def test_pipeline_restapi(make_inline_audio_vcon: vcon.Vcon):

  pipe_name = "unit_test_pipe1"
  pipe2_name = "unit_test_pipe2"
  bad_pipe_name = pipe_name + "_bad"
  with fastapi.testclient.TestClient(py_vcon_server.restapi) as client:
    # Clean up junk left over from prior tests
    delete_response = client.delete(
        "/pipeline/{}".format(
          pipe_name
        )
      )
    assert(delete_response.status_code == 404 or
      delete_response.status_code == 204)
    delete_response = client.delete(
        "/pipeline/{}".format(
          pipe2_name
        )
      )
    assert(delete_response.status_code == 404 or
      delete_response.status_code == 204)

    get_response = client.get(
        "/pipelines"
      )
    assert(get_response.status_code == 200)
    pipe_list = get_response.json()
    print("pipe list: {}".format(pipe_list))
    assert(isinstance(pipe_list, list))
    assert(not pipe_name in pipe_list)
    assert(not pipe2_name in pipe_list)
    assert(not bad_pipe_name in pipe_list)

    # attemt to add a invalid pipeline
    set_response = client.put(
        "/pipeline/{}".format(
          bad_pipe_name
        ),
        json = {"foo": "bar"}, 
        params = { "validate_processor_options": True}
      )
    assert(set_response.status_code == 422)

    set_response = client.put(
        "/pipeline/{}".format(
          pipe_name
        ),
        json = PIPE_DEF1_DICT, 
        params = { "validate_processor_options": True}
      )
    resp_json = set_response.json()
    print("response content: {}".format(resp_json))
    assert(set_response.status_code == 422)
    assert(resp_json["detail"] == "processor: foo not registered")

    set_response = client.put(
        "/pipeline/{}".format(
          pipe_name
        ),
        json = PIPE_DEF1_DICT,
        params = { "validate_processor_options": False}
      )
    print("response dir: {}".format(dir(set_response)))
    resp_content = set_response.content
    print("response content: {}".format(resp_content))
    assert(set_response.status_code == 204)
    assert(len(resp_content) == 0)
    #assert(resp_json["detail"] == "processor: foo not registered")

    print("PIPE_DEF2: {}".format(PIPE_DEF2_DICT))
    assert(PIPE_DEF2_DICT["pipeline_options"]["timeout"] == test_timeout)
    set_response = client.put(
        "/pipeline/{}".format(
          pipe2_name
        ),
        json = PIPE_DEF2_DICT, 
        params = { "validate_processor_options": True}
      )
    resp_content = set_response.content
    if(set_response.status_code != 204):
      print("put: /pipeline/{} returned: {} {}".format(
          pipe2_name,
          set_response.status_code,
          resp_content 
        ))
    assert(set_response.status_code == 204)
    assert(len(resp_content) == 0)

    get_response = client.get(
        "/pipelines"
      )
    assert(get_response.status_code == 200)
    pipe_list = get_response.json()
    print("pipe list: {}".format(pipe_list))
    assert(isinstance(pipe_list, list))
    assert(pipe_name in pipe_list)
    assert(pipe2_name in pipe_list)
    assert(not bad_pipe_name in pipe_list)

    get_response = client.get(
        "/pipeline/{}".format(
          pipe2_name
      ))
    assert(get_response.status_code == 200)
    pipe2_def_dict = get_response.json()
    assert(pipe2_def_dict["pipeline_options"]["timeout"] == test_timeout)

    get_response = client.get(
        "/pipeline/{}".format(
          bad_pipe_name
        )
      )

    assert(get_response.status_code == 404)

    get_response = client.get(
        "/pipeline/{}".format(
          pipe_name
        )
      )

    assert(get_response.status_code == 200)
    pipe_json = get_response.json()
    pipe_def = py_vcon_server.pipeline.PipelineDefinition(**pipe_json)
    print("got pipeline: {}".format(pipe_json))
    assert(pipe_def.pipeline_options.timeout == 33)
    assert(len(pipe_def.processors) == 2)
    assert(pipe_def.processors[0].processor_name == "foo")
    assert(pipe_def.processors[0].processor_options.a == 3)
    assert(pipe_def.processors[0].processor_options.b == "abc")
    assert(pipe_def.processors[1].processor_name == "whisper_base")
    assert(pipe_def.processors[1].processor_options.output_types == ["vendor"])

    # put the vcon in Storage in a known state
    assert(len(make_inline_audio_vcon.dialog) == 1)
    assert(len(make_inline_audio_vcon.analysis) == 0)
    inline_audio_vcon_dict = make_inline_audio_vcon.dumpd()
    test_parsed_model = vcon.pydantic_utils.validate_construct(py_vcon_server.processor.VconUnsignedObject, inline_audio_vcon_dict)
    set_response = client.post("/vcon", json = inline_audio_vcon_dict)
    assert(set_response.status_code == 204)
    assert(make_inline_audio_vcon.uuid == UUID)

    # non-existing pipeline name
    post_response = client.post(
      "/pipeline/{}/run/{}".format(
          "bogus_pipeline",
          UUID
        ),
        params = {
            "save_vcons": False,
            "return_results": True
          },
        headers={"accept": "application/json"},
      )
    pipeline_out_dict = post_response.json()
    print("pipe out: {}".format(pipeline_out_dict))
    assert(post_response.status_code == 404)

    # non-existing vCon UUID
    post_response = client.post(
      "/pipeline/{}/run/{}".format(
          pipe2_name,
          "bogus_UUID"
        ),
        params = {
            "save_vcons": False,
            "return_results": True
          },
        headers={"accept": "application/json"},
      )
    pipeline_out_dict = post_response.json()
    print("pipe out: {}".format(pipeline_out_dict))
    assert(post_response.status_code == 500)
    # Run the pipeline on a simple/small vCon, should timeout
    post_response = client.post(
      "/pipeline/{}/run/{}".format(
          pipe2_name,
          UUID
        ),
        params = {
            "save_vcons": False,
            "return_results": True
          },
        headers={"accept": "application/json"},
      )
    pipeline_out_dict = post_response.json()
    print("pipe out: {}".format(pipeline_out_dict))
    if(post_response.status_code == 200):
      # TODO: this should fail with timeout of 0.1
      assert(len(pipeline_out_dict["vcons"]) == 1)
      assert(len(pipeline_out_dict["vcons_modified"]) == 1)
      assert(pipeline_out_dict["vcons_modified"][0])
      modified_vcon = vcon.Vcon()
      modified_vcon.loadd(pipeline_out_dict["vcons"][0])
      assert(len(modified_vcon.dialog) == 1)
      assert(modified_vcon.dialog[0]["type"] == "recording")
      assert(len(modified_vcon.analysis) == 2)
      assert(modified_vcon.analysis[0]["type"] == "transcript")
      assert(modified_vcon.analysis[0]["vendor"] == "deepgram")
      assert(modified_vcon.analysis[0]["product"] == "transcription")
      assert(modified_vcon.analysis[1]["type"] == "summary")
      assert(modified_vcon.analysis[1]["vendor"] == "openai")
      assert(modified_vcon.analysis[1]["product"] == "ChatCompletion")
    elif(post_response.status_code == 430):
      # pipe_out_dict
      # TODO confirm timeout in error message
      pass
    else:
      assert(post_response.status_code != 200)


    # Give more time so that pipeline does not timeout
    more_time_pipe_dict = copy.deepcopy(PIPE_DEF2_DICT)
    more_time_pipe_dict["pipeline_options"]["timeout"] = TIMEOUT
    assert(more_time_pipe_dict["pipeline_options"]["timeout"] == TIMEOUT)
    set_response = client.put(
        "/pipeline/{}".format(
          pipe2_name
        ),
        json = more_time_pipe_dict, 
        params = { "validate_processor_options": True}
      )
    resp_content = set_response.content
    assert(set_response.status_code == 204)
    assert(len(resp_content) == 0)

    # get and check pipe timeout from DB
    get_response = client.get(
        "/pipeline/{}".format(
          pipe2_name
        )
      )

    assert(get_response.status_code == 200)
    pipe_json = get_response.json()
    pipe_def = py_vcon_server.pipeline.PipelineDefinition(**pipe_json)
    print("got pipeline: {}".format(pipe_json))
    assert(pipe_def.pipeline_options.timeout == TIMEOUT)
    assert(len(pipe_def.processors) == 2)
    assert(pipe_def.processors[0].processor_name == "deepgram")
    # Expecting: format_options, should_process and input_vcon_index in dict
    assert(len(vcon.pydantic_utils.get_dict(pipe_def.processors[0].processor_options, exclude_none=True)) == 5)
    assert(pipe_def.processors[0].processor_options.input_vcon_index == 0)
    assert(pipe_def.processors[0].processor_options.should_process == True)
    assert(pipe_def.processors[1].processor_name == "openai_chat_completion")
    assert(len(vcon.pydantic_utils.get_dict(pipe_def.processors[1].processor_options, exclude_none=True)) == 5)
    assert(pipe_def.processors[1].processor_options.input_vcon_index == 0)
    assert(pipe_def.processors[1].processor_options.should_process == True)


    # run again with longer timeout, should succeed this time
    post_response = client.post(
      "/pipeline/{}/run/{}".format(
          pipe2_name,
          UUID
        ),
        params = {
            "save_vcons": False,
            "return_results": True
          },
        headers={"accept": "application/json"},
      )
    pipeline_out_dict = post_response.json()
    print("pipe out: {}".format(pipeline_out_dict))
    assert(post_response.status_code == 200)
    assert(len(pipeline_out_dict["vcons"]) == 1)
    assert(len(pipeline_out_dict["vcons_modified"]) == 1)
    assert(pipeline_out_dict["vcons_modified"][0])
    modified_vcon = vcon.Vcon()
    modified_vcon.loadd(pipeline_out_dict["vcons"][0])
    assert(len(modified_vcon.dialog) == 1)
    assert(modified_vcon.dialog[0]["type"] == "recording")
    assert(len(modified_vcon.analysis) == 2)
    assert(modified_vcon.analysis[0]["type"] == "transcript")
    assert(modified_vcon.analysis[0]["vendor"] == "deepgram")
    assert(modified_vcon.analysis[0]["product"] == "transcription")
    assert(modified_vcon.analysis[1]["type"] == "summary")
    assert(modified_vcon.analysis[1]["vendor"] == "openai")
    assert(modified_vcon.analysis[1]["product"] == "ChatCompletion")

    # run with invalid pipeline name
    post_response = client.post(
      "/pipeline/{}/run".format(
          "bogus_pipeline"
        ),
        json = make_inline_audio_vcon.dumpd(),
        params = {
            "save_vcons": False,
            "return_results": True
          },
        headers={"accept": "application/json"},
      )
    pipeline_out_dict = post_response.json()
    print("pipe out: {}".format(pipeline_out_dict))
    assert(post_response.status_code == 404)

    # run with vCon in body, should succeed
    post_response = client.post(
      "/pipeline/{}/run".format(
          pipe2_name
        ),
        json = make_inline_audio_vcon.dumpd(),
        params = {
            "save_vcons": False,
            "return_results": True
          },
        headers={"accept": "application/json"},
      )
    pipeline_out_dict = post_response.json()
    print("pipe out: {}".format(pipeline_out_dict))
    assert(post_response.status_code == 200)
    assert(len(pipeline_out_dict["vcons"]) == 1)
    assert(len(pipeline_out_dict["vcons_modified"]) == 1)
    assert(pipeline_out_dict["vcons_modified"][0])
    modified_vcon = vcon.Vcon()
    modified_vcon.loadd(pipeline_out_dict["vcons"][0])
    assert(len(modified_vcon.dialog) == 1)
    assert(modified_vcon.dialog[0]["type"] == "recording")
    assert(len(modified_vcon.analysis) == 2)
    assert(modified_vcon.analysis[0]["type"] == "transcript")
    assert(modified_vcon.analysis[0]["vendor"] == "deepgram")
    assert(modified_vcon.analysis[0]["product"] == "transcription")
    assert(modified_vcon.analysis[1]["type"] == "summary")
    assert(modified_vcon.analysis[1]["vendor"] == "openai")
    assert(modified_vcon.analysis[1]["product"] == "ChatCompletion")
    # The pipeline was run with no save of the vCons at the end.
    # Verify that the vCon in Storage did not get updated
    get_response = client.get(
      "/vcon/{}".format(UUID),
      headers={"accept": "application/json"},
      )
    assert(get_response.status_code == 200)
    vcon_dict = get_response.json()
    assert(len(vcon_dict["dialog"]) == 1)
    assert(len(vcon_dict["analysis"]) == 0)

    # Run the pipeline again, on a simple/small vCon
    # This time request that the vCon be updated in Storage
    post_response = client.post(
      "/pipeline/{}/run/{}".format(
          pipe2_name,
          UUID
        ),
        params = {
            "save_vcons": True,
            "return_results": False
          },
        headers = {"accept": "application/json"},
      )
    assert(post_response.status_code == 200)
    pipeline_out_dict = post_response.json()
    print("pipe out: {}".format(pipeline_out_dict))
    assert(pipeline_out_dict is None)

    # test commit of vCons after pipeline run
    # Verify that the vCon in Storage DID get updated
    get_response = client.get(
      "/vcon/{}".format(UUID),
      headers={"accept": "application/json"},
      )
    assert(get_response.status_code == 200)
    vcon_dict = get_response.json()
    modified_vcon = vcon.Vcon()
    modified_vcon.loadd(vcon_dict)
    assert(len(modified_vcon.dialog) == 1)
    assert(modified_vcon.dialog[0]["type"] == "recording")
    assert(len(modified_vcon.analysis) == 2)
    assert(modified_vcon.analysis[0]["type"] == "transcript")
    assert(modified_vcon.analysis[0]["vendor"] == "deepgram")
    assert(modified_vcon.analysis[0]["product"] == "transcription")
    assert(modified_vcon.analysis[1]["type"] == "summary")
    assert(modified_vcon.analysis[1]["vendor"] == "openai")
    assert(modified_vcon.analysis[1]["product"] == "ChatCompletion")

    # Non existant pipeline
    delete_response = client.delete(
        "/pipeline/{}".format(
          bad_pipe_name
        )
      )
    assert(delete_response.status_code == 404)
    del_json = delete_response.json()
    assert(del_json["detail"] == "pipeline: unit_test_pipe1_bad not found")

    delete_response = client.delete(
        "/pipeline/{}".format(
          pipe_name
        )
      )
    assert(delete_response.status_code == 204)
    assert(len(delete_response.content) == 0)

    delete_response = client.delete(
        "/pipeline/{}".format(
          pipe2_name
        )
      )
    assert(delete_response.status_code == 204)
    assert(len(delete_response.content) == 0)

    get_response = client.get(
        "/pipelines"
      )
    assert(get_response.status_code == 200)
    pipe_list = get_response.json()
    print("pipe list: {}".format(pipe_list))
    assert(isinstance(pipe_list, list))
    assert(not pipe_name in pipe_list)
    assert(not bad_pipe_name in pipe_list)


@pytest.mark.asyncio
async def test_pipeline_conditional(make_inline_audio_vcon: vcon.Vcon):
  pipe_name = "unit_test_pipe1"

  generic_options = py_vcon_server.processor.VconProcessorOptions(
      ** (PIPE_CONDITIONAL_DICT["processors"][1]["processor_options"])
    )
  io_object = py_vcon_server.processor.VconProcessorIO(None)
  io_object.set_parameter("has_dialogs", "false")
  formatted_options = io_object.format_parameters_to_options(generic_options)
  assert(formatted_options.should_process is False)

  with fastapi.testclient.TestClient(py_vcon_server.restapi) as client:
    set_response = client.put(
        "/pipeline/{}".format(
          pipe_name
        ),
        json = PIPE_CONDITIONAL_DICT,
        params = { "validate_processor_options": True}
      )
    resp_content = set_response.content
    if(set_response.status_code != 204):
      print("put: /pipeline/{} returned: {} {}".format(
          pipe_name,
          set_response.status_code,
          resp_content
        ))
    assert(set_response.status_code == 204)
    assert(len(resp_content) == 0)
    # check the model
    vcon.pydantic_utils.validate_construct(py_vcon_server.processor.VconUnsignedObject, make_inline_audio_vcon.dumpd())

    # run with vCon in body, should succeed
    post_response = client.post(
      "/pipeline/{}/run".format(
          pipe_name
        ),
        json = make_inline_audio_vcon.dumpd(),
        params = {
            "save_vcons": False,
            "return_results": True
          },
        headers={"accept": "application/json"},
      )
    pipeline_out_dict = post_response.json()
    print("pipe out: {}".format(pipeline_out_dict))
    assert(post_response.status_code == 200)
    assert(len(pipeline_out_dict["vcons"]) == 1)
    assert(len(pipeline_out_dict["vcons_modified"]) == 1)
    # As we pass the vCon into the RESDful API it is considered new/modified
    # WRT the vCon DB
    assert(pipeline_out_dict["vcons_modified"][0])
    unmodified_vcon = vcon.Vcon()
    unmodified_vcon.loadd(pipeline_out_dict["vcons"][0])
    print("pipeline output keys: {}".format(pipeline_out_dict.keys()))
    assert(len(unmodified_vcon.dialog) == 1)
    assert(len(unmodified_vcon.analysis) == 0)
    assert(len(pipeline_out_dict["parameters"]) == 2)


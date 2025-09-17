# Copyright (C) 2023-2025 SIPez LLC.  All rights reserved.
""" Unit tests for VconProcessorIO """

import asyncio
import pydantic
import pytest
import pytest_asyncio
import importlib
import copy
import py_vcon_server.processor
from common_setup import UUID, make_2_party_tel_vcon
import vcon
import vcon.pydantic_utils
from py_vcon_server.settings import VCON_STORAGE_URL

# Stuff to test:
#  add
#  can't add same uuid
#  update
#  can't update non-existing uuid
#  with and without lock
#  readonly and read/write

VCON_STORAGE = None

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
  # Init storge
  vs = py_vcon_server.db.VconStorage.instantiate(VCON_STORAGE_URL)
  global VCON_STORAGE
  VCON_STORAGE = vs

  yield
  # teardown storage
  VCON_STORAGE = None
  await vs.shutdown()
 
 
@pytest.mark.asyncio
async def test_processor_io_vcons(make_2_party_tel_vcon: vcon.Vcon):
  vcon_object = make_2_party_tel_vcon
  assert(vcon_object.uuid == UUID)

  io_object = py_vcon_server.processor.VconProcessorIO(VCON_STORAGE)
  assert(io_object.num_vcons() == 0)
  await io_object.add_vcon(vcon_object)
  assert(len(io_object._vcons) == 1)
  assert(len(io_object._vcon_locks) == 1)
  assert(len(io_object._vcon_update) == 1)
  assert(io_object._vcon_locks[0] is None)
  assert(not io_object._vcon_update[0])

  try:
    # index too big
    io_object.is_vcon_modified(10)
    raise Exception("Should not get here index 10 does not exist")
  except Exception:
    pass

  vcon2_object = copy.deepcopy(vcon_object)
  assert(vcon2_object.uuid == UUID)
  vcon2_object.parties[0]["tel"] = "abcd"
  vcon2_object.parties[1]["tel"] = "efgh"

  try:
    await io_object.add_vcon(vcon2_object)
    raise Exception("Should fail as vCon with same UUID already exists in io object")

  except Exception as e:
    if(str(e).startswith("('Cannot add duplicate")):
      pass
    else:
      raise e

  # different UUID should now be allowed
  vcon3_object = vcon.Vcon()
  vcon3_object.set_uuid("py-vcon.org")
  await io_object.add_vcon(vcon3_object)
  assert(len(io_object._vcons) == 2)
  assert(io_object.num_vcons() == 2)
  assert(len(io_object._vcon_locks) == 2)
  assert(len(io_object._vcon_update) == 2)
  assert(io_object._vcon_locks[1] is None)
  assert(not io_object._vcon_update[1])

  output = await io_object.get_output()
  assert(len(output.vcons) == 2)
  assert(len(output.vcons_modified) == 2)
  assert(not output.vcons_modified[0])
  assert(not output.vcons_modified[1])

  try:
    await io_object.update_vcon(vcon_object)
    raise Exception("same UUID should not be allowed as it was added readonly")

  except Exception as e:
    if("has no write lock" in str(e)):
      pass
    else:
      raise e

  new_vcon = vcon.Vcon()
  new_vcon.set_uuid("test.py-vcon.org")
  try:
    await io_object.update_vcon(new_vcon)
    raise Exception("new UUID should not be allowed as update")
  except Exception:
    pass

  vcon4_object = vcon.Vcon()
  try:
    await io_object.add_vcon(vcon4_object, "lockkey")
    raise Exception("should fail as we have given a new vCon with a locak key, but labeled it readonly")

  except Exception as e:
    if(str(e).startswith("Should not lock readonly vCon")):
      pass
    else:
      raise e


  # New processor IO object to test read/write features
  rw_io_object = py_vcon_server.processor.VconProcessorIO(VCON_STORAGE)
  # Add with lock and read_write
  await rw_io_object.add_vcon(vcon_object, "fake_key", False)
  assert(len(rw_io_object._vcons) == 1)
  assert(len(rw_io_object._vcon_locks) == 1)
  assert(len(rw_io_object._vcon_update) == 1)
  assert(rw_io_object._vcon_locks[0] == "fake_key")
  assert(not rw_io_object._vcon_update[0])

  await rw_io_object.update_vcon(vcon2_object)
  assert(len(rw_io_object._vcons) == 1)
  assert(len(rw_io_object._vcon_locks) == 1)
  assert(len(rw_io_object._vcon_update) == 1)
  assert(rw_io_object._vcon_locks[0] == "fake_key")
  assert(rw_io_object._vcon_update[0])
  assert((await rw_io_object.get_vcon()).parties[0]["tel"] == "abcd")
  assert((await rw_io_object.get_vcon()).parties[1]["tel"] == "efgh")
  try:
    # Index too big
    await rw_io_object.get_vcon(index=10)
    raise Exception("Should not get here index 10 too big")
  except py_vcon_server.processor.VconNotFound:
    pass

  # Add with no lock and read_write
  await rw_io_object.add_vcon(vcon4_object, None, False)
  # Assumes the vCon does not exist in VconStorage, so no lock needed
  assert(len(rw_io_object._vcons) == 2)
  assert(len(rw_io_object._vcon_locks) == 2)
  assert(len(rw_io_object._vcon_update) == 2)
  assert(rw_io_object._vcon_locks[0] == "fake_key")
  assert(rw_io_object._vcon_locks[1] is None)
  assert(rw_io_object._vcon_update[0])
  assert(rw_io_object._vcon_update[1])
  assert(len((await rw_io_object.get_vcon(1)).parties) == 0)

  # test parameters
  try:
    rw_io_object.get_parameter("foo")
    raise Exception("Expected throw of parameter foo not found")

  except KeyError as foo_not_found:
    # expected
    pass

  try:
    # format_options references undefined key foo
    rw_io_object.format_parameters_to_options({"format_options": {"foo2": "ddd {foo} ggg"}})
    raise Exception("Should have rasied exception for undefined parameter foo")
  except py_vcon_server.processor.ParameterNotFound:
    pass

  try:
    # passing in wrong type
    rw_io_object.format_parameters_to_options([])
    raise Exception("Should have rasied exception for invalid type (list)")
  except Exception:
    pass

  try:
    # passing in empty UUID array
    rw_io_object.add_vcon_uuid_queue_job("foo", [], None)
    raise Exception("Should have rasied exception for empty list")
  except Exception:
    pass

  rw_io_object.set_parameter("foo", "bar")
  assert(rw_io_object.get_parameter("foo") == "bar")
  rw_io_object.set_parameter("x", 5)
  assert(rw_io_object.get_parameter("x") == 5)

  format_options = {
      "input_vcon_index": "{x}",
      "yyy": "{foo} {foo} {x}"
    }
  generic_options = py_vcon_server.processor.VconProcessorOptions(format_options = format_options)

  formated_options = rw_io_object.format_parameters_to_options(generic_options)
  assert(isinstance(formated_options, py_vcon_server.processor.VconProcessorOptions))
  assert(isinstance(formated_options.input_vcon_index, int))
  assert(formated_options.input_vcon_index == 5)
  assert(formated_options.yyy == "bar bar 5")
  assert(generic_options.should_process is not None)
  assert(generic_options.should_process) # should default to True

  if_options = py_vcon_server.processor.VconProcessorOptions(should_process = False)
  assert(not if_options.should_process)
  try:
    if_options = py_vcon_server.processor.VconProcessorOptions(should_process = None)
    raise Exception("None should not be accepted as a value for should_process")
  except vcon.pydantic_utils.ValidationErrorType:
    # expected
    pass
  if_options = py_vcon_server.processor.VconProcessorOptions(should_process = len(""))
  assert(not if_options.should_process)
  if_options = py_vcon_server.processor.VconProcessorOptions(should_process = "no")
  assert(not if_options.should_process)
  if_options = py_vcon_server.processor.VconProcessorOptions(should_process = "true")
  assert(if_options.should_process)
  try:
    if_options = py_vcon_server.processor.VconProcessorOptions(should_process = 4)
    raise Exception("int greater than 1 should not be accepted as a value for should_process")
  except vcon.pydantic_utils.ValidationErrorType:
    # expected
    pass
  if_options = py_vcon_server.processor.VconProcessorOptions(should_process = 0)
  assert(not if_options.should_process)


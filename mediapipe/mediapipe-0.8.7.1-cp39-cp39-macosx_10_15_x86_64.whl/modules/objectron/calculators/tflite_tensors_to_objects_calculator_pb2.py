# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mediapipe/modules/objectron/calculators/tflite_tensors_to_objects_calculator.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from mediapipe.framework import calculator_pb2 as mediapipe_dot_framework_dot_calculator__pb2
try:
  mediapipe_dot_framework_dot_calculator__options__pb2 = mediapipe_dot_framework_dot_calculator__pb2.mediapipe_dot_framework_dot_calculator__options__pb2
except AttributeError:
  mediapipe_dot_framework_dot_calculator__options__pb2 = mediapipe_dot_framework_dot_calculator__pb2.mediapipe.framework.calculator_options_pb2
from mediapipe.modules.objectron.calculators import belief_decoder_config_pb2 as mediapipe_dot_modules_dot_objectron_dot_calculators_dot_belief__decoder__config__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='mediapipe/modules/objectron/calculators/tflite_tensors_to_objects_calculator.proto',
  package='mediapipe',
  syntax='proto2',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\nRmediapipe/modules/objectron/calculators/tflite_tensors_to_objects_calculator.proto\x12\tmediapipe\x1a$mediapipe/framework/calculator.proto\x1a\x43mediapipe/modules/objectron/calculators/belief_decoder_config.proto\"\xa3\x03\n\'TfLiteTensorsToObjectsCalculatorOptions\x12\x13\n\x0bnum_classes\x18\x01 \x01(\x05\x12\x15\n\rnum_keypoints\x18\x02 \x01(\x05\x12\"\n\x17num_values_per_keypoint\x18\x03 \x01(\x05:\x01\x32\x12\x36\n\x0e\x64\x65\x63oder_config\x18\x04 \x01(\x0b\x32\x1e.mediapipe.BeliefDecoderConfig\x12\x1d\n\x12normalized_focal_x\x18\x05 \x01(\x02:\x01\x31\x12\x1d\n\x12normalized_focal_y\x18\x06 \x01(\x02:\x01\x31\x12\'\n\x1cnormalized_principal_point_x\x18\x07 \x01(\x02:\x01\x30\x12\'\n\x1cnormalized_principal_point_y\x18\x08 \x01(\x02:\x01\x30\x32`\n\x03\x65xt\x12\x1c.mediapipe.CalculatorOptions\x18\xbe\xff\xdc} \x01(\x0b\x32\x32.mediapipe.TfLiteTensorsToObjectsCalculatorOptions'
  ,
  dependencies=[mediapipe_dot_framework_dot_calculator__pb2.DESCRIPTOR,mediapipe_dot_modules_dot_objectron_dot_calculators_dot_belief__decoder__config__pb2.DESCRIPTOR,])




_TFLITETENSORSTOOBJECTSCALCULATOROPTIONS = _descriptor.Descriptor(
  name='TfLiteTensorsToObjectsCalculatorOptions',
  full_name='mediapipe.TfLiteTensorsToObjectsCalculatorOptions',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='num_classes', full_name='mediapipe.TfLiteTensorsToObjectsCalculatorOptions.num_classes', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='num_keypoints', full_name='mediapipe.TfLiteTensorsToObjectsCalculatorOptions.num_keypoints', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='num_values_per_keypoint', full_name='mediapipe.TfLiteTensorsToObjectsCalculatorOptions.num_values_per_keypoint', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=True, default_value=2,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='decoder_config', full_name='mediapipe.TfLiteTensorsToObjectsCalculatorOptions.decoder_config', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='normalized_focal_x', full_name='mediapipe.TfLiteTensorsToObjectsCalculatorOptions.normalized_focal_x', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(1),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='normalized_focal_y', full_name='mediapipe.TfLiteTensorsToObjectsCalculatorOptions.normalized_focal_y', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(1),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='normalized_principal_point_x', full_name='mediapipe.TfLiteTensorsToObjectsCalculatorOptions.normalized_principal_point_x', index=6,
      number=7, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='normalized_principal_point_y', full_name='mediapipe.TfLiteTensorsToObjectsCalculatorOptions.normalized_principal_point_y', index=7,
      number=8, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
    _descriptor.FieldDescriptor(
      name='ext', full_name='mediapipe.TfLiteTensorsToObjectsCalculatorOptions.ext', index=0,
      number=263667646, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=True, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=205,
  serialized_end=624,
)

_TFLITETENSORSTOOBJECTSCALCULATOROPTIONS.fields_by_name['decoder_config'].message_type = mediapipe_dot_modules_dot_objectron_dot_calculators_dot_belief__decoder__config__pb2._BELIEFDECODERCONFIG
DESCRIPTOR.message_types_by_name['TfLiteTensorsToObjectsCalculatorOptions'] = _TFLITETENSORSTOOBJECTSCALCULATOROPTIONS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TfLiteTensorsToObjectsCalculatorOptions = _reflection.GeneratedProtocolMessageType('TfLiteTensorsToObjectsCalculatorOptions', (_message.Message,), {
  'DESCRIPTOR' : _TFLITETENSORSTOOBJECTSCALCULATOROPTIONS,
  '__module__' : 'mediapipe.modules.objectron.calculators.tflite_tensors_to_objects_calculator_pb2'
  # @@protoc_insertion_point(class_scope:mediapipe.TfLiteTensorsToObjectsCalculatorOptions)
  })
_sym_db.RegisterMessage(TfLiteTensorsToObjectsCalculatorOptions)

_TFLITETENSORSTOOBJECTSCALCULATOROPTIONS.extensions_by_name['ext'].message_type = _TFLITETENSORSTOOBJECTSCALCULATOROPTIONS
mediapipe_dot_framework_dot_calculator__options__pb2.CalculatorOptions.RegisterExtension(_TFLITETENSORSTOOBJECTSCALCULATOROPTIONS.extensions_by_name['ext'])

# @@protoc_insertion_point(module_scope)

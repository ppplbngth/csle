# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: client_manager.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14\x63lient_manager.proto\"\x10\n\x0eStopClientsMsg\"|\n\x0fStartClientsMsg\x12\x1d\n\x15time_step_len_seconds\x18\x01 \x01(\x05\x12-\n\x10workflows_config\x18\x02 \x01(\x0b\x32\x13.WorkflowsConfigDTO\x12\x1b\n\x07\x63lients\x18\x03 \x03(\x0b\x32\n.ClientDTO\"\x94\x03\n\tClientDTO\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x1d\n\x15workflow_distribution\x18\x02 \x03(\x02\x12:\n\x17\x63onstant_arrival_config\x18\x03 \x01(\x0b\x32\x19.ConstantArrivalConfigDTO\x12\x32\n\x13sine_arrival_config\x18\x04 \x01(\x0b\x32\x15.SineArrivalConfigDTO\x12\x38\n\x16spiking_arrival_config\x18\x05 \x01(\x0b\x32\x18.SpikingArrivalConfigDTO\x12N\n\"piece_wise_constant_arrival_config\x18\x06 \x01(\x0b\x32\".PieceWiseConstantArrivalConfigDTO\x12\x34\n\x14\x65ptmp_arrival_config\x18\x07 \x01(\x0b\x32\x16.EPTMPArrivalConfigDTO\x12\n\n\x02mu\x18\t \x01(\x02\x12 \n\x18\x65xponential_service_time\x18\n \x01(\x08\"\x0f\n\rGetClientsMsg\"K\n\x10StartProducerMsg\x12\n\n\x02ip\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\x05\x12\x1d\n\x15time_step_len_seconds\x18\x03 \x01(\x05\"\x11\n\x0fStopProducerMsg\"3\n\x1aProbabilityDistributionDTO\x12\x15\n\rprobabilities\x18\x01 \x03(\x02\"@\n\x13TransitionMatrixDTO\x12)\n\x04rows\x18\x01 \x03(\x0b\x32\x1b.ProbabilityDistributionDTO\"l\n\x16WorkflowMarkovChainDTO\x12/\n\x11transition_matrix\x18\x01 \x01(\x0b\x32\x14.TransitionMatrixDTO\x12\x15\n\rinitial_state\x18\x02 \x01(\x05\x12\n\n\x02id\x18\x03 \x01(\x05\"?\n\x12WorkflowServiceDTO\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0b\n\x03ips\x18\x02 \x03(\t\x12\x10\n\x08\x63ommands\x18\x03 \x03(\t\"}\n\x12WorkflowsConfigDTO\x12\x37\n\x16workflow_markov_chains\x18\x01 \x03(\x0b\x32\x17.WorkflowMarkovChainDTO\x12.\n\x11workflow_services\x18\x02 \x03(\x0b\x32\x13.WorkflowServiceDTO\"\xa8\x01\n\nClientsDTO\x12\x13\n\x0bnum_clients\x18\x01 \x01(\x05\x12\x1d\n\x15\x63lient_process_active\x18\x02 \x01(\x08\x12\x17\n\x0fproducer_active\x18\x03 \x01(\x08\x12%\n\x1d\x63lients_time_step_len_seconds\x18\x04 \x01(\x05\x12&\n\x1eproducer_time_step_len_seconds\x18\x05 \x01(\x05\"(\n\x18\x43onstantArrivalConfigDTO\x12\x0c\n\x04lamb\x18\x01 \x01(\x02\"`\n\x14SineArrivalConfigDTO\x12\x0c\n\x04lamb\x18\x01 \x01(\x02\x12\x1b\n\x13time_scaling_factor\x18\x02 \x01(\x02\x12\x1d\n\x15period_scaling_factor\x18\x03 \x01(\x02\"=\n\x17SpikingArrivalConfigDTO\x12\x11\n\texponents\x18\x01 \x03(\x02\x12\x0f\n\x07\x66\x61\x63tors\x18\x02 \x03(\x02\"M\n!PieceWiseConstantArrivalConfigDTO\x12\x13\n\x0b\x62reakvalues\x18\x01 \x03(\x02\x12\x13\n\x0b\x62reakpoints\x18\x02 \x03(\x05\"U\n\x15\x45PTMPArrivalConfigDTO\x12\x0e\n\x06thetas\x18\x01 \x03(\x02\x12\x0e\n\x06gammas\x18\x02 \x03(\x02\x12\x0c\n\x04phis\x18\x03 \x03(\x02\x12\x0e\n\x06omegas\x18\x04 \x03(\x02\x32\x80\x02\n\rClientManager\x12+\n\ngetClients\x12\x0e.GetClientsMsg\x1a\x0b.ClientsDTO\"\x00\x12-\n\x0bstopClients\x12\x0f.StopClientsMsg\x1a\x0b.ClientsDTO\"\x00\x12/\n\x0cstartClients\x12\x10.StartClientsMsg\x1a\x0b.ClientsDTO\"\x00\x12\x31\n\rstartProducer\x12\x11.StartProducerMsg\x1a\x0b.ClientsDTO\"\x00\x12/\n\x0cstopProducer\x12\x10.StopProducerMsg\x1a\x0b.ClientsDTO\"\x00\x62\x06proto3')



_STOPCLIENTSMSG = DESCRIPTOR.message_types_by_name['StopClientsMsg']
_STARTCLIENTSMSG = DESCRIPTOR.message_types_by_name['StartClientsMsg']
_CLIENTDTO = DESCRIPTOR.message_types_by_name['ClientDTO']
_GETCLIENTSMSG = DESCRIPTOR.message_types_by_name['GetClientsMsg']
_STARTPRODUCERMSG = DESCRIPTOR.message_types_by_name['StartProducerMsg']
_STOPPRODUCERMSG = DESCRIPTOR.message_types_by_name['StopProducerMsg']
_PROBABILITYDISTRIBUTIONDTO = DESCRIPTOR.message_types_by_name['ProbabilityDistributionDTO']
_TRANSITIONMATRIXDTO = DESCRIPTOR.message_types_by_name['TransitionMatrixDTO']
_WORKFLOWMARKOVCHAINDTO = DESCRIPTOR.message_types_by_name['WorkflowMarkovChainDTO']
_WORKFLOWSERVICEDTO = DESCRIPTOR.message_types_by_name['WorkflowServiceDTO']
_WORKFLOWSCONFIGDTO = DESCRIPTOR.message_types_by_name['WorkflowsConfigDTO']
_CLIENTSDTO = DESCRIPTOR.message_types_by_name['ClientsDTO']
_CONSTANTARRIVALCONFIGDTO = DESCRIPTOR.message_types_by_name['ConstantArrivalConfigDTO']
_SINEARRIVALCONFIGDTO = DESCRIPTOR.message_types_by_name['SineArrivalConfigDTO']
_SPIKINGARRIVALCONFIGDTO = DESCRIPTOR.message_types_by_name['SpikingArrivalConfigDTO']
_PIECEWISECONSTANTARRIVALCONFIGDTO = DESCRIPTOR.message_types_by_name['PieceWiseConstantArrivalConfigDTO']
_EPTMPARRIVALCONFIGDTO = DESCRIPTOR.message_types_by_name['EPTMPArrivalConfigDTO']
StopClientsMsg = _reflection.GeneratedProtocolMessageType('StopClientsMsg', (_message.Message,), {
  'DESCRIPTOR' : _STOPCLIENTSMSG,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:StopClientsMsg)
  })
_sym_db.RegisterMessage(StopClientsMsg)

StartClientsMsg = _reflection.GeneratedProtocolMessageType('StartClientsMsg', (_message.Message,), {
  'DESCRIPTOR' : _STARTCLIENTSMSG,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:StartClientsMsg)
  })
_sym_db.RegisterMessage(StartClientsMsg)

ClientDTO = _reflection.GeneratedProtocolMessageType('ClientDTO', (_message.Message,), {
  'DESCRIPTOR' : _CLIENTDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:ClientDTO)
  })
_sym_db.RegisterMessage(ClientDTO)

GetClientsMsg = _reflection.GeneratedProtocolMessageType('GetClientsMsg', (_message.Message,), {
  'DESCRIPTOR' : _GETCLIENTSMSG,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:GetClientsMsg)
  })
_sym_db.RegisterMessage(GetClientsMsg)

StartProducerMsg = _reflection.GeneratedProtocolMessageType('StartProducerMsg', (_message.Message,), {
  'DESCRIPTOR' : _STARTPRODUCERMSG,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:StartProducerMsg)
  })
_sym_db.RegisterMessage(StartProducerMsg)

StopProducerMsg = _reflection.GeneratedProtocolMessageType('StopProducerMsg', (_message.Message,), {
  'DESCRIPTOR' : _STOPPRODUCERMSG,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:StopProducerMsg)
  })
_sym_db.RegisterMessage(StopProducerMsg)

ProbabilityDistributionDTO = _reflection.GeneratedProtocolMessageType('ProbabilityDistributionDTO', (_message.Message,), {
  'DESCRIPTOR' : _PROBABILITYDISTRIBUTIONDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:ProbabilityDistributionDTO)
  })
_sym_db.RegisterMessage(ProbabilityDistributionDTO)

TransitionMatrixDTO = _reflection.GeneratedProtocolMessageType('TransitionMatrixDTO', (_message.Message,), {
  'DESCRIPTOR' : _TRANSITIONMATRIXDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:TransitionMatrixDTO)
  })
_sym_db.RegisterMessage(TransitionMatrixDTO)

WorkflowMarkovChainDTO = _reflection.GeneratedProtocolMessageType('WorkflowMarkovChainDTO', (_message.Message,), {
  'DESCRIPTOR' : _WORKFLOWMARKOVCHAINDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:WorkflowMarkovChainDTO)
  })
_sym_db.RegisterMessage(WorkflowMarkovChainDTO)

WorkflowServiceDTO = _reflection.GeneratedProtocolMessageType('WorkflowServiceDTO', (_message.Message,), {
  'DESCRIPTOR' : _WORKFLOWSERVICEDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:WorkflowServiceDTO)
  })
_sym_db.RegisterMessage(WorkflowServiceDTO)

WorkflowsConfigDTO = _reflection.GeneratedProtocolMessageType('WorkflowsConfigDTO', (_message.Message,), {
  'DESCRIPTOR' : _WORKFLOWSCONFIGDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:WorkflowsConfigDTO)
  })
_sym_db.RegisterMessage(WorkflowsConfigDTO)

ClientsDTO = _reflection.GeneratedProtocolMessageType('ClientsDTO', (_message.Message,), {
  'DESCRIPTOR' : _CLIENTSDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:ClientsDTO)
  })
_sym_db.RegisterMessage(ClientsDTO)

ConstantArrivalConfigDTO = _reflection.GeneratedProtocolMessageType('ConstantArrivalConfigDTO', (_message.Message,), {
  'DESCRIPTOR' : _CONSTANTARRIVALCONFIGDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:ConstantArrivalConfigDTO)
  })
_sym_db.RegisterMessage(ConstantArrivalConfigDTO)

SineArrivalConfigDTO = _reflection.GeneratedProtocolMessageType('SineArrivalConfigDTO', (_message.Message,), {
  'DESCRIPTOR' : _SINEARRIVALCONFIGDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:SineArrivalConfigDTO)
  })
_sym_db.RegisterMessage(SineArrivalConfigDTO)

SpikingArrivalConfigDTO = _reflection.GeneratedProtocolMessageType('SpikingArrivalConfigDTO', (_message.Message,), {
  'DESCRIPTOR' : _SPIKINGARRIVALCONFIGDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:SpikingArrivalConfigDTO)
  })
_sym_db.RegisterMessage(SpikingArrivalConfigDTO)

PieceWiseConstantArrivalConfigDTO = _reflection.GeneratedProtocolMessageType('PieceWiseConstantArrivalConfigDTO', (_message.Message,), {
  'DESCRIPTOR' : _PIECEWISECONSTANTARRIVALCONFIGDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:PieceWiseConstantArrivalConfigDTO)
  })
_sym_db.RegisterMessage(PieceWiseConstantArrivalConfigDTO)

EPTMPArrivalConfigDTO = _reflection.GeneratedProtocolMessageType('EPTMPArrivalConfigDTO', (_message.Message,), {
  'DESCRIPTOR' : _EPTMPARRIVALCONFIGDTO,
  '__module__' : 'client_manager_pb2'
  # @@protoc_insertion_point(class_scope:EPTMPArrivalConfigDTO)
  })
_sym_db.RegisterMessage(EPTMPArrivalConfigDTO)

_CLIENTMANAGER = DESCRIPTOR.services_by_name['ClientManager']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _STOPCLIENTSMSG._serialized_start=24
  _STOPCLIENTSMSG._serialized_end=40
  _STARTCLIENTSMSG._serialized_start=42
  _STARTCLIENTSMSG._serialized_end=166
  _CLIENTDTO._serialized_start=169
  _CLIENTDTO._serialized_end=573
  _GETCLIENTSMSG._serialized_start=575
  _GETCLIENTSMSG._serialized_end=590
  _STARTPRODUCERMSG._serialized_start=592
  _STARTPRODUCERMSG._serialized_end=667
  _STOPPRODUCERMSG._serialized_start=669
  _STOPPRODUCERMSG._serialized_end=686
  _PROBABILITYDISTRIBUTIONDTO._serialized_start=688
  _PROBABILITYDISTRIBUTIONDTO._serialized_end=739
  _TRANSITIONMATRIXDTO._serialized_start=741
  _TRANSITIONMATRIXDTO._serialized_end=805
  _WORKFLOWMARKOVCHAINDTO._serialized_start=807
  _WORKFLOWMARKOVCHAINDTO._serialized_end=915
  _WORKFLOWSERVICEDTO._serialized_start=917
  _WORKFLOWSERVICEDTO._serialized_end=980
  _WORKFLOWSCONFIGDTO._serialized_start=982
  _WORKFLOWSCONFIGDTO._serialized_end=1107
  _CLIENTSDTO._serialized_start=1110
  _CLIENTSDTO._serialized_end=1278
  _CONSTANTARRIVALCONFIGDTO._serialized_start=1280
  _CONSTANTARRIVALCONFIGDTO._serialized_end=1320
  _SINEARRIVALCONFIGDTO._serialized_start=1322
  _SINEARRIVALCONFIGDTO._serialized_end=1418
  _SPIKINGARRIVALCONFIGDTO._serialized_start=1420
  _SPIKINGARRIVALCONFIGDTO._serialized_end=1481
  _PIECEWISECONSTANTARRIVALCONFIGDTO._serialized_start=1483
  _PIECEWISECONSTANTARRIVALCONFIGDTO._serialized_end=1560
  _EPTMPARRIVALCONFIGDTO._serialized_start=1562
  _EPTMPARRIVALCONFIGDTO._serialized_end=1647
  _CLIENTMANAGER._serialized_start=1650
  _CLIENTMANAGER._serialized_end=1906
# @@protoc_insertion_point(module_scope)

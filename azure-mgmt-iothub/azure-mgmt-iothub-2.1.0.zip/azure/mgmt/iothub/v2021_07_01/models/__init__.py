# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

try:
    from ._models_py3 import ArmIdentity
    from ._models_py3 import ArmUserIdentity
    from ._models_py3 import CertificateBodyDescription
    from ._models_py3 import CertificateDescription
    from ._models_py3 import CertificateListDescription
    from ._models_py3 import CertificateProperties
    from ._models_py3 import CertificatePropertiesWithNonce
    from ._models_py3 import CertificateVerificationDescription
    from ._models_py3 import CertificateWithNonceDescription
    from ._models_py3 import CloudToDeviceProperties
    from ._models_py3 import EndpointHealthData
    from ._models_py3 import EndpointHealthDataListResult
    from ._models_py3 import EnrichmentProperties
    from ._models_py3 import ErrorDetails
    from ._models_py3 import EventHubConsumerGroupBodyDescription
    from ._models_py3 import EventHubConsumerGroupInfo
    from ._models_py3 import EventHubConsumerGroupName
    from ._models_py3 import EventHubConsumerGroupsListResult
    from ._models_py3 import EventHubProperties
    from ._models_py3 import ExportDevicesRequest
    from ._models_py3 import FailoverInput
    from ._models_py3 import FallbackRouteProperties
    from ._models_py3 import FeedbackProperties
    from ._models_py3 import GroupIdInformation
    from ._models_py3 import GroupIdInformationProperties
    from ._models_py3 import ImportDevicesRequest
    from ._models_py3 import IotHubCapacity
    from ._models_py3 import IotHubDescription
    from ._models_py3 import IotHubDescriptionListResult
    from ._models_py3 import IotHubLocationDescription
    from ._models_py3 import IotHubNameAvailabilityInfo
    from ._models_py3 import IotHubProperties
    from ._models_py3 import IotHubQuotaMetricInfo
    from ._models_py3 import IotHubQuotaMetricInfoListResult
    from ._models_py3 import IotHubSkuDescription
    from ._models_py3 import IotHubSkuDescriptionListResult
    from ._models_py3 import IotHubSkuInfo
    from ._models_py3 import IpFilterRule
    from ._models_py3 import JobResponse
    from ._models_py3 import JobResponseListResult
    from ._models_py3 import ManagedIdentity
    from ._models_py3 import MatchedRoute
    from ._models_py3 import MessagingEndpointProperties
    from ._models_py3 import Name
    from ._models_py3 import NetworkRuleSetIpRule
    from ._models_py3 import NetworkRuleSetProperties
    from ._models_py3 import Operation
    from ._models_py3 import OperationDisplay
    from ._models_py3 import OperationInputs
    from ._models_py3 import OperationListResult
    from ._models_py3 import PrivateEndpoint
    from ._models_py3 import PrivateEndpointConnection
    from ._models_py3 import PrivateEndpointConnectionProperties
    from ._models_py3 import PrivateLinkResources
    from ._models_py3 import PrivateLinkServiceConnectionState
    from ._models_py3 import RegistryStatistics
    from ._models_py3 import Resource
    from ._models_py3 import RouteCompilationError
    from ._models_py3 import RouteErrorPosition
    from ._models_py3 import RouteErrorRange
    from ._models_py3 import RouteProperties
    from ._models_py3 import RoutingEndpoints
    from ._models_py3 import RoutingEventHubProperties
    from ._models_py3 import RoutingMessage
    from ._models_py3 import RoutingProperties
    from ._models_py3 import RoutingServiceBusQueueEndpointProperties
    from ._models_py3 import RoutingServiceBusTopicEndpointProperties
    from ._models_py3 import RoutingStorageContainerProperties
    from ._models_py3 import RoutingTwin
    from ._models_py3 import RoutingTwinProperties
    from ._models_py3 import SharedAccessSignatureAuthorizationRule
    from ._models_py3 import SharedAccessSignatureAuthorizationRuleListResult
    from ._models_py3 import StorageEndpointProperties
    from ._models_py3 import TagsResource
    from ._models_py3 import TestAllRoutesInput
    from ._models_py3 import TestAllRoutesResult
    from ._models_py3 import TestRouteInput
    from ._models_py3 import TestRouteResult
    from ._models_py3 import TestRouteResultDetails
    from ._models_py3 import UserSubscriptionQuota
    from ._models_py3 import UserSubscriptionQuotaListResult
except (SyntaxError, ImportError):
    from ._models import ArmIdentity  # type: ignore
    from ._models import ArmUserIdentity  # type: ignore
    from ._models import CertificateBodyDescription  # type: ignore
    from ._models import CertificateDescription  # type: ignore
    from ._models import CertificateListDescription  # type: ignore
    from ._models import CertificateProperties  # type: ignore
    from ._models import CertificatePropertiesWithNonce  # type: ignore
    from ._models import CertificateVerificationDescription  # type: ignore
    from ._models import CertificateWithNonceDescription  # type: ignore
    from ._models import CloudToDeviceProperties  # type: ignore
    from ._models import EndpointHealthData  # type: ignore
    from ._models import EndpointHealthDataListResult  # type: ignore
    from ._models import EnrichmentProperties  # type: ignore
    from ._models import ErrorDetails  # type: ignore
    from ._models import EventHubConsumerGroupBodyDescription  # type: ignore
    from ._models import EventHubConsumerGroupInfo  # type: ignore
    from ._models import EventHubConsumerGroupName  # type: ignore
    from ._models import EventHubConsumerGroupsListResult  # type: ignore
    from ._models import EventHubProperties  # type: ignore
    from ._models import ExportDevicesRequest  # type: ignore
    from ._models import FailoverInput  # type: ignore
    from ._models import FallbackRouteProperties  # type: ignore
    from ._models import FeedbackProperties  # type: ignore
    from ._models import GroupIdInformation  # type: ignore
    from ._models import GroupIdInformationProperties  # type: ignore
    from ._models import ImportDevicesRequest  # type: ignore
    from ._models import IotHubCapacity  # type: ignore
    from ._models import IotHubDescription  # type: ignore
    from ._models import IotHubDescriptionListResult  # type: ignore
    from ._models import IotHubLocationDescription  # type: ignore
    from ._models import IotHubNameAvailabilityInfo  # type: ignore
    from ._models import IotHubProperties  # type: ignore
    from ._models import IotHubQuotaMetricInfo  # type: ignore
    from ._models import IotHubQuotaMetricInfoListResult  # type: ignore
    from ._models import IotHubSkuDescription  # type: ignore
    from ._models import IotHubSkuDescriptionListResult  # type: ignore
    from ._models import IotHubSkuInfo  # type: ignore
    from ._models import IpFilterRule  # type: ignore
    from ._models import JobResponse  # type: ignore
    from ._models import JobResponseListResult  # type: ignore
    from ._models import ManagedIdentity  # type: ignore
    from ._models import MatchedRoute  # type: ignore
    from ._models import MessagingEndpointProperties  # type: ignore
    from ._models import Name  # type: ignore
    from ._models import NetworkRuleSetIpRule  # type: ignore
    from ._models import NetworkRuleSetProperties  # type: ignore
    from ._models import Operation  # type: ignore
    from ._models import OperationDisplay  # type: ignore
    from ._models import OperationInputs  # type: ignore
    from ._models import OperationListResult  # type: ignore
    from ._models import PrivateEndpoint  # type: ignore
    from ._models import PrivateEndpointConnection  # type: ignore
    from ._models import PrivateEndpointConnectionProperties  # type: ignore
    from ._models import PrivateLinkResources  # type: ignore
    from ._models import PrivateLinkServiceConnectionState  # type: ignore
    from ._models import RegistryStatistics  # type: ignore
    from ._models import Resource  # type: ignore
    from ._models import RouteCompilationError  # type: ignore
    from ._models import RouteErrorPosition  # type: ignore
    from ._models import RouteErrorRange  # type: ignore
    from ._models import RouteProperties  # type: ignore
    from ._models import RoutingEndpoints  # type: ignore
    from ._models import RoutingEventHubProperties  # type: ignore
    from ._models import RoutingMessage  # type: ignore
    from ._models import RoutingProperties  # type: ignore
    from ._models import RoutingServiceBusQueueEndpointProperties  # type: ignore
    from ._models import RoutingServiceBusTopicEndpointProperties  # type: ignore
    from ._models import RoutingStorageContainerProperties  # type: ignore
    from ._models import RoutingTwin  # type: ignore
    from ._models import RoutingTwinProperties  # type: ignore
    from ._models import SharedAccessSignatureAuthorizationRule  # type: ignore
    from ._models import SharedAccessSignatureAuthorizationRuleListResult  # type: ignore
    from ._models import StorageEndpointProperties  # type: ignore
    from ._models import TagsResource  # type: ignore
    from ._models import TestAllRoutesInput  # type: ignore
    from ._models import TestAllRoutesResult  # type: ignore
    from ._models import TestRouteInput  # type: ignore
    from ._models import TestRouteResult  # type: ignore
    from ._models import TestRouteResultDetails  # type: ignore
    from ._models import UserSubscriptionQuota  # type: ignore
    from ._models import UserSubscriptionQuotaListResult  # type: ignore

from ._iot_hub_client_enums import (
    AccessRights,
    AuthenticationType,
    Capabilities,
    DefaultAction,
    EndpointHealthStatus,
    IotHubNameUnavailabilityReason,
    IotHubReplicaRoleType,
    IotHubScaleType,
    IotHubSku,
    IotHubSkuTier,
    IpFilterActionType,
    JobStatus,
    JobType,
    NetworkRuleIPAction,
    PrivateLinkServiceConnectionStatus,
    PublicNetworkAccess,
    ResourceIdentityType,
    RouteErrorSeverity,
    RoutingSource,
    RoutingStorageContainerPropertiesEncoding,
    TestResultStatus,
)

__all__ = [
    'ArmIdentity',
    'ArmUserIdentity',
    'CertificateBodyDescription',
    'CertificateDescription',
    'CertificateListDescription',
    'CertificateProperties',
    'CertificatePropertiesWithNonce',
    'CertificateVerificationDescription',
    'CertificateWithNonceDescription',
    'CloudToDeviceProperties',
    'EndpointHealthData',
    'EndpointHealthDataListResult',
    'EnrichmentProperties',
    'ErrorDetails',
    'EventHubConsumerGroupBodyDescription',
    'EventHubConsumerGroupInfo',
    'EventHubConsumerGroupName',
    'EventHubConsumerGroupsListResult',
    'EventHubProperties',
    'ExportDevicesRequest',
    'FailoverInput',
    'FallbackRouteProperties',
    'FeedbackProperties',
    'GroupIdInformation',
    'GroupIdInformationProperties',
    'ImportDevicesRequest',
    'IotHubCapacity',
    'IotHubDescription',
    'IotHubDescriptionListResult',
    'IotHubLocationDescription',
    'IotHubNameAvailabilityInfo',
    'IotHubProperties',
    'IotHubQuotaMetricInfo',
    'IotHubQuotaMetricInfoListResult',
    'IotHubSkuDescription',
    'IotHubSkuDescriptionListResult',
    'IotHubSkuInfo',
    'IpFilterRule',
    'JobResponse',
    'JobResponseListResult',
    'ManagedIdentity',
    'MatchedRoute',
    'MessagingEndpointProperties',
    'Name',
    'NetworkRuleSetIpRule',
    'NetworkRuleSetProperties',
    'Operation',
    'OperationDisplay',
    'OperationInputs',
    'OperationListResult',
    'PrivateEndpoint',
    'PrivateEndpointConnection',
    'PrivateEndpointConnectionProperties',
    'PrivateLinkResources',
    'PrivateLinkServiceConnectionState',
    'RegistryStatistics',
    'Resource',
    'RouteCompilationError',
    'RouteErrorPosition',
    'RouteErrorRange',
    'RouteProperties',
    'RoutingEndpoints',
    'RoutingEventHubProperties',
    'RoutingMessage',
    'RoutingProperties',
    'RoutingServiceBusQueueEndpointProperties',
    'RoutingServiceBusTopicEndpointProperties',
    'RoutingStorageContainerProperties',
    'RoutingTwin',
    'RoutingTwinProperties',
    'SharedAccessSignatureAuthorizationRule',
    'SharedAccessSignatureAuthorizationRuleListResult',
    'StorageEndpointProperties',
    'TagsResource',
    'TestAllRoutesInput',
    'TestAllRoutesResult',
    'TestRouteInput',
    'TestRouteResult',
    'TestRouteResultDetails',
    'UserSubscriptionQuota',
    'UserSubscriptionQuotaListResult',
    'AccessRights',
    'AuthenticationType',
    'Capabilities',
    'DefaultAction',
    'EndpointHealthStatus',
    'IotHubNameUnavailabilityReason',
    'IotHubReplicaRoleType',
    'IotHubScaleType',
    'IotHubSku',
    'IotHubSkuTier',
    'IpFilterActionType',
    'JobStatus',
    'JobType',
    'NetworkRuleIPAction',
    'PrivateLinkServiceConnectionStatus',
    'PublicNetworkAccess',
    'ResourceIdentityType',
    'RouteErrorSeverity',
    'RoutingSource',
    'RoutingStorageContainerPropertiesEncoding',
    'TestResultStatus',
]

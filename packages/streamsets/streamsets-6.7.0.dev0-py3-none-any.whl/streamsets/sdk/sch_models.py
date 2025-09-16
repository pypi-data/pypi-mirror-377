#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Classes for ControlHub-related models.

This module provides implementations of classes with which users may interact in the course of
writing tests that exercise ControlHub functionality.
"""
# fmt: off
import collections
import copy
import enum
import io
import ipaddress
import itertools
import json
import logging
import re
import uuid
import warnings
import zipfile
from abc import ABCMeta
from collections import namedtuple
from datetime import datetime, timedelta
from time import sleep, time

import inflection
import requests
import urllib3
import yaml
from requests.exceptions import HTTPError

from . import sch_api
from .analytics import analytics_class_decorator
from .constants import (
    DEFAULT_MAX_CPU_LOAD_VALUE, DEFAULT_MAX_MEMORY_USED_VALUE, DEFAULT_MAX_PIPELINES_RUNNING_VALUE,
    ENGINELESS_CONNECTION_ID, ENGINELESS_ENGINE_ID, SDC_CONNECTIONS_BW_COMPATIBILITY, SNOWFLAKE_ENGINE_ID,
    SNOWFLAKE_EXECUTOR_TYPE, SNOWFLAKE_STAGE_RENAME_ALIASES, ST_PIPELINE_BW_COMPATIBILITY, STAGE_CONFIG_OVERRIDES,
    ServiceConfigurationProperty, StageConfigurationProperty,
)
from .exceptions import InternalServerError, ProjectAccessError, ServiceDefinitionNotFound, TopologyIssuesError
from .models import Configuration, _StageWithPredicates
from .sdc import DataCollector as SdcDataCollector
from .sdc_api import ApiClient as SdcApiClient
from .sdc_models import Batch as SdcBatch
from .sdc_models import PipelineBuilder as SdcPipelineBuilder
from .sdc_models import PipelineMetrics as SdcPipelineMetrics
from .sdc_models import Stage as SdcStage
from .st import Transformer as StTransformer
from .st_api import ApiClient as StApiClient
from .st_models import PipelineBuilder as StPipelineBuilder
from .st_models import Stage as StStage
from .utils import (
    DEFAULT_PROVISIONING_SPEC, METERING_METRIC_LOOKUP, TRANSFORMER_DEFAULT_EXECUTION_MODE, MutableKwargs, SeekableList,
    Version, build_tag_from_raw_tag, convert_last_modified_on_field_for_saql, format_sch_log, get_attribute,
    get_bw_compatibility_map, get_library_directory_name, get_params, get_stage_library_display_name_from_library,
    get_stage_library_name_from_display_name, get_topology_nodes, reversed_dict, set_acl,
    top_objects_by_metering_metric, update_acl_permissions, wait_for_condition,
)

# fmt: on

logger = logging.getLogger(__name__)

json_to_python_style = lambda x: inflection.underscore(x)
python_to_json_style = lambda x: inflection.camelize(x, uppercase_first_letter=False)

ModelCollectionResults = collections.namedtuple('ModelCollectionResults', ['results', 'kwargs'])
# CollectionModelResults contains API results from classes that subclass PaginationMixin. The 'class_type' attribute
# indicates which class PaginationMixin._paginate should instantiate before iterating over results.
CollectionModelResults = collections.namedtuple(
    'CollectionModelResults', ['results', 'kwargs', 'class_type', 'class_kwargs']
)
NameMap = namedtuple('NameMap', ['label', 'fieldName', 'name', 'sdk'])
ChooseOption = namedtuple('ChooseOption', ['UI_VALUE', 'SDK_VALUE'])

MILLIS_IN_HOUR = 3600000
METERING_MAX_DAYS = 60

LOG4J_VERSION_1 = '1'
LOG4J_VERSION_2 = '2'
MIN_ENGINE_VERSION_WITH_LOG4J_VER2 = Version('5.0.0')
SDC_LOG4J_VER1_PROPERTIES_FILENAME = 'sdc-log4j.properties'
SDC_LOG4J_VER2_PROPERTIES_FILENAME = 'sdc-log4j2.properties'
TRANSFORMER_LOG4J_VER1_PROPERTIES_FILENAME = 'transformer-log4j.properties'
TRANSFORMER_LOG4J_VER2_PROPERTIES_FILENAME = 'transformer-log4j2.properties'

ALL_TOPOLOGY_SYSTEMS = [
    {'label': 'ADLS Gen1', 'icon': 'adls1.png', 'colorIcon': 'Destination_Azure_Data_Lake_Storage_Gen1.png'},
    {'label': 'ADLS Gen2', 'icon': 'adls2.png', 'colorIcon': 'Destination_Azure_Data_Lake_Storage_Gen2.png'},
    {'label': 'Amazon S3', 'icon': 's3.png', 'colorIcon': 'Origin_Amazon_S3.png'},
    {
        'label': 'Azure Data Lake Store',
        'icon': 'data-lake-store.png',
        'colorIcon': 'Destination_Azure_Data_Lake_Storage_Legacy.png',
    },
    {'label': 'Azure SQL', 'icon': 'azuresql.png', 'colorIcon': 'Destination_Azure_SQL.png'},
    {'label': 'Cassandra', 'icon': 'cassandra.png', 'colorIcon': 'Destination_Cassandra.png'},
    {'label': 'CoAP', 'icon': 'coap.png', 'colorIcon': 'Destination_CoAP_Client.png'},
    {'label': 'Delta Lake', 'icon': 'delta.png', 'colorIcon': 'Destination_Delta_Lake.png'},
    {'label': 'Dev Data', 'icon': 'dev.png', 'colorIcon': 'Origin_Dev_Data_Generator.png'},
    {'label': 'Directory', 'icon': 'directory.png', 'colorIcon': 'Origin_Directory.png'},
    {'label': 'Elasticsearch', 'icon': 'elasticsearch.png', 'colorIcon': 'Origin_Elasticsearch.png'},
    {'label': 'File Tail', 'icon': 'fileTail.png', 'colorIcon': 'Origin_File_Tail.png'},
    {'label': 'Flume', 'icon': 'flume.png', 'colorIcon': 'Destination_Flume.png'},
    {'label': 'Google Bigtable', 'icon': 'bigtable.png', 'colorIcon': 'Destination_Google_Bigtable.png'},
    {'label': 'HBase', 'icon': 'hbase.png', 'colorIcon': 'Destination_HBase.png'},
    {'label': 'HTTP Client', 'icon': 'httpclient.png', 'colorIcon': 'Destination_HTTP_Client.png'},
    {'label': 'Hadoop FS', 'icon': 'hdfs.png', 'colorIcon': 'Destination_Hadoop_FS.png'},
    {'label': 'Hive', 'icon': 'hive.png', 'colorIcon': 'Destination_Hive.png'},
    {'label': 'InfluxDB', 'icon': 'influxdb.png', 'colorIcon': 'Destination_InfluxDB.png'},
    {'label': 'JDBC', 'icon': 'rdbms.png', 'colorIcon': 'Destination_JDBC_Producer.png'},
    {'label': 'JMS', 'icon': 'jms.png', 'colorIcon': 'Destination_JMS_Producer.png'},
    {'label': 'Kafka', 'icon': 'kafka.png', 'colorIcon': 'Origin_Kafka.png'},
    {'label': 'Kinesis', 'icon': 'kinesis.png', 'colorIcon': 'Destination_Kinesis_Producer.png'},
    {'label': 'Kinesis Firehose', 'icon': 'kinesisfirehose.png', 'colorIcon': 'Destination_Kinesis_Firehose.png'},
    {'label': 'Kudu', 'icon': 'kudu.png', 'colorIcon': 'Destination_Kudu.png'},
    {'label': 'Local FS', 'icon': 'localfilesystem.png', 'colorIcon': 'Destination_Local_FS.png'},
    {'label': 'MapR FS', 'icon': 'mapr.png', 'colorIcon': 'Destination_MapR_FS.png'},
    {'label': 'MapR Streams', 'icon': 'mapr.png', 'colorIcon': 'Destination_MapR_Streams_Producer.png'},
    {'label': 'MapR DB', 'icon': 'mapr.png', 'colorIcon': 'Destination_MapR_DB.png'},
    {'label': 'MapR DB JSON', 'icon': 'mapr.png', 'colorIcon': 'Destination_MapR_DB.png'},
    {'label': 'MemSQL', 'icon': 'memsql.png', 'colorIcon': 'Destination_MemSQL_Fast_Loader.png'},
    {'label': 'MongoDB', 'icon': 'mongodb.png', 'colorIcon': 'Destination_MongoDB.png'},
    {'label': 'MQTT', 'icon': 'Origin_MQTT_Subscriber.png', 'colorIcon': 'Origin_MQTT_Subscriber.png'},
    {'label': 'Omniture', 'icon': 'omniture_icon.png', 'colorIcon': 'Origin_Omniture.png'},
    {'label': 'Oracle', 'icon': 'oracle.png', 'colorIcon': 'Origin_Oracle_CDC_Client.png'},
    {'label': 'Pulsar', 'icon': 'Origin_Pulsar_Consumer.png', 'colorIcon': 'Origin_Pulsar_Consumer.png'},
    {'label': 'RabbitMQ', 'icon': 'rabbitmq.png', 'colorIcon': 'Origin_RabbitMQ_Consumer.png'},
    {'label': 'Redis', 'icon': 'redis.png', 'colorIcon': 'Origin_Redis_Consumer.png'},
    {'label': 'Salesforce', 'icon': 'salesforce.png', 'colorIcon': 'Origin_Salesforce.png'},
    {
        'label': 'SAP HANA',
        'icon': 'Origin_SAP_HANA_Query_Consumer.png',
        'colorIcon': 'Origin_SAP_HANA_Query_Consumer.png',
    },
    {'label': 'SDC RPC', 'icon': 'sdcipc.png', 'colorIcon': 'Origin_SDC_RPC.png'},
    {'label': 'SFTP/FTP Client', 'icon': 'sftp-client.png', 'colorIcon': 'Origin_SFTP_FTP_FTPS_Client.png'},
    {'label': 'Snowflake', 'icon': 'snowflake.png', 'colorIcon': 'Destination_Snowflake.png'},
    {'label': 'Solr', 'icon': 'solr.png', 'colorIcon': 'Destination_Solr.png'},
    {'label': 'TCP', 'icon': 'ethernet.png', 'colorIcon': 'Origin_TCP_Server.png'},
    {'label': 'Teradata', 'icon': 'teradata.png', 'colorIcon': 'Origin_Teradata_Consumer.png'},
    {'label': 'To Error', 'icon': 'toerror.png', 'colorIcon': 'Destination_To_Error.png'},
    {'label': 'Trash', 'icon': 'trash.png', 'colorIcon': 'Destination_Trash.png'},
    {'label': 'UDP Source', 'icon': 'udp.png', 'colorIcon': 'Origin_UDP_Source.png'},
    {'label': 'Wave Analytics', 'icon': 'waveanalytics.png', 'colorIcon': 'Destination_Einstein_Analytics.png'},
    {'label': 'WebSocket', 'icon': 'websockets.png', 'colorIcon': 'Origin_WebSocket_Server.png'},
]


class BaseModel:
    """Base class for ControlHub models that essentially just wrap a dictionary.

    Args:
        data (:obj:`dict`): The underlying JSON representation of the model.
        attributes_to_ignore (:obj:`list`, optional): A list of string attributes to mask from being handled
            by this class' __setattr__ method. Default: ``None``.
        attributes_to_remap (:obj:`dict`, optional): A dictionary of attributes to remap with the desired attributes
            as keys and the corresponding property name in the JSON representation as values. Default: ``None``.
        repr_metadata (:obj:`list`, optional): A list of attributes to use in the model's __repr__ string.
            Default: ``None``.
    """

    def __new__(cls, *args, **kwargs):
        instance = super(BaseModel, cls).__new__(cls)
        super(BaseModel, instance).__setattr__('_data_internal', {})
        super(BaseModel, instance).__setattr__('_attributes_to_ignore', [])
        super(BaseModel, instance).__setattr__('_attributes_to_remap', {})
        super(BaseModel, instance).__setattr__('_repr_metadata', [])

        return instance

    def __init__(self, data, attributes_to_ignore=None, attributes_to_remap=None, repr_metadata=None):
        # _data_internal is introduced to  help inherited classes that need to load _data when _data is accessed
        # e.g. Pipeline
        super().__setattr__('_data_internal', data)
        super().__setattr__('_attributes_to_ignore', attributes_to_ignore or [])
        super().__setattr__('_attributes_to_remap', attributes_to_remap or {})
        super().__setattr__('_repr_metadata', repr_metadata or [])

    @property
    def _data_internal(self):
        return self.__dict__['_data'] if '_data' in self.__dict__ else None

    @_data_internal.setter
    def _data_internal(self, data):
        self.__dict__['_data'] = data

    @property
    def _data(self):
        return self._data_internal

    @_data.setter
    def _data(self, data):
        self._data_internal = data

    def __getattr__(self, name):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            return self._data_internal[remapped_name]
        elif (
            name_ in self._data_internal
            and name_ not in self._attributes_to_ignore
            and name not in self._attributes_to_remap.values()
        ):
            return self._data_internal[name_]
        raise AttributeError('Could not find attribute {}.'.format(name_))

    def __setattr__(self, name, value):
        name_ = python_to_json_style(name)
        properties_dict = self.__class__.__dict__
        # Check if property has a setter
        if name in properties_dict and properties_dict[name].fset:
            super().__setattr__(name, value)
        elif name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            self._data_internal[remapped_name] = value
        elif (
            name_ in self._data_internal
            and name_ not in self._attributes_to_ignore
            and name not in self._attributes_to_remap.values()
        ):
            self._data_internal[name_] = value
        else:
            super().__setattr__(name, value)

    def __dir__(self):
        return sorted(
            list(dir(object))
            + list(self.__dict__.keys())
            + list(
                json_to_python_style(key)
                for key in self._data_internal.keys()
                if key not in (list(self._attributes_to_remap.values()) + self._attributes_to_ignore)
            )
            + list(self._attributes_to_remap.keys())
        )

    def __eq__(self, other):
        return self._data_internal == other._data_internal

    def __repr__(self):
        return '<{} ({})>'.format(
            self.__class__.__name__, ', '.join('{}={}'.format(key, getattr(self, key)) for key in self._repr_metadata)
        )


class UiMetadataBaseModel(BaseModel):
    def __getattr__(self, name):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            return self._data_internal[remapped_name]['value']
        elif (
            name_ in self._data_internal
            and name not in self._attributes_to_ignore
            and name not in self._attributes_to_remap.values()
        ):
            if isinstance(self._data_internal[name_], dict):
                return self._data_internal[name_]['value']
            else:
                return self._data_internal[name_]
        raise AttributeError('Could not find attribute {}.'.format(name_))

    def __setattr__(self, name, value):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            self._data_internal[remapped_name]['value'] = value
        elif (
            name_ in self._data_internal
            and name not in self._attributes_to_ignore
            and name not in self._attributes_to_remap.values()
        ):
            if isinstance(self._data_internal[name_], dict):
                self._data_internal[name_]['value'] = value
            else:
                self._data_internal[name_] = value
        else:
            super().__setattr__(name, value)


class ModelCollection:
    """Base class wrapper with Abstractions.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
    """

    def __init__(self, control_hub):
        self._control_hub = control_hub
        self._id_attr = 'id'

    def _get_all_results_from_api(self, **kwargs):
        """Used to get multiple (all) results from api.

        Args:
            Optional arguments to be passed to filter the results.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of inherited instances of
                :py:class:`streamsets.sdk.sch_models.BaseModel` and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        pass

    def __iter__(self):
        """Enables the list enumeration or iteration."""
        for item in self._get_all_results_from_api().results:
            yield item

    def __getitem__(self, i):
        """Enables the user to fetch items by index.

        Args:
            i (:obj:`int`): Index of the item.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        return self._get_all_results_from_api().results[i]

    def __len__(self):
        """Provides length (count) of items.

        Returns:
            A :py:obj:`int` object.
        """
        return len(self._get_all_results_from_api().results)

    def __contains__(self, item_given):
        """Checks if given item is in the list of items by comparing the ids.

        Returns:
            A :py:obj:`boolean` object.
        """
        return self.contains(**{self._id_attr: getattr(item_given, self._id_attr)})

    def get(self, **kwargs):
        """
        Args:
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        result, new_kwargs = self._get_all_results_from_api(**kwargs)
        return result.get(**new_kwargs)

    def get_all(self, **kwargs):
        """
        Args:
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        result, new_kwargs = self._get_all_results_from_api(**kwargs)
        return result.get_all(**new_kwargs)

    def __repr__(self):
        return str(self._get_all_results_from_api().results)


class CollectionModel:
    """Base class wrapper with abstractions for pagination.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
    """

    PAGE_LENGTH = 250
    PAGINATION_PARAMS = ['offset', 'len']

    def _paginate(self, **kwargs):
        """Allows fetching of items in batches (pages)

        Workflow:

        1. Determine the total number of items that we need to fetch based on the ``len`` parameter (If not specified,
           assume infinite and fetch until ControlHub returns results).
        2. Use the len(self) (which calls :py:meth:`streamsets.sdk.sch_api.ApiClient.get_pipelines_count`) as a source
           of truth for the total number of pipelines existing in the ControlHub pipeline repository.
        3. Keep incrementing the offset with ``PAGE_LENGTH`` and query with new offset and ``PAGE_LENGTH`` until we
           reach requested number of items or we don't get any more items from ControlHub.
        4. While fetching these items in a loop, it is possible that some of the items are deleted by someone else
           affecting the current offset we are using. To handle this, in the while loop, if the len(self) decreases, we
           reduce the current offset by the number of items decreased (making sure, we aren't missing any items).
        5. In the list of items (order in which ControlHub returns the items), if the items that we already
           queried are deleted, the actual offset we have to use would reduce by the number of items deleted.
           On the otherhand, if
           the items that are deleted are the ones we haven't fetched yet, then we have reduced the offset which is not
           needed and hence end up getting duplicates. To handle this, we use a set to store all the item ids and
           yield only the one's we haven't fetched yet.
           eg. Lets say there are 59 pipelines in ControlHub and the parameter len is not specified.
           After we fetch the first 50 pipelines, if index 48, 49 and 50 pipelines are deleted,
           the sch fetch would miss the new 48th and
           49th pipelines since the offset we would be using would be wrong. To handle this, we will reduce the sch
           offset from 50 to 47 which would mean we would be fetching the 47th pipeline again and we handle this using
           the all_ids set but we won't be missing the new 48th and 49th index pipelines (old 50 and 51).
        """
        if kwargs.get('offset') and not (isinstance(kwargs.get('offset'), int) and kwargs.get('offset') >= 0):
            raise ValueError("`offset` should be an integer with value of at least 0")

        is_api_paginable = lambda rsp: all(i in rsp for i in ['data', 'totalCount', 'offset', 'len'])
        all_ids = set()
        requested_length = kwargs.get('len', float('inf'))
        if requested_length == -1:
            requested_length = float('inf')
        page_length = min(CollectionModel.PAGE_LENGTH, requested_length)
        current_offset = kwargs.get('offset', 0)

        # Fetch results with default offset and length or specified values
        kwargs_without_pagination_params = {
            k: v for k, v in kwargs.items() if k not in CollectionModel.PAGINATION_PARAMS
        }
        logger.debug('Fetching items with offset=%d and len=%d', current_offset, page_length)
        response, current_new_kwargs, class_type, class_kwargs = self._get_all_results_from_api(
            offset=current_offset, len=page_length, **kwargs_without_pagination_params
        )
        previous_length = response['totalCount'] if is_api_paginable(response) else len(self)

        # If an API is paginated, the result set we need to page through will be contained in the response's 'data'
        # attribute. If there is no 'data' attribute, the response itself is the result set (unpaginated API).
        if is_api_paginable(response):
            current_results = SeekableList(class_type(item, **class_kwargs) for item in response['data'])
        else:
            current_results = SeekableList(class_type(item, **class_kwargs) for item in response)

        # Iterate over pages
        while current_results:
            # Filter results based on kwargs specified (ones that are not accepted as arguments for the
            # ControlHub api endpoints)
            current_results = current_results.get_all(**current_new_kwargs)
            for result in current_results:
                # This check is to avoid duplicates especially since we are doing the
                # if current_length < previous_length check below to handle deleted entities.
                item_id = getattr(result, self._id_attr)
                if item_id not in all_ids:
                    all_ids.add(item_id)
                    yield result

            if len(all_ids) >= requested_length:
                return

            current_offset += page_length
            current_length = response['totalCount'] if is_api_paginable(response) else len(self)
            # If the total number of items decreased, reduce the offset by the difference to make sure we return all the
            # items. If duplicates occur in the process as described in step 5 of workflow in the docstring are handled
            # above by checking for the id in all_ids.
            if current_length < previous_length:
                current_offset -= previous_length - current_length
                if current_offset < 0:
                    logger.debug(f'Current offset was negative ({current_offset}), resetting it to 0.')
                    current_offset = 0
            previous_length = current_length
            # If the API we're paging over isn't enabled for pagination, break the loop after returning the first
            # set of results to avoid an infinite loop.
            if 'offset' not in response and 'len' not in response:
                break
            logger.debug('Fetching items with offset=%d and len=%d', current_offset, page_length)
            response, current_new_kwargs, class_type, class_kwargs = self._get_all_results_from_api(
                offset=current_offset, len=page_length, **kwargs_without_pagination_params
            )
            current_results = SeekableList(class_type(item, **class_kwargs) for item in response['data'])

    def __init__(self, control_hub):
        self._control_hub = control_hub
        self._id_attr = 'id'

    def __repr__(self):
        return str([item for item in self._paginate()])

    def __iter__(self):
        for item in self._paginate():
            yield item

    def __contains__(self, item_given):
        return self.contains(**{self._id_attr: getattr(item_given, self._id_attr)})

    def __len__(self):
        """Provides length (count) of items.

        Returns:
            A :py:obj:`int` object.
        """
        results = self._get_all_results_from_api().results
        return len(results['data'] if 'data' in results else results)

    def __getitem__(self, i):
        """Enables the user to fetch items by index.

        Args:
            i (:obj:`int`): Index of the item.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        if not isinstance(i, int) and not isinstance(i, slice):
            raise TypeError('list indices must be integers or slices, not {}'.format(type(i).__name__))

        total_number_of_items = len(self)

        if isinstance(i, int):
            # Convert negative index to positive index
            offset = total_number_of_items + i if i < 0 else i

            if not (0 <= offset < total_number_of_items):
                raise IndexError('list index out of range')

            len_ = 1
            new_i = 0
        else:
            # i is a slice
            if i.step == 0:
                raise ValueError('slice step cannot be zero')
            # i.start could be None
            start = i.start or 0
            # Convert negative index to positive index
            start = total_number_of_items + start if start < 0 else start

            # i.stop could be None and if i.stop is 0, we want it to be 0 so can't do i.stop or total_number_of_items
            # here
            stop = total_number_of_items if i.stop is None else i.stop
            # Convert negative index to positive index
            stop = total_number_of_items + stop if stop < 0 else stop

            step = i.step or 1

            if step < 0:
                # If step is negative, we need to look at the list in reverse
                start, stop = stop, start
                step = -step

            # Determine the number of items to query
            # If start is still negative, we don't need to query for the range start -> 0
            len_ = stop - max(0, start)

            # If length to query <= 0 or stop of the slice is <= 0 no need to query
            if len_ <= 0 or stop <= 0:
                return []

            # Offset cannot be negative
            offset = max(0, start)
            # Create a new slice with shifted indices
            new_i = slice(0, len_, step)

        return list(self._paginate(offset=offset, len=len_))[new_i]

    def _get_all_results_from_api(self, **kwargs):
        """Used to get multiple (all) results from api.

        Args:
            Optional arguments to be passed to filter the results.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of inherited instances of :py:class:`streamsets.sdk.sch_models.BaseModel`
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Deployment`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's __init__
        """
        raise NotImplementedError("Function has not been implemented for class {}".format(type(self).__name__))

    def contains(self, **kwargs):
        """
        Args:
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :py:obj:`boolean` object.
        """
        try:
            self.get(**kwargs)
        except (ValueError, ProjectAccessError):
            # this can occur when a user tries to access a resource from a different project.
            # e.g: org-level connection connectionA: connectionA = sch.connections[0]
            # switch to project projectA via sch.current_project = sch.projects[0]
            # check if the resource exists in a project: connectionA in sch.connections  # should be False
            # but since connections (and classes like Jobs) pass _id_attr in __contains__ we get a ProjectAccessError
            # as we try to get the resource by id instead of trying to get all resources and comparing.
            return False
        return True

    def get_all(self, **kwargs):
        """
        Args:
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        return SeekableList(self._paginate(**kwargs))

    def get(self, **kwargs):
        """
        Args:
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        # This will avoid querying all the items after finding the required item at some point.
        for item in self._paginate(**kwargs):
            return item
        # Raise instance doesn't exist if not found at the end
        raise ValueError(
            'Instance ({}) is not in list'.format(', '.join('{}={}'.format(k, v) for k, v in kwargs.items()))
        )


@analytics_class_decorator
class ACL(BaseModel):
    """Represents an ACL.

    Args:
        acl (:obj:`dict`): JSON representation of an ACL.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.

    Attributes:
        resource_id (:obj:`str`): Resource ID of the ACL.
        resource_owner (:obj:`str`): Resource owner of the ACL.
        resource_created_time (:obj:`str`): Creation time of the resource.
        resource_type (:obj:`str`): Resource type of the ACL.
        last_modified_by (:obj:`str`): Who the resource was last modified by.
        last_modified_on (:obj:`str`): Last modified time of the resource.
        permissions (:py:class:`streamsets.sdk.sch_models.Permissions`): A Collection of Permissions.
        permission_builder (:py:class:`streamsets.sdk.sch_models.ACLPermissionBuilder`): A Permission Builder instance.
    """

    _ATTRIBUTES_TO_REMAP = {
        'resource_id': 'resourceId',
        'resource_owner': 'resourceOwner',
        'resource_created_time': 'resourceCreatedTime',
        'resource_type': 'resourceType',
        'last_modified_by': 'lastModifiedBy',
        'last_modified_on': 'lastModifiedOn',
    }
    _ATTRIBUTES_TO_IGNORE = ['permissions']
    _REPR_METADATA = ['resource_id', 'resource_type']

    def __init__(self, acl, control_hub):
        super().__init__(
            acl,
            attributes_to_remap=ACL._ATTRIBUTES_TO_REMAP,
            attributes_to_ignore=ACL._ATTRIBUTES_TO_IGNORE,
            repr_metadata=ACL._REPR_METADATA,
        )
        self.permissions = SeekableList(
            Permission(permission, self.resource_type, control_hub.api_client)
            for permission in self._data['permissions']
        )
        self._control_hub = control_hub

    def __getitem__(self, key):
        return getattr(self, key)

    def __len__(self):
        return len(self._data)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in {'resource_owner'}:
            set_acl(self._control_hub.api_client, self.resource_type, self.resource_id, self._data)

    @property
    def permission_builder(self):
        """Get a permission builder instance with which a pipeline can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACLPermissionBuilder`.
        """
        permission = {
            property: None for property in self._control_hub._job_api['definitions']['PermissionJson']['properties']
        }

        return ACLPermissionBuilder(permission=permission, acl=self)

    def add_permission(self, permission):
        """Add new permission to the ACL.

        Args:
            permission (:py:class:`streamsets.sdk.sch_models.Permission`): A permission object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        self._data['permissions'].append(permission._data)
        return set_acl(self._control_hub.api_client, self.resource_type, self.resource_id, self._data)

    def remove_permission(self, permission):
        """Remove a permission from ACL.

        Args:
            permission (:py:class:`streamsets.sdk.sch_models.Permission`): A permission object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        permissions = self._data['permissions']
        self._data['permissions'] = [perm for perm in permissions if perm['subjectId'] != permission.subject_id]
        return set_acl(self._control_hub.api_client, self.resource_type, self.resource_id, self._data)


@analytics_class_decorator
class ACLPermissionBuilder:
    """Class to help build the ACL permission.

    Args:
        permission (:py:class:`streamsets.sdk.sch_models.Permission`): A permission object.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): An ACL object.
    """

    def __init__(self, permission, acl):
        self._permission = permission
        self._acl = acl

    def build(self, subject_id, subject_type, actions):
        """Method to help build the ACL permission.

        Args:
            subject_id (:obj:`str`): ID of the USER or GROUP.
            subject_type (:obj:`str`): Type of the subject. Accepted Values are 'USER', 'GROUP'.
            actions (:obj:`list`): A list of actions of type :obj:`str` e.g. ['READ', 'WRITE', 'EXECUTE'].

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Permission`.
        """
        try:
            if subject_type == 'USER':
                # Raises a HTTPError if subject_id not found
                self._acl._control_hub.users.get(id=subject_id)
            elif subject_type == 'GROUP':
                # Raises a ValueError if subject_id not found
                self._acl._control_hub.groups.get(group_id=subject_id)
            else:
                raise TypeError("Subject Type {} is invalid".format(subject_type))
        except (requests.HTTPError, ValueError):
            raise ValueError(
                'Subject ID {} does not exist in this organization.'
                ' Please invite or create the subject first.'.format(subject_id)
            )

        self._permission.update(
            {
                'resourceId': self._acl.resource_id,
                'subjectId': subject_id,
                'subjectType': subject_type,
                'actions': actions,
            }
        )
        return Permission(self._permission, self._acl.resource_type, self._acl._control_hub.api_client)


@analytics_class_decorator
class AdminTool:
    """ControlHub Admin tool model.

    Args:
        base_url (:obj:`str`): Base url of the admin tool.
        username (:obj:`str`): Username for the admin tool.
        password (:obj:`str`): Password for the admin tool.

     Attributes:
        logs (:py:class:`streamsets.sdk.sch_models.Logs`): A collection of system logs from admin app.
    """

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.api_client = sch_api.AdminToolApiClient(base_url, username, password)
        self.api_client.login()

    @property
    def logs(self):
        """Gather system logs from admin app."""
        log_parts = []
        # As per 'https://git.io/JexPa', the streamer uses a buffer of size 50 Kb
        offset_constant = 50 * 1024
        ending_offset = offset_constant
        # Retreive all parts of the text file and combine them
        log_part = self.api_client.get_system_logs(ending_offset=ending_offset).response.text
        while log_part:
            log_parts.append(log_part)
            ending_offset += offset_constant
            log_part = self.api_client.get_system_logs(ending_offset=ending_offset).response.text
        return Logs(''.join(log_parts).split('\n'))


@analytics_class_decorator
class Permission(BaseModel):
    """A container for a permission.

    Args:
        permission (:obj:`dict`): A Python object representation of a permission.
        resource_type (:obj:`str`): String representing the type of resource e.g. 'JOB', 'PIPELINE'.
        api_client (:py:class:`streamsets.sdk.sch_api.ApiClient`): An instance of ApiClient.

    Attributes:
        resource_id (:obj:`str`): Id of the resource e.g. Pipeline or Job.
        subject_id (:obj:`str`): Id of the subject e.g. user id ``'admin@admin'``.
        subject_type (:obj:`str`): Type of the subject e.g. ``'USER'``.
        last_modified_by (:obj:`str`): User who last modified this permission e.g. ``'admin@admin'``.
        last_modified_on (:obj:`int`): Timestamp at which this permission was last modified e.g. ``1550785079811``.
    """

    _ATTRIBUTES_TO_REMAP = {
        'resource_id': 'resourceId',
        'subject_id': 'subjectId',
        'subject_type': 'subjectType',
        'last_modified_by': 'lastModifiedBy',
        'last_modified_on': 'lastModifiedOn',
    }
    _ATTRIBUTES_TO_IGNORE = ['resourceType', 'apiClient']
    _REPR_METADATA = ['resource_id', 'subject_type', 'subject_id']

    class VALID_ACTIONS(enum.Enum):
        READ = 'READ'
        WRITE = 'WRITE'
        EXECUTE = 'EXECUTE'

    def __init__(self, permission, resource_type, api_client):
        super().__init__(
            permission,
            attributes_to_remap=Permission._ATTRIBUTES_TO_REMAP,
            attributes_to_ignore=Permission._ATTRIBUTES_TO_IGNORE,
            repr_metadata=Permission._REPR_METADATA,
        )
        self._resource_type = resource_type
        self._api_client = api_client

    def _valid_action(self, value):
        if "READ" not in value:
            return False
        return all(self.VALID_ACTIONS(i) for i in value)

    def __setattr__(self, key, value):
        if key == 'actions' and not self._valid_action(value):
            raise ValueError(
                'Invalid permission {}, acceptable permissions are ["READ"], ["READ","WRITE"], '
                '["READ","EXECUTE"] or ["READ","WRITE","EXECUTE"]'.format(value)
            )

        super().__setattr__(key, value)
        if key in {'actions', 'subject_id', 'subject_type'}:
            update_acl_permissions(self._api_client, self._resource_type, self._data)


class UserBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.User`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_user_builder`.

    Args:
        user (:obj:`dict`): Python object built from our Swagger UserJson definition.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`. Default: ``None``.
    """

    def __init__(self, user, roles, control_hub=None):
        self._user = user
        self._roles = roles
        self._control_hub = control_hub

    def build(self, email_address):
        """Build the user.

        Args:
            email_address (:obj:`str`): User Email Address.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.User`.
        """
        self._user.update({'email': email_address})
        return User(user=self._user, roles=self._roles, control_hub=self._control_hub)


class User(BaseModel):
    """Model for User.

    Args:
        user (:obj:`dict`): JSON representation of User.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        control_hub (:py:class:`streamsets.sdk.ControlHub`, optional): An instance of Control Hub. Default: ``None``

    Attributes:
        active (:obj:`bool`): Whether the user is active or not.
        created_by (:obj:`str`): Creator of this user.
        created_on (:obj:`str`): Creation time of this user.
        display_name (:obj:`str`): Display name of this user.
        email_address (:obj:`str`): Email address of this user.
        id (:obj:`str`): Id of this user.
        groups (:py:class:`streamsets.sdk.util.SeekableList` of :py:class:`streamsets.sdk.sch_models.Group` instances):
            Groups this user belongs to.
        last_modified_by (:obj:`str`): User last modified by.
        last_modified_on (:obj:`str`): User last modification time.
        organization (:obj:`str`): Organization ID that the user is part of.
        password_expires_on (:obj:`str`): User's password expiration time.
        password_system_generated (:obj:`bool`): Whether User's password is system generated or not.
        organization_roles (:obj:`set`): A set of role labels to be used organization wide.
        project_roles (:obj:`set`): A set of role labels applicable for the user in a project.
        saml_user_name (:obj:`str`): SAML username of user.
        status (:obj:`str`): The status of the user.
    """

    _ATTRIBUTES_TO_IGNORE = [
        'deleteTime',
        'destroyer',
        'groups',
        'migrationAliases',
        'roles',
        'userDeleted',
    ]
    _ATTRIBUTES_TO_REMAP = {
        'created_by': 'creator',
        'email_address': 'email',
        'display_name': 'name',
        'saml_user_name': 'nameInOrg',
        'password_expires_on': 'passwordExpiryTime',
        'password_system_generated': 'passwordGenerated',
    }
    _REPR_METADATA = ['email_address', 'display_name', 'status', 'last_modified_on']

    # Jetty requires every ControlHub user to have the 'user' role, which is hidden in the UI. We'll do the same.
    _ROLES_TO_HIDE = ['user', 'org-user']

    def __init__(self, user, roles, control_hub=None):
        super().__init__(
            user,
            attributes_to_ignore=User._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=User._ATTRIBUTES_TO_REMAP,
            repr_metadata=User._REPR_METADATA,
        )
        self._roles = roles
        self._control_hub = control_hub

    @property
    def groups(self):
        """Get the group memberships for the user."""
        return UserMembership(
            [group for group in self._control_hub.groups if group.group_id in self._data['groups']],
            self._data['groups'],
        )

    @groups.setter
    def groups(self, groups):
        """Set the group membership for the user.

        Args:
            groups: A :obj:`list` of one or more :py:class:`streamsets.sdk.sch_models.Group` instances.
        """
        group_list = groups if isinstance(groups, list) else [groups]
        self._data['groups'] = [group.group_id for group in group_list]

    @property
    def roles(self):
        """Get the roles for the user."""
        warnings.warn(
            'The `roles` attribute is now deprecated for User objects. It has been replaced by the'
            ' `organization_roles` attribute. Please update your usage accordingly.',
            DeprecationWarning,
        )
        return self.organization_roles

    @roles.setter
    def roles(self, value):
        """Set the roles for the user.

        Args:
            value: A :obj:`list` of one or more roles. A role is of type :obj:`str`.
        """
        warnings.warn(
            'The `roles` attribute is now deprecated for User objects. It has been replaced by the'
            ' `organization_roles` attribute. Please update your usage accordingly.',
            DeprecationWarning,
        )
        self.organization_roles = value

    @property
    def organization_roles(self):
        """Get the organization roles for the user."""
        return Roles(
            [self._roles[role] for role in self._data.get('roles', []) if role not in User._ROLES_TO_HIDE],
            self,
            reversed_dict(self._roles),
            role_data_key='roles',
        )

    @organization_roles.setter
    def organization_roles(self, value):
        """Set the organization roles for the user.

        Args:
            value: A :obj:`list` of one or more roles. A role is of type :obj:`str`.
        """
        # We reverse the _roles dictionary to let this setter deal with role labels while still writing role ids.
        role_label_to_id = {role_label: role_id for role_id, role_label in self._roles.items()}

        value_ = value if isinstance(value, list) else [value]
        self._data['roles'] = list({role_label_to_id[role] for role in value_} | set(User._ROLES_TO_HIDE))

    @property
    def project_roles(self):
        """Get the project roles for the user."""
        return Roles(
            [self._roles[role] for role in self._data.get('projectRoles', []) if role not in User._ROLES_TO_HIDE],
            self,
            reversed_dict(self._roles),
            role_data_key='projectRoles',
        )

    @project_roles.setter
    def project_roles(self, value):
        """Set the project roles for the user.

        Args:
            value: A :obj:`list` of one or more roles. A role is of type :obj:`str`.
        """
        # We reverse the _roles dictionary to let this setter deal with role labels while still writing role ids.
        role_label_to_id = {role_label: role_id for role_id, role_label in self._roles.items()}

        value_ = value if isinstance(value, list) else [value]
        self._data['projectRoles'] = list({role_label_to_id[role] for role in value_} | set(User._ROLES_TO_HIDE))

    @property
    def status(self):
        """Get the status of the user. Values that can be returned are either 'ACTIVE' or 'DEACTIVATED'."""
        return 'ACTIVE' if self._data['active'] else 'DEACTIVATED'


class UserMembership(SeekableList):
    """Wrapper class for the list of groups a User is a member of.

    Args:
        groups: A :obj:`list` of :py:class:`streamsets.sdk.sch_models.Group` instances.
        entity (:obj:`list`): List of group IDs for a :py:class:`streamsets.sdk.sch_models.User` object.
    """

    def __init__(self, groups, entity):
        super().__init__(groups)
        self._entity = entity

    def __contains__(self, group):
        return group.group_id in self._entity

    def append(self, group):
        """Add another :py:class:`streamsets.sdk.sch_models.Group` instance for the user.

        Args:
            group (:py:class:`streamsets.sdk.sch_models.Group): A group instance to add.
        """
        # We only need to store a group's ID value, not the whole group instance.
        self._entity.append(group.group_id)

    def remove(self, group):
        """Remove a :py:class:`streamsets.sdk.sch_models.Group` instance from the user.

        Args:
            group (:py:class:`streamsets.sdk.sch_models.Group): The group instance to remove.
        """
        # We only store ID values, so we attempt to remove the ID of the provided group - not the whole group instance.
        self._entity.remove(group.group_id)


@analytics_class_decorator
class Users(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.User` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, roles, organization):
        super().__init__(control_hub)
        self._roles = roles
        self._organization = organization

    def _get_all_results_from_api(self, id=None, organization=None, **kwargs):
        """
        Args:
            id (:obj:`str`, optional): User ID. Default: ``None``.
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            filter_text (:obj:`str`, optional): Only returns instances that match the filter string. This will be
                propagated to the API backend (results filtered server-side instead of client-side).
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.User` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.User`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {
            'offset': None,
            'len': None,
            'order_by': 'ID',
            'order': 'ASC',
            'active': None,
            'filter_text': None,
            'deleted': None,
        }
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if id:
            response = [self._control_hub.api_client.get_user(org_id=organization, user_id=id).response.json()]
        else:
            response = self._control_hub.api_client.get_all_users(
                org_id=organization,
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                active=kwargs_unioned['active'],
                filter_text=kwargs_unioned['filter_text'],
                deleted=kwargs_unioned['deleted'],
                with_wrapper=True,
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(
            response, kwargs_unused, User, {'roles': self._roles, 'control_hub': self._control_hub}
        )


class LoginAudit(BaseModel):
    """Model for LoginAudit.

    Args:
        login_audit (:obj:`dict`): JSON representation of LoginAudit.

    Attributes:
        details (:obj:`str`): Details of login audit.
        ip_address (:obj:`str`): IP address that tried logging in.
        login_time (:obj:`int`): Login time of this user.
        logout_time (:obj:`int`): Time of logout.
        logout_user_id (:obj:`str`): User that attempted logout.
        logout_reason (:obj:`str`): Reason for logout.
        organization (:obj:`str`): Organization ID.
        success (:obj:`bool`): If this login succeeded.
        user_agent (:obj:`str`): User that made login request. May differ from user_id
        user_id (:obj:`str`): ID of user account that login was attempted for.
    """

    _ATTRIBUTES_TO_REMAP = {
        'login_time': 'loginTimestamp',
        'logout_time': 'logoutTimestamp',
        'logout_user_id': 'logoutUser',
        'organization': 'org_id',
    }
    _REPR_METADATA = ['user_id', 'ip_address', 'login_timestamp', 'logout_timestamp']

    def __init__(self, login_audit):
        super().__init__(
            login_audit, attributes_to_remap=LoginAudit._ATTRIBUTES_TO_REMAP, repr_metadata=LoginAudit._REPR_METADATA
        )


@analytics_class_decorator
class LoginAudits(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.LoginAudit` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization
        self._id_attr = 'login_time'

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """
        Args:
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.LoginAudit` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.LoginAudit`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None, 'sort_field': None, 'sort_order': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_login_audits_for_org(
            org_id=organization,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            sort_field=kwargs_unioned['sort_field'],
            sort_order=kwargs_unioned['sort_order'],
            with_wrapper=True,
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, LoginAudit, {})


class ActionAudit(BaseModel):
    """Model for ActionAudit.

    Args:
        action_audit (:obj:`dict`): JSON representation of ActionAudit.

    Attributes:
        action (:obj:`str`): Action performed.
        affected_user_id (:obj:`str`): User ID of the affected user.
        field_type (:obj:`str`): Type of field.
        id (:obj:`str`): ID of this action audit.
        ip_address (:obj:`str`): IP address that tried logging in.
        new_value (:obj:`str`): New value.
        old_value (:obj:`str`): Old Value.
        organization (:obj:`str`): Organization ID.
        requested_user_id (:obj:`str`): User ID of the requested user.
        time (:obj:`int`): Timestamp.
    """

    _ATTRIBUTES_TO_REMAP = {
        'affected_user_id': 'affectsUser',
        'requested_user_id': 'requesterId',
        'organization': 'orgId',
    }
    _REPR_METADATA = ['affected_user_id', 'action', 'time', 'ip_address']

    def __init__(self, action_audit):
        super().__init__(
            action_audit, attributes_to_remap=ActionAudit._ATTRIBUTES_TO_REMAP, repr_metadata=ActionAudit._REPR_METADATA
        )


@analytics_class_decorator
class ActionAudits(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ActionAudit` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """
        Args:
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.ActionAudit` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.ActionAudit`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None, 'sort_field': None, 'sort_order': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_user_actions_for_org(
            org_id=organization,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            sort_field=kwargs_unioned['sort_field'],
            sort_order=kwargs_unioned['sort_order'],
            with_wrapper=True,
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ActionAudit, {})


class ConnectionAudit(BaseModel):
    """Model for ConnectionAudit.

    Args:
        connection_audit (:obj:`dict`): JSON representation of ConnectionAudit.

    Attributes:
        id (:obj:`str`): Connection audit ID.
        organization (:obj:`str`): Organization.
        user_id (:obj:`str`): User ID.
        connection_id (:obj:`str`): Connection ID.
        connection_name (:obj:`str`): Connection name.
        audit_time (:obj:`str`): Audit time.
        audit_action (:obj:`str`): Audit action
    """

    _REPR_METADATA = ['user_id', 'connection_name', 'audit_action', 'audit_time']

    def __init__(self, connection_audit):
        super().__init__(connection_audit, repr_metadata=ConnectionAudit._REPR_METADATA)


@analytics_class_decorator
class ConnectionAudits(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ConnectionAudit` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, start_time=None, end_time=None, organization=None, connection=None, **kwargs):
        """
        Args:
            start_time (:obj:`float`, optional): Start time in milliseconds (will be rounded off to closest integer).
                                                 Default: ``None``. If both start_time and end_time are not specified,
                                                 we return the audits for last 30 days.
            end_time (:obj:`float`, optional): End time in milliseconds (will be rounded off to closest integer).
                                               Default: ``None``. If both start_time and end_time are not specified,
                                               we return the audits for last 30 days.
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            connection (:py:obj:`streamsets.sdk.sch_models.Connection`, optional): Connection object.
                                                                                    Default: ``None``.
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.ConnectionAudit` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.ConnectionAudit`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None, 'sort_field': None, 'sort_order': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if (start_time is None and end_time is not None) or (start_time is not None and end_time is None):
            raise ValueError('Either both or None of start_time and end_time should be specified')
        if start_time is not None and connection is not None:
            raise ValueError('start_time and end_time cannot be specified when connection argument is passed')
        if connection is not None:
            response = self._control_hub.api_client.get_audits_for_connection(
                connection_id=connection.id
            ).response.json()
        elif start_time is None and end_time is None:
            response = self._control_hub.api_client.get_all_connection_audits_last_30_days(
                org_id=organization,
                offset=kwargs_unioned['offset'],
                len_=kwargs_unioned['len'],
                sort_field=kwargs_unioned['sort_field'],
                sort_order=kwargs_unioned['sort_order'],
            ).response.json()
        else:
            response = self._control_hub.api_client.get_all_connection_audits(
                org_id=organization,
                offset=kwargs_unioned['offset'],
                len_=kwargs_unioned['len'],
                sort_field=kwargs_unioned['sort_field'],
                sort_order=kwargs_unioned['sort_order'],
                start_time=int(start_time),
                end_time=int(end_time),
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ConnectionAudit, {})


class Roles(list):
    """Wrapper class over the list of Roles.

    Args:
        values (:obj:`list`): List of roles.
        entity (:py:class:`streamsets.sdk.sch_models.Group`) or
              (:py:class:`streamsets.sdk.sch_models.User`): Group or User object.
        role_label_to_id (:obj:`dict`): Role label to Role ID mapping.
        role_data_key(:obj:`str`): The key the roles map to in the underlying user or group object. Default: ``role``.
    """

    def __init__(self, values, entity, role_label_to_id, role_data_key='role'):
        super().__init__(values)
        self._entity = entity
        self._role_label_to_id = role_label_to_id
        self._role_data_key = role_data_key

    def append(self, value):
        """
        The method appends a role or an iterable of roles

        Args:
            value (:obj:`str`, `iterable`): Role string or an iterable of roles

        Returns:
            None

        Raises:
            TypeError: This exception is raised if the value argument is not a str or iterable of str.
        """
        # If value is str, then push it into a list
        if isinstance(value, str):
            value = [value]

        try:
            for element in value:
                if not isinstance(element, str):
                    raise TypeError

                # Use super().append() to throw corresponding exceptions when necessary.
                super().append(element)
                self._entity._data[self._role_data_key].append(self._role_label_to_id[element])

        except TypeError:
            raise TypeError('Value to append to roles must be a str or an iterable of str')

    def remove(self, value):
        """
        The method removes a role or an iterable of roles

        Args:
            value (:obj:`str`, `iterable`): Role string or an iterable of roles

        Returns:
            None

        Raises:
            TypeError: This exception is raised if the value argument is not a str or iterable of str.
        """
        # If value is str, then push it into a list
        if isinstance(value, str):
            value = [value]

        try:
            for element in value:
                if not isinstance(element, str):
                    raise TypeError

                # Use super().remove() to throw corresponding exceptions when necessary.
                super().remove(element)
                self._entity._data[self._role_data_key].remove(self._role_label_to_id[element])

        except TypeError:
            raise TypeError('Value to remove from roles must be a str or an iterable of str')

    def __delitem__(self, value):
        raise RuntimeError("Please use the append/remove methods to interact with a collection of roles.")

    def pop(self, value=-1):
        raise RuntimeError("Please use the append/remove methods to interact with a collection of roles.")

    def clear(self):
        raise RuntimeError("Please use the append/remove methods to interact with a collection of roles.")

    def sort(self):
        raise RuntimeError("Please use the append/remove methods to interact with a collection of roles.")

    def reverse(self):
        raise RuntimeError("Please use the append/remove methods to interact with a collection of roles.")

    def __setitem__(self, key, value):
        raise RuntimeError("Please use the append/remove methods to interact with a collection of roles.")

    def __iadd__(self, key):
        raise RuntimeError("Please use the append/remove methods to interact with a collection of roles.")

    def __imul__(self, key):
        raise RuntimeError("Please use the append/remove methods to interact with a collection of roles.")

    def extend(self, value):
        raise RuntimeError("Please use the append/remove methods to interact with a collection of roles.")

    def insert(self, ind, value):
        raise RuntimeError("Please use the append/remove methods to interact with a collection of roles.")


class GroupBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Group`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_group_builder`.

    Args:
        group (:obj:`dict`): Python object built from our Swagger GroupJson definition.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`, optional): ControlHub object. Default: ``None``
    """

    def __init__(self, group, roles, control_hub=None):
        self._group = group
        self._roles = roles
        self._control_hub = control_hub

    def build(self, display_name, group_id=None, ldap_groups=None):
        """Build the group.

        Args:
            display_name (:obj:`str`): Group display name.
            group_id (:obj:`str`, optional): Group ID. Can only include letters, numbers, underscores and periods.
                Default: ``None``.
            ldap_groups (:obj:`list`, optional): List of LDAP groups (strings).

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Group`.
        """
        self._group.update(
            {
                'id': '{}@{}'.format(
                    group_id or re.sub(r'[^a-zA-Z_0-9\.]', '_', display_name), self._control_hub.organization
                ),
                'name': display_name,
                'externalGroupIds': ldap_groups,
            }
        )
        return Group(group=self._group, roles=self._roles, control_hub=self._control_hub)


class Group(BaseModel):
    """Model for Group.

    Args:
        group (:obj:`dict`): A Python object representation of Group.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        control_hub (:py:class:`streamsets.sdk.ControlHub`, optional): An instance of Control Hub. Default: ``None``

    Attributes:
        created_by (:obj:`str`): Creator of this group.
        created_on (:obj:`str`): Creation time of this group.
        display_name (:obj:`str`): Display name of this group.
        group_id (:obj:`str`): ID of this group.
        last_modified_by (:obj:`str`): Group last modified by.
        last_modified_on (:obj:`str`): Group last modification time.
        organization (:obj:`str`): Organization this group belongs to.
        organization_roles (:obj:`set`): A set of role labels to be used organization wide.
        project_roles (:obj:`set`): A set of role labels applicable for the user in a project.
        users (:py:class:`streamsets.sdk.util.SeekableList` of :py:class:`streamsets.sdk.sch_models.User` instances):
            Users that are a member of this group.

    """

    _ATTRIBUTES_TO_IGNORE = ['deleteTime', 'destroyer', 'groupDeleted', 'users']

    _ATTRIBUTES_TO_REMAP = {'created_by': 'creator', 'display_name': 'name', 'group_id': 'id'}

    _REPR_METADATA = ['group_id', 'display_name', 'last_modified_on']

    # Jetty requires every ControlHub group to have the 'user' role, which is hidden in the UI. We'll do the same.
    _ROLES_TO_HIDE = ['user', 'org-user']

    def __init__(self, group, roles, control_hub=None):
        super().__init__(
            group,
            attributes_to_ignore=Group._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=Group._ATTRIBUTES_TO_REMAP,
            repr_metadata=Group._REPR_METADATA,
        )
        self._roles = roles
        self._control_hub = control_hub

    @property
    def roles(self):
        """Get the roles for the group."""
        warnings.warn(
            'The `roles` attribute is now deprecated for Group objects. It has been replaced by the'
            ' `organization_roles` attribute. Please update your usage accordingly.',
            DeprecationWarning,
        )
        return self.organization_roles

    @roles.setter
    def roles(self, value):
        """Set the roles for the group.

        Args:
            value: A :obj:`list` of one or more roles. A role is of type :obj:`str`.
        """
        warnings.warn(
            'The `roles` attribute is now deprecated for Group objects. It has been replaced by the'
            ' `organization_roles` attribute. Please update your usage accordingly.',
            DeprecationWarning,
        )
        self.organization_roles = value

    @property
    def organization_roles(self):
        """Get the organization roles for the group."""
        return Roles(
            [self._roles[role] for role in self._data.get('roles', []) if role not in Group._ROLES_TO_HIDE],
            self,
            reversed_dict(self._roles),
            role_data_key='roles',
        )

    @organization_roles.setter
    def organization_roles(self, value):
        """Set the organization roles for the group.

        Args:
            value: A :obj:`list` of one or more roles. A role is of type :obj:`str`.
        """
        # We reverse the _roles dictionary to let this setter deal with role labels while still writing role ids.
        role_label_to_id = reversed_dict(self._roles)

        value_ = value if isinstance(value, list) else [value]
        self._data['roles'] = list({role_label_to_id[role] for role in value_} | set(Group._ROLES_TO_HIDE))

    @property
    def project_roles(self):
        """Get the project roles for the group."""
        return Roles(
            [self._roles[role] for role in self._data.get('projectRoles', []) if role not in Group._ROLES_TO_HIDE],
            self,
            reversed_dict(self._roles),
            role_data_key='projectRoles',
        )

    @project_roles.setter
    def project_roles(self, value):
        """Set the project roles for the group.

        Args:
            value: A :obj:`list` of one or more roles. A role is of type :obj:`str`.
        """
        # We reverse the _roles dictionary to let this setter deal with role labels while still writing role ids.
        role_label_to_id = reversed_dict(self._roles)

        value_ = value if isinstance(value, list) else [value]
        self._data['projectRoles'] = list({role_label_to_id[role] for role in value_} | set(Group._ROLES_TO_HIDE))

    @property
    def users(self):
        """Get the users that are members of the group."""
        return GroupMembers(
            [user for user in self._control_hub.users if user.id in self._data['users']], self._data['users']
        )

    @users.setter
    def users(self, users):
        """Set the users that are members of the group.

        Args:
            users: A :obj:`list` of one or more :py:class:`streamsets.sdk.sch_models.User` instances.
        """
        user_list = users if isinstance(users, list) else [users]
        self._data['users'] = [user.id for user in user_list]


class GroupMembers(SeekableList):
    """Wrapper class for the list of users a Group contains.

    Args:
        members: A :obj:`list` of :py:class:`streamsets.sdk.sch_models.User` instances.
        entity (:obj:`list`): List of user IDs for a :py:class:`streamsets.sdk.sch_models.Group` object.
    """

    def __init__(self, members, entity):
        super().__init__(members)
        self._entity = entity

    def __contains__(self, user):
        return user.id in self._entity

    def append(self, user):
        """Add another :py:class:`streamsets.sdk.sch_models.User` instance to the group.

        Args:
            user (:py:class:`streamsets.sdk.sch_models.User): A user instance to add.
        """
        # We only need to store a user's ID value, not the whole user instance.
        self._entity.append(user.id)

    def remove(self, user):
        """Remove a :py:class:`streamsets.sdk.sch_models.User` instance from the group.

        Args:
            user (:py:class:`streamsets.sdk.sch_models.User): The user instance to remove.
        """
        # We only store ID values, so we attempt to remove the ID of the provided user - not the whole user instance.
        self._entity.remove(user.id)


@analytics_class_decorator
class Groups(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Group` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, roles, organization):
        super().__init__(control_hub)
        self._roles = roles
        self._organization = organization
        self._id_attr = 'group_id'

    def _get_all_results_from_api(self, group_id=None, organization=None, **kwargs):
        """
        Args:
            group_id (:obj:`str`, optional): Group ID. Default: ``None``.
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            filter_text (:obj:`str`, optional): Only returns instances that match the filter string. This will be
                propagated to the API backend (results filtered server-side instead of client-side).
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Group` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Group`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {
            'offset': None,
            'len': None,
            'order_by': 'ID',
            'order': 'ASC',
            'filter_text': None,
            'deleted': None,
        }
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if group_id is not None:
            try:
                group_command = self._control_hub.api_client.get_group(org_id=organization, group_id=group_id)
                response = group_command.response.json() if group_command.response.content else None
                if not response:
                    raise ValueError('Group (group_id={}) not found'.format(group_id))
                kwargs_unused = kwargs_instance.subtract()
                return CollectionModelResults(
                    [response], kwargs_unused, Group, {'roles': self._roles, 'control_hub': self._control_hub}
                )
            except requests.exceptions.HTTPError:
                raise ValueError('Group (group_id={}) not found'.format(group_id))
        response = self._control_hub.api_client.get_all_groups(
            org_id=organization,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            order_by=kwargs_unioned['order_by'],
            order=kwargs_unioned['order'],
            filter_text=kwargs_unioned['filter_text'],
            deleted=kwargs_unioned['deleted'],
            with_wrapper=True,
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(
            response, kwargs_unused, Group, {'roles': self._roles, 'control_hub': self._control_hub}
        )


class OrganizationBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Organization`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_organization_builder`.

    Args:
        organization (:obj:`dict`): Python object built from our Swagger UserJson definition.
    """

    def __init__(self, organization, organization_admin_user):
        self._organization = organization
        self._organization_admin_user = organization_admin_user

    def build(
        self, id, name, admin_user_id, admin_user_display_name, admin_user_email_address, admin_user_ldap_user_name=None
    ):
        """Build the organization.

        Args:
            id (:obj:`str`): Organization ID.
            name (:obj:`str`): Organization name.
            admin_user_id (:obj:`str`): User Id of the admin of this organization.
            admin_user_display_name (:obj:`str`): User display name of admin of this organization.
            admin_user_email_address (:obj:`str`): User email address of admin of this organization.
            admin_user_ldap_user_name (:obj:`str`, optional): LDAP username. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Organization`.
        """
        self._organization.update({'id': id, 'name': name, 'primaryAdminId': admin_user_id})
        self._organization_admin_user.update(
            {
                'id': admin_user_id,
                'name': admin_user_display_name,
                'email': admin_user_email_address,
                'organization': id,
                'nameInOrg': admin_user_ldap_user_name,
            }
        )
        return Organization(self._organization, self._organization_admin_user)


@analytics_class_decorator
class Organization(BaseModel):
    """Model for Organization.

    Args:
        organization (:obj:`str`): Organization Id.
        organization_admin_user (:obj:`str`, optional): Default: ``None``.
        api_client (:py:obj:`streamsets.sdk.sch_api.ApiClient`, optional): Default: ``None``.

    Attributes:
        default_user_password_expiry_time_in_days (:obj:`str`): Default expiry time of the user password for the organization.
        configuration (:py:class:`streamsets.sdk.models.Configuration`): Configuration for the organization.
        admin_user_id (:obj:`str`): Organization admin's user ID.
        created_by (:obj:`str`): Who the Organization was created by.
        saml_intergration_enabled (:obj:`bool`): Whether SAML integration is enabled.
    """

    _ATTRIBUTES_TO_IGNORE = [
        'configuration',
        'passwordExpiryTimeInMillis',
    ]
    _ATTRIBUTES_TO_REMAP = {
        'admin_user_id': 'primaryAdminId',
        'created_by': 'creator',
        'saml_intergration_enabled': 'externalAuthEnabled',
    }
    _REPR_METADATA = ['id', 'name']

    def __init__(self, organization, organization_admin_user=None, api_client=None):
        super().__init__(
            organization,
            attributes_to_ignore=Organization._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=Organization._ATTRIBUTES_TO_REMAP,
            repr_metadata=Organization._REPR_METADATA,
        )
        self._organization_admin_user = organization_admin_user
        self._api_client = api_client

    @property
    def default_user_password_expiry_time_in_days(self):
        """Get the default expiry time of the user password for the organization."""
        return self._data['passwordExpiryTimeInMillis'] / 86400000  # 1 d => ms

    @default_user_password_expiry_time_in_days.setter
    def default_user_password_expiry_time_in_days(self, value):
        """Set the default expiry time of the user password for the organization.

        Args:
            value(:obj:`int`): Default expiry time of the user password for the organization.
        """
        self._data['passwordExpiryTimeInMillis'] = value * 86400000

    @property
    def configuration(self):
        """Get the :py:class:`streamsets.sdk.models.Configuration` instance for the organization."""
        configuration = self._api_client.get_organization_configuration(self.id).response.json()

        # Some of the config names are a bit long, so shorten them slightly...
        ID_TO_REMAP = {
            'Timestamp of the contract expiration': 'Timestamp of the contract expiration.'
            ' Only applicable to enterprise accounts',
            'Timestamp of the trial expiration': 'Timestamp of the trial expiration.'
            ' Only applicable to trial accounts',
        }
        return Configuration(
            configuration=configuration,
            update_callable=self._api_client.update_organization_configuration,
            update_callable_kwargs=dict(org_id=self.id),
            id_to_remap=ID_TO_REMAP,
        )

    @configuration.setter
    def configuration(self, value):
        """Set a configuration object for the organization.

        Args:
            value: Value to set for 'id'.
        """
        self._api_client.update_organization_configuration(self.id, value._data)

    @property
    def ip_auth_enabled(self):
        """Returns whether IP Auth rules are enabled for the organization.

        Returns:
            An :obj:`bool`.
        """
        configs = self._api_client.get_organization_configuration_v2(org_id=self.id).response.json()
        return configs.get('ipAuthRules', {}).get('enabled')

    @ip_auth_enabled.setter
    def ip_auth_enabled(self, value):
        """Sets whether IP Auth rules are enabled for the organization.

        Args:
            value (:obj:`bool`): Whether IP Auth should be enabled for the organization.
        """

        if not isinstance(value, bool):
            raise TypeError("ip_auth_enabled should be of type bool.")

        configs = self._api_client.get_organization_configuration_v2(org_id=self.id).response.json()

        if value is True and len(configs.get('ipAuthRules', {}).get('rules')) == 0:
            raise ValueError("No rules added, add at least one rule before enabling IP Auth.")

        configs['ipAuthRules']['enabled'] = value
        # clear configs to avoid updating something that is not allowed by org admins.
        configs['configs'].clear()
        self._api_client.update_organization_configuration_v2(data=configs, org_id=self.id)

    @property
    def ip_auth_rules(self):
        """The current set of IP Auth rules in the organization.

        Returns:
            An :obj:`tuple` containing :obj:`dict` for each IP Auth rule in the organization.
        """
        configs = self._api_client.get_organization_configuration_v2(org_id=self.id).response.json()

        # casting the list to a tuple so that it is immutable by the user. To avoid any confusion with usability.
        return tuple(configs.get('ipAuthRules', {}).get('rules'))

    @ip_auth_rules.setter
    def ip_auth_rules(self, value):
        raise NotImplementedError(
            "Not possible to directly set the value of IP auth rules."
            "Use `add_ip_auth_ruleset` and `remove_ip_auth_ruleset` to modify the rules."
        )

    def add_ip_auth_ruleset(self, ip_address, bitmask=32, comment=''):
        """Add a rule to the IP Auth ruleset.

        Args:
            ip_address (:obj:`str`): IP Address to be added. Should be IPv4.
            bitmask (:obj:`int`, optional): Bitmask to apply to the IP Address. Default ``32``.
            comment (:obj:`str`, optional): Comments to be made regarding the rule.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """

        if not isinstance(ip_address, str):
            raise TypeError("ip_address should be of type str")

        try:
            # ensure the address passed it a valid IPv4 address
            ipaddress.IPv4Address(ip_address)
        except ipaddress.AddressValueError:
            raise ValueError("ip_address is not a valid IPv4 address.")

        if not isinstance(bitmask, int):
            raise TypeError("bitmask should be of type int")

        if bitmask < 0 or bitmask > 32:
            raise ValueError("bitmask value must be within the inclusive range 0-32.")

        if not isinstance(comment, str):
            raise TypeError("comment should be of type str")

        new_rule = dict(ruleType='IPV4_ALLOW', address=ip_address, bitMask=bitmask, comment=comment)

        configs = self._api_client.get_organization_configuration_v2(org_id=self.id).response.json()
        configs['ipAuthRules']['rules'].append(new_rule)
        # clear configs to avoid updating something that is not allowed by org admins.
        configs['configs'].clear()

        command = self._api_client.update_organization_configuration_v2(data=configs, org_id=self.id)
        return command

    def remove_ip_auth_ruleset(self, ip_address, bitmask=32):
        """Remove all rules that have the same IP address and bitmask.

        Args:
            ip_address (:obj:`str`): IP address to remove from the ruleset.
            bitmask (:obj:`int`, optional): Bitmask to remove from the ruleset. Default ``32``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """

        if not isinstance(ip_address, str):
            raise TypeError("ip_address should be of type str")

        if not isinstance(bitmask, int):
            raise TypeError("bitmask should be of type int")

        configs = self._api_client.get_organization_configuration_v2(org_id=self.id).response.json()
        ip_rules = configs.get('ipAuthRules', {}).get('rules')

        filtered_rules = list(
            filter(lambda rule: not (rule.get('address') == ip_address and rule.get('bitMask') == bitmask), ip_rules)
        )

        if len(filtered_rules) == 0 and configs.get('ipAuthRules', {}).get('enabled'):
            raise ValueError("Cannot delete all rules when IP Auth is enabled.")

        configs['ipAuthRules']['rules'] = filtered_rules
        # clear configs to avoid updating something that is not allowed by org admins.
        configs['configs'].clear()
        command = self._api_client.update_organization_configuration_v2(data=configs, org_id=self.id)
        return command


@analytics_class_decorator
class Organizations(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Organization` instances."""

    def _get_all_results_from_api(self, **kwargs):
        """
        Args:
            kwargs: optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Organization` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Organization`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.get_all_organizations(
            offset=kwargs_unioned['offset'], len=kwargs_unioned['len']
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(
            response, kwargs_unused, Organization, {'api_client': self._control_hub.api_client}
        )


class ApiCredentialBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ApiCredential`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_api_credential_builder`.

    Args:
        api_credential (:obj:`dict`): Python object built from our Swagger ApiCredentialJson definition.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    def __init__(self, api_credential, control_hub):
        self._api_credential = api_credential
        self._control_hub = control_hub

    def build(self, name, user_id=None):
        """Build the ApiCredential.

        Args:
            name (:obj:`str`): ApiCredential name.
            user_id (:obj:`str`, optional): User ID for whom the credentials should be created,
                                            can only be used as an Org-Admin.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ApiCredential`.
        """
        api_credential = ApiCredential(api_credential=self._api_credential, control_hub=self._control_hub)
        api_credential.name = name
        api_credential._request = {'label': name, 'generateAuthToken': True, 'active': True, 'userId': user_id}
        return api_credential


class ApiCredential(BaseModel):
    """Model for ApiCredential.

    Args:
        api_credential (:obj:`dict`): A Python object representation of ApiCredential.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object. Default: ``None``

    Attributes:
        active (:obj:`bool`): Whether the API Credential is active or not.
        auth_token (:obj:`str`): Auth token to be used while making an API call.
        created_by (:obj:`str`): User that created this API Credential.
        created_for (:obj:`str`): The user who should use the API Credential.
        credential_id (:obj:`str`): Credential ID to be used while making an API call.
        name (:obj:`str`): Name of the API Credential.
    """

    _ATTRIBUTES_TO_REMAP = {
        'created_by': 'registeredBy',
        'created_for': 'userId',
        'credential_id': 'componentId',
        'name': 'label',
    }

    _REPR_METADATA = ['name', 'credential_id', 'active', 'created_for', 'created_by']

    def __init__(self, api_credential, control_hub=None):
        super().__init__(
            api_credential,
            attributes_to_remap=ApiCredential._ATTRIBUTES_TO_REMAP,
            repr_metadata=ApiCredential._REPR_METADATA,
        )
        self._control_hub = control_hub


@analytics_class_decorator
class ApiCredentials(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ApiCredential` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    def __init__(self, control_hub):
        super().__init__(control_hub)
        self._id_attr = 'credential_id'

    def _get_all_results_from_api(self, **kwargs):
        """
        Args:
            kwargs: optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.ApiCredential` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        # These kwargs values allow us to pass any kwargs, unused by the API call, back to the calling method for
        # additional filtering. The len/offset values are provided by _paginate, and they're added as defaults below so
        # that the subtract() method doesn't pass them back for filtering.
        kwargs_defaults = {'len': None, 'offset': 0}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        response = self._control_hub.api_client.get_api_user_credentials(self._control_hub.organization).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ApiCredential, {'control_hub': self._control_hub})


@analytics_class_decorator
class DataCollector(BaseModel):
    """Model for Data Collector.

    Attributes:
        execution_mode (:obj:`bool`): ``True`` for Edge and ``False`` for SDC.
        id (:obj:`str`): Data Collectort id.
        labels (:obj:`list`): Labels for Data Collector.
        last_validated_on (:obj:`str`): Last validated time for Data Collector.
        reported_labels (:obj:`list`): Reported labels for Data Collector.
        url (:obj:`str`): Data Collector's url.
        accessible (:obj:`bool`): Whether the Data Collector instance is accessible.
        responding (:obj:`bool`): Whether the Data Collector instance is responding.
        attributes (:obj:`dict`): Data Collector's attributes.
        attributes_updated_on (:obj:`str`): When the Data Collector's attributes were last updated on.
        authentication_token_generated_on (:obj:`str`): When the Data Collector authentication token was generated.
        jobs (:py:class:`streamsets.sdk.sch_models.Job`): The Data Collector's jobs.
        job_ids (:obj:`str`): Data Collector's job ids.
        registered_by (:obj:`str`): Who registered the Data Collector.
        pipelines_committed (:obj:`list` of (:obj:`str` objects)): Pipelines that have been committed.
        resource_thresholds (:obj:`str`): DataCollector resource thresholds.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): DataCollector ACL.
    """

    _ATTRIBUTES_TO_IGNORE = ['offsetProtocolVersion', 'edge']
    _ATTRIBUTES_TO_REMAP = {'execution_mode': 'edge', 'last_validated_on': 'lastReportedTime', 'url': 'httpUrl'}
    _REPR_METADATA = ['id', 'url']

    def __init__(self, data_collector, control_hub):
        super().__init__(
            data_collector,
            attributes_to_ignore=DataCollector._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=DataCollector._ATTRIBUTES_TO_REMAP,
            repr_metadata=DataCollector._REPR_METADATA,
        )
        self._control_hub = control_hub

    @property
    def accessible(self):
        """Returns a :obj:`bool` for whether the Data Collector instance is accessible."""
        try:
            # We disable InsecureRequestWarning and disable SSL certificate verification to enable self-signed certs.
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            requests.get(self.http_url, verify=False, timeout=5)
            return True
        except requests.exceptions.ConnectionError:
            return False

    @property
    def responding(self):
        """Returns a :obj:`bool` for whether the Data Collector instance is responding."""
        self._refresh()
        return self._data['responding']

    @property
    def attributes(self):
        """Returns a :obj:`dict` of Data Collector attributes."""
        return self._component['attributes']

    @property
    def attributes_updated_on(self):
        """Returns when the Data Collector attributes was updated."""
        return self._component['attributesUpdatedOn']

    @property
    def authentication_token_generated_on(self):
        """Returns when the Data Collector authentication token was generated."""
        return self._component['authTokenGeneratedOn']

    @property
    def _instance(self):
        # Disable SSL cert verification to enable use of self-signed certs.
        SdcDataCollector.VERIFY_SSL_CERTIFICATES = False
        return SdcDataCollector(
            self.url,
            control_hub=self._control_hub,
            sdc_id=self.id if self._control_hub.use_websocket_tunneling else None,
        )

    @property
    def jobs(self):
        """Returns the Data Collector :py:class:`streamsets.sdk.sch_models.Job` instances."""
        return SeekableList(self._control_hub.jobs.get(id=job_id) for job_id in self.job_ids)

    @property
    def job_ids(self):
        """Returns the Data Collector Job ids."""
        # Separated this out, to help make stuff more performant since, DataCollector.jobs would make one api call for
        # every job id. People can choose to use this method if they need just the ids and they have lot of jobs.
        return [
            item['jobId'] for item in self._control_hub.api_client.get_pipelines_running_in_sdc(self.id).response.json()
        ]

    @property
    def registered_by(self):
        """Returns who the Data Collector was registered by."""
        return self._component['registeredBy']

    @property
    def pipelines_committed(self):
        """Pipelines that have been committed.

        Returns:
            A :obj:`list` of Job IDs (:obj:`str` objects).
        """
        self._refresh()
        return self._data['pipelinesCommitted']

    @property
    def resource_thresholds(self):
        """Return DataCollector resource thresholds.

        Returns:
            A :obj:`dict` of DataCollector thresholds named as "max_memory_used", "max_cpu_load"
                and "max_pipelines_running"
        """
        self._refresh()
        thresholds = {
            'max_memory_used': self._data.get('maxMemoryUsed'),
            'max_cpu_load': self._data.get('maxCpuLoad'),
            'max_pipelines_running': self._data.get('maxPipelinesRunning'),
        }
        return thresholds

    @property
    def acl(self):
        """Get DataCollector ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_engine_acl(engine_id=self.id).response.json(), self._control_hub)

    @acl.setter
    def acl(self, sdc_acl):
        """Update DataCollector ACL.

        Args:
            sdc_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The sdc ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.set_engine_acl(engine_id=self.id, engine_acl_json=sdc_acl._data)

    def _refresh(self):
        self._data = self._control_hub.api_client.get_sdc(data_collector_id=self.id).response.json()


@analytics_class_decorator
class Transformer(BaseModel):
    """Model for Transformer.

    Attributes:
        execution_mode (:obj:`str`):
        id (:obj:`str`): Transformer id.
        labels (:obj:`list`): Labels for Transformer.
        last_validated_on (:obj:`str`): Last validated time for Transformer.
        reported_labels (:obj:`list`): Reported labels for Transformer.
        url (:obj:`str`): Transformer's url.
        version (:obj:`str`): Transformer's version.
        accessible (:obj:`bool`): Whether the Transformer instance is accessible.
        attributes (:obj:`dict`): Transformer's attributes.
        attributes_updated_on (:obj:`str`): When the Transformer's attributes were last updated on.
        authentication_token_generated_on (:obj:`str`): When the Transformer authentication token was generated.
        registered_by (:obj:`str`): Who registered the Transformer.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): Transformer ACL.
    """

    _ATTRIBUTES_TO_IGNORE = ['offsetProtocolVersion', 'edge']
    _ATTRIBUTES_TO_REMAP = {'execution_mode': 'edge', 'last_validated_on': 'lastReportedTime', 'url': 'httpUrl'}
    _REPR_METADATA = ['id', 'url']

    def __init__(self, transformer, control_hub):
        super().__init__(
            transformer,
            attributes_to_ignore=Transformer._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=Transformer._ATTRIBUTES_TO_REMAP,
            repr_metadata=Transformer._REPR_METADATA,
        )
        self._control_hub = control_hub

    @property
    def accessible(self):
        """Returns a :obj:`bool` for whether the Transformer instance is accessible."""
        try:
            # We disable InsecureRequestWarning and disable SSL certificate verification to enable self-signed certs.
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            requests.get(self.http_url, verify=False, timeout=5)
            return True
        except requests.exceptions.ConnectionError:
            return False

    @property
    def attributes(self):
        """Returns a :obj:`dict` of Transformer attributes."""
        return self._component['attributes']

    @property
    def attributes_updated_on(self):
        """Returns when the Transformer attributes was updated."""
        return self._component['attributesUpdatedOn']

    @property
    def authentication_token_generated_on(self):
        """Returns when the Transformer authentication token was generated."""
        return self._component['authTokenGeneratedOn']

    @property
    def _instance(self):
        # Disable SSL cert verification to enable use of self-signed certs.
        StTransformer.VERIFY_SSL_CERTIFICATES = False
        return StTransformer(
            server_url=self.url,
            control_hub=self._control_hub,
            transformer_id=self.id if self._control_hub.use_websocket_tunneling else None,
        )

    @property
    def registered_by(self):
        """Returns who the Transformer was registered by."""
        return self._component['registeredBy']

    @property
    def acl(self):
        """Get Transformer ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_engine_acl(engine_id=self.id).response.json(), self._control_hub)

    @acl.setter
    def acl(self, transformer_acl):
        """Update Transformer ACL.

        Args:
            transformer_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The transformer ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.set_engine_acl(engine_id=self.id, engine_acl_json=transformer_acl._data)


@analytics_class_decorator
class ProvisioningAgent(BaseModel):
    """Model for Provisioning Agent.

    Args:
        provisioning_agent (:obj:`dict`): A Python object representation of Provisioning Agent.
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.

    Attributes:
        deployments (:py:class:`streamsets.sdk.sch_models.LegacyDeployments`): ProvisioningAgent deployments.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): ProvisioningAgent ACL
    """

    _REPR_METADATA = ['id', 'name', 'type', 'version']

    def __init__(self, provisioning_agent, control_hub):
        # This is hardcoded in domainserver https://git.io/JecVj
        provisioning_agent['type'] = 'Kubernetes'
        super().__init__(provisioning_agent, repr_metadata=ProvisioningAgent._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def deployments(self):
        """Get the deployments associated with the Provisioning Agent.

        Returns:
              A :obj:`list` of :py:class:`streamsets.sdk.sch_models.LegacyDeployment` instances.
        """
        return self._control_hub.legacy_deployments.get_all(dpm_agent_id=self.id)

    @property
    def acl(self):
        """Get the ACL of a Provisioning Agent.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(
            self._control_hub.api_client.get_provisioning_agent_acl(dpm_agent_id=self.id).response.json(),
            self._control_hub,
        )

    @acl.setter
    def acl(self, dpm_agent_acl):
        """Set the ACL of a Provisioning Agent.

        Args:
            dpm_agent_acl: A DPM Agent ACL instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        self._control_hub.api_client.set_provisioning_agent_acl(
            dpm_agent_id=self.id, dpm_agent_acl_json=dpm_agent_acl._data
        )


@analytics_class_decorator
class ProvisioningAgents(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ProvisioningAgent` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, id=None, organization=None, **kwargs):
        """
        Args:
            id (:obj:`str`, optional): Default: ``None``.
            organization (:obj:`str`, optional): Default: ``None``.
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.ProvisioningAgent` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.ProvisioningAgent`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order_by': 'LAST_REPORTED_TIME', 'order': 'DESC', 'version': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if id is not None:
            try:
                response = [self._control_hub.api_client.get_provisioning_agent(agent_id=id).response.json()]
            except requests.exceptions.HTTPError:
                raise ValueError('Provisioning Agent (id={}) not found'.format(id))
        else:
            response = self._control_hub.api_client.return_all_provisioning_agents(
                organization=organization,
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                version=kwargs_unioned['version'],
                with_wrapper=True,
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ProvisioningAgent, {'control_hub': self._control_hub})


class LegacyDeploymentBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.LegacyDeployment`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_deployment_builder`.

    Args:
        deployment (:obj:`dict`): Python object that represents Deployment JSON.
    """

    def __init__(self, deployment):
        self._deployment = deployment

    def build(
        self,
        name,
        provisioning_agent,
        number_of_data_collector_instances,
        spec=None,
        description=None,
        data_collector_labels=None,
    ):
        """Build the deployment.

        Args:
            name (:obj:`str`): Deployment Name.
            provisioning_agent (:py:obj:`streamsets.sdk.sch_models.ProvisioningAgent`): Agent to use.
            number_of_data_collector_instances (obj:`int`): Number of sdc instances.
            spec (:obj:`dict`, optional): Deployment yaml in dictionary format. Will use default yaml used by ui if
                                          left out.
            description (:obj:`str`, optional): Default: ``None``.
            data_collector_labels (:obj:`list`, optional): Default: ``['all']``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.LegacyDeployment`.
        """
        current_deployment = dict(self._deployment)
        if spec:
            spec = yaml.dump(spec, default_flow_style=False)
        current_deployment.update(
            {
                'name': name,
                'description': description,
                'labels': data_collector_labels or [],
                'numInstances': number_of_data_collector_instances,
                'spec': spec or DEFAULT_PROVISIONING_SPEC,
                'agentId': provisioning_agent.id,
            }
        )
        return LegacyDeployment(deployment=current_deployment)


@analytics_class_decorator
class LegacyDeployment(BaseModel):
    """Model for Deployment.

    Args:
        deployment (:obj:`dict`): A Python object representation of Deployment.
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.

    Attributes:
        spec (:obj:`str`): LegacyDeployment's spec.
        status (:obj:`str`): LegacyDeployment's status.
        provisioning_agent (:py:class:`streamsets.sdk.sch_models.ProvisioningAgents`): LegacyDeployment's Provisioning Agents.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): LegacyDeployment's ACL.
        number_of_data_collector_instances (:obj:`int`): The Legacy Deployment's number of data collector instances.
    """

    _ATTRIBUTES_TO_REMAP = {'number_of_data_collector_instances': 'numInstances'}
    _REPR_METADATA = ['id', 'name', 'number_of_data_collector_instances', 'status']

    def __init__(self, deployment, control_hub=None):
        super().__init__(
            deployment,
            attributes_to_remap=LegacyDeployment._ATTRIBUTES_TO_REMAP,
            repr_metadata=LegacyDeployment._REPR_METADATA,
        )
        self._control_hub = control_hub
        self._spec_internal = deployment['spec']

    @property
    def _data(self):
        if not self._spec_internal:
            self._load_data()
        return self._data_internal

    @_data.setter
    def _data(self, data):
        self._data_internal = data

    @property
    def spec(self):
        """Get the spec of the Legacy Deployment."""
        if not self._spec_internal:
            self._load_data()
        return self._data_internal['spec']

    @spec.setter
    def spec(self, spec):
        """Set the spec of the Legacy Deployment."""
        self._data_internal['spec'] = spec
        self._spec_internal = spec

    @property
    def status(self):
        """Get the status of the Legacy Deployment."""
        return self._data['currentDeploymentStatus']['status']

    @property
    def provisioning_agent(self):
        """Get the provisioning agent of the Legacy Deployment."""
        return self._control_hub.provisioning_agents.get(id=self._data['currentDeploymentStatus']['dpmAgent']['id'])

    @property
    def acl(self):
        """Get the ACL of a Deployment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(
            self._control_hub.api_client.get_legacy_deployment_acl(deployment_id=self.id).response.json(),
            self._control_hub,
        )

    @acl.setter
    def acl(self, deployment_acl):
        """Set the ACL of a Deployment.

        Args:
            deployment_acl: A Deployment ACL instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        self._control_hub.api_client.set_legacy_deployment_acl(
            deployment_id=self.id, deployment_acl_json=deployment_acl._data
        )

    def _load_data(self):
        data = self._control_hub.api_client.get_legacy_deployment(
            deployment_id=self._data_internal['id']
        ).response.json()
        self._spec_internal = self._data_internal['spec'] = data['spec']


@analytics_class_decorator
class LegacyDeployments(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.LegacyDeployment` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, id=None, organization=None, **kwargs):
        """
        Args:
            id (:obj:`str`, optional): Default: ``None``.
            organization (:obj:`str`, optional): Default: ``None``.
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Deployment` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Deployment`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {
            'offset': 0,
            'len': None,
            'order_by': 'LAST_MODIFIED_ON',
            'order': 'DESC',
            'dpm_agent_id': None,
            'deployment_status': None,
        }
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if id is not None:
            try:
                response = [self._control_hub.api_client.get_legacy_deployment(deployment_id=id).response.json()]
            except requests.exceptions.HTTPError:
                raise ValueError('Deployment (id={}) not found'.format(id))
        else:
            response = self._control_hub.api_client.return_all_legacy_deployments(
                organization=organization,
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                dpm_agent_id=kwargs_unioned['dpm_agent_id'],
                deployment_status=kwargs_unioned['deployment_status'],
                with_wrapper=True,
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, LegacyDeployment, {'control_hub': self._control_hub})


class SchSdcStage(SdcStage):
    pass


class SchStStage(StStage):
    pass


class PipelineBuilder(SdcPipelineBuilder):
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Pipeline`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_pipeline_builder`.

    Args:
        pipeline (:obj:`dict`): Python object built from our Swagger PipelineJson definition.
        data_collector_pipeline_builder (:py:class:`streamsets.sdk.sdc_models.PipelineBuilder`): Data Collector Pipeline
                                                                                                 Builder object.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Default: ``None``.
        fragment (:obj:`boolean`, optional): Specify if a fragment builder. Default: ``False``.
        engine_start_up_time (:obj:`int`, optional): Engine's start up time. Default: ``0``.
    """

    def __init__(
        self, pipeline, data_collector_pipeline_builder, control_hub=None, fragment=False, engine_start_up_time=0
    ):
        super().__init__(
            data_collector_pipeline_builder._pipeline, data_collector_pipeline_builder._definitions, fragment=fragment
        )
        self._data_collector_pipeline_builder = data_collector_pipeline_builder
        self._sch_pipeline = pipeline
        self._control_hub = control_hub
        self._fragment = fragment
        self._config_key = 'pipelineFragmentConfig' if 'pipelineFragmentConfig' in self._pipeline else 'pipelineConfig'
        self._sch_pipeline['fragment'] = self._fragment
        self._engine_start_up_time = engine_start_up_time
        # Convert SDC stage to ControlHub stage object

        self._all_stages = {
            stage_name: type(stage_name, (_SchSdcStage, stage_type), {'_attributes': stage_type._attributes})
            for stage_name, stage_type in self._all_stages.items()
        }

    def _update_stages_definition(self):
        """Update the available stages if a change to the engine was detected."""
        engine_id = self._sch_pipeline["sdcId"]
        if engine_id in [SNOWFLAKE_ENGINE_ID, ENGINELESS_ENGINE_ID]:
            return
        updated_engine = self._control_hub.engines.get(id=engine_id)
        if updated_engine._data["startUpTime"] != self._engine_start_up_time:
            self._engine_start_up_time = updated_engine._data["startUpTime"]
            self._definitions = updated_engine._instance.definitions
            # Update the sdc PipelineBuilder _all_stages first
            self._all_stages = PipelineBuilder._generate_all_stages(self._definitions)
            # Update the sch PipelineBuilder _all_stages
            self._all_stages = {
                stage_name: type(stage_name, (_SchSdcStage, stage_type), {'_attributes': stage_type._attributes})
                for stage_name, stage_type in self._all_stages.items()
            }

    def _get_stage_configs_names_mapping(self, stage_name, stage_name_type='label'):
        """Returns a list of named tuples for each configuration field.

        Each record contains label, fieldName, and full name for a configuration field.
        Note: 'label' and 'fieldName' are not guaranteed to be unique across all configurations.

        Args:
            stage_name (:obj:`str`): Name of the stage type (eg. 'Dev Raw Data Source')
            stage_name_type (:obj:`str`): Type of stage_name value. Available options: ['label', 'name']. Default ``label``.

        Returns:
            (:obj:`list`): List of tuples, each tuple contains mapped names for configuration field.
        """
        if stage_name_type == 'label':
            raw_stage = self._get_stage_data(label=stage_name)[0]
        elif stage_name_type == 'name':
            raw_stage = self._get_stage_data(name=stage_name)[0]
        else:
            raise ValueError(
                f"Incorrect stage_name_type parameter ({stage_name_type}). Allowed values are: ['label', 'name']."
            )

        service_definitions = {service['provides']: service for service in self._definitions['services']}

        names = []

        # add simple field config
        for field_config in raw_stage.definition['configDefinitions']:
            sdk_name, a = get_attribute(field_config)
            names.append(
                NameMap(
                    label=field_config['label'],
                    fieldName=field_config['fieldName'],
                    name=field_config['name'],
                    sdk=sdk_name,
                )
            )

        # add services fields config (with full name <service_name>.<field_name>) - this name is probably invisible for the end user
        for service in raw_stage.definition['services']:
            for field_config in service_definitions[service['service']]['configDefinitions']:
                sdk_name, a = get_attribute(field_config)
                names.append(
                    NameMap(
                        label=field_config['label'],
                        fieldName=field_config['fieldName'],
                        name=field_config['name'],
                        sdk=sdk_name,
                    )
                )

        return names

    def get_stage_configuration_options(
        self, config_name, stage_name, config_name_type='label', stage_name_type='label'
    ):
        """Gets available configuration options.

        Args:
            config_name (:obj:`str`): Name of the configuration field.
            stage_name (:obj:`str`): Name of the stage type (eg. com_streamsets_pipeline_stage_devtest_rawdata_RawDataDSource)
            config_name_type (:obj:`str`): Type of config_name value. Available options: ['full_name', 'field_name', 'label', 'sdk']. Default ``label``.
            stage_name_type (:obj:`str`): Type of stage_name value. Available options: ['label', 'name']. Default ``label``.

        Returns:
            (:obj:`list`, optional): List of tuples.

        Raises:
            ValueError: If incorrect value of config_name_type.
            ValueError: If config_name value is not in configuration fields list for stage.
        """
        ALLOWED_CONFIG_NAME_TYPES = {'full_name': 'name', 'field_name': 'fieldName', 'label': 'label', 'sdk': 'sdk'}

        if not isinstance(config_name_type, str) or config_name_type not in ALLOWED_CONFIG_NAME_TYPES.keys():
            raise ValueError(
                f"Incorrect config_name_type parameter ({config_name_type}). Allowed values are: {ALLOWED_CONFIG_NAME_TYPES.keys()}."
            )

        if stage_name_type == 'label':
            raw_stage = self._get_stage_data(label=stage_name)[0]
        elif stage_name_type == 'name':
            raw_stage = self._get_stage_data(name=stage_name)[0]
        else:
            raise ValueError(
                f"Incorrect stage_name_type parameter ({stage_name_type}). Allowed values are: ['label', 'name']."
            )

        configuration_names = [
            name_map
            for name_map in self._get_stage_configs_names_mapping(stage_name, stage_name_type=stage_name_type)
            if getattr(name_map, ALLOWED_CONFIG_NAME_TYPES[config_name_type]) == config_name
        ]

        if len(configuration_names) < 1:
            raise ValueError(f"Unknown config name '{config_name}'")
        if len(configuration_names) > 1:
            warnings.warn(
                f"Config name '{config_name}' is ambiguous and could be resolved with any of the following values: "
                "{[c.name for c in configuration_names]}. Using the first one value.",
                warnings.RuntimeWarning,
            )

        config_name = configuration_names[0].name
        cname_split = config_name.split('.')
        is_service_config = len(cname_split) > 1

        # Get config definition:
        if is_service_config:
            # get definitions of services used in this stage
            services_name_list = [service['service'] for service in raw_stage.definition['services']]
            services_configs = [
                service for service in self._definitions['services'] if service['provides'] in services_name_list
            ]

            # iterable of all config fields in services
            config_fields = itertools.chain(
                *[service_config['configDefinitions'] for service_config in services_configs]
            )

        else:
            # simple field config
            config_fields = raw_stage.definition['configDefinitions']

        config = next(filter(lambda config_field: config_field['name'] == config_name, config_fields), None)

        # if config is not of type VALUE_CHOOSER return 'nothing'
        if config is None or config['type'] != 'MODEL' or config['model']['modelType'] != 'VALUE_CHOOSER':
            return None

        # if field is of type VALUE_CHOOSER return all options
        return [
            ChooseOption(label, value) for label, value in zip(config['model']['labels'], config['model']['values'])
        ]

    def add_stage(self, label=None, name=None, type=None, library=None):
        """Add a stage to the pipeline.

        When specifying a stage, either ``label`` or ``name`` must be used. ``type`` and ``library``
        may also be used to select a particular stage if ambiguities exist. If ``type`` and/or ``library``
        are omitted, the first stage definition matching the given ``label`` or ``name`` will be
        used.

        Args:
            label (:obj:`str`, optional): Stage label to use when selecting stage from
                definitions. Default: ``None``.
            name (:obj:`str`, optional): Stage name to use when selecting stage from
                definitions. Default: ``None``.
            type (:obj:`str`, optional): Stage type to use when selecting stage from
                definitions (e.g. `origin`, `destination`, `processor`, `executor`). Default: ``None``.
            library (:obj:`str`, optional): Stage library to use when selecting stage from
                definitions. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.SchSdcStage`.
        """
        self._update_stages_definition()

        if label in SNOWFLAKE_STAGE_RENAME_ALIASES.keys():
            label = SNOWFLAKE_STAGE_RENAME_ALIASES[label]

        stage_definition, stage_instance = next(
            (stage.definition, stage.instance)
            for stage in self._get_stage_data(label=label, name=name, type=type, library=library)
            if stage.definition.get('errorStage') is False
        )

        self._pipeline[self._config_key]['stages'].append(stage_instance)

        supported_connection_types = [
            config['connectionType']
            for config in stage_definition['configDefinitions']
            # we want all the fields that have connectionType
            if config.get('connectionType')
        ]

        variable_output_drive = stage_definition.get('outputStreamsDrivenByConfig', None)
        extra_args = {'variable_output_drive': variable_output_drive} if variable_output_drive else {}

        return self._all_stages.get(stage_instance['stageName'], SchSdcStage)(
            stage=stage_instance,
            pipeline=self,
            output_streams=stage_definition.get('outputStreams', 0),
            supported_connection_types=supported_connection_types,
            **extra_args,
        )

    def remove_stage(self, stage):
        """Remove a stage from the pipeline builder.

        Args:
            stage (:py:class:`streamsets.sdk.sdc_models.Stage`): Stage to disconnect.
        """
        # Validate that the stage passed was created by the PipelineBuilder object
        if self != stage._pipeline:
            raise ValueError(
                "Stage '{}' does not belong to the PipelineBuilder '{}'. Please pass a valid"
                " stage that has already been added to the PipelineBuilder.".format(stage, self)
            )

        # Find the stage within the PipelineBuilder
        stage_instance = next(
            (
                stage_instance
                for stage_instance in self._pipeline[self._config_key]['stages']
                if stage_instance['instanceName'] == stage.instance_name
            ),
            None,
        )

        if stage_instance:
            # Remove stage from PipelineBuilder
            self._pipeline[self._config_key]['stages'] = [
                pipeline_stage
                for pipeline_stage in self._pipeline[self._config_key]['stages']
                if pipeline_stage['instanceName'] != stage.instance_name
            ]

            # Disconnect output lanes if they exist
            if stage_instance['outputLanes']:
                stage.disconnect_output_lanes(all_stages=True)
        else:
            raise ValueError(
                "Stage '{}' does not exist in the stages of PipelineBuilder '{}'. Please pass a valid"
                " stage that has already been added to the PipelineBuilder.".format(stage, self)
            )

    def build(self, title='Pipeline', description='', labels=None, build_from_imported=False, **kwargs):
        """Build the pipeline.

        Args:
            title (:obj:`str`, optional): Title of the pipeline.
            description (:obj:`str`, optional): Description of the pipeline. Default: ````.
            labels (:obj:`list`, optional): List of pipeline labels of type :obj:`str`. Default: ``None``.
            build_from_imported (:obj:`boolean`, optional): Whether we want to build a pipeline
             from an imported pipeline. Default: ``False``

        Returns:
            An instance of :py:class`streamsets.sdk.sch_models.Pipeline`.
        """
        if build_from_imported:
            pipeline = Pipeline(
                pipeline=self._sch_pipeline,
                builder=self,
                pipeline_definition=json.loads(self._sch_pipeline['pipelineDefinition']),
                rules_definition=json.loads(self._sch_pipeline['currentRules']['rulesDefinition']),
                control_hub=self._control_hub,
                library_definitions=self._definitions,
            )
            pipeline.name = title
            pipeline.description = description
            if labels:
                pipeline.add_label(*labels)
            return pipeline
        sdc_pipeline = super().build(title=title)
        sch_pipeline = (_Pipeline)(
            pipeline=self._sch_pipeline,
            builder=self,
            pipeline_definition=sdc_pipeline._data[self._config_key],
            rules_definition=sdc_pipeline._data['pipelineRules'],
            control_hub=self._control_hub,
            library_definitions=self._definitions,
        )
        if 'metadata' not in sch_pipeline._pipeline_definition:
            sch_pipeline._pipeline_definition['metadata'] = {}
        if kwargs.get('preserve_id'):
            sch_pipeline.pipeline_id = sch_pipeline._pipeline_definition['metadata']['dpm.pipeline.id']
            sch_pipeline.commit_id = sch_pipeline._pipeline_definition['metadata']['dpm.pipeline.commit.id']
            # Also preserving pipeline name, assuming people will do another separate commit to update it.
            sch_pipeline.name = sch_pipeline._pipeline_definition['info']['title']
            sch_pipeline._pipeline_definition['title'] = sch_pipeline._pipeline_definition['info']['title']
        else:
            sch_pipeline.name = title
            sch_pipeline.description = description
        fragment_commit_ids = sdc_pipeline._data.get('fragmentCommitIds')
        sch_pipeline._data['fragmentCommitIds'] = fragment_commit_ids
        if labels:
            sch_pipeline.add_label(*labels)
        # Logic as seen at https://git.io/JUWpZ
        connection_ids = [stage.connection for stage in sch_pipeline.stages if hasattr(stage, 'connection')]
        if connection_ids:
            sch_pipeline._pipeline_definition['metadata']['dpm.pipeline.connections'] = ','.join(connection_ids)
        return sch_pipeline

    def import_pipeline(self, pipeline, commit_id_regeneration=True, regenerate_id=True, **kwargs):
        """Import a pipeline into the PipelineBuilder to use as a starting point based off of an existing Pipeline.

        Args:
            pipeline(:py:class`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            commit_id_regeneration(:obj:`bool`, optional): Whether to use the imported pipeline's commit ID. When set to
                                                          False, the imported pipeline will be edited as-is without
                                                          a fresh pipeline being created. Default: True
            regenerate_id(:obj:`bool`, optional): Whether to use the imported pipeline's pipeline_id. When set to False,
                                                  the imported pipeline's pipeline_id will be used. Default: True
        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.PipelineBuilder`.
        """
        if isinstance(pipeline, dict):
            warnings.warn(
                'A new import_pipeline method has been created to allow for a pipeline object to be passed'
                ' instead of a dictionary. Please pass in a streamsets.sdk.sch_models.Pipeline to use this'
                ' new method. The older iteration of this method will be depreciated in future releases.',
                DeprecationWarning,
            )
            return super().import_pipeline(pipeline, **kwargs)
        elif not isinstance(pipeline, Pipeline):
            raise ValueError('Pipeline parameter must be a valid streamsets.sdk.sch_models.Pipeline object')

        # The _sch_pipeline attribute maps to the _data attribute of the imported pipeline
        self._sch_pipeline = pipeline._data.copy()

        # If commit_id_regeneration is False, setting commitId to None, so we don't tether the newly constructed
        # pipeline with the imported one
        if commit_id_regeneration:
            self._sch_pipeline['commitId'] = None

        # The _pipeline attribute requires exported pipeline data in the form of a dictionary
        # See pipeline param in the PipelineBuilder.import_pipeline method of sdc_models for an example of this
        pipelines_archive = zipfile.ZipFile(io.BytesIO(self._control_hub.export_pipelines([pipeline])))
        pipeline_dict = json.loads(pipelines_archive.read(pipelines_archive.namelist()[0]).decode())

        # Always regenerate the pipeline id unless regenerate_id is specified as False.
        if regenerate_id:
            config_key = 'pipelineFragmentConfig' if 'pipelineFragmentConfig' in pipeline_dict else 'pipelineConfig'
            pipeline_dict[config_key]['info']['pipelineId'] = None
            self._sch_pipeline['pipelineId'] = None
        self._pipeline = pipeline_dict

        return self


class StPipelineBuilder(StPipelineBuilder):
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Pipeline`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_pipeline_builder`.

    Args:
        pipeline (:obj:`dict`): Python object built from our Swagger PipelineJson definition.
        transformer_pipeline_builder (:py:class:`streamsets.sdk.sdc_models.PipelineBuilder`): Transformer Pipeline
                                                                                              Builder object.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Default: ``None``.
        fragment (:obj:`boolean`, optional): Specify if a fragment builder. Default: ``False``.
        engine_start_up_time (:obj:`int`, optional): Engine's start up time. Default: ``0``.
    """

    def __init__(
        self, pipeline, transformer_pipeline_builder, control_hub=None, fragment=False, engine_start_up_time=0
    ):
        super().__init__(transformer_pipeline_builder._pipeline, transformer_pipeline_builder._definitions)
        # TODO: fragment=fragment)
        self._transformer_pipeline_builder = transformer_pipeline_builder
        self._sch_pipeline = pipeline
        self._control_hub = control_hub
        self._fragment = fragment
        self._config_key = 'pipelineFragmentConfig' if 'pipelineFragmentConfig' in self._pipeline else 'pipelineConfig'
        self._sch_pipeline['fragment'] = self._fragment
        self._engine_start_up_time = engine_start_up_time
        # Convert Transformer stage to ControlHub stage object
        self._all_stages = {
            stage_name: type(stage_name, (_SchStStage, stage_type), {'_attributes': stage_type._attributes})
            for stage_name, stage_type in self._all_stages.items()
        }

    def _update_stages_definition(self):
        """Update the available stages if a change to the engine was detected."""
        engine_id = self._sch_pipeline["sdcId"]
        updated_engine = self._control_hub.engines.get(id=engine_id)
        if updated_engine._data["startUpTime"] != self._engine_start_up_time:
            self._definitions = updated_engine._instance.definitions
            # Update the st PipelineBuilder _all_stages first
            self._all_stages = StPipelineBuilder._generate_all_stages(self._definitions)
            # Update the sch PipelineBuilder _all_stages
            self._all_stages = {
                stage_name: type(stage_name, (_SchStStage, stage_type), {'_attributes': stage_type._attributes})
                for stage_name, stage_type in self._all_stages.items()
            }

    def add_stage(self, label=None, name=None, type=None, library=None):
        """Add a stage to the pipeline.

        When specifying a stage, either ``label`` or ``name`` must be used. ``type`` and ``library``
        may also be used to select a particular stage if ambiguities exist. If ``type`` and/or ``library``
        are omitted, the first stage definition matching the given ``label`` or ``name`` will be
        used.

        Args:
            label (:obj:`str`, optional): Transformer stage label to use when selecting stage from
                definitions. Default: ``None``.
            name (:obj:`str`, optional): Transformer stage name to use when selecting stage from
                definitions. Default: ``None``.
            type (:obj:`str`, optional): Transformer stage type to use when selecting stage from
                definitions (e.g. `origin`, `destination`, `processor`, `executor`). Default: ``None``.
            library (:obj:`str`, optional): Transformer stage library to use when selecting stage from
                definitions. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.SchStStage`.
        """
        self._update_stages_definition()

        stage_definition, stage_instance = next(
            (stage.definition, stage.instance)
            for stage in self._get_stage_data(label=label, name=name, type=type, library=library)
            if stage.definition.get('errorStage') is False
        )

        self._pipeline['pipelineConfig']['stages'].append(stage_instance)

        supported_connection_types = [
            config['connectionType']
            for config in stage_definition['configDefinitions']
            # we want all the fields that have connectionType
            if config.get('connectionType')
        ]

        variable_output_drive = stage_definition.get('outputStreamsDrivenByConfig', None)
        extra_args = {'variable_output_drive': variable_output_drive} if variable_output_drive else {}

        return self._all_stages.get(stage_instance['stageName'], SchStStage)(
            stage=stage_instance,
            pipeline=self,
            output_streams=stage_definition.get('outputStreams', 0),
            supported_connection_types=supported_connection_types,
            **extra_args,
        )

    def remove_stage(self, stage):
        """Remove a stage from the pipeline builder.

        Args:
            stage (:py:class:`streamsets.sdk.sdc_models.Stage`): Stage to disconnect.
        """
        # Validate that the stage passed was created by the PipelineBuilder object
        if self != stage._pipeline:
            raise ValueError(
                "Stage '{}' does not belong to the PipelineBuilder '{}'. Please pass a valid"
                " stage that has already been added to the PipelineBuilder.".format(stage, self)
            )

        # Find the stage within the PipelineBuilder
        stage_instance = next(
            (
                stage_instance
                for stage_instance in self._pipeline[self._config_key]['stages']
                if stage_instance['instanceName'] == stage.instance_name
            ),
            None,
        )

        if stage_instance:
            # Remove stage from PipelineBuilder
            self._pipeline[self._config_key]['stages'] = [
                pipeline_stage
                for pipeline_stage in self._pipeline[self._config_key]['stages']
                if pipeline_stage['instanceName'] != stage.instance_name
            ]

            # Disconnect output lanes if they exist
            if stage_instance['outputLanes']:
                stage.disconnect_output_lanes(all_stages=True)
        else:
            raise ValueError(
                "Stage '{}' does not exist in the stages of PipelineBuilder '{}'. Please pass a valid"
                " stage that has already been added to the PipelineBuilder.".format(stage, self)
            )

    def build(self, title='Pipeline', description='', build_from_imported=False, **kwargs):
        """Build the pipeline.

        Args:
            title (:obj:`str`): Title of the pipeline.
            description (:obj:`str`, optional): Description of the pipeline. Default: ````.
            build_from_imported (:obj:`boolean`, optional): Whether we want to build a pipeline
             from an imported pipeline. Default: ``False``

        Returns:
            An instance of :py:class`streamsets.sdk.sch_models.Pipeline`.
        """
        if build_from_imported:
            pipeline = Pipeline(
                pipeline=self._sch_pipeline,
                builder=self,
                pipeline_definition=json.loads(self._sch_pipeline['pipelineDefinition']),
                rules_definition=json.loads(self._sch_pipeline['currentRules']['rulesDefinition']),
                control_hub=self._control_hub,
            )
            pipeline.name = title
            pipeline.description = description
            return pipeline

        st_pipeline = super().build(title=title)
        sch_pipeline = (_Pipeline)(
            pipeline=self._sch_pipeline,
            builder=self,
            pipeline_definition=st_pipeline._data[self._config_key],
            rules_definition=st_pipeline._data['pipelineRules'],
            control_hub=self._control_hub,
        )
        sch_pipeline.name = title
        sch_pipeline.description = description
        fragment_commit_ids = st_pipeline._data.get('fragmentCommitIds')
        sch_pipeline._data['fragmentCommitIds'] = fragment_commit_ids
        execution_mode = kwargs.get('execution_mode', TRANSFORMER_DEFAULT_EXECUTION_MODE)
        sch_pipeline._pipeline_definition['executorType'] = 'TRANSFORMER'
        sch_pipeline.configuration['executionMode'] = execution_mode
        return sch_pipeline

    def import_pipeline(self, pipeline, commit_id_regeneration=True, regenerate_id=True, **kwargs):
        """Import a pipeline into the PipelineBuilder to use as a starting point based off of an existing Pipeline.

        Args:
            pipeline(:py:class`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            commit_id_regeneration(:obj:`bool`, optional): Whether to use the imported pipeline's commit ID. When set to
                                                          False, the imported pipeline will be edited as-is without
                                                          a fresh pipeline being created. Default: True
            regenerate_id(:obj:`bool`, optional): Whether to use the imported pipeline's pipeline_id. When set to False,
                                                  the imported pipeline's pipeline_id will be used. Default: True

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.PipelineBuilder`.
        """
        if isinstance(pipeline, dict):
            warnings.warn(
                'A new import_pipeline method has been created to allow for a pipeline object to be passed'
                ' instead of a dictionary. Please pass in a streamsets.sdk.sch_models.Pipeline to use this'
                ' new method. The older iteration of this method will be depreciated in future releases.',
                DeprecationWarning,
            )
            return super().import_pipeline(pipeline, **kwargs)
        elif not isinstance(pipeline, Pipeline):
            raise ValueError('Pipeline parameter must be a valid streamsets.sdk.sch_models.Pipeline object')

        # The _sch_pipeline attribute maps to the _data attribute of the imported pipeline
        self._sch_pipeline = pipeline._data.copy()

        # If commit_id_regeneration is False, setting commitId to None, so we don't tether the newly constructed
        # pipeline with the imported one
        if commit_id_regeneration:
            self._sch_pipeline['commitId'] = None

        # The _pipeline attribute requires exported pipeline data in the form of a dictionary
        # See pipeline param in the PipelineBuilder.import_pipeline method of sdc_models for an example of this
        pipelines_archive = zipfile.ZipFile(io.BytesIO(self._control_hub.export_pipelines([pipeline])))
        pipeline_dict = json.loads(pipelines_archive.read(pipelines_archive.namelist()[0]).decode())

        # Always regenerate the pipeline id unless regenerate_id is specified as False.
        if regenerate_id:
            pipeline_dict['pipelineConfig']['info']['pipelineId'] = None
            self._sch_pipeline['pipelineId'] = None
        self._pipeline = pipeline_dict

        return self


@analytics_class_decorator
class Pipeline(BaseModel):
    """Model for Pipeline.

    Args:
        builder (:py:class:`streamsets.sdk.sch_models.PipelineBuilder`): Pipeline Builder object.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`, optional): ControlHub object. Default: ``None``.
        engine_id (:obj:`str`): The ID of the authoring engine for this pipeline.
        library_definitions (:obj:`dict`, optional): Library Definition in JSON format. Default: ``None``.
        pipeline (:obj:`dict`): Pipeline in JSON format.
        pipeline_definition (:obj:`dict`): Pipeline Definition in JSON format.
        rules_definition (:obj:`dict`): Rules Definition in JSON format.

    Attributes:
        library_definitions (:obj:`dict`): Pipeline's Library Definitions.
        pipeline_definition (:obj:`dict`): Pipeline's definitions.
        commits (list of :py:class:`streamsets.sdk.sch_models.PipelineCommit` instances): Pipeline's commits.
        tags (list of :py:class:`streamsets.sdk.sch_models.Tag` instances): Pipeline's tags.
        configuration (:py:class:`streamsets.sdk.models.Configuration`): Pipeline's configuration.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): Pipeline's ACL.
        stages:  Pipeline's Stages.
        error_stage: Pipeline's Error Stage.
        stats_aggregator_stage: Pipeline's States Aggregator Stage.
        parameters (:obj:`str`): Pipeline's parameters.
        name (:obj:`str`): Pipeline's name.
        description (:obj:`str`): Pipeline's description.
        labels (:obj:`str`): Pipeline's labels.
        engine_id (:obj:`str`): Pipeline's SDC ID.
    """

    _ATTRIBUTES_TO_IGNORE = ['name', 'description']
    _ATTRIBUTES_TO_REMAP = {'engine_id': 'sdcId'}
    _REPR_METADATA = ['pipeline_id', 'commit_id', 'name', 'version']

    def __init__(
        self, pipeline, builder, pipeline_definition, rules_definition, control_hub=None, library_definitions=None
    ):
        super().__init__(
            pipeline,
            attributes_to_ignore=Pipeline._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=Pipeline._ATTRIBUTES_TO_REMAP,
            repr_metadata=Pipeline._REPR_METADATA,
        )

        self._library_definitions = library_definitions
        self._pipeline_definition_internal = pipeline_definition
        self._rules_definition = rules_definition

        self._control_hub = control_hub
        self._builder = builder

        self._parameters = None

    @property
    def _pipeline_definition(self):
        # Load data if not exists whenever this function is called
        if not self._pipeline_definition_internal:
            self._load_data()
        return self._pipeline_definition_internal

    @_pipeline_definition.setter
    def _pipeline_definition(self, pipeline_definition):
        self._pipeline_definition_internal = pipeline_definition

    @property
    def _data(self):
        # Load data if not exists whenever this function is called
        if not self._pipeline_definition_internal:
            self._load_data()
        return self._data_internal

    @_data.setter
    def _data(self, data):
        self._data_internal = data

    @property
    def _library_definitions(self):
        if not self._data_internal['libraryDefinitions']:
            if self.commit_id:
                self._load_data()

            # If we don't have any definitions available, it's because the pipeline is in draft mode. We make a call
            # directly to the engine to retrieve its definitions, just like we would for a PipelineBuilder.
            if not self._data_internal['libraryDefinitions']:
                try:
                    if self.executor_type == SNOWFLAKE_EXECUTOR_TYPE:
                        self._data_internal['libraryDefinitions'] = (
                            self._control_hub.api_client.get_pipelines_definitions(
                                SNOWFLAKE_EXECUTOR_TYPE
                            ).response.text
                        )
                    else:
                        authoring_engine = self._control_hub.engines.get(id=self.sdc_id)
                        engine_lib_definitions = authoring_engine._instance.api_client.get_definitions()
                        self._data_internal['libraryDefinitions'] = json.dumps(engine_lib_definitions)
                except (ValueError, InternalServerError) as e:
                    if self.executor_type == SNOWFLAKE_EXECUTOR_TYPE:
                        error_message = (
                            'Editing pipeline {} is not supported when the snowpark engine is not accessible,'
                            ' please check connectivity to the StreamSets Platform or contact StreamSets Support.'.format(
                                self.pipeline_id
                            )
                        )
                    else:
                        error_message = (
                            'Editing pipeline {} is not supported when the engine is not accessible,'
                            ' please check if the engine {} is running and try again.'.format(
                                self.pipeline_id, self.sdc_id
                            )
                        )
                    raise ValueError(error_message) from e

        return json.loads(self._data_internal['libraryDefinitions'])

    @_library_definitions.setter
    def _library_definitions(self, library_definition):
        # if provided library_definition is a dict, convert it first before setting it
        if isinstance(library_definition, dict):
            self._data_internal['libraryDefinitions'] = json.dumps(library_definition)
        else:
            self._data_internal['libraryDefinitions'] = library_definition

    @property
    def library_definitions(self):
        """Get the Pipeline's (:obj:`dict`) Library Definitions."""
        return self._library_definitions

    @library_definitions.setter
    def library_definitions(self, library_definition):
        """Set the Pipeline's (:obj:`dict`) Library Definitions.

        Args:
            library_definition (:obj:`dict`): The library definitions to set.
        """
        self._library_definitions = library_definition

    @property
    def pipeline_definition(self):
        """Get the Pipeline's (:obj:`dict`) Pipeline Definitions."""
        # Load data if not exists whenever this function is called
        if not self._pipeline_definition_internal:
            self._load_data()
        return self._data_internal['pipelineDefinition']

    @pipeline_definition.setter
    def pipeline_definition(self, pipeline_definition):
        """Set the Pipeline's (:obj:`dict`) Pipeline Definitions.

        Args:
            pipeline_definition (:obj:`dict`): The Pipeline definitions to set.
        """
        self._pipeline_definition_internal = pipeline_definition

    def _load_data(self):
        data = self._control_hub.api_client.get_pipeline_commit(self.commit_id).response.json()
        self._data_internal['libraryDefinitions'] = data['libraryDefinitions']
        self._data_internal['pipelineDefinition'] = data['pipelineDefinition']
        self._data_internal['currentRules'] = data['currentRules']
        self._pipeline_definition_internal = json.loads(data['pipelineDefinition'])
        self._rules_definition = json.loads(data['currentRules']['rulesDefinition'])

    @property
    def commits(self):
        """Get commits for this pipeline.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of instances of
            :py:class:`streamsets.sdk.sch_models.PipelineCommit`.
        """
        return SeekableList(
            PipelineCommit(commit, control_hub=self._control_hub)
            for commit in self._control_hub.api_client.get_pipeline_commits(
                pipeline_id=self.pipeline_id
            ).response.json()
        )

    @property
    def tags(self):
        """Get tags for this pipeline.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of instances of
            :py:class:`streamsets.sdk.sch_models.PipelineTag`.
        """
        return SeekableList(
            PipelineTag(tag, control_hub=self._control_hub)
            for tag in self._control_hub.api_client.get_pipeline_tags(pipeline_id=self.pipeline_id).response.json()
        )

    @property
    def configuration(self):
        """Get pipeline's configuration.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Configuration`.
        """
        definitions = self._library_definitions
        pipeline_definition_key = 'pipelineFragment' if self.fragment else 'pipeline'
        config_definitions = {} if not definitions else definitions[pipeline_definition_key][0]['configDefinitions']

        mapping = {}
        for config_definition in config_definitions:
            attribute_name, config_name = get_attribute(config_definition)
            mapping[attribute_name] = config_name

        compatibility_map = (
            get_bw_compatibility_map(self.sdc_version, ST_PIPELINE_BW_COMPATIBILITY)
            if getattr(self, 'executor_type', None) == 'TRANSFORMER'
            else {}
        )

        return Configuration(
            compatibility_map=compatibility_map,
            configuration=self._pipeline_definition['configuration'],
            id_to_remap=mapping,
        )

    @property
    def acl(self):
        """Get pipeline ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(
            self._control_hub.api_client.get_pipeline_acl(pipeline_id=self.pipeline_id).response.json(),
            self._control_hub,
        )

    @acl.setter
    def acl(self, pipeline_acl):
        """Update pipeline ACL.

        Args:
            pipeline_acl (:py:class:`streamsets.sdk.sch_models.ACL`): Pipeline ACL in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sch_api.Command`.
        """
        return self._control_hub.api_client.set_pipeline_acl(
            pipeline_id=self.pipeline_id, pipeline_acl_json=pipeline_acl._data
        )

    def _get_stage_class(self, stage_definition, library_definitions):
        stage_name = stage_definition.get('name', 'DefaultStage')
        stage_class_default = _SchSdcStage if self.executor_type in ['COLLECTOR', 'SNOWPARK'] else _SchStStage

        # Get configuration definition attributes
        attributes = collections.defaultdict(list)
        for config_definition in stage_definition.get('configDefinitions', []):
            attribute_name, config_name = get_attribute(config_definition)
            attributes[attribute_name].append(StageConfigurationProperty(config_name=config_name))

        for service in stage_definition.get('services', []):
            service_name = service['service']

            service_definition = next(
                (
                    service_def
                    for service_def in library_definitions.get('services', [])
                    if service_def['provides'] == service_name
                ),
                None,
            )

            if service_definition is None:
                raise ServiceDefinitionNotFound('Could not find definition of service {}'.format(service_name))

            for config_definition in service_definition.get('configDefinitions', []):
                attribute_name, config_name = get_attribute(config_definition)
                attributes[attribute_name].append(
                    ServiceConfigurationProperty(service_name=service_name, config_name=config_name)
                )

        if stage_name in STAGE_CONFIG_OVERRIDES:
            attributes.update(STAGE_CONFIG_OVERRIDES[stage_name])

        # Invoke the _StageWithPredicates class IFF the stage's output streams are governed by lane predicates
        variable_output_drive = stage_definition.get('outputStreamsDrivenByConfig', None)
        if variable_output_drive and variable_output_drive == 'lanePredicates':
            stage_class = type(stage_name, (_StageWithPredicates, stage_class_default), {'_attributes': attributes})
        else:
            stage_class = type(stage_name, (stage_class_default,), {'_attributes': attributes})

        return stage_class

    @property
    def stages(self):
        """Get the stages of the Pipeline."""
        # Will lazy load library definitions if they do not exist
        library_definitions = self._library_definitions

        stage_list = SeekableList()
        for stage in self._pipeline_definition['stages']:
            if not ('instanceName' in stage and 'stageName' in stage):
                continue

            stage_definition = next(
                (stage_def for stage_def in library_definitions['stages'] if stage_def['name'] == stage['stageName']),
                {},
            )

            if not stage_definition:
                logger.debug("Definitions not found for stage {}".format(stage['stageName']))

            supported_connection_types = [
                config['connectionType']
                for config in stage_definition.get('configDefinitions', [])
                if config.get('connectionType')
            ]

            extra_args = {}
            variable_output_drive = stage_definition.get('outputStreamsDrivenByConfig')
            if variable_output_drive == 'lanePredicates':
                extra_args.update({'variable_output_drive': variable_output_drive})

            stage_class = self._get_stage_class(stage_definition, library_definitions)
            stage_object = stage_class(
                stage=stage,
                pipeline=self,
                supported_connection_types=supported_connection_types,
                **extra_args,
            )
            stage_list.append(stage_object)

        return stage_list

    @property
    def error_stage(self):
        """Get the error stage of the Pipeline."""
        library_definitions = self._library_definitions
        stage_definition = self._pipeline_definition.get('errorStage', {})

        if not stage_definition:
            return None

        stage_class = self._get_stage_class(stage_definition, library_definitions)
        stage_object = stage_class(stage=stage_definition, pipeline=self)

        return stage_object

    @property
    def stats_aggregator_stage(self):
        """Get the stats aggregator stage of the Pipeline."""
        library_definitions = self._library_definitions
        stage_definition = self._pipeline_definition.get('statsAggregatorStage', {})

        if not stage_definition:
            return None

        stage_class = self._get_stage_class(stage_definition, library_definitions)
        stage_object = stage_class(stage=stage_definition, pipeline=self)

        return stage_object

    @property
    def parameters(self):
        """Get the pipeline parameters.

        Returns:
            A dict like, :py:obj:`streamsets.sdk.sch_models.PipelineParameters` object of parameter key-value pairs.
        """
        if self._parameters is None:
            self._parameters = PipelineParameters(self)
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Create new set of pipeline parameters by replacing existing ones if any.

        Args:
            parameters (:obj:`dict`): A dictionary of key-value parameters to set.
        """
        self.parameters._create(parameters)

    @property
    def name(self):
        """Get the name of the Pipeline."""
        return self._data['name']

    @name.setter
    def name(self, name):
        """Set the name of the Pipeline.

        Args:
            name (:obj:`str`): A name to set.
        """
        self._pipeline_definition['title'] = name
        self._data['name'] = name

    @property
    def description(self):
        """Get the description of the Pipeline."""
        return self._data['description']

    @description.setter
    def description(self, description):
        """Set the description of the Pipeline.

        Args:
            description (:obj:`str`): A name to set.
        """
        self._pipeline_definition['description'] = description
        self._data['description'] = description

    @property
    def labels(self):
        """Get the pipeline labels.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of instances of
            :py:class:`streamsets.sdk.sch_models.PipelineLabel`.
        """
        if self._data['pipelineLabels'] is not None:
            return SeekableList(PipelineLabel(label) for label in self._data['pipelineLabels'])
        else:
            return SeekableList()

    @property
    def sdc_id(self):
        """Get the SDC ID of the Pipeline."""
        warnings.warn(
            'The sdc_id attribute is now deprecated for Pipeline objects. It has been replaced by the'
            ' `engine_id` attribute. Please update your usage accordingly.',
            DeprecationWarning,
        )
        return self.engine_id

    @sdc_id.setter
    def sdc_id(self, value):
        """Set the SDC ID of the Pipeline.

        Args:
            value (:obj:`str`): The SDC id to set.
        """
        warnings.warn(
            'The sdc_id attribute is now deprecated for Pipeline objects. It has been replaced by the'
            ' `engine_id` attribute. Please update your usage accordingly.',
            DeprecationWarning,
        )
        self.engine_id = value

    @property
    def sdc_version(self):
        return self._data['sdcVersion']

    @sdc_version.setter
    def sdc_version(self, value):
        raise AttributeError("Sorry, 'sdc_version' is a read-only attribute.")

    @property
    def engine_id(self):
        """Get the Engine ID of the Pipeline."""
        return self._data['sdcId']

    @engine_id.setter
    def engine_id(self, value):
        """Set the Engine ID of the Pipeline.

        Args:
            value (:obj:`str`): The Engine id to set.
        """
        self._data['sdcId'] = value
        self._data['sdcVersion'] = self._control_hub.engines.get(id=value).version

    def add_label(self, *labels):
        """Add a label

        Args:
            *labels: One or more instances of :obj:`str`
        """
        if 'labels' not in self._pipeline_definition['metadata']:
            self._pipeline_definition['metadata']['labels'] = []
        if self._data['pipelineLabels'] is None:
            self._data['pipelineLabels'] = []
        for label in labels:
            self._pipeline_definition['metadata']['labels'].append(label)
            # Logic as seen at https://git.io/JfPhk
            parent_id = (
                '{}:{}'.format('/'.join(label.split('/')[:-1]), self._control_hub.organization)
                if label.split('/')[0:-1]
                else None
            )
            self._data['pipelineLabels'].append(
                {
                    'id': '{}:{}'.format(label, self._control_hub.organization),
                    'label': label.split('/')[-1],
                    'parentId': parent_id,
                    'organization': self._control_hub.organization,
                }
            )

    def remove_label(self, *labels):
        """Remove a label

        Args:
            *labels: One or more instances of :obj:`str`
        """
        for label in labels:
            if label in self._pipeline_definition['metadata']['labels']:
                self._pipeline_definition['metadata']['labels'].remove(label)
                item = self.labels.get(label=label)
                self._data['pipelineLabels'].remove(item._data)
            else:
                logger.warning('Label %s is not an assigned label for this pipeline. Ignoring this label.', label)

    def _get_builder(self):
        executor_type = {'COLLECTOR': 'data_collector', 'TRANSFORMER': 'transformer', 'SNOWPARK': 'snowflake'}
        if not self._builder:
            engine_id = self._data['sdcId'] if self.executor_type != SNOWFLAKE_EXECUTOR_TYPE else None
            self._builder = self._control_hub.get_pipeline_builder(
                engine_type=executor_type.get(self.executor_type), engine_id=engine_id
            )

            # Setting additional metadata of the fragments into the PipelineBuilder
            self._builder._fragment_commit_ids = []
            self._builder._fragment_instance_count = collections.defaultdict(int)
            for fragment_data in self._pipeline_definition['fragments']:
                self._builder._fragment_commit_ids.append(fragment_data['metadata']['dpm.pipeline.commit.id'])
                self._builder._fragment_instance_count[fragment_data['title']] += 1

            # Have the Builder and Pipeline point to the same point in memory. This is done to ensure that any changes
            # to the builder will reflect in the Pipeline.
            self._builder._sch_pipeline = self._data
            self._builder._pipeline[self._builder._config_key] = self._pipeline_definition

        return self._builder

    def add_stage(self, label=None, name=None, type=None, library=None):
        """Add a stage to the pipeline.

        When specifying a stage, either ``label`` or ``name`` must be used. ``type`` and ``library``
        may also be used to select a particular stage if ambiguities exist. If ``type`` and/or ``library``
        are omitted, the first stage definition matching the given ``label`` or ``name`` will be
        used.

        Args:
            label (:obj:`str`, optional): Stage label to use when selecting stage from
                definitions. Default: ``None``.
            name (:obj:`str`, optional): Stage name to use when selecting stage from
                definitions. Default: ``None``.
            type (:obj:`str`, optional): Stage type to use when selecting stage from
                definitions (e.g. `origin`, `destination`, `processor`, `executor`). Default: ``None``.
            library (:obj:`str`, optional): Stage library to use when selecting stage from
                definitions. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.SchSdcStage`
             or :py:class:`streamsets.sdk.sch_models.SchStStage`.
        """
        # If _library_definitions is not populated, we call the internal _library_definitions property to perform
        # lazy-loading of the underlying data
        if not self._data_internal['libraryDefinitions']:
            self._library_definitions

        try:
            pipeline_builder = self._get_builder()
        # ValueError gets raised by the Engines class when trying to find an inaccessible Engine
        # However, sometimes ControlHub finds the Inaccessible Engine instance but we then error out later
        # downstream of the get_pipeline_builder method and throws an InternalServerError
        except (ValueError, InternalServerError) as e:
            raise ValueError(
                'Editing pipeline {} is not supported when the engine is not accessible,'
                ' please check if the engine is running and try again.'.format(self.pipeline_id)
            ) from e

        stage = pipeline_builder.add_stage(label=label, name=name, type=type, library=library)

        # Arrange the pipeline stages so that stages don't overlap in the UI
        pipeline_builder._auto_arrange()

        stage._pipeline = self

        return stage

    def remove_stages(self, *stages):
        """Remove one or more stages from a Pipeline.

        Args:
            stages (:py:class:`streamsets.sdk.sdc_models.Stage` or :py:class:`streamsets.sdk.st_models.Stage`):
            One or more stage objects
        """

        # Create a map of stage_instance_name: stage for stages that exist within the Pipeline
        instance_names_to_remove = {stage.instance_name: stage for stage in stages if stage._pipeline == self}

        # If no valid stages have been provided, raise ValueError
        if not instance_names_to_remove:
            raise ValueError(
                'No valid stages have been provided. Please provide stages that exist within the Pipeline'
                ' {}.'.format(self)
            )

        # Fragments are represented as stages and contain an extra config identifying it as a fragment. Hence,
        # we create a map of fragment_instance_id: fragment for fragments that exist within the Pipeline
        fragment_instance_ids_to_remove = {
            stage._data['uiInfo']['fragmentInstanceId']: stage
            for stage in instance_names_to_remove.values()
            if 'fragmentInstanceId' in stage._data['uiInfo']
        }

        # Remove stages from the Pipeline
        self._pipeline_definition_internal['stages'] = [
            pipeline_stage
            for pipeline_stage in self._pipeline_definition_internal['stages']
            if pipeline_stage['instanceName'] not in instance_names_to_remove
        ]

        # Remove fragments from the Pipeline
        self._pipeline_definition_internal['fragments'] = [
            pipeline_stage
            for pipeline_stage in self._pipeline_definition_internal['fragments']
            if pipeline_stage['fragmentInstanceId'] not in fragment_instance_ids_to_remove
        ]

        # Disconnect output lanes if they exist and remove any trace of fragments in _builder
        for instance_name, stage_instance in instance_names_to_remove.items():
            if stage_instance.output_lanes:
                stage_instance.disconnect_output_lanes(all_stages=True)

            if self._builder and 'fragmentInstanceId' in stage_instance._data['uiInfo']:
                self._builder._fragment_commit_ids.remove(stage_instance._data['uiInfo']['pipelineCommitId'])
                self._builder._fragment_instance_count[stage_instance._data['uiInfo']['fragmentName']] -= 1

    def add_fragment(self, fragment, parameter_name_prefix=None):
        """Add a fragment to the pipeline.

        Args:
            fragment (py:obj:`streamsets.sdk.sch_models.Pipeline`): Fragment to add.
            parameter_name_prefix (:obj:`str`, optional): Prefix name for the parameters of fragment. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.Stage`.
        """
        try:
            pipeline_builder = self._get_builder()
        # ValueError gets raised by the Engines class when trying to find an inaccessible Engine
        # However, sometimes ControlHub finds the Inaccessible Engine instance but we then error out later
        # downstream of the get_pipeline_builder method and throws an InternalServerError
        except (ValueError, InternalServerError) as e:
            raise ValueError(
                'Editing pipeline {} is not supported when the engine is not accessible,'
                ' please check if the engine is running and try again.'.format(self.pipeline_id)
            ) from e

        fragment = pipeline_builder.add_fragment(fragment=fragment, parameter_name_prefix=parameter_name_prefix)

        # Arrange the pipeline stages so that stages don't overlap in the UI
        pipeline_builder._auto_arrange()

        return fragment

    def get_jobs_using_pipeline(self):
        """Get the jobs that are running on this pipeline.

        Returns:
            An instance of :py:class:`streamsets.sdk.utils.SeekableList` containing instances of
            :py:class:`streamsets.sdk.sch_models.Job` that run on this pipeline.

        """
        get_active_jobs_response = self._control_hub.api_client.get_active_jobs(
            self._control_hub.organization, self.commit_id
        ).response

        jobs = SeekableList([Job(job_data, self._control_hub) for job_data in get_active_jobs_response.json()])

        return jobs


class PipelineLabel(BaseModel):
    """Model for pipeline label.

    Args:
        pipeline_label (:obj:`dict`): Pipeline label in JSON format.

    Attributes:
        label (:obj:`str`): The pipeline label.
    """

    _REPR_METADATA = ['label']
    _ATTRIBUTES_TO_REMAP = {'youngest_child_label': 'label'}

    def __init__(self, pipeline_label):
        super().__init__(
            pipeline_label,
            repr_metadata=PipelineLabel._REPR_METADATA,
            attributes_to_remap=PipelineLabel._ATTRIBUTES_TO_REMAP,
        )

    @property
    def label(self):
        """Get the pipeline label."""
        return self.id.split(':')[0]


@analytics_class_decorator
class PipelineLabels(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.PipelineLabel` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, organization=None, parent_id=None, **kwargs):
        """Args offset, len, order are not exposed directly as arguments because of their limited use by normal users
        but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization id of pipeline. Default: ``None``.
            parent_id (:obj:`str`, optional): ID of the parent pipeline label. Default: ``None``.
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.PipelineLabel` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.PipelineLabel`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order': 'DESC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_pipeline_labels(
            organization=organization,
            parent_id=parent_id,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            order=kwargs_unioned['order'],
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, PipelineLabel, {})


class PipelineCommit(BaseModel):
    """Model for pipeline commit.

    Args:
        pipeline_commit (:obj:`dict`): Pipeline commit in JSON format.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.

    Attributes:
        pipeline (:py:class:`streamsets.sdk.sch_models.Pipeline`): The commit's pipeline.
    """

    _REPR_METADATA = ['commit_id', 'version', 'commit_message']

    def __init__(self, pipeline_commit, control_hub=None):
        super().__init__(pipeline_commit, repr_metadata=PipelineCommit._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def pipeline(self):
        """Get the commits pipeline."""
        return self._control_hub.pipelines.get(commit_id=self.commit_id)


class PipelineTag(BaseModel):
    """Model for pipeline tag.

    Args:
        pipeline_tag (:obj:`dict`): Pipeline tag in JSON format.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    _REPR_METADATA = ['id', 'commit_id', 'name', 'message']

    def __init__(self, pipeline_tag, control_hub=None):
        super().__init__(pipeline_tag, repr_metadata=PipelineTag._REPR_METADATA)
        self._control_hub = control_hub


class PipelineParameters(collections.abc.Mapping):
    """Parameters for pipelines.

    Args:
        pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline Instance.
    """

    def __init__(self, pipeline):
        self._store = {parameter['key']: parameter['value'] for parameter in pipeline.configuration['constants']}
        self._pipeline = pipeline

    def update(self, parameters_dict):
        """Update existing parameters. Works similar to Python dictionary update.

        Args:
            parameters_dict (:obj:`dict`): Dictionary of key-value pairs to be used as parameters.
        """
        self._store.update(parameters_dict)
        self._create(self._store)

    def _create(self, parameters_dict):
        """Create a new set of parameters discarding existing ones.

        Args:
            parameters_dict (:obj:`dict`): Dictionary of key-value pairs to be used as parameters.
        """
        self._pipeline.configuration['constants'] = []
        self._store = parameters_dict.copy()
        for key, value in parameters_dict.items():
            self._pipeline.configuration['constants'].append({'key': key, 'value': value})
        config_key = 'pipelineFragmentConfig' if 'pipelineFragmentConfig' in self._pipeline._data else 'pipelineConfig'
        self._pipeline._data[config_key] = json.dumps(self._pipeline.pipeline_definition)

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return str(self._store)


@analytics_class_decorator
class Pipelines(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Pipeline` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization
        self._id_attr = 'pipeline_id'

    def __len__(self):
        return self._control_hub.api_client.get_pipelines_count(organization=None, system=False).response.json()[
            'count'
        ]

    def _get_all_results_from_api(
        self,
        commit_id=None,
        organization=None,
        label=None,
        template=False,
        fragment=False,
        using_fragment=None,
        draft=None,
        search=None,
        **kwargs,
    ):
        """Args offset, len, order_by, order, system, filter_text, only_published, execution_modes, start_time, end_time
         and user_ids are not exposed directly as arguments because of their limited use by normal users but, could
        still be specified just like any other args with the help of kwargs.

        Args:
            commit_id (:obj:`str`, optional): Pipeline commit id. Default: ``None``.
            organization (:obj:`str`, optional): Organization id of pipeline. Default: ``None``.
            label (:obj:`str`, optional): Label of pipeline. Default: ``None``.
            template (:obj:`boolean`, optional): Indicate if requesting pipeline templates or pipelines.
                                                 Default: ``False``.
            fragment (:obj:`boolean`, optional): Specify if querying for fragments. Default: ``False``.
            using_fragment (:py:obj:`streamsets.sdk.sch_models.Pipeline`, optional): Pipelines using this fragment.
                                                                                     Default: ``None``.
            draft (:py:obj:`boolean`, optional): Indicate if requesting draft pipelines. Default: ``None``.
            search (:obj:`str`, optional): Search query for finding pipelines or fragments. Default: ``None``.
            filter_text (:obj:`str`, optional): Only returns instances that match the filter string. This will be
                propagated to the API backend (results filtered server-side instead of client-side).
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Pipeline` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Pipeline`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        if draft is not None and Version(self._control_hub.version) < Version('3.18.0'):
            raise ValueError('Argument draft cannot be specified for this version of ControlHub')
        kwargs_defaults = {
            'offset': None,
            'len': None,
            'order_by': 'LAST_MODIFIED_ON',
            'order': None,
            'system': None,
            'filter_text': None,
            'only_published': False,
            'execution_modes': None,
            'start_time': -1,
            'end_time': -1,
            'user_ids': None,
        }
        pipeline_id = kwargs.pop('pipeline_id', None)
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if label is not None:
            if self._control_hub.current_project is not None:
                label = f"{label}--{self._control_hub.current_project.id}"
            label_id_org = self._organization if organization is None else organization
            pipeline_label_id = '{}:{}'.format(label, label_id_org)
        else:
            pipeline_label_id = None
        if pipeline_id:
            only_published = not draft
            pipeline_commit_json = self._control_hub.api_client.get_latest_pipeline_commit(
                pipeline_id=pipeline_id, only_published=only_published
            ).response.json()
            response = [] if not pipeline_commit_json['commitId'] else [pipeline_commit_json]
        elif commit_id:
            response = [self._control_hub.api_client.get_pipeline_commit(commit_id=commit_id).response.json()]
        elif using_fragment:
            fragment_commit_id = using_fragment.commit_id
            response = self._control_hub.api_client.get_pipelines_using_fragment(
                fragment_commit_id=fragment_commit_id,
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
            ).response.json()
        elif template:
            response = self._control_hub.api_client.return_all_pipeline_templates(
                pipeline_label_id=pipeline_label_id,
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                system=kwargs_unioned['system'],
                filter_text=kwargs_unioned['filter_text'],
                execution_modes=kwargs_unioned['execution_modes'],
                start_time=kwargs_unioned['start_time'],
                end_time=kwargs_unioned['end_time'],
                user_ids=kwargs_unioned['user_ids'],
            ).response.json()
        elif fragment:
            if search:
                response = self._control_hub.api_client.get_fragments_by_query(
                    search=search,
                    org_id=self._control_hub.organization,
                    order_by=convert_last_modified_on_field_for_saql(kwargs_unioned['order_by'].lower()),
                    offset=kwargs_unioned['offset'],
                    len=kwargs_unioned['len'],
                ).response.json()
            else:
                response = self._control_hub.api_client.return_all_pipeline_fragments(
                    organization=organization,
                    pipeline_label_id=pipeline_label_id,
                    offset=kwargs_unioned['offset'],
                    len=kwargs_unioned['len'],
                    order_by=kwargs_unioned['order_by'],
                    order=kwargs_unioned['order'],
                    system=kwargs_unioned['system'],
                    filter_text=kwargs_unioned['filter_text'],
                    only_published=kwargs_unioned['only_published'],
                    execution_modes=kwargs_unioned['execution_modes'],
                    start_time=kwargs_unioned['start_time'],
                    end_time=kwargs_unioned['end_time'],
                    user_ids=kwargs_unioned['user_ids'],
                    draft=draft,
                ).response.json()
        elif search:
            response = self._control_hub.api_client.get_pipelines_by_query(
                search=search,
                org_id=self._control_hub.organization,
                order_by=convert_last_modified_on_field_for_saql(kwargs_unioned['order_by'].lower()),
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
            ).response.json()
        else:
            response = self._control_hub.api_client.return_all_pipelines(
                organization=organization,
                pipeline_label_id=pipeline_label_id,
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                system=kwargs_unioned['system'],
                filter_text=kwargs_unioned['filter_text'],
                only_published=kwargs_unioned['only_published'],
                execution_modes=kwargs_unioned['execution_modes'],
                start_time=kwargs_unioned['start_time'],
                end_time=kwargs_unioned['end_time'],
                user_ids=kwargs_unioned['user_ids'],
                draft=draft,
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(
            response,
            kwargs_unused,
            Pipeline,
            {'builder': None, 'pipeline_definition': None, 'rules_definition': None, 'control_hub': self._control_hub},
        )


class JobBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Job`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_job_builder`.

    Args:
        job (:obj:`dict`): Python object built from our Swagger JobJson definition.
    """

    def __init__(self, job, control_hub):
        self._job = job
        self._control_hub = control_hub

    def build(
        self,
        job_name,
        pipeline,
        job_template=False,
        runtime_parameters=None,
        pipeline_commit=None,
        pipeline_tag=None,
        pipeline_commit_or_tag=None,
        tags=None,
    ):
        """Build the job.

        Args:
            job_name (:obj:`str`): Name of the job.
            pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            job_template (:obj:`boolean`, optional): Indicate if it is a Job Template. Default: ``False``.
            runtime_parameters (:obj:`dict`, optional): Runtime Parameters for the Job or Job Template.
                                                        Default: ``None``.
            pipeline_commit (:py:obj:`streamsets.sdk.sch_models.PipelineCommit`): Default: ``None`, which resolves to
                                                                                  the latest pipeline commit.
            pipeline_tag (:py:obj:`streamsets.sdk.sch_models.PipelineTag`): Default: ``None`, which resolves to
                                                                            the latest pipeline tag.
            pipeline_commit_or_tag (:obj:`str`, optional): Default: ``None``, which resolves to the latest pipeline
                                                           commit.
            tags (:obj:`list`, optional): Job tags. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        if pipeline_commit and pipeline_tag:
            raise ValueError('Cannot specify both the arguments pipeline_commit and pipeline_tag at the same time.')

        if pipeline_commit_or_tag:
            logger.warning(
                'pipeline_commit_or_tag argument will be removed in a future release. Please use '
                'pipeline_commit, pipeline_tag arguments instead.'
            )
            if pipeline_commit or pipeline_tag:
                raise ValueError(
                    'Cannot specify both the arguments pipeline_commit_or_tag and '
                    '{} at the same time'.format('pipeline_commit' if pipeline_commit else 'pipeline_tag')
                )

        executor_type = pipeline._data['executorType'] if 'executorType' in pipeline._data else None
        if job_template:
            assert runtime_parameters is not None, "Please specify at least one runtime parameter."
        if pipeline_tag:
            pipeline_version = pipeline.commits.get(commit_id=pipeline_tag.commit_id).version
        else:
            pipeline_version = pipeline.version
        self._job.update(
            {
                'name': job_name,
                'pipelineCommitId': (
                    pipeline_commit_or_tag
                    or getattr(pipeline_commit, 'commit_id', None)
                    or getattr(pipeline_tag, 'commit_id', None)
                    or pipeline.commit_id
                ),
                'pipelineCommitLabel': 'v{}'.format(getattr(pipeline_commit, 'version', None) or pipeline_version),
                'pipelineId': pipeline.pipeline_id,
                'pipelineName': pipeline.name,
                'rulesId': pipeline.current_rules['id'],
                'jobTemplate': job_template,
                'runtimeParameters': '{}' if runtime_parameters is None else json.dumps(runtime_parameters),
                'executorType': executor_type,
            }
        )
        job = Job(job=self._job, control_hub=self._control_hub)
        if tags:
            job.add_tag(*tags)
        return job


class JobCommittedOffset(BaseModel):
    """Model for committedOffsets for an instance of :py:class:`streamsets.sdk.sch_models.Job`.

    Args:
        committed_offset (:obj:`dict`): Committed offset in JSON format
    """

    _REPR_METADATA = ['version', 'offsets']

    def __init__(self, committed_offset):
        super().__init__(committed_offset, repr_metadata=JobCommittedOffset._REPR_METADATA)


class JobOffset(BaseModel):
    """Model for offset.

    Args:
        offset (:obj:`dict`): Offset in JSON format.
    """

    _REPR_METADATA = ['sdc_id', 'pipeline_id']

    def __init__(self, offset):
        super().__init__(offset, repr_metadata=JobOffset._REPR_METADATA)


class JobRunEvent(BaseModel):
    """Model for an event in a Job Run.

    Args:
        event (:obj:`dict`): Job Run Event in JSON format.
    """

    _REPR_METADATA = ['user', 'time', 'status']

    def __init__(self, event):
        super().__init__(event, repr_metadata=JobRunEvent._REPR_METADATA)


@analytics_class_decorator
class JobStatus(BaseModel):
    """Model for Job Status.

    Attributes:
        color (:obj:`str`): Job status color.
        run_history (:py:class:`streamsets.sdk.utils.SeekableList`) of
                    (:py:class:`streamsets.sdk.utils.JobRunHistoryEvent`): History of a particular job run.
        offsets (:py:class:`streamsets.sdk.utils.SeekableList`) of
                (:py:class:`streamsets.sdk.utils.JobPipelineOffset`): Offsets after the job run.

    Args:
        status (:obj:`dict`): Job status in JSON format.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    _ATTRIBUTES_TO_IGNORE = ['pipelineOffsets']
    _REPR_METADATA = ['status', 'color']
    # We generate different canonical string representation of the class instance if it's created in the context
    # of a job history view.
    _JOB_HISTORY_VIEW_REPR_METADATA = ['status', 'start_time', 'finish_time', 'run_count']

    def __init__(self, status, control_hub, **kwargs):
        super().__init__(
            status,
            repr_metadata=(
                JobStatus._REPR_METADATA
                if not kwargs.get('job_history_view')
                else JobStatus._JOB_HISTORY_VIEW_REPR_METADATA
            ),
        )
        self._control_hub = control_hub

    @property
    def color(self):
        """Get the color of the Job Status."""
        return self._data.get('color')

    @property
    def run_history(self):
        """Get the run history of the Job Status."""
        return SeekableList(
            JobRunEvent(event)
            for event in self._control_hub.api_client.get_job_status_history_for_run(
                job_status_id=self.id, offset=0, len=-1
            ).response.json()
        )

    @property
    def offsets(self):
        """Get the offsets of the Job Status."""
        if 'pipelineOffsets' not in self._data or not self._data['pipelineOffsets']:
            return None
        return SeekableList(JobOffset(pipeline_offset) for pipeline_offset in self._data['pipelineOffsets'])

    def __eq__(self, other):
        # Handle the case of a JobStatus being compared to a None, str (e.g. 'ACTIVE') or list of statuses
        return (
            self.status == other
            if other is None or isinstance(other, str)
            else (self.status in other if isinstance(other, list) else super().__eq__(other))
        )


class JobMetrics(BaseModel):
    """Model for job metrics.

    Attributes:
        error_count (:obj:`int`): The number of error records generated by this run of the Job.
        error_records_per_sec (:obj:`float`): The number of error records per second generated by this run of the Job.
        input_count (:obj:`int`): The number of records ingested by this run of the Job.
        input_records_per_sec (:obj:`float`): The number of records per second ingested by this run of the Job.
        output_count (:obj:`int`): The number of records output by this run of the Job.
        output_records_per_sec (:obj:`float`): The number of records output per second by the run of the Job.
        pipeline_version (:obj:`str`): The version of the pipeline that was used in this Job run.
        run_count (:obj:`int`): The count corresponding to this Job run.
        sdc_id (:obj:`str`): The ID of the SDC instance on which this Job run was executed.
        stage_errors_count (:obj:`int`): The number of stage error records generated by this run of the Job.
        stage_error_records_per_sec (:obj:`float`): The number of stage error records generated per second by this run
                                                    of the job.
        total_error_count (:obj:`int`): The total number of both error records and stage errors generated by this run
                                        of the job.

    Args:
        metrics (:obj:`dict`): Metrics counts in JSON format.
    """

    _ATTRIBUTES_TO_REMAP = {
        'error_records_per_sec': 'errorM1Rate',
        'input_records_per_sec': 'inputM1Rate',
        'output_records_per_sec': 'outputM1Rate',
        'stage_error_records_per_sec': 'stageErrorsM1Rate',
    }
    _ATTRIBUTES_TO_IGNORE = ['jobId', 'lastUpdatedOn', 'organization', 'stageId']
    _REPR_METADATA = ['run_count', 'input_count', 'output_count', 'total_error_count']

    def __init__(self, metrics):
        super().__init__(
            metrics,
            attributes_to_ignore=JobMetrics._ATTRIBUTES_TO_IGNORE,
            repr_metadata=JobMetrics._REPR_METADATA,
            attributes_to_remap=JobMetrics._ATTRIBUTES_TO_REMAP,
        )
        # Aggregating error counts as done in the UI: https://git.io/JYNdT
        self.total_error_count = self._data['errorCount'] + self._data['stageErrorsCount']


class JobTimeSeriesMetrics(BaseModel):
    """Model for job metrics.

    Attributes:
        input_records (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                   'Record Count Time Series' or
                                                                                   'Record Throughput Time Series'.
        output_records (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                    'Record Count Time Series' or
                                                                                    'Record Throughput Time Series'.
        error_records (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                   'Record Count Time Series' or
                                                                                   'Record Throughput Time Series'.
        batch_counter (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                   'Batch Throughput Time Series'.
        batch_processing_timer (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                            'Batch Processing Timer
                                                                                            seconds'.

    Args:
        metrics (:obj:`dict`): Metrics in JSON format.
    """

    _ATTRIBUTES_TO_REMAP = {
        'input_records': 'pipeline_batchInputRecords_meter',
        'output_records': 'pipeline_batchOutputRecords_meter',
        'error_records': 'pipeline_batchErrorRecords_meter',
        'batch_counter': 'pipeline_batchCount_meter',
        'batch_processing_timer': 'stage_batchProcessing_timer',
    }
    _METRIC_TYPE_ATTRS = {
        'Record Count Time Series': ['input_records', 'output_records', 'error_records'],
        'Record Throughput Time Series': ['input_records', 'output_records', 'error_records'],
        'Batch Throughput Time Series': ['batch_counter'],
        'Stage Batch Processing Timer seconds': ['batch_processing_timer'],
    }

    def __init__(self, metrics, metric_type):
        data = {}
        repr_metadata = []
        attributes_map_inverted = {v: k for k, v in JobTimeSeriesMetrics._ATTRIBUTES_TO_REMAP.items()}
        for metric in metrics:
            series = metric['series']
            if series:
                name = metric['series'][0]['name']
                remapped_name = attributes_map_inverted[name]
                data[name] = JobTimeSeriesMetric(metric, remapped_name)
                repr_metadata.append(remapped_name)
            else:
                data = {
                    JobTimeSeriesMetrics._ATTRIBUTES_TO_REMAP[attr]: None
                    for attr in JobTimeSeriesMetrics._METRIC_TYPE_ATTRS[metric_type]
                }
        super().__init__(
            data, attributes_to_remap=JobTimeSeriesMetrics._ATTRIBUTES_TO_REMAP, repr_metadata=repr_metadata
        )


class JobTimeSeriesMetric(BaseModel):
    """Model for job metrics.

    Attributes:
        name (:obj:`str`): Name of measurement.
        values (:obj:`list`): Timeseries data.
        time_series (:obj:`dict`): Timeseries data with timestamp as key and metric value as value.

    Args:
        metric (:obj:`dict`): Metrics in JSON format.
    """

    _REPR_METADATA = ['name', 'time_series']
    _ATTRIBUTES_TO_IGNORE = ['columns', 'tags']

    def __init__(self, metric, metric_type):
        if metric.get('error'):
            # Not throwing an exception because if one metric fails, every other metric won't be displayed because of
            # __repr__ of JobTimeSeriesMetrics.
            logger.warning('Fetching metrics for %s failed with error %s', metric_type, metric.get('error'))
        super().__init__(
            metric['series'][0],
            repr_metadata=JobTimeSeriesMetric._REPR_METADATA,
            attributes_to_ignore=JobTimeSeriesMetric._ATTRIBUTES_TO_IGNORE,
        )

    @property
    def time_series(self):
        """Get the time series (:obj:`dict`)."""
        time_series = {}
        for k, v in self.values:
            time_series[k] = v
        return time_series


class JobDataCollector(DataCollector):
    """Model for job Data Collector.

    Attributes:
        pipeline (:py:class:`streamsets.sdk.sch_models.Pipeline`): A Pipeline instance.
        pipeline_id (:obj:`str'): The Pipeline ID.

    Args:
        data_collector (:py:class:`streamsets.sdk.sch_models.DataCollector`): A Data Collector.
        pipeline_name (:obj:`str`): The Pipeline name.
    """

    def __init__(self, data_collector, pipeline_name):
        super().__init__(data_collector._data, data_collector._control_hub)
        self._pipeline_name = pipeline_name

    @property
    def pipeline(self):
        """Get the Job Data Collector's pipeline (:py:class:`streamsets.sdk.sch_models.Pipeline`)."""
        return self._instance.pipelines.get(id=self.pipeline_id)

    @property
    def pipeline_id(self):
        """Get the Job Data Collector's pipeline ID (:obj:`str`)."""
        id_separator = getattr(self, 'id_separator', '__')
        pipeline_id = self._pipeline_name.replace(':', '__') if id_separator == '__' else self._pipeline_name
        return pipeline_id


class JobTransformer(Transformer):
    """Model for job Transformer.

    Attributes:
        pipeline (:py:class:`streamsets.sdk.sch_models.Pipeline`): A Pipeline instance.
        pipeline_id (:obj:`str'): The Pipeline ID.

    Args:
        transformer (:py:class:`streamsets.sdk.sch_models.Transformer`): A Transformer.
        pipeline_name (:obj:`str`): The Pipeline name.
    """

    def __init__(self, transformer, pipeline_name):
        super().__init__(transformer._data, transformer._control_hub)
        self._pipeline_name = pipeline_name

    @property
    def pipeline(self):
        """Get the Job Transformer's pipeline (:py:class:`streamsets.sdk.sch_models.Pipeline`)."""
        return self._instance.pipelines.get(id=self.pipeline_id)

    @property
    def pipeline_id(self):
        """Get the Job Transformer's pipeline ID (:obj:`str`)."""
        id_separator = getattr(self, 'id_separator', '__')
        pipeline_id = self._pipeline_name.replace(':', '__') if id_separator == '__' else self._pipeline_name
        return pipeline_id


class Tag(BaseModel):
    """Model for tag.

    Args:
        tag (:obj:`dict`): tag in JSON format.

    Attributes:
        id (:obj:`str`): The full ID of the tag, in ``'tag:organization'`` format.
        organization (:obj:`str`): The ID of the organization that the tag belongs to.
        parent_id (:obj:`str`): ID of the parent tag if this tag is a child.
        tag (:obj:`str`): The tag's label.
    """

    _REPR_METADATA = ['tag']
    _ATTRIBUTES_TO_REMAP = {'youngest_child_label': 'tag'}

    def __init__(self, tag):
        super().__init__(tag, repr_metadata=Tag._REPR_METADATA, attributes_to_remap=Tag._ATTRIBUTES_TO_REMAP)

    @property
    def tag(self):
        """Get the Tag."""
        return ':'.join(self.id.split(':')[:-1])


@analytics_class_decorator
class JobTags(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Tag` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, organization=None, parent_id=None, **kwargs):
        """Args offset, len, order are not exposed directly as arguments because of their limited use by normal users
        but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization id of job. Default: ``None``.
            parent_id (:obj:`str`, optional): ID of the parent job tag. Default: ``None``.
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Tag` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Tag`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order': 'DESC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_job_tags(
            organization=organization,
            parent_id=parent_id,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            order=kwargs_unioned['order'],
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Tag, {})


@analytics_class_decorator
class Step(BaseModel):
    """Model for Job Step.

    Attributes:
        id (:obj:`str`): Step ID.
        job_id (:obj:`str`): Job ID.
        sequence_id (:obj:`str`): Job Sequence ID.
        job_name (:obj:`str`): Job Sequence name.
        organization (:obj:`str`): Organization that the Job Sequence is a part of.
        status (:obj:`str`): Job Sequence status.
        step_number (:obj:`str`): Job Sequence status.
    """

    _REPR_METADATA = ['id', 'status', 'step_number']

    def __init__(self, step, sequence, control_hub=None):
        super().__init__(step, repr_metadata=Step._REPR_METADATA)
        self._control_hub = control_hub
        self._job_sequence = sequence

    @property
    def step_jobs(self):
        """The Jobs that are part of the Step.

        Returns:
            A (:py:class:`streamsets.sdk.utils.SeekableList`) of (:py:class:`streamsets.sdk.sch_models.Job`) objects.
        """
        job_ids = [job_data['jobId'] for job_data in self._data['jobs']]

        jobs_json = self._control_hub.api_client.get_jobs(job_ids).response.json()

        jobs = SeekableList(Job(job_json, control_hub=self._control_hub) for job_json in jobs_json)

        return jobs

    @property
    def name(self):
        """Get the name of the Step.

        Returns:
            A (:obj:`str`) object.
        """
        return self._data['name']

    @name.setter
    def name(self, value):
        """Set the name of the Step.

        Args:
            value (:obj:`str`): The name to set.
        """
        self._data['name'] = value
        data = self._job_sequence._create_steps_payload()
        self._control_hub.api_client.update_steps_of_job_sequence(self._job_sequence.id, data).response.json()

    @property
    def finish_conditions(self):
        """The Finish Conditions that are part of the Step.

        Returns:
            A (:py:class:`streamsets.sdk.utils.SeekableList`) of
             (:py:class:`streamsets.sdk.sch_models.FinishCondition`) objects.
        """
        jobs_data = [job for job in self._data['jobs'] if job['finishCondition'] is not None]

        finish_conditions = SeekableList(
            FinishCondition(
                finish_condition=job['finishCondition'], job_id=job['jobId'], step=self, control_hub=self._control_hub
            )
            for job in jobs_data
        )

        return finish_conditions

    def create_finish_condition(
        self, condition_type, job, move_job_to_error=False, crontab_mask=None, end_time=None, timezone=None
    ):
        """Create a Finish Conditions in the Step.

        Args:
            condition_type (:obj:`str`): The Condition Type. Accepted Values are 'END_TIME' & 'CRON'.
            job (:py:class:`streamsets.sdk.sch_models.Job`): A (:py:class:`streamsets.sdk.sch_models.Job`) object.
            move_job_to_error (:obj:`bool`, , optional): Whether to Move Job to Error.
            crontab_mask (:obj:`str`, , optional): The Cron expression for the Finish Condition. Only set when condition_type is 'CRON'
            end_time (:obj:`str`, , optional): The End Time for the Finish Condition. Only set when condition_type is 'END_TIME'
            timezone (:obj:`str`, , optional): The Timezone for the Finish Condition. Only set when condition_type is 'END_TIME'

        """
        if not isinstance(condition_type, str):
            raise TypeError('finish_condition must be a string')

        condition_type = condition_type.upper()
        if not hasattr(FinishCondition.ConditionTypes, condition_type):
            raise ValueError(
                '{} is not a valid value, accepted values are {}'.format(
                    condition_type, [accepted_value.value for accepted_value in FinishCondition.ConditionTypes]
                )
            )

        payload = {"conditionType": condition_type, "moveJobToError": move_job_to_error}

        if condition_type == FinishCondition.ConditionTypes.CRON.value:
            if end_time or timezone:
                raise ValueError('Cannot set end_time and timezone when condition_type is CRON')
            if crontab_mask is None:
                raise ValueError('crontab_mask cannot be None when condition_type is CRON')
            payload['crontabMask'] = crontab_mask
        elif condition_type == FinishCondition.ConditionTypes.END_TIME.value:
            if crontab_mask:
                raise ValueError('Cannot set crontab_mask when condition_type is END_TIME')
            if end_time is None or timezone is None:
                raise ValueError('end_time and timezone cannot be None when condition_type is END_TIME')
            payload.update({'endTime': end_time, 'timezone': timezone})

        if not isinstance(move_job_to_error, bool):
            raise TypeError('move_job_to_error must be a boolean')

        step_job = next(data for data in self._data['jobs'] if data['jobId'] == job.job_id)

        if not step_job:
            raise ValueError("job must be a part of the step")

        if step_job['finishCondition']:
            raise ValueError('The Step Job already has a finish condition. Please update the existing one instead')

        response = self._control_hub.api_client.create_finish_condition(
            sequence_id=self._job_sequence.id, step_job_instance_id=step_job['id'], finish_condition_json=payload
        ).response.json()

        step_job['finishCondition'] = response

        return FinishCondition(finish_condition=response, job_id=job.job_id, step=self, control_hub=self._control_hub)

    def update_finish_condition(self, finish_condition):
        """Update the Step's Finish Conditions.

        Args:
            finish_condition (:py:class:`streamsets.sdk.sch_models.FinishCondition`): FinishCondition instance.
        """
        if not isinstance(finish_condition, FinishCondition):
            raise TypeError('finish_condition must be a :py:class:`streamsets.sdk.sch_models.FinishCondition` instance')

        finish_condition_ids = [condition.id for condition in self.finish_conditions]
        if finish_condition.id not in finish_condition_ids:
            raise ValueError('finish_condition should be a part of the step in order to update')

        payload = {
            "conditionType": finish_condition.condition_type,
            "moveJobToError": finish_condition.move_job_to_error,
        }

        if finish_condition.condition_type == FinishCondition.ConditionTypes.CRON.value:
            payload['crontabMask'] = finish_condition.crontab_mask
        elif finish_condition.condition_type == FinishCondition.ConditionTypes.END_TIME.value:
            payload['endTime'] = finish_condition.end_time
            payload['timezone'] = finish_condition.timezone

        response = self._control_hub.api_client.update_finish_condition(
            sequence_id=self._job_sequence.id,
            step_job_instance_id=finish_condition.step_job_instance_id,
            finish_condition_id=finish_condition.id,
            update_finish_condition_json=payload,
        ).response.json()

        finish_condition._data = response

    def delete_finish_condition(self, finish_condition):
        """Delete the Finish Conditions from the Step.

        Args:
            finish_condition (:py:class:`streamsets.sdk.sch_models.FinishCondition`): FinishCondition instance.
        """
        if not isinstance(finish_condition, FinishCondition):
            raise TypeError('finish_condition must be a :py:class:`streamsets.sdk.sch_models.FinishCondition` instance')

        finish_condition_ids = [condition.id for condition in self.finish_conditions]
        if finish_condition.id not in finish_condition_ids:
            raise ValueError('finish_condition should be a part of the step in order to delete')

        self._control_hub.api_client.delete_finish_condition(
            sequence_id=self._job_sequence.id,
            step_job_instance_id=finish_condition.step_job_instance_id,
            finish_condition_id=finish_condition.id,
        )

        step_job = next(data for data in self._data['jobs'] if data['id'] == finish_condition.step_job_instance_id)
        step_job['finishCondition'] = None

    def add_jobs(self, jobs, ignore_error=True):
        """List of Jobs to add to the Step.

        Args:
            jobs (:obj:`list` of :py:class:`streamsets.sdk.sch_models.Job`): Job to add to the step.
            ignore_error (:obj:`bool`): Whether to ignore Job errors or not. Default: ``True``.
        """
        # Create a new step with passed in Jobs
        self._job_sequence.add_step_with_jobs(jobs, parallel_jobs=True, ignore_error=ignore_error)

        # Copy over that new steps' jobs
        step_with_new_jobs = self._job_sequence.steps[-1]
        idx = self._job_sequence._data['steps'].index(self._data)
        self._job_sequence._data['steps'][idx]['jobs'].extend(step_with_new_jobs._data['jobs'])

        # Remove new step
        self._job_sequence.remove_step(step_with_new_jobs)

        # Update Job info in sch - this will add the job to this step
        data = self._job_sequence._create_steps_payload()
        self._job_sequence._data = self._control_hub.api_client.update_steps_of_job_sequence(
            self._job_sequence.id, data
        ).response.json()
        self._data = next(step_data for step_data in self._job_sequence._data['steps'] if step_data['id'] == self.id)

    def remove_jobs(self, *jobs):
        """Removes Jobs from Step.

        Args:
            jobs: One or more :py:class:`streamsets.sdk.sch_models.Job` instances.
        """
        job_ids_within_step = [job_data['jobId'] for job_data in self._data['jobs']]
        ids_to_delete = set()

        # Validation
        for job in jobs:
            if not isinstance(job, Job):
                raise TypeError("jobs must be one or more :py:class:`streamsets.sdk.sch_models.Job` instances.")
            if job.job_id not in job_ids_within_step:
                raise ValueError("job with job_id {} is not a part of the sequence {}".format(job.job_id, self.id))

            ids_to_delete.add(job.job_id)

        # Remove from local memory
        idx = self._job_sequence._data['steps'].index(self._data)
        self._job_sequence._data['steps'][idx]['jobs'] = [
            job for job in self._data['jobs'] if job['jobId'] not in ids_to_delete
        ]

        # Make change in ControlHub
        data = self._job_sequence._create_steps_payload()
        self._job_sequence._data = self._control_hub.api_client.update_steps_of_job_sequence(
            self._job_sequence.id, data
        ).response.json()

        # Change step data
        self._data = next(step_data for step_data in self._job_sequence._data['steps'] if step_data['id'] == self.id)


@analytics_class_decorator
class JobSequence(BaseModel):
    """Model for Job Sequence

    Args:
        job_sequence (:obj:`dict`): The job sequence Swagger JSON.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.

    Attributes:
        id (:obj:`str`): Job Sequence ID.
        name (:obj:`str`): Job Sequence name.
        description (:obj:`str`): Job Sequence description.
        organization (:obj:`str`): Organization that the Job Sequence is a part of.
        created_by (:obj:`str`): Who created the Job Sequence.
        create_time (:obj:`str`): When the Job Sequence was created.
        last_modified_by (:obj:`str`): Who the Job Sequence was last modified by.
        last_modified_time (:obj:`str`): When the Job Sequence was last modified.
        start_time (:obj:`str`): Start time of the Job Sequence.
        end_time (:obj:`str`): End time of the Job Sequence.
        time_zone (:obj:`str`): Job Sequence timezone.
        cron_tab_mask (:obj:`str`): Cron tab mask of the Job Sequence.
        steps (:obj:`str`): Job Sequence steps.
        status (:obj:`str`): Job Sequence status.
    """

    _REPR_METADATA = ['id', 'name', 'start_time', 'status', 'next_run_time']

    class LogType(enum.Enum):
        SEQUENCE_START = 'SEQUENCE_START'
        SCHEDULER_TRIGGER_ERROR = 'SCHEDULER_TRIGGER_ERROR'
        STEP_START = 'STEP_START'
        SEQUENCE_NEXT_STEP_START = 'SEQUENCE_NEXT_STEP_START'

    class LogLevel(enum.Enum):
        INFO = 'INFO'
        WARN = 'WARN'
        ERROR = 'ERROR'

    class JobSequenceStatusType(enum.Enum):
        INACTIVE = 'INACTIVE'
        DISABLED = 'DISABLED'
        ACTIVE = 'ACTIVE'
        ERROR = 'ERROR'

    def __init__(self, job_sequence, control_hub=None):
        super().__init__(job_sequence, repr_metadata=JobSequence._REPR_METADATA)
        self._control_hub = control_hub

    def _create_steps_payload(self):
        data = []
        for step in self.steps:
            step_data = {
                "id": step.id,
                "name": step.name,
                "stepNumber": step.step_number,
                "ignoreError": step.ignore_error,
                "jobIds": [job['jobId'] for job in step.jobs],
            }
            data.append(step_data)

        return data

    @property
    def history_logs(self):
        """Get the history logs of the Job Sequence.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.JobSequenceHistoryLogs`.
        """
        return JobSequenceHistoryLogs(self._control_hub, sequence_id=self.id)

    def delete_history_logs(self, history_logs):
        """Delete history logs from the Job Sequence.

        Args:
            history_logs (:obj:`list` of :py:class:`streamsets.sdk.sch_models.JobSequenceHistoryLog`): History Logs to delete.
        """
        existing_job_sequence_history_log_ids = [
            history_log.id for history_log in self.history_logs.get_all(last_run_only=False)
        ]
        history_log_ids = []

        for history_log in history_logs:
            if not isinstance(history_log, JobSequenceHistoryLog):
                raise TypeError('All objects within history_logs must be JobSequenceHistoryLog instances')

            if history_log.id not in existing_job_sequence_history_log_ids:
                raise ValueError('History log {} must be a part of Sequence {}'.format(history_log.id, self.id))

            history_log_ids.append(history_log.id)

        self._control_hub.api_client.delete_job_sequence_history_logs(history_log_ids)

    def get_history_log(
        self, log_type=None, log_level=None, last_run_only=None, run_id=None, from_date=None, to_date=None
    ):
        """Get the history log of the Job Sequence.

         Args:
             log_type (:obj:`str`, optional): Accepted values are "SEQUENCE_START", "SCHEDULER_TRIGGER_ERROR",
              "STEP_START". Default: `None`.
             log_level (:obj:`str`, optional): Accepted values are "INFO", "WARN", "ERROR". Default: `None`.
             last_run_only (:obj:`bool`, optional): Whether to return History Log for the last run only. Default: `None`.
             run_id (:obj:`str`, optional): The desired Run ID to get the History Log for. Default: `None`.
             from_date (:obj:`str`, optional): The starting date from which we'd like to see the History Log for. Default: `None`.
             to_date (:obj:`str`, optional): The end date till which we'd like to see the History Log for. Default: `None`.

        Returns:
            A :obj:`SeekableList` of  :py:class:`streamsets.sdk.sch_models.JobSequenceHistoryLog` objects.
        """
        warnings.warn(
            'This method of streamsets.sdk.sch_models.JobSequence will be removed in a '
            'future release. Please use the history_logs property instead.',
            DeprecationWarning,
        )

        return self.history_logs.get_all(
            log_type=log_type,
            log_level=log_level,
            last_run_only=last_run_only,
            run_id=run_id,
            from_date=from_date,
            to_date=to_date,
        )

    @property
    def run_ids(self):
        """Get all the run IDs of the Job Sequence.

        Returns:
            An :obj:`list` of :obj:`int`.
        """
        return self._control_hub.api_client.get_all_run_ids_of_job_sequence(self.id).response.json()

    def mark_job_as_finished(self, job):
        """Send an event in Control Hub indicating that a job has finished.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): Job to mark as finished.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        if not isinstance(job, Job):
            raise TypeError("job must be an instance of :py:class:`streamsets.sdk.sch_models.Job`")

        return self._control_hub.api_client.mark_job_as_finished(job.job_id)

    @property
    def steps(self):
        """The Steps that are part of the Job Sequence.

        Returns:
            A (:py:class:`streamsets.sdk.utils.SeekableList`) of (:py:class:`streamsets.sdk.sch_models.Step`) objects.
        """
        steps = SeekableList(Step(step, sequence=self, control_hub=self._control_hub) for step in self._data['steps'])
        steps.sort(key=lambda job_step: job_step.step_number)

        return steps

    @steps.setter
    def steps(self):
        logger.warning("Cannot manually change steps, use the move_step method instead.")

    def move_step(self, step, target_step_number, swap=False):
        """Move one Step to another index within the Job Sequence.

        Args:
            step (:py:class:`streamsets.sdk.sch_models.Step`): The step to be moved.
            target_step_number (:obj:`int`): The step number to move the step to.
            swap (:obj:`bool`): Whether to swap the step with the step in the given index, if False, this will move
            the step to the index and shift the steps to the right. Default: ``False``.
        """
        if not isinstance(step, Step):
            raise TypeError('The step must be of type :py:class:`streamsets.sdk.sch_models.Step`')
        if not isinstance(target_step_number, int):
            raise TypeError('The target_step_number must be of type :obj:`int`')
        if not isinstance(swap, bool):
            raise TypeError('The swap must be of type :obj:`bool`')
        if step.step_number == target_step_number:
            raise ValueError('The target_step_number must not be equal to step.step_number')

        # The step_number attribute of Step class range from 1 to n.
        steps = self.steps
        if target_step_number > len(steps):
            raise ValueError(
                'The target_step_number must not be greater than the number of steps {}'.format(len(steps))
            )

        if swap:
            tmp_step_number = step.step_number
            step.step_number = steps[target_step_number - 1].step_number
            steps[target_step_number - 1].step_number = tmp_step_number

        else:
            # Adjust the step numbers by incrementing or decrementing (using `move_value`) the step_number attribute
            # for all steps between the current step and the target position
            if step.step_number > target_step_number:
                from_index, to_index = target_step_number - 1, step.step_number - 1
                move_value = 1
            else:
                from_index, to_index = step.step_number, target_step_number
                move_value = -1

            for idx in range(from_index, to_index):
                steps[idx].step_number += move_value

            # In the end, move the step to move_to_step_number
            step.step_number = target_step_number

        data = self._create_steps_payload()
        self._data = self._control_hub.api_client.update_steps_of_job_sequence(self.id, data).response.json()

    def add_step_with_jobs(self, jobs, parallel_jobs=False, ignore_error=True):
        """Generate one or more Steps by providing new Job objects to be added to the Job Sequence.

        Args:
            jobs (:obj:`list` of :py:class:`streamsets.sdk.sch_models.Job`): Jobs to be added to the Job Sequence as
             part of the step.
            parallel_jobs  (:obj:`bool`): Whether the passed in Jobs will be a part of the same step or not.
             Default: ``False``.
            ignore_error (:obj:`bool`): Whether to ignore Job errors or not. Default: ``True``.
        """
        # Validation
        if not isinstance(jobs, list) or not all(isinstance(job_instance, Job) for job_instance in jobs):
            raise TypeError("jobs must be a list of type :py:class:`streamsets.sdk.sch_models.Job` instances.")
        if any(job.job_sequence for job in jobs):
            raise ValueError("jobs must not be a part of a Job Sequence")
        if not isinstance(parallel_jobs, bool):
            raise TypeError("parallel_jobs must be a boolean")
        if not isinstance(ignore_error, bool):
            raise TypeError("ignore_error must be a boolean")

        last_step_number = 0 if not self.steps else self.steps[-1].step_number
        new_step_number = last_step_number + 1
        data = []

        # If parallel_jobs is True, all passed in jobs will be a part of the same step
        if parallel_jobs:
            job_ids = [job.job_id for job in jobs]
            data.append({"stepNumber": new_step_number, "ignoreError": ignore_error, "jobIds": job_ids})

        # If parallel_jobs is False, all passed in jobs will be appended sequentially to the end of the Sequence
        else:
            for job in jobs:
                data.append({"stepNumber": new_step_number, "ignoreError": ignore_error, "jobIds": [job.job_id]})
                new_step_number += 1

        # Control Hub sends back the new Job Sequence _data, overwrite old _data
        self._data = self._control_hub.api_client.add_step_jobs_to_job_sequence(self.id, data).response.json()

    def remove_step(self, step):
        """Remove a Step from a Job Sequence.

        Args:
            step: A :py:class:`streamsets.sdk.sch_models.Step` instance.
        """
        if not isinstance(step, Step):
            raise TypeError("The step should be a :py:class:`streamsets.sdk.sch_models.Step` instance.")

        step_data_to_remove = next((step_data for step_data in self._data['steps'] if step_data['id'] == step.id), None)
        if not step_data_to_remove:
            raise ValueError("The step is not a part of the sequence {}".format(self.id))

        self._data['steps'].remove(step_data_to_remove)

        # This reorders the step_numbers of all steps, and ensures that step numbers remain sequential after removal
        for idx, step in enumerate(self.steps):
            step.step_number = idx + 1

        # Make change in ControlHub
        data = self._create_steps_payload()
        self._data = self._control_hub.api_client.update_steps_of_job_sequence(self.id, data).response.json()

    def refresh(self):
        self._data = self._control_hub.api_client.get_job_sequence(self.id).response.json()


class FinishCondition(BaseModel):
    """Model for Job Sequence Finish Condition.

    Args:
        finish_condition (:obj:`dict`): JSON representation of a Finish Condition.
        job_id (:obj:`str`): The Job ID.
        step (:py:class:`streamsets.sdk.sch_models.Step`): The Step that the finish condition is a part of.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub Object.

    Attributes:
        id (:obj:`str`): Finish Condition ID.
        condition_type (:obj:`str`): Condition Type. Accepted Values are 'END_TIME' & 'CRON'
        crontab_mask (:obj:`str`): The Cron expression for the Finish Condition. Only set when condition_type is 'CRON'
        end_time (:obj:`int`): The End Time for the Finish Condition. Only set when condition_type is 'END_TIME'
        timezone (:obj:`str`): The Timezone for the Finish Condition. Only set when condition_type is 'END_TIME'
        move_job_to_error (:obj:`bool`): Whether to Move Job to Error.
    """

    _REPR_METADATA = ['job_id', 'condition_type', 'move_job_to_error']

    class ConditionTypes(enum.Enum):
        END_TIME = 'END_TIME'
        CRON = 'CRON'

    def __init__(self, finish_condition, job_id, step, control_hub=None):
        super().__init__(finish_condition, repr_metadata=FinishCondition._REPR_METADATA)
        self._control_hub = control_hub
        self._step = step
        self.job_id = job_id

    @property
    def job(self):
        return self._control_hub.jobs.get(job_id=self.job_id)

    @property
    def condition_type(self):
        return self._data['conditionType']

    @condition_type.setter
    def condition_type(self, value):
        if not isinstance(value, str):
            raise TypeError('value must be of type string')

        value = value.upper()

        if not hasattr(self.ConditionTypes, value):
            raise ValueError(
                '{} is not a valid value, accepted values are {}'.format(
                    value, [accepted_value.value for accepted_value in self.ConditionTypes]
                )
            )

        self._data['conditionType'] = value

    @property
    def crontab_mask(self):
        if self._data['conditionType'] != FinishCondition.ConditionTypes.CRON.value:
            raise TypeError('Cannot get crontab_mask if condition_type is not CRON')

        return self._data['crontabMask']

    @crontab_mask.setter
    def crontab_mask(self, value):
        if not isinstance(value, str):
            raise TypeError('value must be of type string')

        if self._data['conditionType'] != FinishCondition.ConditionTypes.CRON.value:
            raise TypeError('Cannot set crontab_mask if condition_type is not CRON')

        self._data['crontabMask'] = value

    @property
    def end_time(self):
        if self._data['conditionType'] != FinishCondition.ConditionTypes.END_TIME.value:
            raise TypeError('Cannot get end_time if condition_type is not END_TIME')

        return self._data['endTime']

    @end_time.setter
    def end_time(self, value):
        if not isinstance(value, int):
            raise TypeError('value must be of type int')

        if self._data['conditionType'] != FinishCondition.ConditionTypes.END_TIME.value:
            raise TypeError('Cannot set end_time if condition_type is not END_TIME')

        self._data['endTime'] = value

    @property
    def timezone(self):
        if self._data['conditionType'] != FinishCondition.ConditionTypes.END_TIME.value:
            raise TypeError('Cannot get timezone if condition_type is not END_TIME')

        return self._data['timezone']

    @timezone.setter
    def timezone(self, value):
        if not isinstance(value, str):
            raise TypeError('value must be of type string')

        if self._data['conditionType'] != FinishCondition.ConditionTypes.END_TIME.value:
            raise TypeError('Cannot set timezone if condition_type is not END_TIME')

        self._data['timezone'] = value


class JobSequenceHistoryLog(BaseModel):
    """Wrapper class for representing JobSequence History Log.

    Args:
        history_log (:obj:`dict`): JSON representation of a History Log.
    """

    _REPR_METADATA = ['timestamp', 'logMessage', 'logType', 'logLevel']

    def __init__(self, history_log):
        super().__init__(
            history_log,
            repr_metadata=JobSequenceHistoryLog._REPR_METADATA,
        )


@analytics_class_decorator
class JobSequenceHistoryLogs(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.JobSequenceHistoryLog` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): An instance of the ControlHub.
    """

    def __init__(self, control_hub, sequence_id):
        self._control_hub = control_hub
        self._id_attr = 'id'
        self._id = sequence_id

    def _get_all_results_from_api(self, **kwargs):
        """Args offset, len_, order_by, order are not exposed directly as arguments because of their limited use by
        normal users but, could still be specified just like any other args with the help of kwargs.

        Args:
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.JobSequenceHistoryLog` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.JobSequenceHistoryLog`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {
            'offset': 0,
            'len': None,
            'log_type': None,
            'log_level': None,
            'last_run_only': None,
            'run_id': None,
            'from_date': None,
            'to_date': None,
        }
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.get_job_sequence_log_history(
            sequence_id=self._id,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            log_type=(
                JobSequence.LogType(kwargs_unioned['log_type'].upper()).value if kwargs_unioned['log_type'] else None
            ),
            log_level=(
                JobSequence.LogLevel(kwargs_unioned['log_level'].upper()).value if kwargs_unioned['log_level'] else None
            ),
            last_run_only=kwargs_unioned['last_run_only'],
            run_id=kwargs_unioned['run_id'],
            from_date=kwargs_unioned['from_date'],
            to_date=kwargs_unioned['to_date'],
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, JobSequenceHistoryLog, {})


@analytics_class_decorator
class JobSequences(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.JobSequence` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): An instance of the ControlHub.
    """

    def __init__(self, control_hub):
        self._control_hub = control_hub
        self._id_attr = 'id'

    def _get_all_results_from_api(self, organization=None, search=None, **kwargs):
        """Args offset, len_, order_by, order are not exposed directly as arguments because of their limited use by
        normal users but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.JobSequence` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.JobSequence`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """

        kwargs_defaults = {'offset': 0, 'len': None, 'order_by': 'LAST_MODIFIED_TIME', 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if 'id' in kwargs_unioned:
            response = [self._control_hub.api_client.get_job_sequence(sequence_id=kwargs_unioned['id']).response.json()]
        elif search:
            response = self._control_hub.api_client.get_job_sequence_aql_search(
                search=search.query, offset=kwargs_unioned['offset'], len=kwargs_unioned['len']
            ).response.json()
        else:
            response = self._control_hub.api_client.get_all_job_sequences(
                organization=organization,
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, JobSequence, {'control_hub': self._control_hub})


class JobSequenceBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.JobSequence`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_job_sequence_builder`.

    Args:
        job_sequence (:obj:`dict`): Python object built from our Swagger PipelineJson definition.
    """

    def __init__(self, job_sequence, control_hub=None):
        self._job_sequence = job_sequence
        self._control_hub = control_hub

    def add_start_condition(self, start_time=0, end_time=0, time_zone='UTC', crontab_mask='0/1 * 1/1 * ? *'):
        """Add a start condition.

        Args:
            start_time (:obj:`int`, optional): Unix timestamp representing the start time for the Job Sequence.
             Default: `0`.
            end_time (:obj:`int`, optional): Unix timestamp representing the end time for the Job Sequence.
             Default: `0`.
            time_zone (:obj:`str`, optional): Time Zone of the Job Sequence. Default: ``UTC``.
            crontab_mask (:obj:`str`, optional): Cron Tab Mask of the Job Sequence. Default: `None`.
        """
        if not isinstance(start_time, int):
            raise TypeError("start_time should be of type int")
        if not isinstance(end_time, int):
            raise TypeError("end_time should be of type int")
        if not isinstance(time_zone, str):
            raise TypeError("time_zone should be of type str")
        if not isinstance(crontab_mask, str):
            raise TypeError("crontab_mask should be of type str")

        self._job_sequence.update(
            {
                "startTime": start_time,
                "endTime": end_time,
                "timezone": time_zone,
                "crontabMask": crontab_mask,
            }
        )

    def build(self, name='Job Sequence', description=None):
        """Build the Job Sequence.

        Args:
            name (:obj:`str`, optional): Name of the Job Sequence. Default: ``Job Sequence``.
            description (:obj:`str`, optional): End time for the Job Sequence. Default: `None`.

        Returns:
            A :py:class:`streamsets.sdk.sch_models.JobSequence` instances.
        """
        if not isinstance(name, str):
            raise TypeError("The name should be of type str")
        if description and not isinstance(description, str):
            raise TypeError("The description should be of type str")

        self._job_sequence.update(
            {
                "name": name,
                "description": description,
            }
        )

        return JobSequence(self._job_sequence, control_hub=self._control_hub)


@analytics_class_decorator
class Job(BaseModel):
    """Model for Job.

    Attributes:
        archived (:obj:`bool`): Flag that indicates if this job is archived.
        commit_id (:obj:`str`): Pipeline commit id.
        commit_label (:obj:`str`): Pipeline commit label.
        created_by (:obj:`str`): User that created this job.
        created_on (:obj:`int`): Time at which this job was created.
        data_collector_labels (:obj:`list`): Labels of the data collectors.
        delete_after_completion (:obj:`bool`): Flag that indicates if this job should be deleted after completion.
        description (:obj:`str`): Job description.
        destroyer (:obj:`str`): Job destroyer.
        enable_failover (:obj:`bool`): Flag that indicates if failover is enabled.
        enable_time_series_analysis (:obj:`bool`): Flag that indicates if time series is enabled.
        execution_mode (:obj:`bool`): True for Edge and False for SDC.
        job_deleted (:obj:`bool`): Flag that indicates if this job is deleted.
        job_id (:obj:`str`): Id of the job.
        job_name (:obj:`str`): Name of the job.
        last_modified_by (:obj:`str`): User that last modified this job.
        last_modified_on (:obj:`int`): Time at which this job was last modified.
        number_of_instances (:obj:`int`): Number of instances.
        pipeline_force_stop_timeout (:obj:`int`): Timeout for Pipeline force stop.
        pipeline_id (:obj:`str`): Id of the pipeline that is running the job.
        pipeline_name (:obj:`str`): Name of the pipeline that is running the job.
        pipeline_rule_id (:obj:`str`): Rule Id of the pipeline that is running the job.
        read_policy (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Read Policy of the job.
        runtime_parameters (:obj:`str`): Run-time parameters of the job.
        static_parameters (:obj:`list`): List of parameters that cannot be overriden.
        statistics_refresh_interval_in_millisecs (:obj:`int`): Refresh interval for statistics in milliseconds.
        status (:obj:`string`): Status of the job.
        history (:py:class:`streamsets.sdk.utils.SeekableList`) of (:py:class:`streamsets.sdk.sch_models.JobStatus`):
         Status and run count history for the Job.
        template_run_history_list (:obj:`list`): List of job template run history.
        write_policy (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Write Policy of the job.
    """

    _ATTRIBUTES_TO_IGNORE = [
        'currentJobStatus',
        'deleteTime',
        'destroyer',
        'organization',
        'parentJobId',
        'provenanceMetaData',
        'runtimeParameters',
        'systemJobId',
    ]
    _ATTRIBUTES_TO_REMAP = {
        'commit_id': 'pipelineCommitId',
        'commit_label': 'pipelineCommitLabel',
        'created_by': 'creator',
        'created_on': 'createTime',
        'data_collector_labels': 'labels',
        'delete_after_completion': 'deleteAfterCompletion',
        'enable_failover': 'migrateOffsets',
        'enable_time_series_analysis': 'timeSeries',
        'execution_mode': 'edge',
        'job_id': 'id',
        'job_name': 'name',
        'number_of_instances': 'numInstances',
        'pipeline_rule_id': 'rulesId',
        'pipeline_force_stop_timeout': 'forceStopTimeout',
        'require_job_error_acknowledgement': 'needsManualAck',
        'static_parameters': 'staticParameters',
        'statistics_refresh_interval_in_millisecs': 'statsRefreshInterval',
        'system_job_id': 'systemJobId',
        'template_run_history_list': 'templateRunHistoryList',
    }
    _REPR_METADATA = ['job_id', 'job_name']

    def __init__(self, job, control_hub=None):
        super().__init__(
            job,
            attributes_to_ignore=Job._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=Job._ATTRIBUTES_TO_REMAP,
            repr_metadata=Job._REPR_METADATA,
        )
        self._control_hub = control_hub
        self.read_policy = None
        self.write_policy = None

    def refresh(self):
        self._data = self._control_hub.api_client.get_job(self.job_id).response.json()

    @property
    def data_collectors(self):
        data_collectors = SeekableList()
        for pipeline_status in self.pipeline_status:
            # warning: some downstream uses incorrectly rely on the ValueError raised by the SeekableList here
            data_collector = self._control_hub.engines.get(id=pipeline_status.sdc_id, engine_type='COLLECTOR')
            pipeline_name = pipeline_status.name
            data_collectors.append(JobDataCollector(data_collector=data_collector, pipeline_name=pipeline_name))
        return data_collectors

    @property
    def transformers(self):
        transformers = SeekableList()
        for pipeline_status in self.pipeline_status:
            # warning: some downstream uses incorrectly rely on the ValueError raised by the SeekableList here
            transformer = self._control_hub.engines.get(id=pipeline_status.sdc_id, engine_type='TRANSFORMER')
            pipeline_name = pipeline_status.name
            transformers.append(JobTransformer(transformer=transformer, pipeline_name=pipeline_name))
        return transformers

    @property
    def status(self):
        """Current job status."""
        current_job_status = self._data['currentJobStatus']
        # Newly added jobs have a currentJobStatus of None, so need to be handled accordingly.
        return JobStatus(current_job_status, self._control_hub) if current_job_status is not None else None

    @property
    def current_status(self):
        logger.debug('Job.current_status will be removed in a future release. Please use Job.status instead.')
        current_job_status = self._data['currentJobStatus']
        return JobStatus(current_job_status, self._control_hub) if current_job_status is not None else None

    @property
    def history(self):
        """Status and run count history for the Job."""
        job_statuses = self._control_hub.api_client.get_job_status_history(job_id=self.job_id, offset=0, len=-1)
        return SeekableList(
            JobStatus(job_status, self._control_hub, job_history_view=True)
            for job_status in job_statuses.response.json()
        )

    @property
    def job_history(self):
        """Status and run count history for the Job."""
        return JobStatuses(self._control_hub, job_id=self.job_id)

    @property
    def job_sequence(self):
        """Get the Job Sequence that this job is a part of.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.JobSequence` or ``None``.
        """
        response_json = self._control_hub.api_client.get_job_sequence_for_job_id(self.job_id).response.json()

        if not response_json:
            return None

        job_sequence_json = self._control_hub.api_client.get_job_sequence(
            sequence_id=response_json[0]['sequenceId']
        ).response.json()
        job_sequence = JobSequence(job_sequence=job_sequence_json, control_hub=self._control_hub)

        return job_sequence

    @property
    def realtime_summary(self):
        """Get the Realtime Summary of the Job.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.PipelineMetrics` or
             :py:class:`streamsets.sdk.st_models.PipelineMetrics`.
        """
        engine = None

        # Wait for engine availability as a job starts
        def _engine_availability_established(job):
            nonlocal engine
            try:
                engine = job.data_collectors[0]
                return engine is not None
            except IndexError as ex:
                logger.debug('Execution engine is still not available: %s', ex)

        wait_for_condition(_engine_availability_established, [self], timeout=300)

        if self._control_hub.use_websocket_tunneling:
            # Get the realtime summary using control hub API with tunneling

            response = self._control_hub.api_client.get_job_realtime_summary(engine.id, engine.pipeline_id).response
            return SdcPipelineMetrics(response.json())
        else:
            # Get the realtime summary from engine directly
            pipeline_metrics = engine._instance.get_pipeline_metrics(engine.pipeline)
            return pipeline_metrics

    @property
    def start_time(self):
        return datetime.fromtimestamp(self._data['currentJobStatus']['startTime'] / 1000)

    @property
    def pipeline_status(self):
        # We use type to create a trivial class as a container for the dictionaries we get from
        # ControlHub containing pipeline status.
        PipelineStatus = type('PipelineStatus', (BaseModel,), {})
        if not self._data.get('currentJobStatus', None) or not self._data['currentJobStatus'].get('pipelineStatus', []):
            return SeekableList([])
        return SeekableList(
            PipelineStatus(pipeline_status, repr_metadata=['sdc_id', 'name'])
            for pipeline_status in self._data['currentJobStatus']['pipelineStatus']
        )

    @property
    def runtime_parameters(self):
        return RuntimeParameters(self._data['runtimeParameters'], self)

    @runtime_parameters.setter
    def runtime_parameters(self, value):
        self._data['runtimeParameters'] = json.dumps(value)

    @property
    def acl(self):
        """Get job ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_job_acl(job_id=self.job_id).response.json(), self._control_hub)

    @acl.setter
    def acl(self, job_acl):
        """Update job ACL.

        Args:
            job_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The job ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.set_job_acl(job_id=self.job_id, job_acl_json=job_acl._data)

    @property
    def commit(self):
        """Get pipeline commit of the job.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.PipelineCommit`.
        """
        return self.pipeline.commits.get(commit_id=self._data['pipelineCommitId'])

    @commit.setter
    def commit(self, pipeline_commit):
        """Update pipeline commit of the job.

        Args:
            pipeline_commit (:py:class:`streamsets.sdk.sch_models.PipelineCommit`): Pipeline commit instance.
        """
        self._data['pipelineCommitId'] = pipeline_commit.commit_id
        self._data['pipelineCommitLabel'] = 'v{}'.format(pipeline_commit.version)

    @property
    def tag(self):
        """Get pipeline tag of the job.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.PipelineTag`.
        """
        try:
            return self.pipeline.tags.get(commit_id=self._data['pipelineCommitId'])
        except ValueError:
            return None

    @tag.setter
    def tag(self, pipeline_tag):
        """Update pipeline tag of the job.

        Args:
            pipeline_tag (:py:class:`streamsets.sdk.sch_models.PipelineTag`): Pipeline tag instance.
        """
        self._data['pipelineCommitId'] = pipeline_tag.commit_id
        pipeline_commit = self.pipeline.commits.get(commit_id=pipeline_tag.commit_id)
        self._data['pipelineCommitLabel'] = 'v{}'.format(pipeline_commit.version)

    @property
    def system_job(self):
        """Get the sytem Job for this job if exists.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        system_job_id = self._control_hub.jobs.get(job_id=self.job_id).system_job_id
        if system_job_id is not None:
            return self._control_hub.jobs.get(job_id=system_job_id, system=True)

    @property
    def pipeline(self):
        """Get the pipeline object corresponding to this job."""
        return self._control_hub.pipelines.get(commit_id=self._data['pipelineCommitId'])

    @property
    def _pipeline_version(self):
        """Get the version of the pipeline.

        Returns:
            An instance of :obj:`int`.
        """
        return self.pipeline_commit_label.replace('v', '')

    def get_snowflake_generated_queries(self):
        """Retrieve the Snowflake generated queries of the last run of the job.

        Returns:
            A :obj:`list` of :obj:`dict` instances, one dictionary per query.
        """
        run_count = self._control_hub.api_client.get_current_job_status(self.job_id).response.json()['runCount']
        snowflake_queries = self._control_hub.api_client.get_snowflake_generated_queries(self.job_id, run_count)
        return snowflake_queries.response.json()

    @property
    def tags(self):
        """Get the job tags.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of instances of
            :py:class:`streamsets.sdk.sch_models.Tag`.
        """
        job_tags = self._data.get('jobTags', []) or []
        if not job_tags:
            raw_job_tags = self._data.get('rawJobTags', []) or []
            if raw_job_tags:
                organization = self._control_hub.organization
                job_tags = [build_tag_from_raw_tag(raw_tag, organization) for raw_tag in raw_job_tags]
                self._data['jobTags'] = job_tags
        return SeekableList(Tag(tag) for tag in job_tags)

    def add_tag(self, *tags):
        """Add a tag

        Args:
            *tags: One or more instances of :obj:`str`
        """
        current_tags = [tag.tag for tag in self.tags]
        if not self._data.get('jobTags', None):
            self._data['jobTags'] = []
        if not self._data.get('rawJobTags', None):
            self._data['rawJobTags'] = current_tags
        for tag in tags:
            self._data['rawJobTags'].append(tag)
            tag_json = build_tag_from_raw_tag(tag, self._control_hub.organization)
            self._data['jobTags'].append(tag_json)

    def remove_tag(self, *tags):
        """Remove a tag

        Args:
            *tags: One or more instances of :obj:`str`
        """
        current_tags = [tag.tag for tag in self.tags]
        for tag in tags:
            if tag in current_tags:
                current_tags.remove(tag)
                item = self.tags.get(tag=tag)
                self._data['jobTags'].remove(item._data)
            else:
                logger.warning('Tag %s is not an assigned tag for this pipeline. Ignoring this tag.', tag)
        self._data['rawJobTags'] = current_tags

    def get_run_logs(self):
        """Retrieve the logs for the last run of the job.

        Returns:
            A :obj:`list` of :obj:`dict` instances, one dictionary per log line.
        """
        run_count = self._control_hub.api_client.get_current_job_status(self.job_id).response.json()['runCount']
        job_logs = self._control_hub.api_client.get_job_run_logs(self.job_id, run_count)
        return job_logs.response.json()

    @property
    def metrics(self):
        """The metrics from all runs of a Job.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.JobMetrics` instances.

        """
        metrics = self._control_hub.api_client.get_job_record_count_for_all_runs(job_id=self.job_id).response.json()
        # Manually set the run count because the Metrics API doesn't return a 'runCount' value for the last job run, and
        # stops at the second last job run. Note, even if there is only job run, then we get one record where 'runCount'
        # is still not returned. See the UI implementation here: https://git.io/JYNdT
        if metrics:
            max_record_count = max(metric.get('runCount', 0) for metric in metrics.values())
            metrics['0']['runCount'] = max_record_count + 1
        return SeekableList(
            sorted((JobMetrics(metrics[metric]) for metric in metrics), key=lambda x: x.run_count, reverse=True)
        )

    def time_series_metrics(self, metric_type, time_filter_condition='LAST_5M', **kwargs):
        """Get historic time series metrics for the job.

        Args:
            metric_type (:obj:`str`): metric type in {'Record Count Time Series', 'Record Throughput Time Series',
                                                      'Batch Throughput Time Series',
                                                      'Stage Batch Processing Timer seconds'}.
            time_filter_condition (:obj:`str`, optional): Default: ``'LAST_5M'``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetrics`.
        """

        def generate_body(column, measurements, self):
            body = []
            for measurement in measurements:
                time_series_query_json = self._time_series_query_json.copy()
                time_series_query_json.update(
                    {
                        'columns': [column],
                        'jobId': self.job_id,
                        'measurement': measurement,
                        'pipelineVersion': self._pipeline_version,
                        'sdcId': self._data['currentJobStatus']['sdcIds'][0],
                    }
                )
                body.append(time_series_query_json)
            return body

        # Swagger for time series does not exist yet (DPM-6328). So, using a static json here.
        self._time_series_query_json = {
            'columns': None,
            'jobId': None,
            'measurement': None,
            'pipelineVersion': None,
            'sdcId': None,
        }
        record_meter_types = [
            'PIPELINE_BATCH_INPUT_RECORDS_METER',
            'PIPELINE_BATCH_OUTPUT_RECORDS_METER',
            'PIPELINE_BATCH_ERROR_RECORDS_METER',
        ]
        metric_type_to_body_params = {
            'Record Count Time Series': generate_body('count', record_meter_types, self),
            'Record Throughput Time Series': generate_body('m1_rate', record_meter_types, self),
            'Batch Throughput Time Series': generate_body('m1_rate', ['PIPELINE_BATCH_COUNT_METER'], self),
            'Stage Batch Processing Timer seconds': generate_body('mean', ['STAGE_BATCH_PROCESSING_TIMER'], self),
        }
        return JobTimeSeriesMetrics(
            self._control_hub.api_client.get_job_time_series_metrics(
                metric_type_to_body_params[metric_type], time_filter_condition, **kwargs
            ).response.json(),
            metric_type,
        )

    @property
    def committed_offsets(self):
        """Get the committed offsets for a given job id.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.JobCommittedOffset`.
        """
        committed_offsets = self._control_hub.api_client.get_job_committed_offsets(job_id=self.job_id)

        return JobCommittedOffset(committed_offsets.response.json()) if committed_offsets.response.text else None

    @property
    def latest_committed_offsets(self):
        """Get the latest committed offsets for a given job id.

        Returns:
            A (:obj:`dict`) object.
        """
        latest_committed_offsets = self._control_hub.api_client.get_job_latest_committed_offsets(job_id=self.job_id)

        return latest_committed_offsets.response.json()


@analytics_class_decorator
class JobStatuses(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.JobStatus` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): An instance of the ControlHub.
    """

    def __init__(self, control_hub, job_id):
        self._control_hub = control_hub
        self._id_attr = 'id'
        self._id = job_id

    def _get_all_results_from_api(self, **kwargs):
        """Args offset, len_, order_by, order are not exposed directly as arguments because of their limited use by
        normal users but, could still be specified just like any other args with the help of kwargs.

        Args:
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.JobStatus` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.JobStatus`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'search': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.get_saql_job_status_history(
            job_id=self._id,
            search=kwargs_unioned['search'].query if kwargs_unioned['search'] else kwargs_unioned['search'],
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, JobStatus, {'control_hub': self._control_hub})


@analytics_class_decorator
class Snapshot(BaseModel):
    """Model for Snapshot.

    Args:
        snapshot (:obj:`dict`): Python object representation of the snapshot.
        draft_run (:py:class:`streamsets.sdk.sch.DraftRun`): DraftRun object.

    Attributes:
        batch_number (:obj:`int`): The number of the batch that the snapshot captured.
        batches (:obj:`list`): A list of :py:class:`streamsets.sdk.sdc_models.Batch` instances.
        id (:obj:`str`): The snapshot's ID.
        name (:obj:`str`): The snapshot's name.
        pipeline_id (:obj:`str`): The ID of the pipeline that the snapshot belongs to.
        time_stamp (:obj:`int`): The creation date of the snapshot as a unix timestamp.

    """

    _REPR_METADATA = ['name', 'time_stamp', 'batch_number']

    def __init__(self, snapshot, draft_run):
        super().__init__(snapshot, repr_metadata=Snapshot._REPR_METADATA)
        self._draft_run = draft_run
        self._control_hub = draft_run._control_hub
        self._data = snapshot
        self._batches = None

    @property
    def batch_number(self):
        return self._data['batchNumber']

    @property
    def id(self):
        return self._data['id']

    @property
    def name(self):
        return self._data['label']

    @property
    def pipeline_id(self):
        return self._data['name']

    @property
    def time_stamp(self):
        return self._data['timeStamp']

    @property
    def batches(self):
        if not self._batches:
            snapshot_batches = self._get_batches().get('snapshotBatches', [])
            self._batches = [SdcBatch(snapshot_batch) for snapshot_batch in snapshot_batches]
        return self._batches

    def _get_batches(self):
        engine_id = self._draft_run._data["currentJobStatus"]["sdcIds"][0]
        engine = self._control_hub.engines.get(id=engine_id)
        engine_pipeline_id = self._draft_run._data["currentJobStatus"]["enginePipelineId"]
        job_id = self._draft_run.job_id
        job_run_count = self._draft_run.history[0].run_count
        if self._control_hub.use_websocket_tunneling:
            tunneling_instance = engine._tunneling_connection
            response = self._control_hub.api_client.get_snapshot_data(
                engine_id=engine_id,
                engine_pipeline_id=engine_pipeline_id,
                snapshot_id=self.id,
                job_id=job_id,
                tunneling_instance_id=tunneling_instance,
                job_run_count=job_run_count,
            ).response
        else:
            response = engine._api_client.get_snapshot_data(
                pipeline_id=engine_pipeline_id,
                snapshot_name=self.id,
                snapshot_label=self.name,
                job_id=job_id,
                job_run_count=job_run_count,
            ).response

        if not response.content:
            return {}
        return response.json()

    def __getitem__(self, key):
        return self.batches[0][key.instance_name if isinstance(key, SdcStage) else key]

    def __iter__(self):
        for snapshot_batch in self.batches:
            yield snapshot_batch

    def __len__(self):
        return len(self.batches)


@analytics_class_decorator
class DraftRun(Job):
    """Model for DraftRun.

    Attributes:
        commit_id (:obj:`str`): Pipeline commit id.
        commit_label (:obj:`str`): Pipeline commit label.
        created_by (:obj:`str`): User that created this job.
        created_on (:obj:`int`): Time at which this job was created.
        data_collector_labels (:obj:`list`): Labels of the data collectors.
        delete_after_completion (:obj:`bool`): Flag that indicates if this job should be deleted after completion.
        description (:obj:`str`): Job description.
        enable_failover (:obj:`bool`): Flag that indicates if failover is enabled.
        enable_time_series_analysis (:obj:`bool`): Flag that indicates if time series is enabled.
        execution_mode (:obj:`bool`): True for Edge and False for SDC.
        job_id (:obj:`str`): Id of the job.
        job_name (:obj:`str`): Name of the job.
        last_modified_by (:obj:`str`): User that last modified this job.
        last_modified_on (:obj:`int`): Time at which this job was last modified.
        number_of_instances (:obj:`int`): Number of instances.
        pipeline_force_stop_timeout (:obj:`int`): Timeout for Pipeline force stop.
        pipeline_id (:obj:`str`): Id of the pipeline that is running the job.
        pipeline_name (:obj:`str`): Name of the pipeline that is running the job.
        pipeline_rule_id (:obj:`str`): Rule Id of the pipeline that is running the job.
        read_policy (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Read Policy of the job.
        runtime_parameters (:obj:`str`): Run-time parameters of the job.
        static_parameters (:obj:`list`): List of parameters wjat cannot be overriden.
        statistics_refresh_interval_in_millisecs (:obj:`int`): Refresh interval for statistics in milliseconds.
        status (:obj:`string`): Status of the job.
        snapshots (:py:class:`streamsets.sdk.utils.SeekableList`) of (:py:class:`streamsets.sdk.sch_models.Snapshot`):
         Snapshots belonging to the draft run.
    """

    def get_logs(self, ending_offset=-1):
        """Retrieve the logs from the engine.

        Args:
            ending_offset (:obj:`int`, optional): The offset to capture logs up until. Default: ``-1``

        Returns:
            A :obj:`list` of :obj:`dict` instances, one dictionary per log line.
        """
        self.refresh()
        engine_id = self._data["currentJobStatus"]["sdcIds"][0]
        engine = self._control_hub.engines.get(id=engine_id)
        engine_pipeline_id = self._data["currentJobStatus"]["enginePipelineId"]
        if self._control_hub.use_websocket_tunneling:
            tunneling_instance = engine._tunneling_connection
            return self._control_hub.api_client.get_draft_run_logs(
                engine_id, engine_pipeline_id, tunneling_instance, ending_offset
            ).response.json()
        return engine._api_client.get_logs(ending_offset=ending_offset, pipeline=engine_pipeline_id).response.json()

    @property
    def snapshots(self):
        """Snapshots belonging to the draft run.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Snapshot` instances.
        """

        self.refresh()

        job_run_count = self.history[0].run_count
        engine_id = self._data["currentJobStatus"]["sdcIds"][0]
        engine = self._control_hub.engines.get(id=engine_id)
        engine_pipeline_id = self._data["currentJobStatus"]["enginePipelineId"]
        if self._control_hub.use_websocket_tunneling:
            tunneling_instance = engine._tunneling_connection
            response = self._control_hub.api_client.get_draft_run_snapshots(
                engine_id=engine_id,
                engine_pipeline_id=engine_pipeline_id,
                job_id=self.job_id,
                tunneling_instance_id=tunneling_instance,
                job_run_count=job_run_count,
            ).response
        else:
            response = engine._api_client.get_snapshots_by_pipeline(
                pipeline_id=engine_pipeline_id, job_id=self.job_id, job_run_count=job_run_count
            ).response

        if not response.content:
            return SeekableList()
        return SeekableList(
            Snapshot(snapshot, self) for snapshot in sorted(response.json(), key=lambda x: x['timeStamp'])
        )

    def capture_snapshot(self):
        """Generate a new snapshot.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """

        def snapshot_label_count():
            current_snapshots = self.snapshots
            last_count = 0
            if current_snapshots:
                last_count = current_snapshots[-1].name.split("Snapshot")[1]
            return int(last_count) + 1

        self.refresh()
        if self.status.status != 'ACTIVE':
            raise Exception("Draft Run isn't active, snapshot can't be taken.")

        engine_id = self._data["currentJobStatus"]["sdcIds"][0]
        engine = self._control_hub.engines.get(id=engine_id)
        engine_pipeline_id = self._data['currentJobStatus']['enginePipelineId']
        snapshot_label = "Snapshot{}".format(snapshot_label_count())
        if self._control_hub.use_websocket_tunneling:
            tunneling_instance = engine._tunneling_connection
            return self._control_hub.api_client.generate_snapshot(
                engine_id=engine_id,
                engine_pipeline_id=engine_pipeline_id,
                snapshot_label=snapshot_label,
                tunneling_instance_id=tunneling_instance,
            )

        snapshot_id = '{}{}'.format('snapshot', int(datetime.now().timestamp() * 1000))
        return engine._api_client.capture_snapshot(
            pipeline_id=engine_pipeline_id, snapshot_name=snapshot_id, snapshot_label=snapshot_label
        )

    def wait_for_finished_snapshot(self, timeout_sec=30):
        start_waiting_time = time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time() < stop_waiting_time:
            job_run_count = self.history[0].run_count
            engine_id = self._data["currentJobStatus"]["sdcIds"][0]
            engine = self._control_hub.engines.get(id=engine_id)
            engine_pipeline_id = self._data["currentJobStatus"]["enginePipelineId"]

            if self._control_hub.use_websocket_tunneling:
                tunneling_instance = engine._tunneling_connection
                response = self._control_hub.api_client.get_draft_run_snapshots(
                    engine_id=engine_id,
                    engine_pipeline_id=engine_pipeline_id,
                    job_id=self.job_id,
                    tunneling_instance_id=tunneling_instance,
                    job_run_count=job_run_count,
                ).response
            else:
                response = engine._api_client.get_snapshots_by_pipeline(
                    pipeline_id=engine_pipeline_id, job_id=self.job_id, job_run_count=job_run_count
                ).response

            logger.debug('response.content: %s', response.content)

            # Loop back until response content starts coming through.
            if not response.content:
                continue

            is_in_progress = response.json()[0]['inProgress']  # First snapshot is most current
            snapshot_name = response.json()[0]['label']
            logger.debug('Pipeline (%s) snapshot (%s) in progress: %s', self.pipeline_id, snapshot_name, is_in_progress)

            if not is_in_progress:
                logger.info(
                    'Pipeline (%s) snapshot (%s) complete (took %.2f s).',
                    self.pipeline_id,
                    snapshot_name,
                    time() - start_waiting_time,
                )
                return self

            sleep(1)

        # We got out of the loop and did not get to the finished state.
        raise TimeoutError('Timed out after {} seconds while waiting for snapshot to complete.'.format(timeout_sec))

    def remove_snapshot(self, snapshot):
        """Remove a snapshot.

        Args:
            snapshot (:py:obj:`streamsets.sdk.sch_models.Snapshot`): Snapshot object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        self.refresh()
        job_run_count = self.history[0].run_count
        engine_id = self._data["currentJobStatus"]["sdcIds"][0]
        engine = self._control_hub.engines.get(id=engine_id)
        engine_pipeline_id = self._data["currentJobStatus"]["enginePipelineId"]
        if self._control_hub.use_websocket_tunneling:
            tunneling_instance = engine._tunneling_connection
            snapshot_command = self._control_hub.api_client.remove_snapshot(
                engine_id=engine_id,
                engine_pipeline_id=engine_pipeline_id,
                snapshot_id=snapshot.id,
                tunneling_instance_id=tunneling_instance,
            )
        else:
            snapshot_command = engine._api_client.delete_snapshot(
                pipeline_id=engine_pipeline_id, snapshot_id=snapshot.id, job_id=self.job_id, job_run_count=job_run_count
            )
        return snapshot_command


@analytics_class_decorator
class DraftRuns(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.DraftRun` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    def __init__(self, control_hub):
        self._control_hub = control_hub
        self._id_attr = 'job_id'

    def _get_all_results_from_api(self, organization=None, search=None, **kwargs):
        """Args order_by, offset, len are not exposed directly as arguments because of their limited use by
        normal users but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            search (:obj:`str`, optional): Only return draft runs that match the search query. Default: ``None``.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.DraftRun` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.DraftRun`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'order_by': 'modified_on', 'search': None, 'offset': 0, 'len': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.get_draft_runs_by_query(
            search=search,
            org_id=self._control_hub.organization,
            order_by=kwargs_unioned['order_by'].lower(),
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
        ).response.json()

        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, DraftRun, {'control_hub': self._control_hub})


@analytics_class_decorator
class Jobs(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Job` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    def __init__(self, control_hub):
        self._control_hub = control_hub
        self._id_attr = 'job_id'

    def __len__(self):
        return self._control_hub.api_client.get_jobs_count(
            organization=None, removed=False, system=False
        ).response.json()['count']

    def count(self, status):
        """Get job counts by status.

        Args:
            status (:obj:`str`): Status of the jobs in {'ACTIVE', 'INACTIVE', 'ACTIVATING', 'DEACTIVATING',
                                                        'INACTIVE_ERROR', 'ACTIVE_GREEN', 'ACTIVE_RED', ''}

        Returns:
            An instance of :obj:`int` indicating the count of jobs with specified status.
        """
        counts = {
            item['status']: item['count']
            for item in self._control_hub.api_client.get_job_count_by_status().response.json()['data']
        }
        if status not in counts:
            raise ValueError('Specified status {} is invalid'.format(status))
        return counts[status]

    def _get_all_results_from_api(
        self, id=None, job_id=None, organization=None, job_status=None, search=None, **kwargs
    ):
        """Args order_by, order, removed, system, filter_text, job_status, job_label, edge, len, offset are not exposed
        directly as arguments because of their limited use by normal users but, could still be specified just like any
        other args with the help of kwargs.

        Args:
            id (:obj:`str`, optional): Job ID. Default: ``None``.
                This attribute will be deprecated in a future release. Please use job_id instead.
            job_id (:obj:`str`, optional): Job ID. Default: ``None``.
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            job_status (:obj:`str`, optional): Only return jobs of a particular status. Default: ``None``.
                Acceptable values are 'INACTIVE', 'ACTIVATING', 'ACTIVATION_ERROR', 'ACTIVE', 'DEACTIVATING',
                'INACTIVE_ERROR'.
            filter_text (:obj:`str`, optional): Only returns instances that match the filter string. This will be
                propagated to the API backend (results filtered server-side instead of client-side).
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Job` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Job`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {
            'order_by': 'CREATE_TIME',
            'order': 'ASC',
            'removed': False,
            'system': False,
            'filter_text': None,
            'job_search_operation': 'EQUALS',
            'job_search_text': '',
            'job_label': None,
            'edge': None,
            'offset': 0,
            'len': None,
            'executor_type': None,
            'job_tag': None,
            'job_template': None,
        }
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if id is not None:
            warnings.warn(
                'The attribute id of streamsets.sdk.sch_models.Jobs will be removed in a '
                'future release. Please use job_id instead.',
                DeprecationWarning,
            )
            job_id = id
        if kwargs_unioned['job_tag']:
            kwargs_unioned['job_tag'] = '{}:{}'.format(kwargs_unioned['job_tag'], self._control_hub.organization)
        if job_id is not None:
            try:
                response = [self._control_hub.api_client.get_job(job_id).response.json()]
            except requests.exceptions.HTTPError:
                raise ValueError('Job (id={}) not found'.format(job_id))
        elif job_status is not None:
            try:
                response = self._control_hub.api_client.get_jobs_by_status(
                    organization=organization,
                    order_by=kwargs_unioned['order_by'],
                    order=kwargs_unioned['order'],
                    removed=kwargs_unioned['removed'],
                    system=kwargs_unioned['system'],
                    filter_text=kwargs_unioned['filter_text'],
                    job_search_operation=kwargs_unioned['job_search_operation'],
                    job_search_text=kwargs_unioned['job_search_text'],
                    job_status=job_status,
                    edge=kwargs_unioned['edge'],
                    offset=kwargs_unioned['offset'],
                    len=kwargs_unioned['len'],
                    executor_type=kwargs_unioned['executor_type'],
                    job_tag=kwargs_unioned['job_tag'],
                    with_wrapper=True,
                ).response.json()
            except requests.exceptions.HTTPError:
                raise ValueError('Jobs with (status={}) not found'.format(job_status))
        elif search:
            if kwargs_unioned['job_template']:
                response = self._control_hub.api_client.get_job_templates_by_query(
                    search=search,
                    org_id=self._control_hub.organization,
                    order_by=convert_last_modified_on_field_for_saql(kwargs_unioned['order_by'].lower()),
                    offset=kwargs_unioned['offset'],
                    len=kwargs_unioned['len'],
                ).response.json()
            else:
                response = self._control_hub.api_client.get_jobs_by_query(
                    search=search,
                    org_id=self._control_hub.organization,
                    order_by=convert_last_modified_on_field_for_saql(kwargs_unioned['order_by'].lower()),
                    offset=kwargs_unioned['offset'],
                    len=kwargs_unioned['len'],
                ).response.json()
        else:
            response = self._control_hub.api_client.return_all_jobs(
                organization=organization,
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                removed=kwargs_unioned['removed'],
                system=kwargs_unioned['system'],
                filter_text=kwargs_unioned['filter_text'],
                job_search_operation=kwargs_unioned['job_search_operation'],
                job_search_text=kwargs_unioned['job_search_text'],
                job_status=job_status,
                job_label=kwargs_unioned['job_label'],
                edge=kwargs_unioned['edge'],
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                executor_type=kwargs_unioned['executor_type'],
                with_wrapper=True,
                job_tag=kwargs_unioned['job_tag'],
                job_template=kwargs_unioned['job_template'],
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Job, {'control_hub': self._control_hub})


class JobTemplateRunHistory(BaseModel):
    """Model for Job Template Run history.

    Args:
        configuration (:obj:`str`)
        optimistic_lock_version (:obj:`int`)
        run_count (:obj:`int`)
        template_id (:obj:`str`)
        template_job_id (:obj:`str`): ID of the Job Template.
        time (:obj:`int`)
        user (:obj:`str`)
    """

    _ATTRIBUTES_TO_REMAP = {
        'template_id': 'id',
    }
    _REPR_METADATA = ['template_id', 'user']

    def __init__(self, JobTemplateRunHistory, control_hub=None):
        super().__init__(
            JobTemplateRunHistory,
            attributes_to_remap=JobTemplateRunHistory._ATTRIBUTES_TO_REMAP,
            repr_metadata=JobTemplateRunHistory._REPR_METADATA,
        )
        self._control_hub = control_hub


class RuntimeParameters:
    """Wrapper for ControlHub job runtime parameters.

    Args:
        runtime_parameters (:obj:`str`): Runtime parameter.
        job (:py:obj:`streamsets.sdk.sch_models.Job`): Job object.
    """

    def __init__(self, runtime_parameters, job):
        self._data = json.loads(runtime_parameters) if runtime_parameters else {}
        self._job = job

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._propagate()

    def update(self, runtime_parameters):
        self._data.update(runtime_parameters)
        self._propagate()

    def _propagate(self):
        self._job._data['runtimeParameters'] = json.dumps(self._data)

    def __repr__(self):
        return str(self._data)

    def __bool__(self):
        return bool(self._data)


@analytics_class_decorator
class TopologyBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Topology`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_topology_builder`.

    Attributes:
        topology_nodes (:py:class:`streamsets.sdk.utils.SeekableList`) of
         (:py:class:`streamsets.sdk.sch_models.TopologyNode`): Nodes currently part of the topology held by the TopologyBuilder.

    Args:
        topology (:obj:`dict`): Python object built from our Swagger TopologyJson definition.
        control_hub (:py:class:`streamsets.sdk.ControlHub`, optional): Control Hub instance. Default: ``None``
    """

    def __init__(self, topology, control_hub=None):
        self._topology = topology
        self._default_topology = topology
        self._control_hub = control_hub

    @property
    def topology_nodes(self):
        """Get all of the nodes currently part of the topology held by the TopologyBuilder.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.TopologyNode`
                instances.
        """
        topology_definition = self._topology['topologyDefinition']
        if isinstance(self._topology['topologyDefinition'], str):
            topology_definition = json.loads(self._topology['topologyDefinition'])
        return SeekableList(TopologyNode(node) for node in topology_definition['topologyNodes'])

    def build(self, topology_name=None, description=None):
        """Build the topology.

        Args:
            topology_name (:obj:`str`, optional): Name of the topology. This parameter is required when building a new
                topology.
            description (:obj:`str`, optional): Description of the topology. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Topology`.
        """

        if topology_name is None and self._topology['name'] is None:
            raise TopologyIssuesError(
                "The Topology's 'name' attribute is empty, and no topology_name was supplied to"
                "build(). Please provide a topology_name."
            )
        if topology_name is not None:
            self._topology.update({'name': topology_name})
        self._topology.update({'description': description})
        # Convert topologyDefinition from dict to str for consistency with Topology class
        self._topology['topologyDefinition'] = json.dumps(self._topology['topologyDefinition'])
        return Topology(topology=self._topology, control_hub=self._control_hub)

    def import_topology(self, topology):
        """Import an existing topology to be used in the builder.

        Args:
            topology (:py:class:`streamsets.sdk.sch_models.Topology`): An existing Topology instance to modify.
        """
        if not topology.commit_id:
            raise TopologyIssuesError('Cannot call import_topology using an unpublished topology.')
        self._topology.update(topology._data)
        # Convert topologyDefinition from str to dict for processing
        self._topology['topologyDefinition'] = json.loads(self._topology['topologyDefinition'])

    def add_job(self, job):
        """Add a job node to the Topology being built.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): An instance of a job to be added.
        """
        # Based off of https://t.ly/6y7o
        pipeline_json = self._control_hub.api_client.get_pipeline_commit(
            commit_id=job.pipeline.commit_id
        ).response.json()
        pipeline_definition = json.loads(pipeline_json['pipelineDefinition'])
        library_definitions = json.loads(pipeline_json['libraryDefinitions'])
        topology_nodes = (
            self._topology['topologyDefinition']['topologyNodes'] if 'topologyDefinition' in self._topology else {}
        )
        x_pos = 100
        y_pos = 50

        for topology_node in topology_nodes:
            if topology_node['uiInfo']['xPos'] >= x_pos:
                x_pos = topology_node['uiInfo']['xPos'] + 250
        nodes = get_topology_nodes([job], pipeline_json, pipeline_definition, x_pos, y_pos)

        for node in nodes:
            icon_key = '{}:{}'.format(node['library'], node['stageName'])
            if (
                'stageIcons' in library_definitions
                and library_definitions['stageIcons']
                and icon_key in library_definitions['stageIcons']
            ):
                self._topology['topologyDefinition']['stageIcons'][icon_key] = library_definitions['stageIcons'][
                    icon_key
                ]

        topology_nodes.extend(nodes)

    def add_system(self, name):
        """Add a system node to the Topology being built.

        Args:
            name (:obj:`str`): The name of the system to add to the topology.
        """
        topology_node_json = {
            'nodeType': None,
            'instanceName': None,
            'library': None,
            'stageName': None,
            'stageVersion': None,
            'jobId': None,
            'pipelineId': None,
            'pipelineCommitId': None,
            'pipelineVersion': None,
            'inputLanes': [],
            'outputLanes': [],
            'uiInfo': {},
        }
        try:
            system = next(system for system in ALL_TOPOLOGY_SYSTEMS if system['label'] == name)
        except StopIteration:
            raise TopologyIssuesError(f'No system found with the name "{name}".')
        topology_nodes = (
            self._topology['topologyDefinition']['topologyNodes'] if 'topologyDefinition' in self._topology else {}
        )
        x_pos = 100
        y_pos = 50

        for topology_node in topology_nodes:
            if topology_node['uiInfo']['xPos'] >= x_pos:
                x_pos = topology_node['uiInfo']['xPos'] + 250

        system_node = copy.deepcopy(topology_node_json)
        system_node['nodeType'] = 'SYSTEM'
        system_node['instanceName'] = 'ADDED_SEPARATELY:SYSTEM:{}'.format(int(datetime.utcnow().timestamp() * 1000))
        system_node['outputLanes'] = ['{}OutputLane1'.format(system_node['instanceName'])]
        system_node['uiInfo']['label'] = system['label']
        system_node['uiInfo']['xPos'] = x_pos
        system_node['uiInfo']['yPos'] = y_pos
        system_node['uiInfo']['icon'] = system['icon']
        system_node['uiInfo']['colorIcon'] = system['colorIcon']

        topology_nodes.append(system_node)

    def delete_node(self, topology_node):
        """Delete a system or job node from the topology.

        Args:
            topology_node (:py:class:`streamsets.sdk.sch_models.TopologyNode`): An instance of a TopologyNode to delete
                from the topology.

        """
        # Based off of https://git.io/JRoAC
        try:
            node_index, selected_node = next(
                (index, node)
                for index, node in enumerate(self.topology_nodes)
                if node.instance_name == topology_node.instance_name
            )
        except ValueError as ex:
            ex.message = 'The specified node does not exist within this topology.'
            raise
        if isinstance(self._topology, dict):
            del self._topology['topologyDefinition']['topologyNodes'][node_index]
        else:
            del json.loads(self._topology['topologyDefinition'])['topologyNodes'][node_index]

        # Remove the inputLanes that reference the deleted node's outputLane
        for topology_node in self.topology_nodes:
            for lane_index, input_lane in enumerate(topology_node.input_lanes):
                if input_lane in selected_node.output_lanes:
                    del topology_node.input_lanes[lane_index]


class TopologyNode(BaseModel):
    """Model for a node within a Topology.

    Args:
        topology_node_json (:obj:`dict`): JSON representation of a Topology Node.

    Attributes:
        node_type (:obj:`str`): The type of this node, i.e. SYSTEM, JOB, etc.
        instance_name (:obj:`str`): The name of this node instance.
        stage_name (:obj:`str`): The name of the stage in this node.
        stage_version (:obj:`str`): The version of the stage in this node.
        job_id (:obj:`str`): The ID of the job in this node.
        pipeline_id (:obj:`str`): The pipeline ID associated with the job in this node.
        pipeline_commit_id (:obj:`str`): The commit ID of the pipeline.
        pipeline_version (:obj:`str`): The version of the pipeline.
        input_lanes (:obj:`list`): A list of :obj:`str` representing the input lanes for this node.
        output_lanes (:obj:`list`): A list of :obj:`str` representing the output lanes for this node.
        name (:obj:`str`): Name of the Topology Node.
    """

    _REPR_METADATA = ['name', 'node_type']
    _ATTRIBUTES_TO_IGNORE = ['uiInfo', 'library']

    def __init__(self, topology_node_json):
        super().__init__(
            topology_node_json,
            attributes_to_ignore=TopologyNode._ATTRIBUTES_TO_IGNORE,
            repr_metadata=TopologyNode._REPR_METADATA,
        )

    @property
    def name(self):
        return self._data['uiInfo']['label']


@analytics_class_decorator
class Topology(BaseModel):
    """Model for Topology.

    Args:
        topology (:obj:`dict`): JSON representation of Topology.

    Attributes:
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): Topology ACL.
        commit_id (:obj:`str`): Pipeline commit id.
        commit_message (:obj:`str`): Commit Message.
        commit_time (:obj:`int`): Time at which commit was made.
        committed_by (:obj:`str`): User that made the commit.
        data_slas (:py:class:`streamsets.sdk.utils.SeekableList`) of (:py:class:`streamsets.sdk.sch_models.DataSla`):
         Data SLAs currently part of the topology.
        default_topology (:obj:`bool`): Default Topology.
        description (:obj:`str`): Topology description.
        draft (:obj:`bool`): Indicates whether this topology is a draft.
        jobs (:py:class:`streamsets.sdk.utils.SeekableList`) of (:py:class:`streamsets.sdk.sch_models.Job`):
         Jobs currently part of the topology.
        last_modified_by (:obj:`str`): User that last modified this topology.
        last_modified_on (:obj:`int`): Time at which this topology was last modified.
        new_pipeline_version_available (:obj:`bool`): Whether any job in the topology has a new pipeline version to be
            updated to.
        nodes (:py:class:`streamsets.sdk.utils.SeekableList`) of (:py:class:`streamsets.sdk.sch_models.TopologyNode`):
         Nodes currently part of the topology.
        organization (:obj:`str`): Id of the organization.
        parent_version (:obj:`str`): Version of the parent topology.
        topology_definition (:obj:`str`): Definition of the topology.
        topology_id (:obj:`str`): Id of the topology.
        topology_name (:obj:`str`): Name of the topology.
        validation_issues (:obj:`dict`): Any validation issues that exist for this Topology.
        version (:obj:`str`): Version of this topology.
    """

    _ATTRIBUTES_TO_IGNORE = ['provenanceMetaData']
    _ATTRIBUTES_TO_REMAP = {'committed_by': 'committer', 'topology_name': 'name'}
    _REPR_METADATA = ['topology_id', 'topology_name']

    def __init__(self, topology, control_hub=None):
        super().__init__(
            topology,
            attributes_to_ignore=Topology._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=Topology._ATTRIBUTES_TO_REMAP,
            repr_metadata=Topology._REPR_METADATA,
        )
        self._control_hub = control_hub
        self._topology_definition_internal = (
            json.loads(topology['topologyDefinition'])
            if isinstance(topology['topologyDefinition'], str)
            else topology['topologyDefinition']
        )
        self._validation_issues = []
        self._new_pipeline_version_map = {}
        self._new_pipeline_version_available = False

    @property
    def _data(self):
        # Check if data exists, otherwise load it
        if not self._topology_definition_internal:
            self._load_data()
        return self._data_internal

    @_data.setter
    def _data(self, data):
        self._data_internal = data

    @property
    def _topology_definition(self):
        # Check if data exists, otherwise load it
        if not self._topology_definition_internal:
            self._load_data()
        return self._topology_definition_internal

    @_topology_definition.setter
    def _topology_definition(self, topology_definition):
        self._topology_definition_internal = topology_definition

    @property
    def topology_definition(self):
        # Check if data exists, otherwise load it
        if not self._topology_definition_internal:
            self._load_data()
        return self._data_internal['topologyDefinition']

    @topology_definition.setter
    def topology_definition(self, topology_definition):
        self._topology_definition_internal = topology_definition

    def _load_data(self):
        data = self._control_hub.api_client.get_topology_for_commit_id(
            commit_id=self._data_internal['commitId'], validate=True
        ).response.json()
        self._data_internal['topologyDefinition'] = data['topology']['topologyDefinition']
        self._topology_definition_internal = json.loads(data['topology']['topologyDefinition'])

    @property
    def nodes(self):
        """Get the job and system nodes that make up the Topology.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.TopologyNode`
                instances.
        """
        return SeekableList(TopologyNode(topology_node) for topology_node in self._topology_definition['topologyNodes'])

    @property
    def jobs(self):
        """Get the jobs that are contained within the Topology.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Job` instances.
        """
        job_ids = list({job_node['jobId'] for job_node in self._get_topology_job_nodes()})
        return SeekableList(self._control_hub.jobs.get(job_id=job_id) for job_id in job_ids)

    @property
    def acl(self):
        """Get the ACL of a Topology.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(
            self._control_hub.api_client.get_topology_acl(topology_id=self.topology_id).response.json(),
            self._control_hub,
        )

    @acl.setter
    def acl(self, topology_acl):
        self._control_hub.api_client.set_topology_acl(
            topology_id=self.topology_id, topology_acl_json=topology_acl._data
        )

    @property
    def data_slas(self):
        return SeekableList(
            [
                DataSla(sla, self._control_hub)
                for sla in self._control_hub.api_client.get_data_sla(
                    organization=self._control_hub.organization, topology_commit_id=self.commit_id
                ).response.json()
            ]
        )

    @property
    def validation_issues(self):
        """Get any validation issues that are detected for the Topology.

        Returns:
            A (:obj:`list`) of validation issues in JSON format.
        """
        self._validation_issues = (
            self._control_hub.api_client.get_topology_for_commit_id(
                commit_id=self.commit_id, validate=True
            ).response.json()['issues']
            if self.commit_id is not None
            else []
        )
        return self._validation_issues

    @property
    def new_pipeline_version_available(self):
        """Determine if a new pipeline version is available for any jobs in the Topology.

        Returns:
            A (:obj:`bool`) value.
        """
        self._update_new_pipeline_version_map()
        return self._new_pipeline_version_available

    def _auto_fix_topology(self, topology, topology_definition):
        # Auto fix a topology - based off of https://git.io/J4AuC
        if self._validation_issues and len(self._validation_issues):
            for issue in self._validation_issues:
                removed_output_lanes = []
                if issue['code'] == 'TOPOLOGY_08' and issue['additionalInfo'] and issue['additionalInfo']['jobId']:
                    # The job has been updated with a new version of the pipeline
                    job_id = issue['additionalInfo']['jobId']
                    pipeline_commit_id = issue['additionalInfo']['pipelineCommitId']
                    job_node = next(
                        node
                        for node in topology_definition['topologyNodes']
                        if node['nodeType'] == 'JOB' and node['jobId'] == job_id
                    )
                    updated_pipeline = self._control_hub.api_client.get_pipeline_commit(
                        commit_id=pipeline_commit_id
                    ).response.json()
                    job_node['pipelineCommitId'] = pipeline_commit_id
                    job_node['pipelineVersion'] = updated_pipeline['version']
                    pipeline_definition = json.loads(updated_pipeline['pipelineDefinition'])
                    stage_instances = pipeline_definition['stages']

                    target_stage_instances = [
                        stage
                        for stage in stage_instances
                        if stage['uiInfo']['stageType'] == 'TARGET' or stage['uiInfo']['stageType'] == 'EXECUTOR'
                    ]

                    new_output_lanes = []
                    output_stream_labels = []
                    output_stream_texts = []

                    for count, target_stage_instance in enumerate(target_stage_instances):
                        lane_prefix = '{}:LANE:'.format(target_stage_instance['instanceName'])
                        existing_lane = next((lane for lane in job_node['outputLanes'] if lane_prefix in lane), None)
                        if existing_lane:
                            new_output_lanes.append(existing_lane)
                        else:
                            new_output_lanes.append(
                                '{}:LANE:{}{}'.format(
                                    target_stage_instance['instanceName'],
                                    int(datetime.utcnow().timestamp() * 1000),
                                    count + 1,
                                )
                            )
                        output_stream_labels.append(target_stage_instance['uiInfo']['label'])
                        output_stream_texts.append(target_stage_instance['uiInfo']['label'][0:1])

                    if 'errorStage' in pipeline_definition:
                        error_stage_instance = pipeline_definition['errorStage']
                        lane_prefix = '{}:LANE:'.format(error_stage_instance['instanceName'])
                        existing_lane = next((lane for lane in job_node['outputLanes'] if lane_prefix in lane), None)
                        if existing_lane:
                            new_output_lanes.append(existing_lane)
                        else:
                            new_output_lanes.append(
                                '{}:LANE:{}{}'.format(
                                    error_stage_instance['instanceName'],
                                    int(datetime.utcnow().timestamp() * 1000),
                                    len(target_stage_instances) + 1,
                                )
                            )
                        output_stream_labels.append(error_stage_instance['uiInfo']['label'])
                        output_stream_texts.append(error_stage_instance['uiInfo']['label'][0:1])

                    for output_lane in job_node['outputLanes']:
                        if output_lane not in new_output_lanes:
                            removed_output_lanes.append(output_lane)

                    job_node['outputLanes'] = new_output_lanes
                    job_node['uiInfo']['outputStreamLabels'] = output_stream_labels
                    job_node['uiInfo']['outputStreamTexts'] = output_stream_texts
                elif issue['code'] == 'TOPOLOGY_06' and issue['additionalInfo'] and issue['additionalInfo']['jobId']:
                    # The job has been removed, so remove the node
                    job_id = issue['additionalInfo']['jobId']
                    node_index = next(
                        (
                            index
                            for index, node in enumerate(topology_definition['topologyNodes'])
                            if node['nodeType'] == 'JOB' and node['jobId'] == job_id
                        ),
                        None,
                    )
                    if node_index is not None:
                        deleted_job_node = topology_definition['topologyNodes'][node_index]
                        del topology_definition['topologyNodes'][node_index]
                        removed_output_lanes.extend(deleted_job_node['outputLanes'])

                # Remove lanes in removed_output_lanes from all nodes that had them as input_lanes
                if len(removed_output_lanes):
                    for node in topology_definition['topologyNodes']:
                        new_input_lanes = [
                            input_lane for input_lane in node['inputLanes'] if input_lane not in removed_output_lanes
                        ]
                        node['inputLanes'] = new_input_lanes
                # Save the topology
                topology['topologyDefinition'] = json.dumps(topology_definition)
                job_nodes = [
                    topology_node
                    for topology_node in topology_definition['topologyNodes']
                    if topology_node['nodeType'] == 'JOB'
                ]
                if len(job_nodes) > 0:
                    self._update_new_pipeline_version_map()
                return self._control_hub.api_client.update_topology(
                    commit_id=topology['commitId'], topology_json=topology
                )

    def _different_job_nodes(self, jobs, pipelines_map):
        # Treat nodes as standalone entities, ignoring connections - Based off of https://git.io/JR9Xz
        nodes = []
        stage_icons = {}
        x_pos = 100
        max_y_pos = y_pos = 50
        prefix = 0

        for job in jobs:
            pipeline = pipelines_map[job.pipeline_commit_id]
            pipeline_definition = pipeline['pipelineDefinition']
            prefix += 1
            job_nodes = get_topology_nodes([job], pipeline, pipeline_definition, x_pos, y_pos, postfix=prefix)
            for node in job_nodes:
                nodes.append(node)
                max_y_pos = node['uiInfo']['yPos'] if node['uiInfo']['yPos'] >= max_y_pos else max_y_pos
            y_pos = max_y_pos + 150 if max_y_pos > 50 else 50
        return nodes, stage_icons if len(stage_icons) else self._topology_definition['stageIcons']

    def _get_topology_job_nodes(self):
        # Get the Job nodes in a Topology - based off of https://bit.ly/2M6sPLv
        if self._topology_definition is not None:
            return [
                topology_node
                for topology_node in self._topology_definition['topologyNodes']
                if topology_node['nodeType'] == 'JOB'
            ]
        else:
            return []

    def _on_update_to_latest(self):
        # Upgrade a topology's jobs to the latest pipeline change - based off of https://git.io/JBuUc
        jobs_to_update = []
        for topology_node in self._topology_definition['topologyNodes']:
            if topology_node['nodeType'] == 'JOB':
                latest_pipeline = self._new_pipeline_version_map[topology_node['pipelineId']]
                if latest_pipeline and latest_pipeline['commitId'] != topology_node['pipelineCommitId']:
                    jobs_to_update.append(topology_node['jobId'])
        self._control_hub.api_client.upgrade_jobs(jobs_to_update)

    def _refresh(self):
        # Refresh a topology's data representation with the most current
        self._data = self._control_hub.api_client.get_topology_for_commit_id(commit_id=self.commit_id).response.json()
        self._topology_definition = (
            json.loads(self._data['topologyDefinition'])
            if isinstance(self._data['topologyDefinition'], str)
            else self._data['topologyDefinition']
        )

    def _update_new_pipeline_version_map(self):
        # Map new pipeline versions to job nodes - based off of https://git.io/JBuJI
        pipelines = []
        pipeline_version_map = {}
        job_nodes = self._get_topology_job_nodes()
        if len(job_nodes):
            for node in job_nodes:
                pipelines.append(
                    self._control_hub.api_client.get_latest_pipeline_commit(
                        pipeline_id=node['pipelineId']
                    ).response.json()
                )
            if len(pipelines):
                for pipeline in pipelines:
                    pipeline_version_map[pipeline['pipelineId']] = pipeline
                for node in job_nodes:
                    new_version_pipeline = pipeline_version_map[node['pipelineId']]
                    self._new_pipeline_version_available = self._new_pipeline_version_available or (
                        new_version_pipeline and new_version_pipeline['commitId'] != node['pipelineCommitId']
                    )
        self._new_pipeline_version_map = pipeline_version_map

    def add_data_sla(self, data_sla):
        """Add SLA.

        Args:
            data_sla (:py:class:`streamsets.sdk.sch_models.DataSla`): Data SLA object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        cmd = self._control_hub.api_client.add_data_sla(data_sla._data)
        data_sla._data = cmd.response.json()
        return cmd

    def activate_data_sla(self, *data_slas):
        """Activate Data SLAs.

        Args:
            *data_slas: One or more instances of :py:class:`streamsets.sdk.sch_models.DataSla`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        cmd = self._control_hub.api_client.activate_data_sla([data_sla.id for data_sla in data_slas])
        for data_sla in data_slas:
            data_sla._refresh()
        return cmd

    def deactivate_data_sla(self, *data_slas):
        """Deactivate Data SLAs.

        Args:
            *data_slas: One or more instances of :py:class:`streamsets.sdk.sch_models.DataSla`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        cmd = self._control_hub.api_client.deactivate_data_sla([data_sla.id for data_sla in data_slas])
        for data_sla in data_slas:
            data_sla._refresh()
        return cmd

    def delete_data_sla(self, *data_slas):
        """Delete Data SLAs.

        Args:
            *data_slas: One or more instances of :py:class:`streamsets.sdk.sch_models.DataSla`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.delete_data_sla([data_sla.id for data_sla in data_slas])

    def acknowledge_job_errors(self):
        """Acknowledge all errors for the jobs in a topology.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        job_ids = list({job_node['jobId'] for job_node in self._get_topology_job_nodes()})
        return self._control_hub.api_client.jobs_acknowledge_errors(job_ids)

    def start_all_jobs(self):
        """Start all jobs of a topology.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        job_ids = list({job_node['jobId'] for job_node in self._get_topology_job_nodes()})
        response = self._control_hub.api_client.start_jobs(job_ids)
        for job_id in job_ids:
            self._control_hub.api_client.wait_for_job_status(job_id=job_id, status='ACTIVE')
        return response

    def stop_all_jobs(self, force=False):
        """Stop all jobs of a topology.

        Args:
            force (:obj:`bool`, optional): Force topology jobs to stop. Default: ``False``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        job_ids = list({job_node['jobId'] for job_node in self._get_topology_job_nodes()})
        if force:
            response = self._control_hub.api_client.force_stop_jobs(job_ids)
        else:
            response = self._control_hub.api_client.stop_jobs(job_ids)
        for job_id in job_ids:
            self._control_hub.api_client.wait_for_job_status(job_id=job_id, status='INACTIVE')
        return response

    def update_jobs_to_latest_change(self):
        """Upgrade a topology's job(s) to the latest corresponding pipeline change.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        # Based off of https://git.io/J4AtD
        if self.commit_id:
            self._update_new_pipeline_version_map()
            if self._new_pipeline_version_available:
                self._on_update_to_latest()
                return self.auto_fix()

    def auto_fix(self):
        """Auto-fix a topology by rectifying invalid or removed jobs, outdated jobs, etc.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        # Based off of https://git.io/J4AGv
        if self.commit_id:
            validated_topology = self._control_hub.api_client.get_topology_for_commit_id(
                commit_id=self.commit_id, validate=True
            ).response.json()
            self._data = validated_topology['topology'] if validated_topology['topology'] is not None else self._data
            self._validation_issues = validated_topology['issues']
            self._new_pipeline_version_available = False
            if self._validation_issues:
                if not self.draft:
                    self._data = self._control_hub.api_client.create_topology_draft(
                        commit_id=self.commit_id
                    ).response.json()
                response = self._auto_fix_topology(self._data, self._topology_definition)
                self._refresh()
                return response

    def auto_discover_connections(self):
        """Auto discover connecting systems between nodes in a Topology.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        # Based off of https://git.io/JRKmU
        pipelines_map = {}
        pipeline_commit_id_list = []
        job_id_list = []
        jobs = self.jobs

        for job in jobs:
            if job.job_id not in job_id_list:
                job_id_list.append(job.job_id)
                if job.pipeline_commit_id not in pipeline_commit_id_list:
                    pipeline_commit_id_list.append(job.pipeline_commit_id)
        pipelines = self._control_hub.api_client.get_pipelines_commit(body=pipeline_commit_id_list).response.json()
        for pipeline in pipelines:
            pipeline['pipelineDefinition'] = json.loads(pipeline['pipelineDefinition'])
            pipeline['libraryDefinitions'] = json.loads(pipeline['libraryDefinitions'])
            pipelines_map[pipeline['commitId']] = pipeline

        new_topology_nodes, new_stage_icons = self._different_job_nodes(jobs, pipelines_map)
        if not self.draft:
            self._data = self._control_hub.api_client.create_topology_draft(commit_id=self.commit_id).response.json()
        # Based off of https://git.io/JR9SI
        new_topology_definition = json.loads(self._data['topologyDefinition'])
        new_topology_definition['topologyNodes'] = new_topology_nodes
        new_topology_definition['stageIcons'] = new_stage_icons
        self._data['topologyDefinition'] = json.dumps(new_topology_definition)
        response = self._control_hub.api_client.update_topology(
            commit_id=self._data['commitId'], topology_json=self._data
        )
        self._refresh()
        return response


@analytics_class_decorator
class Topologies(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Topology` instances.
    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): An instance of the ControlHub.
    """

    def __init__(self, control_hub):
        super().__init__(control_hub)
        self._id_attr = 'topology_id'

    def _get_all_results_from_api(self, commit_id=None, organization=None, **kwargs):
        """Args offset, len_, order_by, order are not exposed directly as arguments because of their limited use by
        normal users but, could still be specified just like any other args with the help of kwargs.
        Args:
            commit_id (:obj:`str`, optional): Topology commit ID. Default: ``None``.
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            **kwargs: Optional other arguments to be passed to filter the results offline.
        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Topology` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Topology`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order_by': 'LAST_MODIFIED_TIME', 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.return_all_topologies(
            organization=organization,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            order_by=kwargs_unioned['order_by'],
            order=kwargs_unioned['order'],
            with_wrapper=True,
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Topology, {'control_hub': self._control_hub})


class DataSla(BaseModel):
    """Model for DataSla.

    Args:
        data_sla (:obj:`dict`): JSON representation of SLA.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): An instance of the Control Hub.
    """

    _ATTRIBUTES_TO_REMAP = {'status': 'slaStatus'}
    _REPR_METADATA = ['label', 'last_modified_on', 'status']

    def __init__(self, data_sla, control_hub):
        super().__init__(
            data_sla, attributes_to_remap=DataSla._ATTRIBUTES_TO_REMAP, repr_metadata=DataSla._REPR_METADATA
        )
        self._control_hub = control_hub

    def _refresh(self):
        topology = self._control_hub.topologies.get(commit_id=self.topology_commit_id)
        self._data = topology.data_slas.get(id=self.id)._data


class DataSlaBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.DataSla`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_data_sla_builder`.

    Args:
        data_sla (:obj:`dict`): Python object built from our Swagger DataSlaJson definition.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): An instance of the Control Hub.
    """

    def __init__(self, data_sla, control_hub):
        self._data_sla = data_sla
        self._control_hub = control_hub

    def build(
        self,
        topology,
        label,
        job,
        alert_text,
        qos_parameter='THROUGHPUT_RATE',
        function_type='Max',
        min_max_value=100,
        enabled=True,
    ):
        """Build the Data Sla.

        Args:
            topology (:py:class:`streamsets.sdk.sch_models.Topology`): Topology object.
            label (:obj:`str`): Label for the SLA.
            job (:obj:`list`): List of :py:class:`streamsets.sdk.sch_models.Job` objects.
            alert_text (:obj:`str`): Alert text.
            qos_parameter (:obj:`str`, optional): paramter in {'THROUGHPUT_RATE', 'ERROR_RATE'}.
                Default: ``'THROUGHPUT_RATE'``.
            function_type (:obj:`str`, optional): paramter in {'Max', 'Min'}. Default: ``'Max'``.
            min_max_value (:obj:`str`, optional): Default: ``100``.
            enabled (:obj:`boolean`, optional): Default: ``True``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.DataSla`.
        """
        sla_definition = json.dumps(
            {
                'enabled': enabled,
                'qosParameter': qos_parameter,
                'slaConditions': [{'slaFunctionType': function_type.upper(), 'value': min_max_value}],
                'jobIds': [job.job_id],
                'alertText': alert_text,
            }
        )
        self._data_sla.update(
            {
                'label': label,
                'topologyCommitId': topology.commit_id,
                'topologyId': topology.topology_id,
                'slaDefinition': sla_definition,
            }
        )
        return DataSla(data_sla=self._data_sla, control_hub=self._control_hub)


class ClassificationRule(UiMetadataBaseModel):
    """Classification Rule Model.

    Args:
        classification_rule (:obj:`dict`): A Python dict representation of classification rule.
        classifiers (:obj:`list`): A list of :py:class:`streamsets.sdk.sch_models.Classifier` instances.
    """

    _ATTRIBUTES_TO_IGNORE = ['classifiers']
    _ATTRIBUTES_TO_REMAP = {}

    def __init__(self, classification_rule, classifiers):
        super().__init__(
            classification_rule,
            attributes_to_ignore=ClassificationRule._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=ClassificationRule._ATTRIBUTES_TO_REMAP,
        )
        self.classifiers = classifiers


class Classifier(UiMetadataBaseModel):
    """Classifier model.

    Attributes:
        patterns (:obj:`str`): Classifier patterns.

    Args:
        classifier (:obj:`dict`): A Python dict representation of classifier.
    """

    _ATTRIBUTES_TO_IGNORE = ['patterns']
    _ATTRIBUTES_TO_REMAP = {
        'case_sensitive': 'sensitive',
        'match_with': 'type',
        'regular_expression_type': 'implementationClassValue',
    }

    # From https://git.io/fA0w2.
    MATCH_WITH_ENUM = {'Field Path': 'FIELD_PATH', 'Field Value': 'FIELD_VALUE'}

    # From https://git.io/fA0w4.
    REGULAR_EXPRESSION_TYPE_ENUM = {'RE2/J': 'RE2J_MATCHER', 'Java Regular Expression': 'REGEX_MATCHER'}

    def __init__(self, classifier):
        super().__init__(
            classifier,
            attributes_to_ignore=Classifier._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=Classifier._ATTRIBUTES_TO_REMAP,
        )

    @property
    def patterns(self):
        return [pattern['value'] for pattern in self._data['patterns']]

    @patterns.setter
    def patterns(self, values):
        self._data['patterns'] = [
            {'messages': [], 'type': 'RSTRING', 'value': value, 'scrubbed': False} for value in values
        ]

    @property
    def _id(self):
        return self._data['id']

    @_id.setter
    def _id(self, value):
        self._data['id'] = value

    @property
    def _rule_uuid(self):
        return self._data['ruleUuid']

    @_rule_uuid.setter
    def _rule_uuid(self, value):
        self._data['ruleUuid'] = value

    @property
    def _uuid(self):
        return self._data['uuid']

    @_uuid.setter
    def _uuid(self, value):
        self._data['uuid'] = value


@analytics_class_decorator
class Environment(BaseModel, metaclass=ABCMeta):
    """Model for Environment. This is an abstract class.

    Attributes:
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): Environment ACL.
        tags (:py:class:`streamsets.sdk.utils.SeekableList` of :obj:`str` instances): Environment tags.
        allow_nightly_engine_builds (:obj:`bool`): Whether or not the environment allows use of nightly engine build.
        created_by (:obj:`str`): User that created this environment.
        created_on (:obj:`int`): Time at which this environment was created.
        environment_id (:obj:`str`): Id of the environment.
        environment_name (:obj:`str`): Name of the environment.
        environment_tags (:obj:`list`): Raw environment tags of the environment.
        environment_type (:obj:`str`): Type of the environment.
        last_modified_by (:obj:`str`): User that last modified this environment.
        last_modified_on (:obj:`int`): Time at which this environment was last modified.
        json_state (:obj:`str`): State of the environment - which is stored in json field called state.
        state (:obj:`str`): State of the environment stateDisplayLabel - shown on the UI as state.
        status (:obj:`str`): Status of the environment.
        status_detail (:obj:`str`): Status detail of the environment.
    """

    _ATTRIBUTES_TO_IGNORE = ['environmentTags', 'userProvided', 'organization', 'statusLastUpdated']
    _ATTRIBUTES_TO_REMAP = {
        'allow_nightly_engine_builds': 'allowSnapshotEngineVersions',
        'created_by': 'creator',
        'created_on': 'createTime',
        'environment_id': 'id',
        'environment_name': 'name',
        'environment_tags': 'rawEnvironmentTags',
        'environment_type': 'type',
        'state': 'stateDisplayLabel',
        'json_state': 'state',
    }
    _REPR_METADATA = ['environment_id', 'environment_name', 'environment_type', 'state']

    class TYPES(enum.Enum):
        AZURE = 'AZURE'
        AWS = 'AWS'
        GCP = 'GCP'
        KUBERNETES = 'KUBERNETES'
        SELF = 'SELF'

    def __init__(
        self, environment, control_hub=None, attributes_to_ignore=None, attributes_to_remap=None, repr_metadata=None
    ):
        attributes_to_ignore = attributes_to_ignore or []
        attributes_to_remap = attributes_to_remap or {}
        repr_metadata = repr_metadata or []
        super().__init__(
            environment,
            attributes_to_ignore=Environment._ATTRIBUTES_TO_IGNORE + attributes_to_ignore,
            attributes_to_remap={**Environment._ATTRIBUTES_TO_REMAP, **attributes_to_remap},
            repr_metadata=Environment._REPR_METADATA + repr_metadata,
        )
        self._control_hub = control_hub

    def __new__(cls, environment, control_hub=None, **kwargs):
        if environment['type'] == 'SELF':
            return super().__new__(SelfManagedEnvironment)
        elif environment['type'] == 'AWS':
            return super().__new__(AWSEnvironment)
        elif environment['type'] == 'AZURE':
            return super().__new__(AzureEnvironment)
        elif environment['type'] == 'GCP':
            return super().__new__(GCPEnvironment)
        elif environment['type'] == 'KUBERNETES':
            return super().__new__(KubernetesEnvironment)
        else:
            return super().__new__(NotImplementedEnvironment)

    def refresh(self):
        self._data = self._control_hub.api_client.get_environment(self.environment_id).response.json()

    @property
    def acl(self):
        """Get environment ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        if isinstance(self, NotImplementedEnvironment):
            raise NotImplementedError("Cannot get ACL for NotImplementedEnvironment class")
        return ACL(
            self._control_hub.api_client.get_environment_acl(environment_id=self.environment_id).response.json(),
            self._control_hub,
        )

    @acl.setter
    def acl(self, environment_acl):
        """Update environment ACL.

        Args:
            environment_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The environment ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        if isinstance(self, NotImplementedEnvironment):
            raise NotImplementedError("Cannot set ACL for NotImplementedEnvironment class")
        return self._control_hub.api_client.set_environment_acl(
            environment_id=self.environment_id, environment_acl_json=environment_acl._data
        )

    @property
    def tags(self):
        """Get the tags.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :obj:`str` instances.
        """
        env_tags = self._data.get('environmentTags', []) or []
        if not env_tags:
            raw_env_tags = self._data.get('rawEnvironmentTags', []) or []
            if raw_env_tags:
                organization = self._control_hub.organization
                env_tags = [build_tag_from_raw_tag(raw_tag, organization) for raw_tag in raw_env_tags]
                self._data['environmentTags'] = env_tags
        return SeekableList(tag['tag'] for tag in env_tags)

    @tags.setter
    def tags(self, tags):
        """Update an Environment object's tags.

        Args:
            tags: A :obj:`list` of one or more :obj:`str` instances.
        """
        if not isinstance(tags, list):
            raise ValueError('The tag(s) provided must be in a list.')
        elif isinstance(self, NotImplementedEnvironment):
            raise NotImplementedError("Cannot set tags for NotImplementedEnvironment class")
        self._data['environmentTags'] = []
        self._data['rawEnvironmentTags'] = tags
        for tag in tags:
            tag_json = build_tag_from_raw_tag(tag, self._control_hub.organization)
            self._data['environmentTags'].append(tag_json)

    def complete(self):
        result = self.environment_name is not None and self.environment_type is not None
        if result:
            result = self.is_complete()
        return result

    def is_complete(self):
        raise NotImplementedError('Method not implemented by class {}'.format(self.__class__))


class NotImplementedEnvironment(Environment):
    """Model for a Environments not yet supported."""

    def __init__(self, environment, control_hub=None):
        super().__init__(environment, control_hub)

    def is_complete(self):
        return True


class SelfManagedEnvironment(Environment):
    """Model for Self Managed Environment."""

    def __init__(self, environment, control_hub=None):
        super().__init__(environment, control_hub)

    def is_complete(self):
        return True


@analytics_class_decorator
class AWSEnvironment(Environment):
    """Model for AWS Environment.

    Attributes:
        access_key_id (:obj:`str`): AWS access key id to access AWS account. Required when credential_type is
            AWS_STATIC_KEYS.
        aws_tags (:obj:`dict`): AWS tags to apply to all provisioned resources in this AWS deployment.
        credentials (:obj:`dict`): Credentials of the environment.
        credential_type (:obj:`str`): Credential Type of the environment.
        default_instance_profile (:obj:`dict`): aarn of default instance profile created as an environment prerequisite.
        region (:obj:`str`): AWS region where VPC is located in case of AWS environment.
        role_arn (:obj:`str`): Role AR of the cross-account role created as an environment prerequisite in
            user's AWS account. Required when credential_type is AWS_CROSS_ACCOUNT_ROLE.
        secret_access_key (:obj:`str`): AWS secret access key to access AWS account. Required when credential_type
            is AWS_STATIC_KEYS.
        subnet_ids (:obj:`str`): Range of Subnet IDs in the VPC.
        security_group_id (:obj:`str`): Security group ID.
        vpc_id (:obj:`str`): Id of the Amazon VPC created as an environment prerequisite in user's AWS account.
    """

    _ATTRIBUTES_TO_REMAP = {
        'credential_type': 'credentialsType',
        'default_instance_profile': 'defaultInstanceProfileArn',
    }
    # Internal value
    CREDENTIALS_TYPE_ACCCESS_KEYS = 'AWS_STATIC_KEYS'
    CREDENTIALS_TYPE_CROSS_ACCOUNT_ROLE = 'AWS_CROSS_ACCOUNT_ROLE'
    # UI shows following way
    CREDENTIALS_TYPE_ACCCESS_KEYS_FROM_UI = 'Access Keys'
    CREDENTIALS_TYPE_CROSS_ACCOUNT_ROLE_FROM_UI = 'Cross-Account Role'

    def __init__(self, environment, control_hub=None):
        super().__init__(environment, control_hub=control_hub, attributes_to_remap=AWSEnvironment._ATTRIBUTES_TO_REMAP)
        command = self._control_hub.api_client.get_aws_external_id(organization=self._control_hub.organization)
        self._external_id = command.response.json()['name']

    @property
    def aws_tags(self):
        if self._data['resourceTags'] is not None:
            # Extract the tags out of 'key=value,key=value' format into [[key, value], [key, value]] format
            tag_pairs = [pair.split('=') for pair in self._data['resourceTags'].split(',')]
            return {key: value for [key, value] in tag_pairs}
        return None

    @aws_tags.setter
    def aws_tags(self, tags):
        """Update the aws_tags.

        Args:
            tags (:obj:`dict`): One or more tags to be set, in key/value pairs.
        """
        if tags is not None:
            if not isinstance(tags, dict):
                raise ValueError('The tag(s) provided must be within a dictionary.')
            self._data['resourceTags'] = ','.join('{}={}'.format(key, value) for key, value in tags.items())

    @property
    def credential_type(self):
        return self._data['credentialsType']

    @property
    def credentials(self):
        return self._data['credentials']

    @property
    def role_arn(self):
        return json.loads(self.credentials)['roleArn']

    @role_arn.setter
    def role_arn(self, role_arn):
        """Internally it updates the credentials with role_arn"""
        if self.credential_type != AWSEnvironment.CREDENTIALS_TYPE_CROSS_ACCOUNT_ROLE_FROM_UI:
            error_message = 'Setting role_arn is not available for credential type other than {}'
            raise ValueError(error_message.format(AWSEnvironment.CREDENTIALS_TYPE_CROSS_ACCOUNT_ROLE_FROM_UI))
        credentials_data = self._data.get('credentials', None)
        if credentials_data is None:
            credentials = {'externalId': self._external_id}
        else:
            credentials = json.loads(credentials_data)
        credentials.update({'roleArn': role_arn})
        self._data['credentials'] = json.dumps(credentials)

    @property
    def access_key_id(self):
        return json.loads(self.credentials)['accessKeyId']

    @access_key_id.setter
    def access_key_id(self, access_key_id):
        """Internally it updates the credentials with access_key_id"""
        if self.credential_type not in [
            AWSEnvironment.CREDENTIALS_TYPE_ACCCESS_KEYS,
            AWSEnvironment.CREDENTIALS_TYPE_ACCCESS_KEYS_FROM_UI,
        ]:
            error_message = 'Setting role_arn is not available for credential type other than {}'
            raise ValueError(error_message.format(AWSEnvironment.CREDENTIALS_TYPE_ACCCESS_KEYS_FROM_UI))
        credentials_data = self._data.get('credentials', None)
        credentials = json.loads(credentials_data) if credentials_data is not None else {}
        credentials.update({'accessKeyId': access_key_id})
        self._data['credentials'] = json.dumps(credentials)

    @property
    def secret_access_key(self):
        return json.loads(self.credentials)['secretAccessKey']

    @secret_access_key.setter
    def secret_access_key(self, secret_access_key):
        """Internally it sets up the credentials with secret_access_key"""
        if self.credential_type not in [
            AWSEnvironment.CREDENTIALS_TYPE_ACCCESS_KEYS,
            AWSEnvironment.CREDENTIALS_TYPE_ACCCESS_KEYS_FROM_UI,
        ]:
            error_message = ('Setting secret_access_key is not available for credential type other than {}',)
            raise ValueError(error_message.format(AWSEnvironment.CREDENTIALS_TYPE_ACCCESS_KEYS_FROM_UI))
        credentials_data = self._data.get('credentials', None)
        credentials = json.loads(credentials_data) if credentials_data is not None else {}
        credentials.update({'secretAccessKey': secret_access_key})
        self._data['credentials'] = json.dumps(credentials)

    @staticmethod
    def get_ui_value_mappings():
        """This method returns a map for the values shown in the UI and internal constants to be used."""
        return {
            'credentialsType': {
                AWSEnvironment.CREDENTIALS_TYPE_ACCCESS_KEYS_FROM_UI: AWSEnvironment.CREDENTIALS_TYPE_ACCCESS_KEYS,
                AWSEnvironment.CREDENTIALS_TYPE_CROSS_ACCOUNT_ROLE_FROM_UI: AWSEnvironment.CREDENTIALS_TYPE_CROSS_ACCOUNT_ROLE,
            }
        }

    def is_complete(self):
        """Checks if all required fields are set in this environment."""
        result = self.credentials
        if result:
            if self.credential_type == AWSEnvironment.CREDENTIALS_TYPE_ACCCESS_KEYS_FROM_UI:
                result = self.secret_access_key is not None and self.access_key_id is not None
            elif self.credential_type == AWSEnvironment.CREDENTIALS_TYPE_CROSS_ACCOUNT_ROLE_FROM_UI:
                result = self.role_arn is not None
            if result:
                result = (
                    self.region is not None
                    and self.vpc_id is not None
                    and self.subnet_ids != []
                    and self.security_group_id is not None
                )
        return result


class AzureEnvironment(Environment):
    """Model for Azure Environment.

    Attributes:
        azure_tags (:obj:`dict`): Azure tags for this environment.
        credential_type (:obj:`str`): Credential type of the environment.
        client_id (:obj:`str`): Client ID of the environment.
        client_secret (:obj:`str`): Client Secret of the environment.
        credentials (:obj:`dict`): Credentials of the environment.
        default_managed_identity (:obj:`str`): default managed identity.
        default_resource_group (:obj:`str`): default resource group.
        region (:obj:`str`):  Azure region where vnet is located.
        subnet_id (:obj:`str`): Subnet ID in the vnet.
        subscription_id (:obj:`str`): Subscription ID in the vnet.
        security_group_id (:obj:`str`): Security group ID.
        tenet_id (:obj:`str`): Tenet ID of the environment.
        vnet_id (:obj:`str`): Id of the vnet.
    """

    _ATTRIBUTES_TO_REMAP = {'credential_type': 'credentialsType', 'vnet_id': 'vpcId'}
    # Internal value
    CREDENTIALS_TYPE_CLIENT_SECRET = 'AZURE_SVC_PRINCIPAL_CLIENT_SECRET'
    # UI shows following way
    CREDENTIALS_TYPE_CLIENT_SECRET_FROM_UI = 'Service Principal Client Secret'

    def __init__(self, environment, control_hub=None):
        super().__init__(
            environment, control_hub=control_hub, attributes_to_remap=AzureEnvironment._ATTRIBUTES_TO_REMAP
        )

    @property
    def azure_tags(self):
        if self._data['resourceTags'] is not None:
            # Extract the tags out of 'key=value,key=value' format into [[key, value], [key, value]] format
            tag_pairs = [pair.split('=') for pair in self._data['resourceTags'].split(',')]
            return {key: value for [key, value] in tag_pairs}
        return None

    @azure_tags.setter
    def azure_tags(self, tags):
        """Update the azure_tags.

        Args:
            tags (:obj:`dict`): One or more tags to be set, in key/value pairs.
        """
        if tags is not None:
            if not isinstance(tags, dict):
                raise ValueError('The tag(s) provided must be within a dictionary.')
            self._data['resourceTags'] = ','.join('{}={}'.format(key, value) for key, value in tags.items())

    @property
    def credential_type(self):
        return self._data['credentialsType']

    @credential_type.setter
    def credential_type(self, credential_type):
        if credential_type == AzureEnvironment.CREDENTIALS_TYPE_CLIENT_SECRET_FROM_UI:
            self._data['credentialsType'] = AzureEnvironment.CREDENTIALS_TYPE_CLIENT_SECRET_FROM_UI
        else:
            raise ValueError('Only valid value for the credential_type is Service Principal Client Secret')

    @property
    def credentials(self):
        return self._data['credentials']

    @property
    def client_id(self):
        return json.loads(self.credentials)['clientId']

    @client_id.setter
    def client_id(self, client_id):
        """Internally it updates the credentials with client_id"""
        credentials_data = self._data.get('credentials', None)
        credentials = json.loads(credentials_data) if credentials_data is not None else {}
        credentials.update({'clientId': client_id})
        self._data['credentials'] = json.dumps(credentials)

    @property
    def client_secret(self):
        return json.loads(self.credentials)['clientSecret']

    @client_secret.setter
    def client_secret(self, client_secret):
        """Internally it updates the credentials with client_secret"""
        credentials_data = self._data.get('credentials', None)
        credentials = json.loads(credentials_data) if credentials_data is not None else {}
        credentials.update({'clientSecret': client_secret})
        self._data['credentials'] = json.dumps(credentials)

    @property
    def tenant_id(self):
        return json.loads(self.credentials)['tenantId']

    @tenant_id.setter
    def tenant_id(self, tenant_id):
        """Internally it updates the credentials with tenant_id"""
        credentials_data = self._data.get('credentials', None)
        credentials = json.loads(credentials_data) if credentials_data is not None else {}
        credentials.update({'tenantId': tenant_id})
        self._data['credentials'] = json.dumps(credentials)

    @property
    def subscription_id(self):
        return json.loads(self.credentials)['subscriptionId']

    @subscription_id.setter
    def subscription_id(self, subscription_id):
        """Internally it updates the credentials with subscription_id"""
        credentials_data = self._data.get('credentials', None)
        credentials = json.loads(credentials_data) if credentials_data is not None else {}
        credentials.update({'subscriptionId': subscription_id})
        self._data['credentials'] = json.dumps(credentials)

    def is_complete(self):
        """Checks if all required fields are set in this environment."""
        return all(
            [
                self.credentials,
                self.client_id,
                self.client_secret,
                self.tenant_id,
                self.subscription_id,
                self.region,
                self.vnet_id,
                self.subnet_id,
                self.security_group_id,
            ]
        )

    @staticmethod
    def get_ui_value_mappings():
        """This method returns a map for the values shown in the UI and internal constants to be used."""
        return {
            'credentialsType': {
                AzureEnvironment.CREDENTIALS_TYPE_CLIENT_SECRET_FROM_UI: AzureEnvironment.CREDENTIALS_TYPE_CLIENT_SECRET
            }
        }


@analytics_class_decorator
class GCPEnvironment(Environment):
    """Model for GCP Environment.

    Attributes:
        credentials (:obj:`dict`): Credentials of the environment.
        account_key_json (:obj:`str`): JSON file contents for the Service Account Key. Required when credential_type
            is GCP_SERVICE_ACCOUNT_KEY.
        project (:obj:`str`): Project where VPC is located.
        gcp_labels (:obj:`dict`): GCP labels for this environment.
        gcp_tags (:obj:`str`): GCP tags to apply to all resources provisioned in GCP account.
        service_account_email (:obj:`str`): Service account ID. Required when credential_type is
            GCP_SERVICE_ACCOUNT_IMPERSONATION.
        vpc_id (:obj:`str`): Id of the GCP VPC created as an environment prerequisite in user's GCP account.
    """

    _ATTRIBUTES_TO_REMAP = {
        'credential_type': 'credentialsType',
        'project': 'projectId',
        'service_account_name': 'externalId',
    }
    # Internal value
    CREDENTIALS_TYPE_SERVICE_ACCOUNT_IMPERSONATION = 'GCP_SERVICE_ACCOUNT_IMPERSONATION'
    CREDENTIALS_TYPE_SERVICE_ACCOUNT_KEY = 'GCP_SERVICE_ACCOUNT_KEY'
    # Internal value
    CREDENTIALS_TYPE_SERVICE_ACCOUNT_IMPERSONATION_FROM_UI = 'Service Account Impersonation'
    CREDENTIALS_TYPE_SERVICE_ACCOUNT_KEY_FROM_UI = 'Service Account Key'

    def __init__(self, environment, control_hub=None):
        super().__init__(environment, control_hub=control_hub, attributes_to_remap=GCPEnvironment._ATTRIBUTES_TO_REMAP)
        command = self._control_hub.api_client.get_gcp_external_id(organization=self._control_hub.organization)
        self._service_account_name = command.response.json()['name']

    @property
    def credentials(self):
        return self._data['credentials']

    @property
    def service_account_email(self):
        return json.loads(self.credentials)['serviceAccountEmail']

    @service_account_email.setter
    def service_account_email(self, service_account_email):
        """Internally it updates the credentials with service_account_email"""
        if self.credential_type != GCPEnvironment.CREDENTIALS_TYPE_SERVICE_ACCOUNT_IMPERSONATION_FROM_UI:
            message = 'Setting service_account_email is not available for credential type other than {}'
            raise ValueError(message.format(GCPEnvironment.CREDENTIALS_TYPE_SERVICE_ACCOUNT_IMPERSONATION_FROM_UI))
        credentials_data = self._data.get('credentials', None)
        if credentials_data is None:
            credentials = {'externalId': self._service_account_name}
        else:
            credentials = json.loads(credentials_data)
        credentials.update({'serviceAccountEmail': service_account_email})
        self._data['credentials'] = json.dumps(credentials)

    @property
    def account_key_json(self):
        return json.loads(self.credentials)['accountKeyJson']

    @account_key_json.setter
    def account_key_json(self, account_key_json):
        """Internally it updates the credentials with account_key_json"""
        if self.credential_type != GCPEnvironment.CREDENTIALS_TYPE_SERVICE_ACCOUNT_KEY_FROM_UI:
            message = 'Setting account_key_json is not available for credential type other than {}'
            raise ValueError(message.format(GCPEnvironment.CREDENTIALS_TYPE_SERVICE_ACCOUNT_KEY_FROM_UI))
        credentials_data = self._data.get('credentials', None)
        credentials = json.loads(credentials_data) if credentials_data is not None else {}
        credentials.update({'accountKeyJson': account_key_json})
        self._data['credentials'] = json.dumps(credentials)

    @property
    def gcp_labels(self):
        if self._data['resourceLabels'] is not None:
            # Extract the labels out of 'key=value,key=value' format into [[key, value], [key, value]] format
            label_pairs = [pair.split('=') for pair in self._data['resourceLabels'].split(',')]
            return {key: value for [key, value] in label_pairs}
        return None

    @gcp_labels.setter
    def gcp_labels(self, labels):
        """Update the gcp_labels.

        Args:
            labels (:obj:`dict`): One or more labels to be set, in key/value pairs.
        """
        if labels is not None:
            if not isinstance(labels, dict):
                raise ValueError('The label(s) provided must be within a dictionary.')
            self._data['resourceLabels'] = ','.join('{}={}'.format(key, value) for key, value in labels.items())

    def is_complete(self):
        """Checks if all required fields are set in this environment."""
        result = self.credentials
        if result:
            if self.credential_type == GCPEnvironment.CREDENTIALS_TYPE_SERVICE_ACCOUNT_KEY_FROM_UI:
                result = self.account_key_json
            elif self.credential_type == GCPEnvironment.CREDENTIALS_TYPE_SERVICE_ACCOUNT_IMPERSONATION_FROM_UI:
                result = self.service_account_email
            if result:
                result = self.project is not None and self.vpc_id is not None
        return result

    def fetch_available_projects(self):
        """Returns the available projects for the given Environment."""
        return self._control_hub.api_client.get_gcp_environment_projects(self.environment_id).response.json()

    def fetch_available_vpcs(self):
        """Returns the available Networks for the given Environment and GCP Project.
        Here it is called vpcs since on UI it is shown as VPC."""
        command = self._control_hub.api_client.get_gcp_environment_networks(
            self.environment_id, project_id=self.project
        )
        return command.response.json()

    def fetch_available_regions(self):
        """Returns the available regions for the given Environment and GCP Project."""
        command = self._control_hub.api_client.get_gcp_environment_regions(self.environment_id, project_id=self.project)
        return command.response.json()

    def fetch_available_service_accounts(self):
        """Returns the available service accounts for the given Environment and GCP Project."""
        command = self._control_hub.api_client.get_gcp_environment_service_accounts(
            self.environment_id, project_id=self.project
        )
        return command.response.json()

    def fetch_available_zones(self, region_id):
        """Returns the available zones for the given environment and GCP project and GCP region."""
        command = self._control_hub.api_client.get_gcp_environment_zones(
            self.environment_id, project_id=self.project, region_id=region_id
        )
        return command.response.json()

    def fetch_available_machine_types(self, zone_id):
        """Returns the available machine types for the given Environment and GCP Project and GCP Zone."""
        command = self._control_hub.api_client.get_gcp_environment_machine_types(
            self.environment_id, project_id=self.project, zone_id=zone_id
        )
        return command.response.json()

    @staticmethod
    def get_ui_value_mappings():
        """This method returns a map for the values shown in the UI and internal constants to be used."""
        return {
            'credentialsType': {
                GCPEnvironment.CREDENTIALS_TYPE_SERVICE_ACCOUNT_IMPERSONATION_FROM_UI: GCPEnvironment.CREDENTIALS_TYPE_SERVICE_ACCOUNT_IMPERSONATION,
                GCPEnvironment.CREDENTIALS_TYPE_SERVICE_ACCOUNT_KEY_FROM_UI: GCPEnvironment.CREDENTIALS_TYPE_SERVICE_ACCOUNT_KEY,
            }
        }


@analytics_class_decorator
class KubernetesEnvironment(Environment):
    """Model for Kubernetes Environment.

    Attributes:
        agent_event_logs (:obj:`list` of :py:class:`streamsets.sdk.sch_models.KubernetesAgentEvent instances):
            Agent logs for the environment.
        agent_java_options (:obj:`str`): Java configuration options set for the Agent.
        agent_status (:obj:`str`): Status of the Agent.
        agent_status_detail (:obj:`str`): Details pertaining to the status of the Agent.
        agent_version (:obj:`str`): Version of the Agent.
        allow_nightly_engine_builds (:obj:`bool`): Whether or not the environment allows use of nightly engine build.
            versions.
        created_by (:obj:`str`): ID of the user who created the environment.
        created_on (:obj:`int`): Millisecond timestamp of when the environment was created.
        environment_id (:obj:`str`): ID of the environment.
        environment_name (:obj:`str`): Name of the environment.
        environment_tags (:obj:`list` of :obj:`str` instances): Tags assigned to the environment.
        environment_type (:obj:`str): Type of the environment.
        kubernetes_labels (:obj:`dict`): Kubernetes labels to apply to all resources provisioned in the Kubernetes
            namespace.
        kubernetes_namespace (:obj:`str`): Name of the Kubernetes namespace to provision the resources in.
        last_modified_by (:obj:`str`): ID of the user who last modified the environment.
        last_modified_on (:obj:`int`): Millisecond timestamp of the last time the environment was modified.
        state (:obj:`str`): The current state of the environment.
    """

    _ATTRIBUTES_TO_IGNORE = [
        'agent',
        'createdOn',
        'credentials',
        'credentialsType',
        'state',
        'status',
        'statusLastUpdated',
        'userProvided',
    ]
    _ATTRIBUTES_TO_REMAP = {'state': 'stateDisplayLabel'}

    def __init__(self, environment, control_hub=None):
        super().__init__(
            environment,
            control_hub=control_hub,
            attributes_to_ignore=KubernetesEnvironment._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=KubernetesEnvironment._ATTRIBUTES_TO_REMAP,
        )

        # We set a default agent version, in case none is provided by the user
        if not self._data['agent'].get('selectedTag') or not self.agent_version:
            agent_versions = self._control_hub.api_client.get_kubernetes_agent_versions().response.json()['data']
            if not agent_versions:
                raise Exception("An agent version must be set when creating the environment, but none are available.")
            self.agent_version = agent_versions[0]['tag']

    @property
    def agent_event_logs(self):
        """Get the Agent event logs for this environment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.KubernetesAgentEvents`
        """
        return KubernetesAgentEvents(self._control_hub, getattr(self, "environment_id", None))

    @property
    def agent_java_options(self):
        """Get the Agent's extra java options.

        Returns:
            A :obj:`str` instance of the agent's extra java options.
        """
        return self._data['agent']['extraJvmOpts']

    @property
    def agent_status(self):
        """Get the Agent's status.

        Returns:
            A :obj:`str` instance of the agent's status.
        """
        return self._data['agent']['status']

    @property
    def agent_status_detail(self):
        """Get the details of the Agent's status

        Returns:
            A :obj:`str` instance of the agent's status detail.
        """
        return self._data['agent']['statusDetail']

    @property
    def agent_version(self):
        return self._data['agent']['selectedTag']

    @agent_version.setter
    def agent_version(self, agent_version):
        """Update the agent_version.

        Args:
            agent_version (:obj:`str`): Agent version to use for the environment.
        """
        self._data['agent']['selectedTag'] = agent_version

    @property
    def kubernetes_labels(self):
        """Kubernetes labels for the environment.

        Returns:
            A (:obj:`dict`) of key: value pairs of labels.
        """
        if self._data['agent']['kubernetesLabels']:
            # Extract the labels out of 'key=value,key=value' format into [[key, value], [key, value]] format
            label_pairs = [pair.split('=') for pair in self._data['agent']['kubernetesLabels'].split(',')]
            return {key: value for [key, value] in label_pairs}
        return None

    @kubernetes_labels.setter
    def kubernetes_labels(self, labels):
        """Update the kubernetes_labels.

        Args:
            labels (:obj:`dict`): One or more labels to be set, in key/value pairs.
        """
        if labels is not None:
            if not isinstance(labels, dict):
                raise ValueError('The label(s) provided must be within a dictionary.')
            self._data['agent']['kubernetesLabels'] = ','.join(
                '{}={}'.format(key, value) for key, value in labels.items()
            )

    @property
    def kubernetes_namespace(self):
        return self._data['agent']['namespace']

    @kubernetes_namespace.setter
    def kubernetes_namespace(self, kubernetes_namespace):
        """Update the kubernetes_namespace.

        Args:
            kubernetes_namespace (:obj:`str`): Name of the Kubernetes namespace to provision the resources in.
        """
        self._data['agent']['namespace'] = kubernetes_namespace

    def apply_agent_yaml_command(self):
        """Gets the installation script to be run for this environment.

        Returns:
            An :obj:`str` instance of the installation command.
        """
        return self._control_hub.api_client.get_kubernetes_apply_agent_yaml_command(self.environment_id).response.text

    def is_complete(self):
        return bool(self.kubernetes_namespace)


@analytics_class_decorator
class Environments(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Environment` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization
        self._id_attr = 'environment_id'

    def _get_all_results_from_api(self, environment_id=None, **kwargs):
        """Args offset, len, order_by, order, tag, with_total_count, state, status, type are not exposed
        directly as arguments because of their limited use by normal users but, could still be specified just like any
        other args with the help of kwargs.

        Args:
            environment_id (:obj:`str`, optional): ID. Default: ``None``.
            kwargs: optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Environment` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {
            'offset': None,
            'len': None,
            'order_by': 'LAST_MODIFIED_TIME',
            'order': 'ASC',
            'tag': None,
            'with_total_count': False,
            'state_display_label': None,
            'status': None,
            'type': None,
        }
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if environment_id is not None:
            try:
                response = [self._control_hub.api_client.get_environment(environment_id).response.json()]
            except requests.exceptions.HTTPError:
                raise ValueError('Environment (environment_id={}) not found'.format(environment_id))
        else:
            response = self._control_hub.api_client.get_all_environments(
                organization=self._organization,
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                tag=kwargs_unioned['tag'],
                state_display_label=kwargs_unioned['state_display_label'],
                status=kwargs_unioned['status'],
                type=kwargs_unioned['type'],
                with_total_count=kwargs_unioned['with_total_count'],
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Environment, {'control_hub': self._control_hub})


@analytics_class_decorator
class EnvironmentTags(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Tag` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, organization=None, parent_id=None, **kwargs):
        """Args offset, len, order are not exposed directly as arguments because of their limited use by normal users
        but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization id of environment. Default: ``None``.
            parent_id (:obj:`str`, optional): ID of the parent environment tag. Default: ``None``.
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Tag` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {'offset': None, 'len': None, 'order': 'DESC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        organization = organization or self._organization
        response = self._control_hub.api_client.get_all_environment_tags(
            organization=organization,
            parent_id=parent_id,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            order=kwargs_unioned['order'],
        ).response.json()

        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Tag, {})


class EnvironmentBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Environment`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_environment_builder`.

    Args:
        environment (:obj:`dict`): Python object built from our Swagger CspEnvironmentJson definition.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    def __init__(self, environment, control_hub):
        self._environment = environment
        self._control_hub = control_hub

    def build(self, environment_name, **kwargs):
        """Define the environment.

        Args:
            environment_name (:obj:`str`): environment name.
            allow_nightly_builds (:obj:`bool`, optional): Default: ``False``.
            allow_nightly_engine_builds (:obj:`bool`, optional): Default: ``False``.
            environment_tags (:obj:`list`, optional): List of tags (strings). Default: ``None``.

        Returns:
            An instance of subclass of :py:class:`streamsets.sdk.sch_models.Environment`.
        """
        allow_snapshot_engine_versions = kwargs.get('allow_nightly_engine_builds') or kwargs.get('allow_nightly_builds')
        self._environment.update(
            {'name': environment_name, 'allowSnapshotEngineVersions': allow_snapshot_engine_versions}
        )
        # if Kubernetes, make the agent attribute a dictionary to be extended later
        if self._environment['type'] == 'KUBERNETES':
            self._environment.update({'agent': {'extraJvmOpts': '', 'kubernetesLabels': '', 'namespace': ''}})
        environment = Environment(self._environment, self._control_hub)
        if kwargs.get('environment_tags'):
            environment.tags = kwargs.get('environment_tags')
        return environment


@analytics_class_decorator
class Engine(BaseModel):
    """Model for Platform Engines.

    Attributes:
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): The engine ACL instance.
        configuration (:py:class:`streamsets.sdk.models.Configuration`): The engine Configuration instance.
        id (:obj:`str`): ID of the engine.
        organization (:obj:`str`): Organization that the engine belongs to.
        engine_url (:obj:`str`): URL registered for the engine.
        version (:obj:`str`): Version of the engine.
        labels (:obj:`list` of :obj:`str` instances): Labels for the engine.
        last_reported_time (:obj:`str`): The last time the engine contacted StreamSets Platform.
        start_up_time (:obj:`str`): The time the engine was started.
        edge (:obj:`bool`): Whether this is an Edge engine or not.
        cpu_load (:obj:`float`): The percent utilization of the CPU by the engine.
        memory_used (:obj:`float`): The amount of memory used by the engine in MB.
        total_memory (:obj:`float`): The total amount of memory configured for the engine in MB.
        running_pipelines (:obj:`int`): The total number of pipelines running on the engine.
        responding (:obj:`bool`): Whether the engine is responding or not.
        engine_type (:obj:`str`): The type of engine.
        max_cpu_load (:obj:`int`): The percentage limit on CPU load configured for this engine.
        max_memory_used (:obj:`int`): The percentage limit on memory configured for this engine.
        max_pipelines_running (:obj:`int`): The limit on the number of concurrent pipelines for this engine.
        deployment_id (:obj:`str`): The ID of the deployment that the engine belongs to.
        directories (:obj:`dict`): The directories of the engine.
        external_libraries (:py:class:`streamsets.sdk.sch_models.ExternalLibrary`): The External Library of the engine.
        memory_used_mb (:obj:`float`): The memory used in MB by the engine.
        resources (:py:class:`streamsets.sdk.sch_models.ExternalResource`): The External Resource of the engine.
        responding (:obj:`bool`): Whether the engine is responding.
        running_pipelines (:obj:`list` of :py:class:`streamsets.sdk.sch_models.Pipeline` instances):
         The running pipelines of the engine.
        running_pipelines_count (:obj:`int`): The running pipelines count of the engine.
        total_memory_mb (:obj:`int`): The total memory in MB of the engine.
        user_stage_libraries (:obj:`dict`): The user stage libraries of the engine.

    """

    _ATTRIBUTES_TO_IGNORE = ['idSeparator', 'pipelinesCommitted', 'offsetProtocolVersion', 'buildTime', 'deploymentId']
    _ATTRIBUTES_TO_REMAP = {
        'running_pipelines_count': 'pipelinesCount',
        'engine_url': 'httpUrl',
        'engine_type': 'executorType',
        'max_memory': 'maxMemoryUsed',
        'max_running_pipeline_count': 'maxPipelinesRunning',
        'memory_used_mb': 'usedMemory',
        'total_memory_mb': 'totalMemory',
    }
    _REPR_METADATA = [
        'id',
        'engine_url',
        'running_pipelines_count',
        'cpu_load',
        'memory_used_mb',
        'last_reported_time',
        'engine_type',
    ]

    def __init__(self, engine, control_hub=None):
        super().__init__(
            engine,
            attributes_to_ignore=Engine._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=Engine._ATTRIBUTES_TO_REMAP,
            repr_metadata=Engine._REPR_METADATA,
        )
        self._control_hub = control_hub

    @property
    def _api_client(self):
        if self._control_hub.use_websocket_tunneling:
            return None
        session_attributes = {'verify': False}
        sch_headers = {
            'X-SS-App-Component-Id': self._control_hub.api_client.session.headers['X-SS-App-Component-Id'],
            'X-SS-App-Auth-Token': self._control_hub.api_client.session.headers['X-SS-App-Auth-Token'],
        }
        if self.engine_type == 'COLLECTOR':
            return SdcApiClient(server_url=self.engine_url, headers=sch_headers, session_attributes=session_attributes)
        if self.engine_type == 'TRANSFORMER':
            return StApiClient(server_url=self.engine_url, headers=sch_headers, session_attributes=session_attributes)

    @property
    def _instance(self):
        if self.engine_type == 'COLLECTOR':
            # Disable SSL cert verification to enable use of self-signed certs.
            SdcDataCollector.VERIFY_SSL_CERTIFICATES = False
            return SdcDataCollector(
                self.engine_url,
                control_hub=self._control_hub,
                sdc_id=self.id if self._control_hub.use_websocket_tunneling else None,
            )
        if self.engine_type == 'TRANSFORMER':
            # Disable SSL cert verification to enable use of self-signed certs.
            StTransformer.VERIFY_SSL_CERTIFICATES = False
            return StTransformer(
                server_url=self.engine_url,
                control_hub=self._control_hub,
                transformer_id=self.id if self._control_hub.use_websocket_tunneling else None,
            )
        return None

    @property
    def _tunneling_connection(self):
        if self._control_hub.use_websocket_tunneling:
            return self._control_hub.api_client.get_tunneling_instance_id(self._data['id']).response.json()[
                'instanceId'
            ]
        return None

    @property
    def acl(self):
        return ACL(self._control_hub.api_client.get_engine_acl(engine_id=self.id).response.json(), self._control_hub)

    @acl.setter
    def acl(self, engine_acl):
        """Update engine ACL.

        Args:
            engine_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The engine ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        if self.deployment_id:
            raise Exception(
                "This Engine's ACL is controlled by its Deployment and cannot be set directly. Refer to the"
                " Deployment's ACL."
            )
        self._control_hub.api_client.set_engine_acl(engine_id=self.id, engine_acl_json=engine_acl._data)

    @property
    def configuration(self):
        if isinstance(self._api_client, SdcApiClient):
            return self._api_client.get_sdc_configuration().response.json()
        if isinstance(self._api_client, StApiClient):
            return self._api_client.get_transformer_configuration().response.json()
        return self._control_hub.api_client.get_engine_configuration(
            self.id, self._tunneling_connection
        ).response.json()

    @property
    def cpu_load(self):
        return round(self._data['cpuLoad'], 2)

    @property
    def deployment_id(self):
        return self._data['deploymentId'] or self._data['cspDeploymentId']

    @property
    def directories(self):
        if isinstance(self._api_client, SdcApiClient):
            # COLLECTOR-1066
            raise Exception(
                'Retrieving the configured directories directly from an Engine is not currently supported'
                ' in the SDK.'
            )
        elif isinstance(self._api_client, StApiClient):
            # COLLECTOR-1066
            raise Exception(
                'Retrieving the configured directories directly from an Engine is not currently supported'
                ' in the SDK.'
            )
        else:
            dir_json = self._control_hub.api_client.get_engine_directories(
                self.id, self._tunneling_connection
            ).response.json()
        directories = {
            'runtime_directory': dir_json['runtimeDir'],
            'configuration_directory': dir_json['configDir'],
            'data_directory': dir_json['dataDir'],
            'log_directory': dir_json['logDir'],
            'resources_directory': dir_json['resourcesDir'],
            'libraries_extra_directory': dir_json['libsExtraDir'],
        }
        return directories

    @property
    def external_libraries(self):
        """Get the external libraries for the engine.

        Returns:
            A :obj:`list` of :py:class:`streamsets.sdk.sch_models.ExternalLibrary` instances.
        """
        if isinstance(self._api_client, SdcApiClient):
            libs = self._api_client.get_sdc_external_libraries().response.json()
        elif isinstance(self._api_client, StApiClient):
            libs = self._api_client.get_transformer_external_libraries().response.json()
        else:
            libs = self._control_hub.api_client.get_engine_external_libraries(
                self.id, self._tunneling_connection
            ).response.json()
        return [ExternalLibrary(lib) for lib in libs]

    @property
    def memory_used_mb(self):
        # Convert bytes to MB, rounded to the hundredths place. Python ignores underscores in int types
        return round(self._data['usedMemory'] / 1_000_000, 2)

    @property
    def resources(self):
        """Get the external resources for the engine.

        Returns:
            A :obj:`list` of :py:class:`streamsets.sdk.sch_models.ExternalResource` instances.
        """
        if isinstance(self._api_client, SdcApiClient):
            files = self._api_client.get_sdc_external_resources().response.json()
        elif isinstance(self._api_client, StApiClient):
            files = self._api_client.get_transformer_external_resources().response.json()
        else:
            files = self._control_hub.api_client.get_engine_external_resources(
                self.id, self._tunneling_connection
            ).response.json()
        return [ExternalResource(file) for file in files]

    @property
    def responding(self):
        self.refresh()
        return self._data['responding']

    @property
    def running_pipelines(self):
        pipelines = []
        for pipeline in self._control_hub.api_client.get_pipelines_running_in_sdc(self.id).response.json():
            run_type = 'Job' if not pipeline['localPipeline'] else 'Test Run'
            last_reported_time = pipeline['lastReportedTime']
            pipelines.append(
                {
                    'pipeline': pipeline['title'],
                    'type': run_type,
                    'status': pipeline['status'],
                    'last_reported_time': last_reported_time,
                    'message': pipeline['message'],
                }
            )
        return pipelines

    @property
    def running_pipelines_count(self):
        return self._data['pipelinesCount']

    @property
    def total_memory_mb(self):
        # Convert bytes to MB, rounded to the hundredths place. Python ignores underscores in int types
        return round(self._data['totalMemory'] / 1_000_000, 2)

    @property
    def user_stage_libraries(self):
        if isinstance(self._api_client, SdcApiClient):
            libs = self._api_client.get_sdc_user_stage_libraries().response.json()
        elif isinstance(self._api_client, StApiClient):
            libs = self._api_client.get_transformer_user_stage_libraries().response.json()
        else:
            libs = self._control_hub.api_client.get_engine_user_stage_libraries(
                self.id, self._tunneling_connection
            ).response.json()
        return [lib['fileName'] for lib in libs]

    def add_external_libraries(self, stage_library, *libraries):
        """Add external libraries to the engine.

        Args:
            stage_library (:obj:`str`): The stage library that includes the stage requiring the external library.
            *libraries: One or more :obj:`file` instances to add to an engine, in binary format.
        """
        lib_directory_name = get_library_directory_name(stage_library, self.engine_type)
        if isinstance(self._api_client, SdcApiClient):
            for lib in libraries:
                self._api_client.add_external_libraries_to_sdc(stage_library=lib_directory_name, external_lib=lib)
        elif isinstance(self._api_client, StApiClient):
            for lib in libraries:
                self._api_client.add_external_libraries_to_transformer(
                    stage_library=lib_directory_name, external_lib=lib
                )
        else:
            for lib in libraries:
                self._control_hub.api_client.add_external_libraries_to_engine(
                    engine_id=self.id,
                    stage_library=lib_directory_name,
                    external_lib=lib,
                    tunneling_instance_id=self._tunneling_connection,
                )

    def add_resources(self, *resources):
        """Add resource files to the engine.

        Args:
            *resources: One or more :obj:`file` instances to add to an engine, in binary format.
        """
        if isinstance(self._api_client, SdcApiClient):
            for resource in resources:
                self._api_client.add_external_resource_to_sdc(resource=resource)
        elif isinstance(self._api_client, StApiClient):
            for resource in resources:
                self._api_client.add_external_resource_to_transformer(resource=resource)
        else:
            for resource in resources:
                self._control_hub.api_client.add_external_resource_to_engine(
                    engine_id=self.id, resource=resource, tunneling_instance_id=self._tunneling_connection
                )

    def delete_external_libraries(self, *libraries):
        """Delete external libraries from the engine.

        Args:
            *libraries: One or more :py:class:`streamsets.sdk.sch_models.ExternalLibrary` instances to
                delete from the engine.
        """
        expanded_library_list = [library._data for library in libraries]
        try:
            if isinstance(self._api_client, SdcApiClient):
                self._api_client.delete_external_libraries_from_sdc(external_libs=expanded_library_list)
            elif isinstance(self._api_client, StApiClient):
                self._api_client.delete_external_libraries_from_transformer(external_libs=expanded_library_list)
            else:
                self._control_hub.api_client.delete_external_libraries_from_engine(
                    engine_id=self.id,
                    external_libs=expanded_library_list,
                    tunneling_instance_id=self._tunneling_connection,
                )
        except requests.exceptions.HTTPError as ex:
            raise ValueError('A library value was supplied that was not found on this engine.') from ex

    def delete_resources(self, *resources):
        """Delete resource files on the engine.

        Args:
            *resources: One or more :py:class:`streamsets.sdk.sch_models.ExternalResource` instances to
                delete from the engine.
        """
        expanded_resource_list = [resource._data for resource in resources]
        try:
            if isinstance(self._api_client, SdcApiClient):
                self._api_client.delete_external_resources_from_sdc(resources=expanded_resource_list)
            elif isinstance(self._api_client, StApiClient):
                self._api_client.delete_external_resources_from_transformer(resources=expanded_resource_list)
            else:
                self._control_hub.api_client.delete_external_resources_from_engine(
                    engine_id=self.id,
                    resources=expanded_resource_list,
                    tunneling_instance_id=self._tunneling_connection,
                )
        except requests.exceptions.HTTPError as ex:
            raise ValueError('A resource value was supplied that was not found on this engine.') from ex

    def get_logs(self, ending_offset=-1):
        """Retrieve the logs for the engine.

        Args:
            ending_offset (:obj:`int`, optional): The offset to capture logs up until. Default: ``-1``

        Returns:
            A :obj:`list` of :obj:`dict` instances, one dictionary per log line.
        """
        if isinstance(self._api_client, SdcApiClient):
            return self._api_client.get_logs(ending_offset=ending_offset).response.json()
        if isinstance(self._api_client, StApiClient):
            return self._api_client.get_logs(ending_offset=ending_offset)
        return self._control_hub.api_client.get_engine_logs(
            self.id, self._tunneling_connection, ending_offset=ending_offset
        ).response.json()

    def get_thread_dump(self):
        """Generate a thread dump for the engine.

        Returns:
            A :obj:`list` of :obj:`dict` instances, one dictionary per thread.
        """
        if isinstance(self._api_client, SdcApiClient):
            return self._api_client.get_sdc_thread_dump().response.json()
        if isinstance(self._api_client, StApiClient):
            return self._api_client.get_transformer_thread_dump().response.json()
        return self._control_hub.api_client.get_engine_thread_dump(self.id, self._tunneling_connection).response.json()

    def refresh(self):
        """Retrieve the latest state of the Engine from Platform, and update the in-memory representation."""
        self._data = self._control_hub.api_client.get_sdc(self.id).response.json()


@analytics_class_decorator
class Engines(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Engine` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    def __init__(self, control_hub):
        super().__init__(control_hub)
        self._organization = control_hub.organization

    def _get_all_results_from_api(self, id=None, label=None, version=None, engine_type=None, **kwargs):
        """The args for edge, offset, len, order_by, and order aren't directly exposed due to their limited use by
        normal users, however they're still accessible via kwargs.

        Args:
            id (:obj:`str`, optional): Get a single engine by ID and ignore all other arguments if provided.
                Default: ``None``
            label (:obj:`str`, optional): A label to filter the engines on. Default: ``None``
            version (:obj:`str`, optional): A version to filter the engines on. Default: ``None``
            engine_type (:obj:`str`, optional): The type of engine to retrieve. Acceptable values are 'COLLECTOR',
                'TRANSFORMER', 'EDGE', and 'SNOWPARK'. Default: ``None``

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Engine` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Engine`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        if engine_type and engine_type not in ('COLLECTOR', 'TRANSFORMER', 'SNOWPARK', 'EDGE'):
            raise ValueError(
                "Pipelines can only be of type 'COLLECTOR', 'TRANSFORMER', 'EDGE' or 'SNOWPARK,"
                " provided type '{}' is invalid".format(engine_type)
            )
        kwargs_defaults = {
            # pagination
            'offset': 0,
            'len': None,
            'order_by': 'HTTP_URL',
            'order': 'ASC',
            # server-side filtering
            'label': label,
            'version': version,
            'engine_type': engine_type or 'COLLECTOR',
            'edge': None,
        }

        if id:
            try:
                response = self._control_hub.api_client.get_engine(engine_id=id).response.json()
                if engine_type:
                    if response['executorType'] != engine_type:
                        raise TypeError(
                            "Provided engine_type '{}' does not match engine_type of engine provided '{}'".format(
                                engine_type, response['executorType']
                            )
                        )
                else:
                    # Since we default to 'COLLECTOR' in kwargs_defaults if engine_type isn't provided,
                    # we need engine_type to be the same as the executorType of the engine we just retrieved
                    kwargs_defaults['engine_type'] = response['executorType']
                kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
                response = [response]
            except (requests.exceptions.HTTPError, requests.exceptions.JSONDecodeError):
                raise ValueError('Engine (id={}) not found'.format(id))

        else:
            kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
            kwargs_unioned = kwargs_instance.union()
            response = self._control_hub.api_client.get_all_registered_engines(
                organization=self._organization,
                edge=kwargs_unioned['edge'],
                label=kwargs_unioned['label'],
                version=kwargs_unioned['version'],
                offset=kwargs_unioned['offset'],
                len_=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                executor_type=kwargs_unioned['engine_type'],
                with_wrapper=True,
            ).response.json()

        return CollectionModelResults(response, kwargs_instance.subtract(), Engine, {'control_hub': self._control_hub})


class ExternalLibrary(dict):
    """Wrapper class for external libraries on an Engine, which stores the full object but only displays the same
        information seen in the UI.

    Attributes:
        library (:obj:`dict`): JSON representation of a library.
    """

    def __init__(self, library):
        self._data = library
        # Only passing in the modified dict so that a user can index on the values shown in repr
        super().__init__({self._data['fileName']: self._data['libraryId']})

    def __repr__(self):
        return str({self._data['fileName']: self._data['libraryId']})


class ExternalResource(dict):
    """Wrapper class for external resources on an Engine, which stores the full object but only displays the same
        information seen in the UI.

    Attributes:
        resource (:obj:`dict`): JSON representation of a resource.
    """

    def __init__(self, resource):
        self._data = resource
        # Only passing in the modified dict so that a user can index on the values shown in repr
        super().__init__({self._data['fileName']: self._data['id']})

    def __repr__(self):
        return str({self._data['fileName']: self._data['id']})


@analytics_class_decorator
class RegisteredEngines(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Engine` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
        deployment_id (:obj:`str`): Deployment ID.
    """

    def __init__(self, control_hub, deployment_id):
        super().__init__(control_hub)
        self._deployment_id = deployment_id

    def _get_all_results_from_api(self, **kwargs):
        """The args for offset, len, order_by, order aren't directly exposed due to their limited use by
        normal users, however they're still accessible via kwargs.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Engine` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Engine`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': 5, 'order_by': 'LAST_REPORTED_TIME', 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.get_deployment_registered_engines(
            deployment_id=self._deployment_id,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            order_by=kwargs_unioned['order_by'],
            order=kwargs_unioned['order'],
            with_wrapper=True,
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Engine, {'control_hub': self._control_hub})


@analytics_class_decorator
class Deployment(BaseModel):
    """Model for Deployment. This is an abstract class.

    Attributes:
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): The Deployment ACL instance.
        created_by (:obj:`str`): User that created this deployment.
        created_on (:obj:`int`): Time at which this deployment was created.
        deployment_events (:obj:`DeploymentEvents`): Name of the deployment.
        deployment_id (:obj:`str`): Id of the deployment.
        deployment_name (:obj:`str`): Name of the deployment.
        deployment_tags (:obj:`list`): Raw deployment tags of the deployment.
        deployment_type (:obj:`str`): Type of the deployment.
        desired_instances (:obj:`int`): The Deployment desired number of instances.
        engine_configuration (:obj:`DeploymentEngineConfiguration`): The Deployment Engine Configuration.
        engine_type (:obj:`str`): The Deployment Engine type.
        engine_version (:obj:`str`): The Deployment Engine Version.
        environment_id (:obj:`list`): Enabled environment where engine will be deployed.
        last_modified_by (:obj:`str`): User that last modified this deployment.
        last_modified_on (:obj:`int`): Time at which this deployment was last modified.
        network_tags (:obj:`list`): The Deployment network tags.
        scala_binary_version (:obj:`str`): scala Binary Version.
        organization (:obj:`str`): The Deployment organization.
        json_state (:obj:`str`): State of the deployment - this is json field called state.
        state (:obj:`str`): State of the deployment - displayed as state on UI.
        status (:obj:`str`): Status of the deployment.
        status_detail (:obj:`str`): Status detail of the deployment.
        registered_engines (:obj:`RegisteredEngines`): Registered Engines of the deployment.
        tags (a :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Tag` instances):
         Tags of the deployment.
    """

    _ATTRIBUTES_TO_IGNORE = [
        'deploymentTags',
        'userProvided',
        'engineConfiguration',
        'organization',
        'statusLastUpdated',
    ]
    _ATTRIBUTES_TO_REMAP = {
        'created_by': 'creator',
        'created_on': 'createTime',
        'deployment_id': 'id',
        'deployment_name': 'name',
        'deployment_tags': 'rawDeploymentTags',
        'deployment_type': 'type',
        'network_tags': 'tags',
        'json_state': 'state',
        'state': 'stateDisplayLabel',
    }
    _REPR_METADATA = ['deployment_id', 'deployment_name', 'deployment_type', 'state']

    class ENGINE_TYPES(enum.Enum):
        DATA_COLLECTOR = 'DC'
        TRANSFORMER = 'TF'

    class TYPES(enum.Enum):
        AZURE_VM = 'AZURE_VM'
        EC2 = 'EC2'
        GCE = 'GCE'
        KUBERNETES = 'KUBERNETES'
        SELF = 'SELF'

    def __init__(
        self, deployment, control_hub=None, attributes_to_ignore=None, attributes_to_remap=None, repr_metadata=None
    ):
        attributes_to_ignore = attributes_to_ignore or []
        attributes_to_remap = attributes_to_remap or {}
        repr_metadata = repr_metadata or []
        super().__init__(
            deployment,
            attributes_to_ignore=Deployment._ATTRIBUTES_TO_IGNORE + attributes_to_ignore,
            attributes_to_remap={**Deployment._ATTRIBUTES_TO_REMAP, **attributes_to_remap},
            repr_metadata=Deployment._REPR_METADATA + repr_metadata,
        )
        self._control_hub = control_hub

    def __new__(cls, deployment, control_hub=None, **kwargs):
        if deployment['type'] == 'SELF':
            return super().__new__(SelfManagedDeployment)
        elif deployment['type'] == 'AZURE_VM':
            return super().__new__(AzureVMDeployment)
        elif deployment['type'] == 'EC2':
            return super().__new__(EC2Deployment)
        elif deployment['type'] == 'GCE':
            return super().__new__(GCEDeployment)
        elif deployment['type'] == 'KUBERNETES':
            return super().__new__(KubernetesDeployment)
        else:
            return super().__new__(NotImplementedDeployment)

    def refresh(self):
        self._data = self._control_hub.api_client.get_deployment(self.deployment_id).response.json()

    @property
    def acl(self):
        """Get deployment ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        if isinstance(self, NotImplementedDeployment):
            raise NotImplementedError("Cannot get ACL for NotImplementedDeployment class")
        return ACL(
            self._control_hub.api_client.get_deployment_acl(deployment_id=self.deployment_id).response.json(),
            self._control_hub,
        )

    @acl.setter
    def acl(self, deployment_acl):
        """Update deployment ACL.

        Args:
            deployment_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The deployment ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        if isinstance(self, NotImplementedDeployment):
            raise NotImplementedError("Cannot set ACL for NotImplementedDeployment class")
        return self._control_hub.api_client.update_deployment_acl(
            deployment_id=self.deployment_id, deployment_acl_json=deployment_acl._data
        )

    @property
    def deployment_events(self):
        """Get the events for a deployment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.DeploymentEvents`
        """
        return DeploymentEvents(self._control_hub, self.deployment_id)

    @property
    def tags(self):
        """Get the tags.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :obj:`str` instances.
        """
        deployment_tags = self._data.get('deploymentTags', []) or []
        if not deployment_tags:
            raw_deployment_tags = self._data.get('rawDeploymentTags', []) or []
            if raw_deployment_tags:
                organization = self._control_hub.organization
                deployment_tags = [build_tag_from_raw_tag(raw_tag, organization) for raw_tag in raw_deployment_tags]
                self._data['deploymentTags'] = deployment_tags
        return SeekableList(tag['tag'] for tag in deployment_tags)

    @tags.setter
    def tags(self, tags):
        """Update a Deployment object's tags.

        Args:
            tags: A :obj:`list` of one or more :obj:`str` instances.
        """
        if not isinstance(tags, list):
            raise ValueError('The tag(s) provided must be in a list.')
        elif isinstance(self, NotImplementedDeployment):
            raise NotImplementedError("Cannot set tags for NotImplementedDeployment class")
        self._data['deploymentTags'] = []
        self._data['rawDeploymentTags'] = tags
        for tag in tags:
            tag_json = build_tag_from_raw_tag(tag, self._control_hub.organization)
            self._data['deploymentTags'].append(tag_json)

    @property
    def engine_instances(self):
        warnings.warn(
            'engine_instances is no longer supported, and will be deprecated in future releases.'
            ' Instead please use desired_instances',
            DeprecationWarning,
        )
        return self.desired_instances

    @engine_instances.setter
    def engine_instances(self, engine_instance_amount):
        """Update the amount of engine instances.

        Args:
            engine_instance_amount (:obj:`int`): Amount of engine instances.
        """
        warnings.warn(
            'engine_instances is no longer supported, and will be deprecated in future releases.'
            ' Instead please use desired_instances',
            DeprecationWarning,
        )
        self._data["desiredInstances"] = engine_instance_amount

    def complete(self):
        result = all(
            [
                self.deployment_name,
                self.deployment_id,
                self.environment,
                self.engine_configuration,
                self.engine_configuration.engine_type,
                self.engine_configuration.engine_version,
            ]
        )
        if result and self.engine_configuration.engine_type == 'TF':
            result = bool(self.engine_configuration.scala_binary_version)
        if result:
            result = self.is_complete()
        return result

    def is_complete(self):
        raise NotImplementedError('Method not implemented by class {}'.format(self.__class__))

    @property
    def engine_configuration(self):
        """The engine configuration of  deployment engine.
        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.DeploymentEngineConfiguration`.
        """
        if isinstance(self, NotImplementedDeployment):
            raise NotImplementedError("Cannot get Engine Configuration for NotImplementedDeployment class")
        self._data['engineConfiguration'] = (
            self._control_hub.api_client.get_deployment_engine_configs(self.deployment_id).response.json()
            if self._data['engineConfiguration'] is None
            else self._data['engineConfiguration']
        )
        return DeploymentEngineConfiguration(self._data['engineConfiguration'], deployment=self)

    @engine_configuration.setter
    def engine_configuration(self, value):
        if isinstance(self, NotImplementedDeployment):
            raise NotImplementedError("Cannot set Engine Configuration for NotImplementedDeployment class")
        self._data['engineConfiguration'] = json.dumps(value)

    @property
    def registered_engines(self):
        """Get the registered engines.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.RegisteredEngines`
        """
        return RegisteredEngines(self._control_hub, self.deployment_id)


class NotImplementedDeployment(Deployment):
    """Model for Deployments not yet supported."""

    def __init__(self, deployment, control_hub=None):
        super().__init__(deployment, control_hub)

    def is_complete(self):
        return True


@analytics_class_decorator
class SelfManagedDeployment(Deployment):
    """Model for self managed Deployment."""

    class InstallMechanism(enum.Enum):
        DEFAULT = 'DEFAULT'
        BACKGROUND = 'BACKGROUND'
        FOREGROUND = 'FOREGROUND'

    class InstallType(enum.Enum):
        DOCKER = 'DOCKER'
        TARBALL = 'TARBALL'

    def __init__(self, deployment, control_hub=None):
        super().__init__(deployment, control_hub)

    def __setattr__(self, key, value):
        if key in ('desired_instances', 'engine_instances'):
            warnings.warn('You cannot set number of instances for a SelfManagedDeployment', UserWarning)
        else:
            super().__setattr__(key, value)

    def is_complete(self):
        """Checks if all required fields are set in this deployment."""
        return bool(self.install_type)

    def _get_supported_java_versions(self):
        """Gets the supported java versions for this deployment.

        Returns:
            An :obj:`list` instance of the supported java versions in string format.
        """
        engine_version_id = self.engine_configuration.engine_version_id
        engine_version_data = self._control_hub.api_client.get_engine_version(engine_version_id).response.json()
        return engine_version_data["supportedJavaVersions"].split(',')

    def install_script(self, install_mechanism='DEFAULT', install_type=None, java_version=None):
        """Gets the installation script to be run for this deployment.

        Args:
            install_mechanism (:obj:`str`, optional): Possible values for install are "DEFAULT", "BACKGROUND" and
                                                      "FOREGROUND". Default: ``DEFAULT``.
            install_type (:obj:`str`, optional): Possible values for install are "DOCKER", "TARBALL". Default: ``None``.
                                                 If not provided will use the value supplied via the deployment.
            java_version (:obj:`str`, optional): Java Development Kit Version to be used. Example: "8".
                Default: ``None``.

        Returns:
            An :obj:`str` instance of the installation command.
        """
        if not hasattr(self.InstallMechanism, install_mechanism.upper()):
            valid_mechanism = ', '.join(mode.name.lower() for mode in self.InstallMechanism)
            raise ValueError(
                "Invalid installation mode. " "Please specify one of the following: {}.".format(valid_mechanism)
            )

        if not install_type:
            install_type = self.install_type
        if not hasattr(self.InstallType, install_type.upper()):
            valid_type = ', '.join(mode.name.lower() for mode in self.InstallType)
            raise ValueError(
                "Invalid installation type. " "Please specify one of the following: {}.".format(valid_type)
            )

        if java_version:
            supported_java_versions = self._get_supported_java_versions()
            if java_version not in supported_java_versions:
                raise ValueError(
                    "Java version {} not supported. Please pick from supported java version(s): {}".format(
                        java_version, supported_java_versions
                    )
                )

        return self._control_hub.api_client.get_self_managed_deployment_install_command(
            self.deployment_id, install_mechanism, install_type, java_version
        ).response.text


class AzureVMDeployment(Deployment):
    """Model for Azure VM Deployment.

    Attributes:
        attach_public_ip (:obj:`bool`):
        azure_tags (:obj:`dict`): Azure tags to apply to all provisioned resources in this Azure deployment.
        desired_instances (:obj:`int`): Number of engine instances to deploy.
        key_pair_name (:obj:`str`): SSH key pair.
        managed_identity (:obj:`str`):
        public_ssh_key (:obj:`str`):
        resource_group (:obj:`str`):
        ssh_key_source (:obj:`str`): SSH key source.
        vm_size (:obj:`str`):
        zones (:obj:`list`) List of zones.
    """

    _ATTRIBUTES_TO_REMAP = {'key_pair_name': 'sshKeyPairName'}

    def __init__(self, deployment, control_hub=None):
        super().__init__(deployment, control_hub, attributes_to_remap=AzureVMDeployment._ATTRIBUTES_TO_REMAP)

    def is_complete(self):
        """Checks if all required fields are set in this deployment."""
        result = all([self.desired_instances >= 0, self.key_pair_name, self.vm_size, self.zones])
        if self.ssh_key_source is not None:
            result = bool(self.key_pair_name)
        return result

    @property
    def azure_tags(self):
        if self._data['resourceTags'] is not None:
            # Extract the tags out of 'key=value,key=value' format into [[key, value], [key, value]] format
            tag_pairs = [pair.split('=') for pair in self._data['resourceTags'].split(',')]
            return {key: value for [key, value] in tag_pairs}
        return None

    @azure_tags.setter
    def azure_tags(self, tags):
        """Update the azure_tags.

        Args:
            tags (:obj:`dict`): One or more tags to be set, in key/value pairs.
        """
        if tags is not None:
            if not isinstance(tags, dict):
                raise ValueError('The tag(s) provided must be within a dictionary.')
            self._data['resourceTags'] = ','.join('{}={}'.format(key, value) for key, value in tags.items())

    @staticmethod
    def get_ui_value_mappings():
        """This method returns a map for the values shown in the UI and internal constants to be used."""
        return {
            'sshKeySource': {'Existing SSH Key Pair Name': 'EXISTING_KEY_PAIR_NAME', 'Public SSH Key': 'PUBLIC_SSH_KEY'}
        }


class EC2Deployment(Deployment):
    """Model for EC2 Deployment.

    Attributes:
        ec2_instance_type (:obj:`str`): Type EC2 engine instance.
        desired_instances (:obj:`int`): No. of EC2 engine instances.
        instance_profile (:obj:`str`): arn of instance profile created as an environment prerequisite.
        key_pair_name (:obj:`str`): SSH key pair.
        aws_tags (:obj:`dict`): AWS tags to apply to all provisioned resources in this AWS deployment.
        ssh_key_source (:obj:`str`): SSH key source.
        tracking_url (:obj:`str`):

    """

    _ATTRIBUTES_TO_REMAP = {
        'ec2_instance_type': 'instanceType',
        'instance_profile': 'instanceProfileArn',
        'key_pair_name': 'sshKeyPairName',
    }

    def __init__(self, deployment, control_hub=None):
        super().__init__(deployment, control_hub, attributes_to_remap=EC2Deployment._ATTRIBUTES_TO_REMAP)

    def is_complete(self):
        """Checks if all required fields are set in this deployment."""
        if not self.instance_profile:
            environment = self._control_hub.environments.get(environment_id=self.environment)
            instance_profile = environment.default_instance_profile
        else:
            instance_profile = self.instance_profile
        result = all([self.desired_instances >= 0, self.ec2_instance_type, instance_profile])
        if result and self.ssh_key_source != "NONE":
            result = bool(self.key_pair_name)
        return result

    @property
    def aws_tags(self):
        if self._data['resourceTags'] is not None:
            # Extract the tags out of 'key=value,key=value' format into [[key, value], [key, value]] format
            tag_pairs = [pair.split('=') for pair in self._data['resourceTags'].split(',')]
            return {key: value for [key, value] in tag_pairs}
        return None

    @aws_tags.setter
    def aws_tags(self, tags):
        """Update the aws_tags.

        Args:
            tags (:obj:`dict`): One or more tags to be set, in key/value pairs.
        """
        if tags is not None:
            if not isinstance(tags, dict):
                raise ValueError('The tag(s) provided must be within a dictionary.')
            self._data['resourceTags'] = ','.join('{}={}'.format(key, value) for key, value in tags.items())


class GCEDeployment(Deployment):
    """Model for GCE Deployment.

    Attributes:
        block_project_ssh_keys (:obj:`bool`): Blocks the use of project-wide public SSH keys to access
            the provisioned VM instances.
        desired_instances (:obj:`int`): Number of engine instances to deploy.
        gcp_labels (:obj:`dict`): GCP labels to apply to all provisioned resources in your GCP project.
        instance_service_account (:obj:`str`): Instance service account.
        machine_type (:obj:`str`): machine type to use for the provisioned VM instances.
        public_ssh_key (:obj:`str`): full contents of public SSH key associated with each VM instance.
        region (:obj:`str`): Region to provision VM instances in.
        tracking_url (:obj:`str`): Tracking URL.
        zone (:obj:`list`): GCP zone
    """

    _ATTRIBUTES_TO_REMAP = {
        'block_project_ssh_keys': 'blockProjectSshKeys',
        'instance_service_account': 'instanceServiceAccountEmail',
        'zone': 'zones',
    }

    def __init__(self, deployment, control_hub=None):
        super().__init__(deployment, control_hub, attributes_to_remap=GCEDeployment._ATTRIBUTES_TO_REMAP)

    def is_complete(self):
        """Checks if all required fields are set in this deployment."""
        return all(
            [self.region, self.zone, self.desired_instances >= 0, self.machine_type, self.instance_service_account]
        )

    @property
    def gcp_labels(self):
        if self._data['resourceLabels'] is not None:
            # Extract the labels out of 'key=value,key=value' format into [[key, value], [key, value]] format
            label_pairs = [pair.split('=') for pair in self._data['resourceLabels'].split(',')]
            return {key: value for [key, value] in label_pairs}
        return None

    @gcp_labels.setter
    def gcp_labels(self, labels):
        """Update the gcp_labels.

        Args:
            labels (:obj:`dict`): One or more labels to be set, in key/value pairs.
        """
        if labels is not None:
            if not isinstance(labels, dict):
                raise ValueError('The label(s) provided must be within a dictionary.')
            self._data['resourceLabels'] = ','.join('{}={}'.format(key, value) for key, value in labels.items())


class KubernetesDeployment(Deployment):
    """Model for Kubernetes Deployment.

    Attributes:
        kubernetes_labels (:obj:`dict`): Kubernetes labels to apply to all provisioned resources in
         your Kubernetes project.
    """

    _ATTRIBUTES_TO_IGNORE = ['kubernetesLabels', 'status', 'statusLastUpdated', 'useSpotInstances']
    _ATTRIBUTES_TO_REMAP = {'hpa_target_cpu_utilization_percentage': 'hpaTargetCPUUtilizationPercentage'}

    def __init__(self, deployment, control_hub=None):
        super().__init__(
            deployment,
            control_hub,
            attributes_to_ignore=KubernetesDeployment._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=KubernetesDeployment._ATTRIBUTES_TO_REMAP,
        )

    @property
    def kubernetes_labels(self):
        """Kubernetes labels for the deployment.

        Returns:
            A (:obj:`dict`) of key: value pairs of labels.
        """
        if self._data.get('kubernetesLabels', None):
            # Extract the labels out of 'key=value,key=value' format into [[key, value], [key, value]] format
            label_pairs = [pair.split('=') for pair in self._data['kubernetesLabels'].split(',')]
            return {key: value for [key, value] in label_pairs}
        return None

    @kubernetes_labels.setter
    def kubernetes_labels(self, labels):
        """Update the kubernetes_labels.

        Args:
            labels (:obj:`dict`): One or more labels to be set, in key/value pairs.
        """
        if labels is not None:
            if not isinstance(labels, dict):
                raise ValueError('The label(s) provided must be within a dictionary.')
            self._data['kubernetesLabels'] = ','.join('{}={}'.format(key, value) for key, value in labels.items())

    def is_complete(self):
        """Checks if all required fields are set in this deployment."""
        return True


class DeploymentBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Deployment`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_deployment_builder`.

    Args:
        deployment (:obj:`dict`): Python object built from our Swagger CspDeploymentJson definition.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    def __init__(self, deployment, control_hub):
        self._deployment = deployment
        self._control_hub = control_hub

    def build(
        self,
        deployment_name,
        engine_type,
        engine_version,
        environment,
        external_resource_location=None,
        engine_labels=None,
        max_cpu_load=DEFAULT_MAX_CPU_LOAD_VALUE,
        max_memory_used=DEFAULT_MAX_MEMORY_USED_VALUE,
        max_pipelines_running=DEFAULT_MAX_PIPELINES_RUNNING_VALUE,
        deployment_tags=None,
        engine_build=None,
        scala_binary_version=None,
        **kwargs,
    ):
        """Define the deployment.

        Args:
            deployment_name (:obj:`str`): deployment name.
            engine_type (:obj:`str`): Type of engine to deploy.
            engine_version (:obj:`str`): Version of engine to deploy.
            environment (:py:class:`streamsets.sdk.sch_models.Environment`): The environment instance.
            external_resource_location (:obj:`str`, optional): External Resource Location URL. Default: ``None``.
            engine_labels (:obj:`list`, optional): List of labels (strings). Default: ``None``.
            max_cpu_load (:obj:`float` or :obj:`int`, optional): Max CPU Load (percent). Default: ``80.0``.
            max_memory_used (:obj:`float` or :obj:`int`, optional): Max Memory Used (percent). Default: ``100.0``.
            max_pipelines_running (:obj:`int`, optional): Max Running Pipeline Count. Default: ``1000000``.
            deployment_tags (:obj:`list`, optional): List of tags (strings). Default: ``None``.
            engine_build (:obj:`str`, optional): Build of engine to deploy. Default: ``None``.
            scala_binary_version (:obj:`str`, optional): Scala binary version required in case of
                engine_type='TF' Default: ``None``.

        Returns:
            An instance of subclass of :py:class:`streamsets.sdk.sch_models.Deployment`.
        """
        max_cpu_load = float(max_cpu_load) if isinstance(max_cpu_load, int) else max_cpu_load
        max_memory_used = float(max_memory_used) if isinstance(max_memory_used, int) else max_memory_used

        if any(not isinstance(argument, str) for argument in [deployment_name, engine_type, engine_version]):
            raise TypeError('deployment_name, engine_type & engine_version must be of type str')

        if any(not isinstance(argument, float) for argument in [max_memory_used, max_cpu_load]):
            raise TypeError('max_memory_used & max_cpu_load must be of type int or float')

        if any(not argument <= 100.0 for argument in [max_memory_used, max_cpu_load]):
            raise ValueError('max_memory_used & max_cpu_load must be smaller than or equal to 100.0')

        if not isinstance(max_pipelines_running, int):
            raise TypeError('max_pipelines_running must be of type int')

        if any(
            argument and not isinstance(argument, str)
            for argument in [external_resource_location, engine_build, scala_binary_version]
        ):
            raise TypeError('external_resource_location, engine_build & scala_binary_version must be of type str')

        if any(argument and not isinstance(argument, list) for argument in [engine_labels, deployment_tags]):
            raise TypeError('engine_labels & deployment_tags must be of type list')

        self._deployment.update(
            {
                'name': deployment_name,
                'engineBuild': engine_build,
                'engineType': engine_type,
                'engineVersion': engine_version,
                'envId': environment.environment_id,
                'scalaBinaryVersion': scala_binary_version,
            }
        )
        self._deployment['engineConfiguration'].update(
            {
                'externalResourcesUri': external_resource_location,
                'labels': engine_labels,
                'maxCpuLoad': max_cpu_load,
                'maxMemoryUsed': max_memory_used,
                'maxPipelinesRunning': max_pipelines_running,
            }
        )
        if environment.environment_type == "AWS":
            self._deployment.update({"sshKeySource": "NONE"})

        deployment = Deployment(self._deployment, self._control_hub)

        if deployment_tags:
            deployment.tags = deployment_tags

        return deployment


@analytics_class_decorator
class Deployments(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Deployment` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization
        self._id_attr = 'deployment_id'

    def _get_all_results_from_api(
        self, deployment_type=None, environment_id=None, tag=None, engine_type=None, deployment_id=None, **kwargs
    ):
        """Args offset, len, order_by, order, tag, with_total_count, state, status, type are not exposed
        directly as arguments because of their limited use by normal users but, could still be specified just like any
        other args with the help of kwargs.

        Args:
            deployment_id (:obj:`str`, optional): ID. Default: ``None``.
            deployment_type (:obj:`str`, optional): Default: ``None``.
            environment_id (:obj:`str`, optional): environment ID. Default: ``None``.
            tag (:obj:`str`, optional): tag. Default: ``None``.
            engine_type (:obj:`str`, optional): ID. Default: ``None``.
            kwargs: optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Deployment` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {
            'offset': None,
            'len': None,
            'order_by': 'LAST_MODIFIED_TIME',
            'order': 'ASC',
            'with_total_count': False,
            'state_display_label': None,
            'status': None,
        }
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if deployment_id is not None:
            try:
                response = [self._control_hub.api_client.get_deployment(deployment_id).response.json()]
            except requests.exceptions.HTTPError:
                raise ValueError('Deployment (deployment_id={}) not found'.format(deployment_id))
        else:
            response = self._control_hub.api_client.get_all_deployments(
                organization=self._organization,
                type=deployment_type,
                environment=environment_id,
                tag=tag,
                engine_type=engine_type,
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                state_display_label=kwargs_unioned['state_display_label'],
                deployment_status=kwargs_unioned['status'],
                with_total_count=kwargs_unioned['with_total_count'],
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Deployment, {'control_hub': self._control_hub})


class DeploymentEngineConfiguration(BaseModel):
    """Model for Deployment engine configuration.


    Attributes:
        advanced_configuration (:obj:`str`):
        aws_image_id (:obj:`str`):
        azure_image_id (:obj:`str`):
        created_by (:obj:`str`): User that created this deployment.
        created_on (:obj:`int`): Time at which this deployment was created.
        download_url (:obj:`list`):
        engine_type (:obj:`list`): engine type.
        engine_version (:obj:`list`): Engine version to deploy.
        id (:obj:`str`): User that created this deployment.
        gcp_image_id (:obj:`str`):
        last_modified_by (:obj:`str`): User that last modified this deployment.
        last_modified_on (:obj:`int`): Time at which this deployment was last modified.
        scala_binary_version (:obj:`str`): scala Binary Version.
        java_configuration (:obj:`DeploymentEngineJavaConfiguration`): Java Configuration instance.
        stage_libs (:obj:`DeploymentStageLibraries`): DeploymentStageLibraries instance.
    """

    _ATTRIBUTES_TO_IGNORE = ['javaConfiguration', 'stageLibs']
    _ATTRIBUTES_TO_REMAP = {
        'created_by': 'creator',
        'created_on': 'createTime',
        'java_configuration': 'jvmConfig',
        'engine_labels': 'labels',
        'external_resource_source': 'externalResourcesUri',
    }
    _REPR_METADATA = ['id', 'engine_type', 'engine_version']

    def __init__(self, deployment_engine_config, deployment=None, control_hub=None):
        super().__init__(
            deployment_engine_config,
            attributes_to_ignore=DeploymentEngineConfiguration._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=DeploymentEngineConfiguration._ATTRIBUTES_TO_REMAP,
            repr_metadata=DeploymentEngineConfiguration._REPR_METADATA,
        )
        self._control_hub = control_hub
        self._deployment = deployment

    @property
    def java_configuration(self):
        return (
            {}
            if self._data.get('jvmConfig', None) is None
            else DeploymentEngineJavaConfiguration(self._data['jvmConfig'], deployment=self._deployment)
        )

    @java_configuration.setter
    def java_configuration(self, value):
        self._data['jvmConfig'] = value
        self._propagate()

    @property
    def advanced_configuration(self):
        return (
            {}
            if self._data.get('advancedConfiguration', None) is None
            else DeploymentEngineAdvancedConfiguration(self._data['advancedConfiguration'], deployment=self._deployment)
        )

    @advanced_configuration.setter
    def advanced_configuration(self, value):
        self._data['advancedConfiguration'] = value
        self._propagate()

    @property
    def stage_libs(self):
        # Pull just the library name out for each stage library, rather than the full canonical library name
        if not self.engine_type and self._data.get('stageLibs') is None:
            raise NotImplementedError(
                "Cannot initialize stage libs as engine_type and engine_version "
                "are not present. Is the object registered on ControlHub?"
            )

        return DeploymentStageLibraries(
            [
                get_stage_library_display_name_from_library(
                    stage_library_name=stage_lib, deployment_type=self.engine_type
                )
                for stage_lib in self._data['stageLibs']
            ],
            self,
        )

    @stage_libs.setter
    def stage_libs(self, libs):
        if not isinstance(libs, list):
            raise ValueError('The libraries provided must be in a list.')

        if not (self.engine_type and self.engine_version):
            raise NotImplementedError(
                "Cannot initialize stage libs as engine_type and engine_version "
                "are not present. Is the object registered on ControlHub?"
            )

        # convert all the stage libs from display format to actual format
        converted_libs = [
            get_stage_library_name_from_display_name(
                stage_library_display_name=display_name,
                deployment_type=self.engine_type,
                deployment_engine_version=self.engine_version,
            )
            for display_name in libs
        ]
        self._data['stageLibs'] = converted_libs

    def _propagate(self):
        if self._deployment:
            self._deployment._data['engineConfiguration'] = self._data


class DeploymentStageLibraries(list):
    """Wrapper class for the list of stage libraries in a deployment.

    Args:
        values (:obj:`list`): A list of stage library names.
        deployment_config (:py:class:`streamsets.sdk.sch_models.DeploymentEngineConfiguration`): The deployment
            engine configuration object that these stage libraries pertain to.
    """

    def __init__(self, values, deployment_config):
        super().__init__(values)
        self._deployment_config = deployment_config

    def _get_full_library_name(self, library_display_name):
        return get_stage_library_name_from_display_name(
            stage_library_display_name=library_display_name,
            deployment_type=self._deployment_config.engine_type,
            deployment_engine_version=self._deployment_config.engine_version,
        )

    def append(self, value):
        # Use super()'s method to throw exceptions when necessary
        super().append(value)
        self._deployment_config._data['stageLibs'].append(self._get_full_library_name(value))

    def extend(self, libs):
        # Use super()'s method to throw exceptions when necessary
        super().extend(libs)
        self._deployment_config._data['stageLibs'].extend([self._get_full_library_name(lib) for lib in libs])

    def remove(self, value):
        # Use super()'s method to throw exceptions when necessary
        # The value to delete may be in 'lib_name:version' format, but only name is stored in stage_libs so we split
        super().remove(value.split(':')[0])
        self._deployment_config._data['stageLibs'].remove(self._get_full_library_name(value))


@analytics_class_decorator
class DeploymentEngineConfigurations(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.DeploymentEngineConfiguration` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
    """

    def _get_all_results_from_api(self, id=None, engine_type='DC', disabled_filter='ONLY_ALLOWED', **kwargs):
        """Args offset, len, order_by, order, tag, with_total_count, state, status, type are not exposed
        directly as arguments because of their limited use by normal users but, could still be specified just like any
        other args with the help of kwargs.

        Args:
            id (:obj:`str`, optional): ID. Default: ``None``.
            deployment_type (:obj:`str`, optional): Default: ``None``.
            environment_id (:obj:`str`, optional): environment ID. Default: ``None``.
            tag (:obj:`str`, optional): tag. Default: ``None``.
            engine_type (:obj:`str`, optional): ID. Default: ``None``.
            disabled_filter (:obj:`str`, optional): Default: ``'ONLY_ALLOWED'``.
            kwargs: optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Deployment` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {
            'offset': None,
            'len': None,
            'order_by': 'CREATE_TIME',
            'order': 'ASC',
            'with_total_count': False,
        }
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if id is not None:
            try:
                response = [self._control_hub.api_client.get_engine_version(id).response.json()]
            except requests.exceptions.HTTPError:
                raise ValueError('DeploymentEngineConfiguration (id={}) not found'.format(id))
        else:
            response = self._control_hub.api_client.get_all_engine_versions(
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                engine_type=engine_type,
                disabled_filter=disabled_filter,
                with_total_count=kwargs_unioned['with_total_count'],
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(
            response, kwargs_unused, DeploymentEngineConfiguration, {'control_hub': self._control_hub}
        )


class DeploymentEngineJavaConfiguration:
    """Model for Deployment engine Java configuration.

    Attributes:
        id (:obj:`str`):
        java_options (:obj:`str`):
        java_memory_strategy (:object:ABSOLUTE/PERCENTAGE)
        maximum_java_heap_size_in_mb (:obj:`long`):
        minimum_java_heap_size_in_mb (:obj:`long`):
        maximum_java_heap_size_in_percent (:obj:`int`):
        minimum_java_heap_size_in_percent (:obj:`int`):
    """

    def __init__(self, deployment_engine_java_configuration, deployment=None):
        self._data = {} if deployment_engine_java_configuration is None else deployment_engine_java_configuration
        self._deployment = deployment

    @property
    def java_options(self):
        return self._data['extraJvmOpts']

    @java_options.setter
    def java_options(self, value):
        self._data['extraJvmOpts'] = value
        self._propagate()

    @property
    def java_memory_strategy(self):
        return self._data['memoryConfigStrategy']

    @java_memory_strategy.setter
    def java_memory_strategy(self, value):
        self._data['memoryConfigStrategy'] = value
        self._propagate()

    @property
    def maximum_java_heap_size_in_mb(self):
        return self._data['jvmMaxMemory']

    @maximum_java_heap_size_in_mb.setter
    def maximum_java_heap_size_in_mb(self, value):
        self._data['jvmMaxMemory'] = value
        self._propagate()

    @property
    def minimum_java_heap_size_in_mb(self):
        return self._data['jvmMinMemory']

    @minimum_java_heap_size_in_mb.setter
    def minimum_java_heap_size_in_mb(self, value):
        self._data['jvmMinMemory'] = value
        self._propagate()

    @property
    def maximum_java_heap_size_in_percent(self):
        return self._data['jvmMaxMemoryPercent']

    @maximum_java_heap_size_in_percent.setter
    def maximum_java_heap_size_in_percent(self, value):
        self._data['jvmMaxMemoryPercent'] = value
        self._propagate()

    @property
    def minimum_java_heap_size_in_percent(self):
        return self._data['jvmMinMemoryPercent']

    @minimum_java_heap_size_in_percent.setter
    def minimum_java_heap_size_in_percent(self, value):
        self._data['jvmMinMemoryPercent'] = value
        self._propagate()

    def _propagate(self):
        if self._deployment is not None:
            self._deployment._data['engineConfiguration']['jvmConfig'] = self._data

    def __repr__(self):
        return str(self._data)

    def __bool__(self):
        return bool(self._data)


class DeploymentEngineAdvancedConfiguration:
    """Model for advanced configuration in Deployment engine configuration.

    Attributes:
        data_collector_configuration (:obj:`dict`): The Data Collector Configuration.
        transformer_configuration (:obj:`dict`): The Transformer Configuration.
        credential_stores (:obj:`dict`) Credential Stores for the Deployment engine configuration.
        proxy_properties (:obj:`dict`): Proxy Properties for the Deployment engine configuration.
        security_policy (:obj:`dict`): Security Policy for the Deployment engine configuration.

    """

    def __init__(self, deployment_engine_advanced_config, deployment=None):
        self._data = {} if deployment_engine_advanced_config is None else json.loads(deployment_engine_advanced_config)
        self._deployment = deployment
        self._engine_type = None if deployment is None else deployment.engine_configuration.engine_type
        self._file_mappings = {
            'security_policy': ('sdc-security.policy' if self._engine_type == 'DC' else 'transformer-security.policy')
        }
        # Handle log4j file mapping according to log4j version
        self._engine_version = None if deployment is None else deployment.engine_configuration.engine_version
        if self._engine_version:
            log4j_version = (
                LOG4J_VERSION_1
                if Version(self._engine_version) < MIN_ENGINE_VERSION_WITH_LOG4J_VER2
                else LOG4J_VERSION_2
            )
            if self._engine_type == 'DC':
                log4j_properties_file = (
                    SDC_LOG4J_VER1_PROPERTIES_FILENAME
                    if log4j_version == LOG4J_VERSION_1
                    else SDC_LOG4J_VER2_PROPERTIES_FILENAME
                )
            elif self._engine_type == 'TF':
                log4j_properties_file = (
                    TRANSFORMER_LOG4J_VER1_PROPERTIES_FILENAME
                    if log4j_version == LOG4J_VERSION_1
                    else TRANSFORMER_LOG4J_VER2_PROPERTIES_FILENAME
                )
            # Set the correct file_name depending on version of log4j
            self._file_mappings['log4j'] = log4j_properties_file

    def __getattr__(self, name):
        if (name == 'log4j' and Version(self._engine_version) < MIN_ENGINE_VERSION_WITH_LOG4J_VER2) or (
            name == 'log4j2' and Version(self._engine_version) >= MIN_ENGINE_VERSION_WITH_LOG4J_VER2
        ):
            return [item['fileContent'] for item in self._data if item['fileName'] == self._file_mappings['log4j']][0]
        raise AttributeError("'DeploymentEngineAdvancedConfiguration' object has no attribute '{}'".format(name))

    def __setattr__(self, name, value):
        if (name == 'log4j' and Version(self._engine_version) < MIN_ENGINE_VERSION_WITH_LOG4J_VER2) or (
            name == 'log4j2' and Version(self._engine_version) >= MIN_ENGINE_VERSION_WITH_LOG4J_VER2
        ):
            self._set_file_content(self._file_mappings['log4j'], value)
            self._propagate()
        else:
            super().__setattr__(name, value)

    def __dir__(self):
        return dir(DeploymentEngineAdvancedConfiguration) + [
            'log4j' if Version(self._engine_version) < MIN_ENGINE_VERSION_WITH_LOG4J_VER2 else 'log4j2'
        ]

    def _set_file_content(self, file_name, value):
        for item in self._data:
            if item['fileName'] == file_name:
                item['fileContent'] = value
                break

    @property
    def data_collector_configuration(self):
        return [item['fileContent'] for item in self._data if item['fileName'] == 'sdc.properties'][0]

    @data_collector_configuration.setter
    def data_collector_configuration(self, value):
        self._set_file_content('sdc.properties', value)
        self._propagate()

    @property
    def transformer_configuration(self):
        return [item['fileContent'] for item in self._data if item['fileName'] == 'transformer.properties'][0]

    @transformer_configuration.setter
    def transformer_configuration(self, value):
        self._set_file_content('transformer.properties', value)
        self._propagate()

    @property
    def credential_stores(self):
        return [item['fileContent'] for item in self._data if item['fileName'] == 'credential-stores.properties'][0]

    @credential_stores.setter
    def credential_stores(self, value):
        self._set_file_content('credential-stores.properties', value)
        self._propagate()

    @property
    def proxy_properties(self):
        return [item['fileContent'] for item in self._data if item['fileName'] == 'proxy.properties'][0]

    @proxy_properties.setter
    def proxy_properties(self, value):
        self._set_file_content('proxy.properties', value)
        self._propagate()

    @property
    def security_policy(self):
        return [
            item['fileContent'] for item in self._data if item['fileName'] == self._file_mappings['security_policy']
        ][0]

    @security_policy.setter
    def security_policy(self, value):
        self._set_file_content(self._file_mappings['security_policy'], value)
        self._propagate()

    def _propagate(self):
        if self._deployment is not None:
            self._deployment._data['engineConfiguration']['advancedConfiguration'] = json.dumps(self._data)

    def __repr__(self):
        return str([item['fileName'] for item in self._data])

    def __bool__(self):
        return bool(self._data)


@analytics_class_decorator
class DeploymentEvents(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.DeploymentEvent` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        deployment_id (:obj:`str`): Deployment Id.
    """

    def __init__(self, control_hub, deployment_id):
        super().__init__(control_hub)
        self._deployment_id = deployment_id

    def _get_all_results_from_api(self, **kwargs):
        """The args for offset, len, and order aren't directly exposed due to their limited use by
        normal users, however they're still accessible via kwargs.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.DeploymentEvent` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.DeploymentEvent`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None, 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.get_deployment_events(
            deployment_id=self._deployment_id,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            order=kwargs_unioned['order'],
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, DeploymentEvent, {})


class DeploymentEvent(BaseModel):
    """Wrapper class for representing DeploymentEvent instances.

    Args:
        deployment_event (:obj:`dict`): JSON representation of a Deployment Event.
    """

    _ATTRIBUTES_TO_IGNORE = ['org', 'cspDeploymentId', 'phase', 'source', 'code']
    _REPR_METADATA = ['time', 'level', 'hostname', 'details']

    def __init__(self, deployment_event):
        super().__init__(
            deployment_event,
            attributes_to_ignore=DeploymentEvent._ATTRIBUTES_TO_IGNORE,
            repr_metadata=DeploymentEvent._REPR_METADATA,
        )


@analytics_class_decorator
class KubernetesAgentEvents(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.KubernetesAgentEvent` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub` in which it is created the Kubernetes
                environment.
        environment_id (:obj:`str`): The Id of the environment, of type Kubernetes, from which agent events will be
            retrieved.
    """

    def __init__(self, control_hub, environment_id):
        super().__init__(control_hub)
        self._environment_id = environment_id

    def _get_all_results_from_api(self, **kwargs):
        """The args for offset, len, and order aren't directly exposed due to their limited use by
        normal users, however they're still accessible via kwargs.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:obj:`dict`): Including the following key-value pairs:

                    len (:obj:`int`): Length of the current page downloaded from the API (i.e., number of events)
                    offset (:obj:`int`): Offset of the current page downloaded from the API.
                    totalCount (:obj:`int`): Total number of events, regardless of API response pagination.
                    data (:obj:`int`): a list of :py:class:`streamsets.sdk.sch_models.KubernetesAgentEvent` instances
                        in JSON format, containing each of the downloaded (in the current API response page) events.

                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.KubernetesAgentEvent`): type of class to instantiate.
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init.
        """
        kwargs_defaults = {'offset': None, 'len': None, 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.get_kubernetes_environment_agent_events(
            environment_id=self._environment_id,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            order=kwargs_unioned['order'],
        ).response.json()

        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, KubernetesAgentEvent, {})


class KubernetesAgentEvent(BaseModel):
    """Wrapper class for representing Kubernetes Agent Event instances.

    Args:
        environment_event (:obj:`dict`): JSON representation of a Kubernetes Agent Event.
    """

    _ATTRIBUTES_TO_IGNORE = ['code', 'cspDeploymentId', 'kubernetesAgentId', 'org', 'phase', 'source', 'sourceType']
    _ATTRIBUTES_TO_REMAP = {'timestamp': 'time'}
    _REPR_METADATA = ['timestamp', 'level', 'details']

    def __init__(self, environment_event):
        super().__init__(
            environment_event,
            attributes_to_ignore=KubernetesAgentEvent._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=KubernetesAgentEvent._ATTRIBUTES_TO_REMAP,
            repr_metadata=KubernetesAgentEvent._REPR_METADATA,
        )


class ClassificationRuleBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ClassificationRule`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_classification_rule_builder`.

    Args:
        classification_rule (:obj:`dict`): Python object defining a classification rule.
        classifier (:obj:`dict`): Python object defining a classifier.
    """

    def __init__(self, classification_rule, classifier):
        self._classification_rule = classification_rule
        self._classifier = classifier
        self.classifiers = []

    def add_classifier(self, patterns=None, match_with=None, regular_expression_type='RE2/J', case_sensitive=False):
        """Add classifier to the classification rule.

        Args:
            patterns (:obj:`list`, optional): List of strings of patterns. Default: ``None``.
            match_with (:obj:`str`, optional): Default: ``None``.
            regular_expression_type (:obj:`str`, optional): Default: ``'RE2/J'``.
            case_sensitive (:obj:`bool`, optional): Default: ``False``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Classifier`.
        """
        classifier = Classifier(classifier=copy.deepcopy(self._classifier))
        classifier.patterns = patterns or ['.*']
        classifier.match_with = Classifier.MATCH_WITH_ENUM.get(match_with) or 'FIELD_PATH'
        classifier.regular_expression_type = Classifier.REGULAR_EXPRESSION_TYPE_ENUM.get(regular_expression_type)
        classifier.case_sensitive = case_sensitive

        classifier._uuid = str(uuid.uuid4())
        classifier._id = '{}:1'.format(classifier._uuid)
        classifier._rule_uuid = self._classification_rule['uuid']
        self.classifiers.append(classifier)
        return classifier

    def build(self, name, category, score):
        """Build the classification rule.

        Args:
            name (:obj:`str`): Classification Rule name.
            category (:obj:`str`): Classification Rule category.
            score (:obj:`float`): Classification Rule score.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ClassificationRule`.
        """
        classification_rule = ClassificationRule(
            classification_rule=self._classification_rule, classifiers=self.classifiers
        )
        classification_rule.name = name
        classification_rule.category = category
        classification_rule.score = score
        return classification_rule


class ProtectionPolicy(UiMetadataBaseModel):
    """Model for Protection Policy.

    Args:
        protection_policy (:obj:`dict`): JSON representation of Protection Policy.
        procedures (:obj:`list`): A list of :py:class:`streamsets.sdk.sch_models.PolicyProcedure` instances,
                    Default: ``None``.

    Attributes:
        procedures (:obj:`PolicyProcedure`): Procedures for the Protection Policy.
        default_setting (:obj:`str`): Sefault Setting for the Protection Policy.
        enactment (:obj:`str`) Enactment for the Protection Policy.
        sampling (:obj:`str`): Sampling for the Protection Policy.
    """

    _ATTRIBUTES_TO_IGNORE = ['enactment', 'defaultSetting', 'procedures']
    _ATTRIBUTES_TO_REMAP = {}
    _REPR_METADATA = ['name']

    # The DEFAULT_POLICY_ENUM supportes mapping for both the 'enactment'
    # property (used prior to ControlHub/SDP 3.14) and the new defaultSetting property
    # that has been introducted starting ControlHub/SDP 3.14
    DEFAULT_POLICY_ENUM = {'No': 'NO', 'Read': 'READ', 'Write': 'WRITE', 'Both': 'BOTH'}

    SAMPLING_ENUM = {
        'Only new Field Paths': 'NEW_PATHS',
        'First Record of Every Batch': 'FIRST_BATCH_RECORD',
        'Random Sample of Records': 'RANDOM_SAMPLE',
        'All records': 'ALL_RECORDS',
        'No records': 'NONE',
    }

    def __init__(self, protection_policy, procedures=None):
        super().__init__(
            protection_policy,
            attributes_to_ignore=ProtectionPolicy._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=ProtectionPolicy._ATTRIBUTES_TO_REMAP,
            repr_metadata=ProtectionPolicy._REPR_METADATA,
        )
        self._procedures = procedures

    @property
    def procedures(self):
        if self._procedures is not None:
            return self._procedures
        if self._data['procedures']:
            return [PolicyProcedure(procedure) for procedure in self._data['procedures']]
        return None

    @property
    def _id(self):
        return self._data['id']

    @_id.setter
    def _id(self, value):
        self._data['id'] = value

    @property
    def default_setting(self):
        # The defaultSetting property only existed in the ControlHub/SDP version 3.14
        # or later.  The SDK supports versions prior to that as well.  So first
        # check and see if the defaultSetting property exists before attempting
        # to return it.
        if 'defaultSetting' in self._data:
            return next(
                (
                    k
                    for k, v in ProtectionPolicy.DEFAULT_POLICY_ENUM.items()
                    if v == self._data['defaultSetting']['value']
                ),
                None,
            )

    @property
    def enactment(self):
        # The enactment property only existed in the ControlHub/SDP versions prior to 3.14
        # The SDK supports older and newer versions. So first check and see if the
        # enactment property exists before attempting to return it.
        if 'enactment' in self._data:
            return next(
                (k for k, v in ProtectionPolicy.DEFAULT_POLICY_ENUM.items() if v == self._data['enactment']['value']),
                None,
            )

    @enactment.setter
    def enactment(self, value):
        self._data['enactment']['value'] = value

    @property
    def sampling(self):
        if 'sampling' in self._data:
            return next(
                (k for k, v in ProtectionPolicy.SAMPLING_ENUM.items() if v == self._data['sampling']['value']), None
            )

    @sampling.setter
    def sampling(self, value):
        if value in ProtectionPolicy.SAMPLING_ENUM:
            self._data['sampling'] = ProtectionPolicy.SAMPLING_ENUM.get(value)
        else:
            raise ValueError('Unknown sampling type ({})'.format(value))


@analytics_class_decorator
class ProtectionPolicies(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.ProtectionPolicy` instances."""

    def _get_all_results_from_api(self, **kwargs):
        """
        Args:
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.ProtectionPolicy` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        protection_policies = []
        response = self._control_hub.api_client.get_protection_policy_list().response.json()['response']
        for protection_policy in response:
            protection_policy['data'].pop('messages', None)
            protection_policies.append(ProtectionPolicy(protection_policy['data']))
        return ModelCollectionResults(SeekableList(protection_policies), kwargs)


class ProtectionPolicyBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ProtectionPolicy`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_protection_policy_builder`.

    Args:
        protection_policy (:obj:`dict`): Python object defining a protection policy.
        policy_procedure (:obj:`dict`): Python object defining a policy procedure.
    """

    def __init__(self, control_hub, protection_policy, policy_procedure):
        self._control_hub = control_hub
        self._protection_policy = protection_policy
        self._policy_procedure = policy_procedure
        self.procedures = []

    def add_procedure(
        self,
        classification_score_threshold=0.5,
        procedure_basis='Category Pattern',
        classification_category_pattern=None,
        field_path=None,
        protection_method=None,
    ):
        procedure = PolicyProcedure(policy_procedure=copy.deepcopy(self._policy_procedure))
        procedure.classification_score_threshold = classification_score_threshold
        if PolicyProcedure._ATTRIBUTES_TO_REMAP['procedure_basis'] in procedure._data:
            procedure.procedure_basis = PolicyProcedure.PROCEDURE_BASIS_ENUM.get(procedure_basis)
        if procedure_basis == 'Category Pattern':
            procedure.classification_category_pattern = classification_category_pattern
        elif procedure_basis == 'Field Path':
            procedure.field_path = field_path
        # https://git.io/fAE0K
        procedure.protection_method = json.dumps(
            {'issues': None, 'schemaVersion': 1, 'stageConfiguration': protection_method._data}
        )

        self.procedures.append(procedure)

    def build(self, name, enactment=None, sampling='All records'):
        protection_policy = ProtectionPolicy(self._protection_policy, self.procedures)
        protection_policy.name = name
        protection_policy.sampling = ProtectionPolicy.SAMPLING_ENUM.get(sampling)
        # The enactment property is only valid for versions before 3.14.  Check
        # if the ControlHub/SDP version if below 3.14 before setting the enactment
        # property.
        if Version(self._control_hub.version) < Version('3.14.0') and enactment is not None:
            protection_policy.enactment = ProtectionPolicy.DEFAULT_POLICY_ENUM.get(enactment)

        return protection_policy


class PolicyProcedure(UiMetadataBaseModel):
    """Model for Policy Procedure.

    Args:
        policy_procedure (:obj:`dict`): JSON representation of Policy Procedure.
    """

    PROCEDURE_BASIS_ENUM = {'Category Pattern': 'CATEGORY_PATTERN', 'Field Path': 'FIELD_PATH'}

    _ATTRIBUTES_TO_IGNORE = ['id', 'optimisticLockVersion', 'version']
    _ATTRIBUTES_TO_REMAP = {
        'classification_category_pattern': 'classificationCategory',
        'classification_score_threshold': 'threshold',
        'procedure_basis': 'subjectType',
        'protection_method': 'transformerConfig',
    }

    def __init__(self, policy_procedure):
        super().__init__(
            policy_procedure,
            attributes_to_ignore=PolicyProcedure._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=PolicyProcedure._ATTRIBUTES_TO_REMAP,
        )

    @property
    def _id(self):
        return self._data['id']

    @_id.setter
    def _id(self, value):
        self._data['id'] = value

    @property
    def _policy_id(self):
        return self._data['policyId']

    @_policy_id.setter
    def _policy_id(self, value):
        self._data['policyId'] = value


class ProtectionMethod(SchSdcStage):
    """Protection Method Model.

    Args:
        stage (:obj:`dict`): JSON representation of a stage.
    """

    STAGE_LIBRARY = 'streamsets-datacollector-dataprotector-lib'
    CRYPTO_STAGE_LIBRARY = 'streamsets-datacollector-crypto-lib'

    def __init__(self, stage):
        super().__init__(stage, label=stage['uiInfo']['label'])


class ProtectionMethodBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ProtectionMethod`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_protection_method_builder`.

    Args:
        pipeline_builder (:py:class:`streamsets.sdk.sch_models.PipelineBuilder`): Pipeline Builder object.
    """

    def __init__(self, pipeline_builder):
        self._pipeline_builder = pipeline_builder

    def build(self, method, library=ProtectionMethod.STAGE_LIBRARY):
        method_stage = self._pipeline_builder.add_stage(label=method, library=library)
        # We generate a single output lane to conform to SDP's expectations for detached stages.
        method_stage.add_output()
        protection_method = type(
            method_stage.stage_name, (ProtectionMethod,), {'_attributes': method_stage._attributes}
        )
        return protection_method(method_stage._data)


class ReportDefinitions(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ReportDefinition` instances."""

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """Args order_by, order, filter_text, len, offset are not exposed directly as arguments because of their limited
        use by normal users but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.ReportDefinition` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'order_by': 'NAME', 'order': 'ASC', 'filter_text': None, 'offset': 0, 'len': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.return_all_report_definitions(
            organization=organization,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            order_by=kwargs_unioned['order_by'],
            order=kwargs_unioned['order'],
            filter_text=kwargs_unioned['filter_text'],
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ReportDefinition, {'control_hub': self._control_hub})


class ReportDefinition(BaseModel):
    """Model for Report Definition.

    Args:
        report_definition (:obj:`dict`): JSON representation of Report Definition.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub instance.

    Attributes:
        reports (:py:class:`streamsets.sdk.sch_models.Reports`): An instance of Reports.
        report_resources (:py:class:`streamsets.sdk.sch_models.ReportResources`): An instance of Report Resources.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): The Report Definition ACL instance.
    """

    _REPR_METADATA = ['id', 'name']

    def __init__(self, report_definition, control_hub):
        super().__init__(report_definition, repr_metadata=ReportDefinition._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def reports(self):
        """Get Reports of the Report Definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Reports`.
        """
        return Reports(self._control_hub, self.id)

    @property
    def report_resources(self):
        """Get Report Resources of the Report Definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ReportResources`.
        """
        return ReportResources(self._data['reportArtifacts'], self)

    def generate_report(self):
        """Generate a Report for Report Definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Report`.
        """
        trigger_time = int(round(time.time() * 1000))
        return GenerateReportCommand(
            self._control_hub,
            self,
            self._control_hub.api_client.generate_report_for_report_definition(self.id, trigger_time).response.json(),
        )

    @property
    def acl(self):
        """Get Report Definition ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(
            self._control_hub.api_client.get_report_definition_acl(report_definition_id=self.id).response.json(),
            self._control_hub,
        )

    @acl.setter
    def acl(self, report_definition_acl):
        """Update Report Definition ACL.

        Args:
            report_definition_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The Report Definition ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.set_report_definition_acl(
            report_definition_id=self.id, report_definition_acl_json=report_definition_acl._data
        )


class GenerateReportCommand:
    """Command to interact with the response from generate_report.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub instance.
        report_definition (:obj:`dict`): JSON representation of Report Definition.
        response (:obj:`dict`): Api response from generating the report.

    Attributes:
        report (:py:class:`streamsets.sdk.sch_models.Report`): An instance of Report.
    """

    def __init__(self, control_hub, report_defintion, response):
        self._control_hub = control_hub
        self._report_defintion = report_defintion
        self.response = response

    @property
    def report(self):
        report = self._report_defintion.reports.get(id=self.response['id'])
        self.response = report._data
        if report.report_status == 'REPORT_TO_BE_GENERATED':
            logger.warning('Report is still being generated...')
        elif report.report_status == 'REPORT_SUCCESS':
            return Report(report, self._control_hub, self._report_defintion.id)
        else:
            raise Exception('Report generation failed with status {}'.format(report.report_status))


class ReportResources:
    """Model for the collection of Report Resources.

    Args:
        report_resources (:obj:`list`): List of Report Resources.
        report_definition (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Report Definition object.
    """

    def __init__(self, report_resources, report_definition):
        self._report_resources = SeekableList(ReportResource(report_resource) for report_resource in report_resources)
        self._report_definition = report_definition

    def get(self, **kwargs):
        return self._report_resources.get(**kwargs)

    def get_all(self, **kwargs):
        return self._report_resources.get_all(**kwargs)

    def __iter__(self):
        for report_resource in self._report_resources:
            yield report_resource

    def __len__(self):
        return len(self._report_resources)

    def __getitem__(self, i):
        return self._report_resources[i]

    def __contains__(self, resource):
        """Check if given resource is in Report Definition resources.

        Args:
            resource (:py:class:streamsets.sdk.sch_models.Job) or (:py:class:streamsets.sdk.sch_models.Topology)

        Returns:
            A :obj:`boolean` indicating if the resource exists.
        """
        assert isinstance(resource, Job) or isinstance(resource, Topology), "Only Job and Topology are supported"
        if isinstance(resource, Job):
            resource_id = resource.job_id
            resource_type = 'JOB'
        else:
            resource_id = resource.commit_id
            resource_type = 'TOPOLOGY'
        for resource in self._report_resources:
            if resource.resource_id == resource_id and resource.resource_type == resource_type:
                return True
        return False

    def __repr__(self):
        return str(self._report_resources)


class ReportResource(BaseModel):
    """Model for Report Resource.

    Args:
        report_resource (:obj:`dict`): JSON representation of Report Resource.
    """

    _REPR_METADATA = ['resource_type', 'resource_id']

    def __init__(self, report_resource):
        super().__init__(report_resource, repr_metadata=ReportResource._REPR_METADATA)


class ReportDefinitionBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ReportDefinition`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_report_definition_builder`.

    Args:
        report_definition (:obj:`dict`): JSON representation of Report Definition.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub instance.
    """

    def __init__(self, report_definition, control_hub):
        self._report_definition = report_definition
        self._report_resources = SeekableList()
        self._control_hub = control_hub

    def import_report_definition(self, report_definition):
        """Import an existing Report Definition to update it.

        Args:
            report_definition (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Report Definition object.
        """
        self._report_definition = report_definition._data
        self._report_resources = SeekableList(
            ReportResource(report_resource) for report_resource in report_definition._data['reportArtifacts']
        )

    def set_data_retrieval_period(self, start_time, end_time):
        """Set Time range over which the report will be generated.

        Args:
            start_time (:obj:`str`) or (:obj:`int`): Absolute or relative start time for the Report.
            end_time (:obj:`str`) or (:obj:`int`): Absolute or relative end time for the Report.
        """
        self._report_definition.update({'startTime': start_time, 'endTime': end_time})

    def add_report_resource(self, resource):
        """Add a given resource to Report Definition resources.

        Args:
            resource (:py:class:`streamsets.sdk.sch_models.Job`) or (:py:class:`streamsets.sdk.sch_models.Topology`)
        """
        if isinstance(resource, Job):
            self._report_resources.append(ReportResource({'resourceId': resource.job_id, 'resourceType': 'JOB'}))
        elif isinstance(resource, Topology):
            self._report_resources.append(
                ReportResource({'resourceId': resource.commit_id, 'resourceType': 'TOPOLOGY'})
            )
        if self._report_definition is not None:
            self._report_definition['reportArtifacts'] = SeekableList(
                report_resource._data for report_resource in self._report_resources
            )

    def remove_report_resource(self, resource):
        """Remove a resource from Report Definition Resources.

        Args:
            resource (:py:class:`streamsets.sdk.sch_models.Job`) or (:py:class:`streamsets.sdk.sch_models.Topology`)

        Returns:
            A resource of type :py:obj:`dict` that is removed from Report Definition Resources.
        """
        if isinstance(resource, Job):
            resource_type = 'JOB'
            resource_id = resource.job_id
        elif isinstance(resource, Topology):
            resource_type = 'TOPOLOGY'
            resource_id = resource.commit_id

        popped = self._report_resources.get(resource_type=resource_type, resource_id=resource_id)
        self._report_resources = SeekableList(
            i for i in self._report_resources if any(getattr(i, k) != v for k, v in popped._data.items())
        )
        if self._report_definition is not None:
            self._report_definition['reportArtifacts'] = SeekableList(
                report_resource._data for report_resource in self._report_resources
            )
        return popped

    def build(self, name, description=None):
        """Build the report definition.

        Args:
            name (:obj:`str`): Name of the Report Definition.
            description (:obj:`str`, optional): Description of the Report Definition. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ReportDefinition`.
        """
        self._report_definition.update({'name': name, 'description': description})
        return ReportDefinition(self._report_definition, self._control_hub)


class Reports(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Report` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
        report_definition_id (:obj:`str`): Report Definition Id.
    """

    def __init__(self, control_hub, report_definition_id):
        super().__init__(control_hub)
        self._report_definition_id = report_definition_id

    def _get_all_results_from_api(self, id=None, **kwargs):
        """Get Reports belonging to a Report Definition. Args offset, len are not exposed directly as arguments because
        of their limited use by normal users but, could still be specified just like any other args with the help of
        kwargs.

        Args:
            id (:obj:`str`, optional): Report Id. Default: ``None``. If specified, only that particular report is
                                       fetched from ControlHub. If not, all reports belonging to this
                                       Report Definition will be fetched and other filters will be applied later.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Report` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Report`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if self._report_definition_id is not None:
            if id is None:
                report_ids = [
                    report['id']
                    for report in self._control_hub.api_client.return_all_reports_from_definition(
                        report_definition_id=self._report_definition_id,
                        offset=kwargs_unioned['offset'],
                        len=kwargs_unioned['len'],
                    ).response.json()['data']
                ]
            else:
                report_ids = [id]
            response = [
                self._control_hub.api_client.get_report_for_given_report_id(
                    self._report_definition_id, report_id
                ).response.json()
                for report_id in report_ids
            ]
        else:
            response = []
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(
            response,
            kwargs_unused,
            Report,
            {'control_hub': self._control_hub, 'report_definition_id': self._report_definition_id},
        )


class Report(BaseModel):
    """Model for Report.

    Args:
        report (:obj:`dict`): JSON representation of Report.
    """

    _REPR_METADATA = ['id', 'name']

    def __init__(self, report, control_hub, report_definition_id):
        super().__init__(report, repr_metadata=Report._REPR_METADATA)
        self._control_hub = control_hub
        self._report_definition_id = report_definition_id

    def download(self):
        """Download the Report in PDF format

        Returns:
            An instance of :obj:`bytes`.
        """
        return self._control_hub.api_client.download_report(self._report_definition_id, self.id, 'PDF').response.content


class SAQLSearch(BaseModel):
    """Model for SAQL Searches.

    Args:
        saql_search_json (:obj:`dict`): The SAQL Search JSON.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.

    Attributes:
        id (:obj:`str`): ID of the SAQL Search.
        orgId (:obj:`str`): ID of the Organization.
        type (:obj:`str`): Type of SAQL search.
        name (:obj:`str`): Name of SAQL search.
        mode (:obj:`str`): Mode of SAQL search.
        query (:obj:`str`): SAQL search query.
        creator (:obj:`str`): Creator of SAQL search.
        createTime (:obj:`str`): Time of creation of SAQL search.
        lastModifiedBy (:obj:`str`): Last author to modify SAQL search.
        lastModifiedOn (:obj:`str`): Last Time of modification of SAQL search.
        favorite (:obj:`boolean`):  Represents whether an SAQL Search is marked as a favorite or not.

    Returns:
        An instance of :py:class:`streamsets.sdk.sch_models.SAQLSearch`.
    """

    _REPR_METADATA = ['id', 'name', 'mode', 'create_time']
    _ATTRIBUTES_TO_IGNORE = ['favorite']

    class ModeType(enum.Enum):
        BASIC = 'BASIC'
        ADVANCED = 'ADVANCED'

        @classmethod
        def has_value(cls, value):
            return value in cls._member_names_

    class PipelineType(enum.Enum):
        PIPELINE = 'PIPELINE'
        FRAGMENT = 'FRAGMENT'

        @classmethod
        def has_value(cls, value):
            return value in cls._member_names_

    class JobType(enum.Enum):
        JOB_INSTANCE = 'JOB_INSTANCE'
        JOB_TEMPLATE = 'JOB_TEMPLATE'
        JOB_DRAFT_RUN = 'JOB_DRAFT_RUN'
        JOB_RUN = 'JOB_RUN'
        JOB_SEQUENCE = 'JOB_SEQUENCE'

        @classmethod
        def has_value(cls, value):
            return value in cls._member_names_

    def __init__(self, saql_search_json, control_hub):
        super().__init__(
            saql_search_json,
            repr_metadata=SAQLSearch._REPR_METADATA,
            attributes_to_ignore=SAQLSearch._ATTRIBUTES_TO_IGNORE,
        )
        self._control_hub = control_hub

    def _decode_basic_query(self):
        """
        Decodes a query in basic mode into a query advanced mode.
        """
        operator_map = {
            'contains': '{} == "*{}*"',
            'is': '{} == "{}"',
            'is not': '{} != "{}"',
            'begins with': '{} == "{}*"',
            'ends with': '{} == "*{}"',
            '>': '{} =gt= {}',
            '<': '{} =lt= {}',
            '>=': '{} =ge= {}',
            '<=': '{} =le= {}',
            '==': '{} == "{}"',
            '!=': '{} != "{}"',
        }
        operators_with_only_query_name_map = {
            'is empty': '{} =null= true',
            'is not empty': '{} =null= false',
            'is true': '{} == true',
            'is false': '{} == false',
        }
        operator_includes_map = {'includes': '{} =in= ({})', 'not includes': '{} =out= ({})'}
        operator_date_map = {
            'is after': '{} =gt= "{}"',
            'is before': '{} =lt= "{}"',
            'is after or on': '{} =ge= "{}"',
            'is on or before': '{} =le= "{}"',
        }

        query = json.loads(self._data['query'])
        query_strings = []
        prev_query_condition_combiner = ''

        for property_filter in query:
            property_name = property_filter['filter']['name'].lower()
            property_operator = property_filter['operator'].lower()
            property_value = property_filter['value']
            property_condition_combiner = property_filter['conditionCombiner']

            if property_operator in operators_with_only_query_name_map:
                string_to_append = operators_with_only_query_name_map[property_operator].format(property_name)
            elif property_operator in operator_map:
                string_to_append = operator_map[property_operator].format(property_name, property_value)
            elif property_operator in operator_includes_map:
                string_to_append = operator_includes_map[property_operator].format(
                    property_name, ','.join(value for value in property_value)
                )
            elif property_operator in operator_date_map:
                string_to_append = operator_date_map[property_operator].format(
                    property_name, property_value.split('T')[0]
                )
            else:
                raise ValueError("Invalid Operator: {}".format(property_operator))

            query_strings.append(
                string_to_append
                if not prev_query_condition_combiner
                else ' {} {}'.format(prev_query_condition_combiner.lower(), string_to_append)
            )
            prev_query_condition_combiner = property_condition_combiner
        query = ''.join(query_strings)
        return query

    @property
    def favorite(self):
        return self._data['favorite']['favorite']

    # TODO: Refactor so we do not call _decode_basic_query everytime
    @property
    def query(self):
        if self.mode == SAQLSearch.ModeType.BASIC.value:
            return self._decode_basic_query()
        return self._data['query']


@analytics_class_decorator
class SAQLSearches(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.SAQLSearch` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
        saql_search_type (:py:class:`streamsets.sdk.sch_models.SAQLSearch.PipelineType`) or
                         (:py:class:`streamsets.sdk.sch_models.SAQLSearch.JobType`) Enum of the SAQL search type,
                          limited to: ``'PIPELINE'``, `'FRAGMENT'``,``'JOB_INSTANCE'``, ``'JOB_TEMPLATE'``
                          and ``'JOB_DRAFT_RUN'``.
    """

    def __init__(self, control_hub, saql_search_type):
        super().__init__(control_hub)
        self._saql_search_type = saql_search_type

    def _get_all_results_from_api(self, name=None, **kwargs):
        """Get all saql searches for a particular saql_search_type.

        Args:
            name (:obj:`str`, optional) Name of SAQL search object. Default: ``None``.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.SAQLSearch` instances
                    in JSON format.
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
                class_type (:py:class:`streamsets.sdk.sch_models.SAQLSearch`): the type of class to instantiate.
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init.
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order_by': "ASC"}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()

        if name and not isinstance(name, str):
            raise TypeError("Name must be a string.")

        if self._saql_search_type in SAQLSearch.PipelineType:
            response = self._control_hub.api_client.get_saql_pipeline_searches(
                name,
                self._saql_search_type.value,
                kwargs_unioned['offset'],
                kwargs_unioned['len'],
                kwargs_unioned['order_by'],
            ).response.json()
        elif self._saql_search_type in SAQLSearch.JobType:
            response = self._control_hub.api_client.get_saql_job_searches(
                name,
                self._saql_search_type.value,
                kwargs_unioned['offset'],
                kwargs_unioned['len'],
                kwargs_unioned['order_by'],
            ).response.json()
        else:
            raise TypeError(
                "SDK method for type: {} has not yet been implemented.".format(self._saql_search_type.value)
            )

        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, SAQLSearch, {'control_hub': self._control_hub})


class SAQLSearchBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.SAQLSearch`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_saql_search_builder`.

    Args:
        saql_search (:obj:`dict`): Python object built from expected SAQL JSON structure
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
        mode (:py:obj:`str`, optional): mode of SAQL Search. Default: ``'BASIC'``
    """

    TYPE_PROPERTY_NAME_MAP = {
        SAQLSearch.PipelineType.PIPELINE.value: (
            'commit_message',
            'committed_by',
            'committed_on',
            'description',
            'draft',
            'engine_type',
            'engine_version',
            'execution_mode',
            'id',
            'label',
            'modified_by',
            'modified_on',
            'latest_version',
            'name',
            'version',
        ),
        SAQLSearch.PipelineType.FRAGMENT.value: (
            'commit_message',
            'committed_by',
            'committed_on',
            'description',
            'draft',
            'engine_type',
            'engine_version',
            'execution_mode',
            'id',
            'label',
            'modified_by',
            'modified_on',
            'latest_version',
            'name',
            'version',
        ),
        SAQLSearch.JobType.JOB_TEMPLATE.value: (
            'archived',
            'created_by',
            'created_on',
            'description',
            'engine_label',
            'engine_type',
            'failover',
            'id',
            'instances',
            'modified_by',
            'modified_on',
            'name',
            'pipeline_name',
            'pipeline_version',
            'tag',
        ),
        SAQLSearch.JobType.JOB_INSTANCE.value: (
            'created_by',
            'created_on',
            'description',
            'engine_label',
            'engine_type',
            'failover',
            'attached_to_template',
            'id',
            'instances',
            'status',
            'color',
            'modified_by',
            'modified_on',
            'name',
            'pipeline_name',
            'pipeline_status',
            'pipeline_version',
            'tag',
        ),
        SAQLSearch.JobType.JOB_DRAFT_RUN.value: (
            'created_by',
            'created_on',
            'engine_type',
            'id',
            'status',
            'color',
            'modified_by',
            'modified_on',
            'name',
            'pipeline_name',
            'pipeline_status',
            'pipeline_version',
        ),
        SAQLSearch.JobType.JOB_RUN.value: (
            'id',
            'previous_id',
            'pipeline_commit_id',
            'run_count',
            'color',
            'status',
            'start_time',
            'finish_time',
            'error_message',
            'input_record_count',
            'output_record_count',
            'error_record_count',
            'current_retry_count',
        ),
        SAQLSearch.JobType.JOB_SEQUENCE.value: (
            'id',
            'name',
            'description',
            'organization',
            'createdBy',
            'createdByEmail',
            'createdByName',
            'createTime',
            'lastModifiedBy',
            'lastModifiedByEmail',
            'lastModifiedByName',
            'lastModifiedTime',
            'startTimeEnabled',
            'startTime',
            'repeatEnabled',
            'crontabMask',
            'endTimeCondition',
            'endTime',
            'timezone',
            'status',
            'lastRunTime',
            'nextRunTime',
            'stepcount',
            'runCount',
            'jobList',
        ),
    }

    OPERATOR_VALUES = (
        'contains',
        'is',
        'is not',
        'begins with',
        'ends with',
        '>',
        '<',
        '>=',
        '<=',
        '==',
        '!=',
        'is empty',
        'is not empty',
        'is true',
        'is false',
        'includes',
        'not includes',
        'is after',
        'is before',
        'is after or on',
        'is on or before',
    )

    def __init__(self, saql_search, control_hub, mode='BASIC'):
        self._saql_search = saql_search
        self._control_hub = control_hub
        self._mode = mode
        self.query = []

    def add_filter(
        self, property_name='name', property_operator='contains', property_value='', property_condition_combiner='AND'
    ):
        """Adds a filter to the SAQL Search Query.

        Args:
            property_name (:py:obj:`str`, optional): Default: ``'name'``
            property_operator (:py:obj:`str`, optional): Default: ``'contains'``
            property_value (:py:obj:`str`, optional): Default: ``''``
            property_condition_combiner (:py:obj:`str`, optional): Default: ``'AND'``
        """
        if self._mode == SAQLSearch.ModeType.ADVANCED.value:
            raise ValueError(
                "Cannot use the SAQLSearchBuilder.add_filter method in ADVANCED mode,"
                " please switch to BASIC mode to use this method."
            )
        if not all(
            isinstance(parameter, str)
            for parameter in [property_name, property_operator, property_value, property_condition_combiner]
        ):
            raise TypeError(
                "property_name, property_operator, property_value & property_condition_combiner must be strings"
            )

        property_name, property_operator = property_name.lower(), property_operator.lower()

        available_property_names = SAQLSearchBuilder.TYPE_PROPERTY_NAME_MAP[self._saql_search['type']]
        if property_name not in available_property_names:
            raise ValueError(
                '{} is not an accepted property name value, the available values for {} are: {}'.format(
                    property_name, self._saql_search['type'], available_property_names
                )
            )
        available_operators = SAQLSearchBuilder.OPERATOR_VALUES
        if property_operator not in available_operators:
            raise ValueError(
                '{} is not an accepted operator value, the available values are: {}'.format(
                    property_operator, available_operators
                )
            )

        query_filter = {
            "filter": {"name": property_name},
            "operator": property_operator,
            "value": property_value,
            "conditionCombiner": property_condition_combiner,
        }
        self.query.append(query_filter)

    def build(self, name):
        """Builder for SAQL Search.

        Args:
            name (:py:obj:`str`): Name of SAQL Search.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.SAQLSearch`.
        """

        if not self.query:
            if self._mode == SAQLSearch.ModeType.BASIC.value:
                self.add_filter()
            else:
                self.query = ""

        if not isinstance(name, str):
            raise TypeError('name should be of type string')

        self._saql_search.update(
            {
                "id": None,
                "creator": None,
                "name": name,
                "query": json.dumps(self.query) if self._mode == SAQLSearch.ModeType.BASIC.value else self.query,
            }
        )

        return SAQLSearch(self._saql_search, self._control_hub)


class ScheduledTaskBaseModel(BaseModel):
    """Base Model for Scheduled Task related classes."""

    def __getattr__(self, name):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            return (
                self._data[remapped_name]['value']
                if 'value' in self._data[remapped_name]
                else self._data[remapped_name]
            )
        elif (
            name_ in self._data
            and name not in self._attributes_to_ignore
            and name not in self._attributes_to_remap.values()
        ):
            return self._data[name_]['value'] if 'value' in self._data[name_] else self._data[name_]
        raise AttributeError('Could not find attribute {}.'.format(name_))

    def __setattr__(self, name, value):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            if 'value' in self._data[remapped_name]:
                self._data[remapped_name]['value'] = value
            else:
                self._data[remapped_name] = value
        elif (
            name_ in self._data
            and name not in self._attributes_to_ignore
            and name not in self._attributes_to_remap.values()
        ):
            if 'value' in self._data[name_]:
                self._data[name_]['value'] = value
            else:
                self._data[name_] = value
        else:
            super().__setattr__(name, value)


@analytics_class_decorator
class ScheduledTaskBuilder:
    """Builder for Scheduled Task.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_scheduled_task_builder`.

    Args:
        job_selection_types (:py:obj:`dict`): JSON representation of job selection types.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub instance.
    """

    def __init__(self, job_selection_types, control_hub):
        self._job_selection_types = job_selection_types
        self._control_hub = control_hub

    def build(
        self,
        task_object,
        action='START',
        name=None,
        description=None,
        cron_expression='0 0 1/1 * ? *',
        time_zone='UTC',
        status='RUNNING',
        start_time=None,
        end_time=None,
        missed_execution_handling='IGNORE',
    ):
        """Builder for Scheduled Task.

        Args:
            task_object (:py:class:`streamsets.sdk.sch_models.Job`) or
                        (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Job or ReportDefinition object.
            action (:obj:`str`, optional): One of the {'START', 'STOP', 'UPGRADE'} actions. Default: ``START``.
            name (:obj:`str`, optional): Name of the task. Default: ``None``.
            description (:obj:`str`, optional): Description of the task. Default: ``None``.
            crontab_mask (:obj:`str`, optional): Schedule in cron syntax. Default: ``"0 0 1/1 * ? *"``. (Daily at 12).
            time_zone (:obj:`str`, optional): Time zone. Default: ``"UTC"``.
            status (:obj:`str`, optional): One of the {'RUNNING', 'PAUSED'} statuses. Default: ``RUNNING``.
            start_time (:obj:`str`, optional): Start time of task. Default: ``None``.
            end_time (:obj:`str`, optional): End time of task. Default: ``None``.
            missed_trigger_handling (:obj:`str`, optional): One of {'IGNORE', 'RUN ALL', 'RUN ONCE'}.
                                                            Default: ``IGNORE``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ScheduledTask`.
        """
        assert isinstance(task_object, Job) or isinstance(
            task_object, ReportDefinition
        ), "Only Job and ReportDefinition are supported"
        params = get_params(parameters=locals(), exclusions=('self', 'task_object'))

        if isinstance(task_object, Job):
            self._job_selection_types['jobId']['value'] = task_object.job_id
            self._job_selection_types['jobName']['value'] = task_object.job_name
            self._job_selection_types['type']['value'] = 'PIPELINE_JOB'
        else:
            self._job_selection_types['reportId']['value'] = task_object.id
            self._job_selection_types['reportName']['value'] = task_object.name
            self._job_selection_types['type']['value'] = 'REPORT_JOB'
        _response = self._control_hub.api_client.trigger_selection_info(
            data={'data': self._job_selection_types}, api_version=2
        )
        task = _response.response.json()['response']['data']

        for key, value in params.items():
            if json_to_python_style(key) in ScheduledTask._ATTRIBUTES_TO_REMAP:
                key = ScheduledTask._ATTRIBUTES_TO_REMAP[json_to_python_style(key)]
            if key == 'action':
                task['executionInfo'][key]['value'] = value
            else:
                task[key]['value'] = value

        return ScheduledTask(task, self._control_hub)


class ScheduledTaskActions(enum.Enum):
    RESUME = 'RESUME'
    PAUSE = 'PAUSE'
    KILL = 'KILL'
    DELETE = 'DELETE'


class ScheduledTaskStatus(enum.Enum):
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'
    KILLED = 'KILLED'
    DELETED = 'DELETED'


@analytics_class_decorator
class ScheduledTask(ScheduledTaskBaseModel):
    """Model for Scheduled Task.

    Args:
        task (:py:obj:`dict`): JSON representation of task.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub instance.


    Attributes:
        runs (:py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.ScheduledTaskRun`):
         Scheduled Task Runs.
        audits (:py:obj:`streamsets.sdk.utils.SeekableList` of
         :py:class:`streamsets.sdk.sch_models.ScheduledTaskAudit`): Scheduled Task Audits.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): ACL of a Scheduled Task.
        job_id (:py:obj:`str`): Job ID for which this task is scheduled.
    """

    _REPR_METADATA = ['id', 'name', 'cron_expression', 'time_zone', 'status', 'next_execution_time']
    _ATTRIBUTES_TO_REMAP = {'cron_expression': 'crontabMask', 'missed_execution_handling': 'missedTriggerHandling'}

    def __init__(self, task, control_hub=None):
        super().__init__(
            task, repr_metadata=ScheduledTask._REPR_METADATA, attributes_to_remap=ScheduledTask._ATTRIBUTES_TO_REMAP
        )
        self._control_hub = control_hub

    @property
    def runs(self):
        """Get Scheduled Task Runs.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.ScheduledTaskRun`.
        """
        _repsonse = self._control_hub.api_client.get_scheduled_task(
            id=self.id, run_info=True, audit_info=False, api_version=2
        )
        runs = _repsonse.response.json()['response']['data']['runs']
        return SeekableList(ScheduledTaskRun(run) for run in runs)

    @property
    def audits(self):
        """Get Scheduled Task Audits.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.ScheduledTaskAudit`.
        """
        _response = self._control_hub.api_client.get_scheduled_task(
            id=self.id, run_info=False, audit_info=True, api_version=2
        )
        audits = _response.response.json()['response']['data']['audits']
        return SeekableList(ScheduledTaskAudit(audit) for audit in audits)

    @property
    def acl(self):
        """Get the ACL of a Scheduled Task.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(
            self._control_hub.api_client.get_scheduled_task_acl(scheduled_task_id=self.id).response.json(),
            self._control_hub,
        )

    @acl.setter
    def acl(self, scheduled_task_acl):
        self._control_hub.api_client.set_scheduled_task_acl(
            scheduled_task_id=self.id, scheduled_task_acl_json=scheduled_task_acl._data
        )

    @property
    def job_id(self):
        """Job ID for which this task is scheduled.

        Returns:
            An instance of :py:obj:`str`.
        """

        return self._data['executionInfo']['pipelineJobId']['value']

    @job_id.setter
    def job_id(self, job_id):
        logger.warning("Cannot manually set job id of a Scheduled Task")


@analytics_class_decorator
class ScheduledTasks(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ScheduledTask` instances."""

    def _get_all_results_from_api(self, **kwargs):
        """Args order_by, offset, len are not exposed directly as arguments because of their limited use by normal
        users but, could still be specified just like any other args with the help of kwargs.

        Args:
            **kwargs: Optional other arguments to be passed to filter the results.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.ScheduledTask` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.ScheduledTask`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': -1, 'order_by': None, 'filter_by': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        api_response = self._control_hub.api_client.get_scheduled_tasks(
            kwargs_unioned['order_by'],
            kwargs_unioned['offset'],
            kwargs_unioned['len'],
            api_version=2,
            filter_by=kwargs_unioned['filter_by'],
        ).response.json()
        tasks = api_response['response']
        response = {
            'totalCount': api_response['paginationInfo']['total'],
            'offset': api_response['paginationInfo']['offset'],
            'len': api_response['paginationInfo']['len'],
            'data': [task['data'] for task in tasks],
        }
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ScheduledTask, {'control_hub': self._control_hub})


class ScheduledTaskRun(ScheduledTaskBaseModel):
    """Scheduled Task Run.

    Args:
        run (:py:obj:`dict`): JSON representation if scheduled task run.
    """

    _REPR_METADATA = ['id', 'scheduledTime']

    def __init__(self, run):
        super().__init__(run, repr_metadata=ScheduledTaskRun._REPR_METADATA)


class ScheduledTaskAudit(ScheduledTaskBaseModel):
    """Scheduled Task Audit.

    Args:
        run (:py:obj:`dict`): JSON representation of scheduled task audit.
    """

    _REPR_METADATA = ['id', 'action']

    def __init__(self, audit):
        super().__init__(audit, repr_metadata=ScheduledTaskAudit._REPR_METADATA)


@analytics_class_decorator
class Subscription(BaseModel):
    """Subscription.

    Args:
        subscription (:obj:`dict`): JSON representation of Subscription.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub instance.

    Attributes:
        events ( A :py:obj:`streamsets.sdk.utils.SeekableList` of
         :py:class:`streamsets.sdk.sch_models.SubscriptionEvent` instances): The Subscription's events.
        action (:py:class:`streamsets.sdk.sch_models.SubscriptionAction`): Action of a Subscription.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): ACL of a Subscription.
    """

    _REPR_METADATA = ['id', 'name']

    def __init__(self, subscription, control_hub):
        super().__init__(subscription, repr_metadata=Subscription._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def events(self):
        """Events of the Subscription."""

        return SeekableList(SubscriptionEvent(event, self._control_hub) for event in self._data['events'])

    @property
    def action(self):
        """Action of the Subscription."""
        return SubscriptionAction(self._data['externalActions'][0])

    @property
    def acl(self):
        """Get the ACL of an Event Subscription.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(
            self._control_hub.api_client.get_subscription_acl(subscription_id=self.id).response.json(),
            self._control_hub,
        )

    @acl.setter
    def acl(self, subscription_acl):
        self._control_hub.api_client.set_subscription_acl(
            subscription_id=self.id, subscription_acl_json=subscription_acl._data
        )


class SubscriptionAction(BaseModel):
    """Action to take when the Subscription is triggered.

    Args:
        action (:obj:`dict`): JSON representation of an Action for a Subscription.
    """

    _REPR_METADATA = ['event_type']

    def __init__(self, action):
        super().__init__(action, repr_metadata=SubscriptionAction._REPR_METADATA)
        self.config = json.loads(self.config) if isinstance(self.config, str) else self.config


class SubscriptionEvent(BaseModel):
    """An Event of a Subscription.

    Args:
        event (:obj:`dict`): JSON representation of Events of a Subscription.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub instance.
    """

    _REPR_METADATA = ['event_type', 'filter']

    def __init__(self, event, control_hub):
        event_types = control_hub._en_translations['notifications']['subscriptions']['events']
        if event['eventType'] in event_types:
            event['eventType'] = event_types[event['eventType']]
        super().__init__(event, repr_metadata=SubscriptionEvent._REPR_METADATA)


class SubscriptionAudit(BaseModel):
    """Model for subscription audit.

    Args:
        audit (:obj:`dict`): JSON representation of a subscription audit.
    """

    _REPR_METADATA = ['subscription_name', 'event_name', 'external_action_type', 'created_time']

    def __init__(self, audit):
        super().__init__(audit, repr_metadata=SubscriptionAudit._REPR_METADATA)


@analytics_class_decorator
class Subscriptions(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Subscription` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """Args offset, len, orderBy, order are not exposed directly as arguments because of their limited use by normal
        users but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Subscription` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Subscription`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order_by': 'CREATE_TIME', 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.get_all_event_subscriptions(
            organization=organization,
            offset=kwargs_unioned['offset'],
            len=kwargs_unioned['len'],
            order_by=kwargs_unioned['order_by'],
            order=kwargs_unioned['order'],
            with_wrapper=True,
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Subscription, {'control_hub': self._control_hub})


class SubscriptionBuilder:
    """Builder for Subscription.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_subscription_builder`.

    Args:
        subscription (:py:obj:`dict`): JSON representation of event subscription.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub instance.
    """

    def __init__(self, subscription, control_hub):
        self._subscription = subscription
        self._events = SeekableList()
        self._action = {}
        self._control_hub = control_hub

    def add_event(self, event_type, filter=""):
        """Add event to the Subscription.

        Args:
            event_type (:obj:`str`): Type of event in {'Job Status Change', 'Data SLA Triggered', 'Pipeline Committed',
                                                       'Pipeline Status Change', 'Report Generated',
                                                       'Data Collector not Responding'}.
            filter (:obj:`str`, optional): Filter to be applied on event. Default: ``""``.
        """
        event = {'eventType': event_type, 'filter': filter}
        if self._subscription is not None:
            self._subscription['events'].append(event)
        self._events.append(SubscriptionEvent(event, self._control_hub))

    def remove_event(self, event_type):
        """Remove event from the subscription.

        Args:
            event_type (:obj:`str`): Type of event in {'Job Status Change', 'Data SLA Triggered', 'Pipeline Committed',
                                                       'Pipeline Status Change', 'Report Generated',
                                                       'Data Collector not Responding'}.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.SubscriptionEvent`.
        """
        popped = self._events.get(event_type=event_type)
        self._events = SeekableList(i for i in self._events if getattr(i, 'event_type') != event_type)
        if self._subscription is not None:
            self._subscription['events'] = [i for i in self._subscription['events'] if i.get(event_type) != event_type]
        return popped

    def import_subscription(self, subscription):
        """Import an existing Subscription into the builder to update it.

        Args:
            subscription (:py:class:`streamsets.sdk.sch_models.Subscription`): Subscription instance.
        """
        self._subscription = subscription._data
        self._events = SeekableList(
            SubscriptionEvent(event, self._control_hub) for event in subscription._data['events']
        )
        self._action = subscription._data['externalActions'][0]

    def set_email_action(self, recipients, subject=None, body=None, external_smtp_url=None, external_smtp_port=None):
        """Set the Email action.

        Args:
            recipients (:obj:`list`): List of email addresses.
            subject (:obj:`str`, optional): Subject of the email. Default: ``None``.
            body (:obj:`str`, optional): Body of the email. Default: ``None``.
            external_smtp_url (:obj:`str`, optional): SMTP URL to route. Default: ``None``.
            external_smtp_port (:obj:`str`, optional): SMTP Port to route. Default: ``None``.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'external_smtp_url', 'external_smtp_port'))
        if external_smtp_url is not None:
            params['externalSMTPUrl'] = external_smtp_url
        if external_smtp_port is not None:
            params['externalSMTPPort'] = external_smtp_port
        self._action.update({'eventType': 'EMAIL', 'config': params})

    def set_webhook_action(
        self,
        uri,
        method='GET',
        content_type=None,
        payload=None,
        auth_type=None,
        username=None,
        password=None,
        timeout=30000,
        headers=None,
        bearer_token=None,
        api_key_key=None,
        api_key_value=None,
        api_key_location=None,
        token_url=None,
        client_id=None,
        client_secret=None,
        scope=None,
        location=None,
        resources=None,
        audiences=None,
    ):
        """Set the Webhook action.

        Args:
            uri (:obj:`str`): URI for the Webhook.
            method (:obj:`str`, optional): HTTP method to use. Default: ``'GET'``.
            content_type (:obj:`str`, optional): Content Type of the request. Default:  ``None``.
            payload (:obj:`str`, optional): Payload of the request. Default:  ``None``.
            auth_type (:obj:`str`, optional): ``'basic'`` or ``None``. Default: ``None``.
            username (:obj:`str`, optional): Username for the authentication. Default: ``None``.
            password (:obj:`str`, optional): Password for the authentication. Default: ``None``.
            timeout (:obj:`int`, optional): Timeout for the Webhook action. Default: ``30000``.
            headers (:obj:`dict`, optional): Headers to be sent to the Webhook call. Default: ``None``.
            bearer_token (:obj:`str`, optional): Bearer token for the authentication. Default: ``None``.
            token_url: (:obj:`str`, optional): Token URL for the authentication. Default: ``None``.
            api_key_key (:obj:`str`, optional): API key name for the authentication. Default: ``None``.
            api_key_value (:obj:`str`, optional): API key value for the authentication. Default: ``None``.
            api_key_location (:obj:`str`, optional): Where to send the api key values. Default: ``None``.
            audiences: (:obj:`list`, optional): Audiences for OAuth2 auth method. Default: ``None``.
            resources: (:obj:`list`, optional): Resources for OAuth2 auth method.  Default: ``None``.
            location: (:obj:`str`, optional): Location of OAuth2 credentials (body or header). Default: ``None``.
            scope: (:obj:`str`, optional): Scope for OAuth2 auth method. Default: ``None``.
            client_secret: (:obj:`str`, optional): Client secret for OAuth2 auth method. Default: ``None``.
            client_id: (:obj:`str`, optional): Client id for OAuth2 auth method. Default: ``None``.
        """
        params = get_params(parameters=locals(), exclusions=('self',))
        if auth_type is None:
            params['authType'] = "none"
        self._action.update({'eventType': 'WEBHOOKV1', 'config': params})

    def build(self, name, description=None):
        """Builder for Scheduled Task.

        Args:
            name (:py:obj:`str`): Name of Subscription.
            description (:py:obj:`str`, optional): Description of subscription. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Subscription`.
        """
        self._subscription['events'] = [event._data for event in self._events]
        self._subscription['externalActions'] = [self._action]
        self._subscription['name'] = name
        self._subscription['description'] = description
        return Subscription(self._subscription, self._control_hub)


@analytics_class_decorator
class Alert(BaseModel):
    """Model for Alerts.

    Attributes:
        message (:obj:`str`): The Alert's message text.
        alert_status (:obj:`str`): The status of the Alert.

    Args:
        alert (:obj:`dict`): JSON representation of an Alert.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """

    _ATTRIBUTES_TO_REMAP = {'message': 'label'}

    _ATTRIBUTES_TO_IGNORE = [
        'ackedBy',
        'ackedOn',
        'additionalInfo',
        'alertType',
        'id',
        'organization',
        'resourceId',
        'ruleId',
    ]

    _REPR_METADATA = ['message', 'alert_status', 'triggered_on']

    def __init__(self, alert, control_hub):
        super().__init__(
            alert,
            attributes_to_ignore=Alert._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=Alert._ATTRIBUTES_TO_REMAP,
            repr_metadata=Alert._REPR_METADATA,
        )
        self._control_hub = control_hub

    def _refresh(self):
        """Refresh an Alert in-memory."""
        resource_alerts = self._control_hub.api_client.get_resource_alerts(
            resource_id=self._data['resourceId'], alert_status='ACKNOWLEDGED'
        )
        self._data = next(alert for alert in resource_alerts.response.json() if alert['id'] == self._data['id'])

    def acknowledge(self):
        """Acknowledge an active Alert."""
        if 'ACTIVE' in self.alert_status:
            self._control_hub.api_client.acknowledge_alert(body=[self._data['id']])
            self._refresh()
        else:
            raise ValueError(
                "Alert is not ACTIVE, and cannot be acknowledged. Current Status: {}".format(self.alert_status)
            )

    def delete(self):
        """Delete an acknowledged Alert."""
        if 'ACKNOWLEDGED' in self.alert_status:
            self._control_hub.api_client.delete_alert(body=[self._data['id']])
        else:
            raise ValueError(
                "Alert is not ACKNOWLEDGED, and cannot be deleted. Current Status: {}".format(self.alert_status)
            )


class Logs:
    """Model for ControlHub logs.

    Args:
        log_lines (:obj:`list`, optional): A list of strings of the log. Default: ``None``.
        data (:py:class:`streamsets.sdk.utils.SeekableList`, optional): A seekable list of logs in json format.
                                                                        Default: ``None``.
    """

    def __init__(self, log_lines=None, data=None):
        self._regex_pattern = (
            r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s\[requestId:(.+)?\]\s\[app:(.+)?\]\s'
            r'\[componentId:(.+)?\]\s\[user:(.+)?\]\s\[thread:(.+)?\]\s(\w+)\s(.+)'
        )
        self._headers = [
            'timestamp',
            'request_id',
            'app',
            'component_id',
            'user',
            'thread',
            'exception_level',
            'message',
        ]
        if data is None:
            self._data = self._process_logs_to_json(log_lines)
        else:
            self._data = data

    def _process_logs_to_json(self, log_lines):
        i = 0
        data = []
        while i < len(log_lines):
            if re.match(self._regex_pattern, log_lines[i]):
                items = re.match(self._regex_pattern, log_lines[i]).groups()
                log_json = {self._headers[i]: items[i] for i in range(len(items))}
                data.append(log_json)
                i += 1
            else:
                # Handle logs where the message is split across multiple lines
                while i < len(log_lines) and not re.match(self._regex_pattern, log_lines[i]):
                    data[-1]['message'] += '\n{}'.format(log_lines[i])
                    i += 1
        data.sort(key=lambda x: x['timestamp'])
        return SeekableList(data)

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return format_sch_log(self._data)

    def __iter__(self):
        for log in self._data:
            yield log

    def __getitem__(self, key):
        return self._data[key]

    def to_dict(self):
        return self._data

    def get_all(self, **kwargs):
        return Logs(data=SeekableList(i for i in self._data if all(i.get(k) == v for k, v in kwargs.items())))

    def time_filter(self, after_timestamp=None, before_timestamp=None):
        """Returns log happened during a specified time interval (open/closed interval).

        Args:
            after_timestamp (:obj:`str`, optional): Specify timestamp in the form of `'2017-04-10 17:53:55,244'` to get
                                                    logs after particular time. Default: ``None``.
            before_timestamp (:obj:`str`, optional): Specify timestamp in the form of `'2017-04-10 17:53:55,244'` to get
                                                    logs before particular time. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Logs`.
        """
        if not after_timestamp and not before_timestamp:
            condition = lambda x: True
        elif after_timestamp and not before_timestamp:
            condition = lambda x: x.get('timestamp') and x.get('timestamp') > after_timestamp
        elif not after_timestamp and before_timestamp:
            condition = lambda x: x.get('timestamp') and x.get('timestamp') < before_timestamp
        else:
            condition = lambda x: (
                x.get('timestamp') and x.get('timestamp') > after_timestamp and x.get('timestamp') < before_timestamp
            )
        return Logs(data=SeekableList(filter(condition, self._data)))


@analytics_class_decorator
class ConnectionBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Connection`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_connection_builder`.

    Args:
        connection (:obj:`dict`): Python object built from our Swagger ConnectionJson definition.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """

    def __init__(self, connection, control_hub):
        self._connection = connection
        self._control_hub = control_hub

    def build(self, title, connection_type, authoring_data_collector=None, tags=None, **kwargs):
        """Define the connection.

        Args:
            title (:obj:`str`): Connection title.
            connection_type (:obj:`str`): Type of connection. The options are 'STREAMSETS_AWS_EMR_CLUSTER',
                'STREAMSETS_MYSQL', 'STREAMSETS_AZURE_SYNAPSE', 'STREAMSETS_ORCHESTRATOR', 'STREAMSETS_INFLUX2',
                'STREAMSETS_DATABRICKS_DELTA_LAKE', 'STREAMSETS_HIVE', 'STREAMSETS_GOOGLE_PUB_SUB',
                'STREAMSETS_BLOB_STORAGE', 'STREAMSETS_MQTT', 'STREAMSETS_MONGODB', 'STREAMSETS_POSTGRES',
                'STREAMSETS_GOOGLE_CLOUD_STORAGE', 'STREAMSETS_CASSANDRA', 'STREAMSETS_JMS', 'STREAMSETS_ELASTICSEARCH',
                'STREAMSETS_ORACLE', 'STREAMSETS_DB2', 'STREAMSETS_ADLS_GEN2', 'STREAMSETS_TERADATA',
                'STREAMSETS_WEBCLIENT', 'STREAMSETS_AEROSPIKE', 'STREAMSETS_SNOWPIPE', 'STREAMSETS_AWS_EMR_CLUSTER',
                'STREAMSETS_SNOWFLAKE', 'STREAMSETS_SPLUNK', 'STREAMSETS_COAP_CLIENT', 'STREAMSETS_OPC_UA_CLIENT',
                'STREAMSETS_COUCHBASE', 'STREAMSETS_MONGODB_ATLAS', 'STREAMSETS_WATSONXDATA',
                'STREAMSETS_AWS_KINESIS_STREAM', 'STREAMSETS_AWS_KINESIS_FIREHOSE', 'STREAMSETS_KUDU',
                'STREAMSETS_PULSAR', 'STREAMSETS_AWS_REDSHIFT', 'STREAMSETS_GOOGLE_BIG_QUERY', 'STREAMSETS_REMOTE_FILE',
                'STREAMSETS_AWS_S3', 'STREAMSETS_KAFKA', 'STREAMSETS_SQLSERVER', 'STREAMSETS_AWS_SQS',
                'STREAMSETS_AWS_EMR_SERVERLESS', 'STREAMSETS_CONNX', 'STREAMSETS_RABBITMQ', 'STREAMSETS_SALESFORCE',
                'STREAMSETS_REDIS' and 'STREAMSETS_JDBC
            authoring_data_collector (:obj:`streamsets.sdk.sch.DataCollector`): Authoring Data Collector.
            tags (:obj:`list`, optional): List of tags (strings). Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Connection`.
        """

        self._connection_type = connection_type
        self._authoring_data_collector = authoring_data_collector
        if not authoring_data_collector:
            self.engine_version_id = kwargs.get('engine_version_id', self._control_hub._default_engine_version_id())
        connection_definition_json = self._get_connection_definition_json()
        connection_definition = self._setup_configuration(dict(connection_definition_json))
        self._connection.update(
            {
                'name': title,
                'connectionType': connection_type,
                'rawConnectionTags': [],
                'sdcId': authoring_data_collector.id if authoring_data_collector else ENGINELESS_CONNECTION_ID,
                'sdcVersion': (
                    authoring_data_collector.version
                    if authoring_data_collector
                    else self.engine_version_id.split(":")[1]
                ),
                'connectionDefinition': json.dumps(connection_definition._data),
                'libraryDefinition': json.dumps(connection_definition_json),
                'typeLabel': connection_definition.label,
            }
        )
        connection = Connection(connection=self._connection, control_hub=self._control_hub)
        if tags:
            connection.add_tag(*tags)
        return connection

    def _get_connection_definition_json(self):
        """Fetch the connection definition.

        Returns:
            An instance of :py:obj:`dict`.
        """
        # Fetch connection definitions
        if self._authoring_data_collector:
            connection_definitions = (
                self._authoring_data_collector._instance.api_client.get_connection_definitions().response.json()[
                    'connections'
                ]
            )
        else:
            connection_definitions = self._control_hub.api_client.get_designer_connection_definition(
                self.engine_version_id
            ).response.json()['connections']

        # Find the connection definition of required type
        for connection_definition in connection_definitions:
            if connection_definition['type'] == self._connection_type:
                return connection_definition
        else:
            raise ValueError(
                'Provided authoring Data Collector does not have appropriate stage lib installed for '
                'connection type {}'.format(self._connection_type)
            )

    def _setup_configuration(self, connection_definition_json):
        """Setup the configuration of the connection.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ConnectionDefinition`.
        """

        # Create configuration json
        connection_definition_json['configuration'] = [
            {'name': config_def['name'], 'value': config_def['defaultValue']}
            for config_def in connection_definition_json['configDefinitions']
        ]
        # Remove config definitons from dictionary as it is not needed in the final json
        del connection_definition_json['configDefinitions']

        connection_definition = ConnectionDefinition(connection_definition_json)
        return connection_definition


@analytics_class_decorator
class ConnectionTags(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Tag` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, organization=None, parent_id=None, **kwargs):
        """Args offset, len_, order are not exposed directly as arguments because of their limited use by normal users
        but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            parent_id (:obj:`str`, optional): Parent tag ID to filter with. Default: ``None``.
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Tag` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Tag`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None, 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_connection_tags(
            organization=organization,
            parent_id=parent_id,
            offset=kwargs_unioned['offset'],
            len_=kwargs_unioned['len'],
            order=kwargs_unioned['order'],
        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Tag, {})


class ConnectionDefinition(BaseModel):
    """Model for connection definition.

    Args:
        connection_definition (:obj:`dict`): A Python object representation of connection definition.
        config_definitions (:obj:`dict`, optional): A Python object representation of configuration definition.
        compatibility_map (:obj:`dict`, optional): A dictionary mapping values used for backwards compatibility.

    Attributes:
        configuration (:py:class:`streamsets.sdk.models.Configuration`): Configuration of the Connection Definition.
    """

    _REPR_METADATA = ['version']

    def __init__(self, connection_definition, config_definitions=None, compatibility_map=None):
        super().__init__(connection_definition)
        self._configuration = Configuration(
            self._data['configuration'],
            id_to_remap=self._create_id_to_remap(config_definitions) if config_definitions else None,
            compatibility_map=compatibility_map,
        )

    @property
    def configuration(self):
        return self._configuration

    def _create_id_to_remap(self, config_definitions):
        mapping = {}
        for config_definition in config_definitions:
            attribute_name, config_name = get_attribute(config_definition)
            mapping[attribute_name] = config_name
        return mapping


@analytics_class_decorator
class Connection(BaseModel):
    """Model for connection.

    Args:
        connection (:obj:`dict`): A Python object representation of Connection.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.

    Attributes:
        connection_definition (:obj:`dict`): The Connection Definition JSON.
        library_definition (:obj:`dict`): The Library Definition JSON.
        pipeline_commits (:py:class:`streamsets.sdk.utils.SeekableList` of
         :py:class:`streamsets.sdk.sch_models.PipelineCommit` instances): Pipeline commits using this connection.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): Update Connection ACL.
        tags (:py:obj:`streamsets.sdk.utils.SeekableList` of instances of :py:class:`streamsets.sdk.sch_models.Tag`):
         Connection tags.
    """

    _REPR_METADATA = ['id', 'name', 'connection_type']

    def __init__(self, connection, control_hub):
        super().__init__(connection, repr_metadata=Connection._REPR_METADATA)
        self._control_hub = control_hub
        connection_type = connection.get('connectionType')
        compatibility_map = (
            get_bw_compatibility_map(connection['sdcVersion'], SDC_CONNECTIONS_BW_COMPATIBILITY[connection_type])
            if connection.get('sdcVersion') and connection_type in SDC_CONNECTIONS_BW_COMPATIBILITY
            else {}
        )
        self._connection_definition_internal = (
            ConnectionDefinition(
                connection_definition=json.loads(connection['connectionDefinition']),
                config_definitions=json.loads(connection['libraryDefinition']).get('configDefinitions'),
                compatibility_map=compatibility_map,
            )
            if connection.get('connectionDefinition') and connection.get('libraryDefinition')
            else None
        )

    @property
    def _data(self):
        if not self._connection_definition_internal:
            self._load_data()
        return self._data_internal

    @_data.setter
    def _data(self, data):
        self._data_internal = data

    @property
    def _connection_definition(self):
        if not self._connection_definition_internal:
            self._load_data()
        return self._connection_definition_internal

    @_connection_definition.setter
    def _connection_definition(self, connection_definition):
        self._connection_definition_internal = connection_definition

    @property
    def connection_definition(self):
        if not self._connection_definition_internal:
            self._load_data()
        return self._connection_definition_internal

    @property
    def library_definition(self):
        if not self._connection_definition_internal:
            self._load_data()
        return self._data_internal['libraryDefinition']

    @property
    def pipeline_commits(self):
        """Get the pipeline commits using this connection.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.PipelineCommit`
                instances.
        """
        response = self._control_hub.api_client.get_pipeline_commits_using_connection(self.id).response.json()
        pipeline_commits = SeekableList()
        for commit_data in response:
            commit_data.update(
                {
                    'commitId': commit_data['pipelineCommitId'],
                    'version': commit_data['pipelineVersion'],
                    'commitMessage': None,
                }
            )
            pipeline_commits.append(PipelineCommit(pipeline_commit=commit_data, control_hub=self._control_hub))
        return pipeline_commits

    @property
    def acl(self):
        """Get Connection ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(
            self._control_hub.api_client.get_connection_acl(connection_id=self.id).response.json(), self._control_hub
        )

    @acl.setter
    def acl(self, connection_acl):
        """Update Connection ACL.

        Args:
            connection_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The Connection ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.update_connection_acl(connection_id=self.id, body=connection_acl._data)

    @property
    def tags(self):
        """Get the connection tags.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of instances of
            :py:class:`streamsets.sdk.sch_models.Tag`.
        """
        connection_tags = self._data.get('tags', []) or []
        if not connection_tags:
            raw_connection_tags = self._data.get('rawConnectionTags', []) or []
            if raw_connection_tags:
                organization = self._control_hub.organization
                connection_tags = [build_tag_from_raw_tag(raw_tag, organization) for raw_tag in raw_connection_tags]
                self._data['tags'] = connection_tags
        return SeekableList(Tag(tag) for tag in connection_tags)

    def _load_data(self):
        data = self._control_hub.api_client.get_connection(connection_id=self.id).response.json()
        self._data_internal = data
        connection_type = data.get('connectionType')
        compatibility_map = (
            get_bw_compatibility_map(data['sdcVersion'], SDC_CONNECTIONS_BW_COMPATIBILITY[connection_type])
            if data.get('sdcVersion') and connection_type in SDC_CONNECTIONS_BW_COMPATIBILITY
            else {}
        )
        self._connection_definition_internal = ConnectionDefinition(
            connection_definition=json.loads(data['connectionDefinition']),
            config_definitions=json.loads(data['libraryDefinition']).get('configDefinitions'),
            compatibility_map=compatibility_map,
        )

    def add_tag(self, *tags):
        """Add a tag

        Args:
            *tags: One or more instances of :obj:`str`
        """
        current_tags = [tag.tag for tag in self.tags]
        if not self._data.get('tags', None):
            self._data['tags'] = []
        if not self._data.get('rawConnectionTags', None):
            self._data['rawConnectionTags'] = current_tags
        for tag in tags:
            self._data['rawConnectionTags'].append(tag)
            tag_json = build_tag_from_raw_tag(tag, self._control_hub.organization)
            self._data['tags'].append(tag_json)

    def remove_tag(self, *tags):
        """Remove a tag

        Args:
            *tags: One or more instances of :obj:`str`
        """
        current_tags = [tag.tag for tag in self.tags]
        for tag in tags:
            if tag in current_tags:
                current_tags.remove(tag)
                item = self.tags.get(tag=tag)
                self._data['tags'].remove(item._data)
            else:
                logger.warning('Tag %s is not an assigned tag for this pipeline. Ignoring this tag.', tag)
        self._data['rawConnectionTags'] = current_tags


@analytics_class_decorator
class Connections(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Connection` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, id=None, organization=None, connection_type=None, **kwargs):
        """Args offset, len, order_by, order, filter_text, with_total_count are not exposed
        directly as arguments because of their limited use by normal users but, could still be specified just like any
        other args with the help of kwargs.

        Args:
            id (:obj:`str`, optional): Connection ID. Default: ``None``.
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            connection_type (:obj:`str`, optional): Type of connection. Default: ``None``.
            filter_text (:obj:`str`, optional): Only returns instances that match the filter string. This will be
                propagated to the API backend (results filtered server-side instead of client-side).
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Connection` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Connection`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {
            'offset': None,
            'len': None,
            'order_by': 'LAST_MODIFIED_TIME',
            'order': 'ASC',
            'filter_text': None,
            'with_total_count': False,
        }
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if id is not None:
            response = [self._control_hub.api_client.get_connection(connection_id=id).response.json()]
        else:
            response = self._control_hub.api_client.get_all_connections(
                organization=organization,
                connection_type=connection_type,
                offset=kwargs_unioned['offset'],
                len=kwargs_unioned['len'],
                order_by=kwargs_unioned['order_by'],
                order=kwargs_unioned['order'],
                filter_text=kwargs_unioned['filter_text'],
                with_total_count=kwargs_unioned['with_total_count'],
            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Connection, {'control_hub': self._control_hub})


class ConnectionVerificationResult(BaseModel):
    """Model for connection verification result.

    Args:
        connection_preview_json (:obj:`dict`): dynamic preview API response JSON.

    Attributes:
        issue_count (:obj:`int`): The count of the number of issues for the connection verification result.
        issue_message (:obj:`str`): The message provided for the connection verification result.
    """

    _REPR_METADATA = ['status']

    def __init__(self, connection_preview_json):
        super().__init__(connection_preview_json, repr_metadata=ConnectionVerificationResult._REPR_METADATA)

    @property
    def issue_count(self):
        """The count of the number of issues for the connection verification result.

        Returns:
              A :obj:`int` that represents the number of issues.
        """
        return self.issues['issueCount']

    @property
    def issue_message(self):
        """The message provided for the connection verification result.

        Returns:
              A :obj:`str` message detailing the response for the connection verification result.
        """
        return next(iter(self.issues['stageIssues'].values()))[0]['message']


@analytics_class_decorator
class MeteringUsage:
    """Get the metering and usage data for a given time frame, not to exceed 60 days. By default, this will retrieve the
    last 30 days of data.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.

    Returns:
        An instance of :py:class:`streamsets.sdk.sch_models.MeteringReport`
    """

    def __init__(self, control_hub):
        self._control_hub = control_hub

    def __repr__(self):
        default_start = datetime.now() - timedelta(30)
        default_end = datetime.now()
        return repr(
            MeteringReport(
                self._control_hub.api_client.get_metering_daily_report(
                    start=int(default_start.timestamp() * 1000), end=int(default_end.timestamp() * 1000)
                ).response.json(),
                default_start,
                default_end,
                self._control_hub,
            )
        )

    def __getitem__(self, time_frame):
        if not isinstance(time_frame, slice):
            raise TypeError('The time frame provided for metering must be a slice object.')
        if not isinstance(time_frame.start, datetime):
            raise TypeError('The start of the time frame for metering must be a datetime object.')
        if time_frame.stop and not isinstance(time_frame.stop, datetime):
            raise TypeError('The end of the time frame for metering must be a datetime object.')
        if time_frame.stop and (time_frame.stop - time_frame.start).days > METERING_MAX_DAYS:
            raise ValueError('The time frame provided cannot exceed 60 contiguous days.')

        start = time_frame.start
        end = time_frame.stop if time_frame.stop else datetime.now()

        return MeteringReport(
            self._control_hub.api_client.get_metering_daily_report(
                start=int(start.timestamp() * 1000), end=int(end.timestamp() * 1000)
            ).response.json(),
            start,
            end,
            self._control_hub,
        )


@analytics_class_decorator
class MeteringReport(BaseModel):
    """Model for handling the results of a Metering report.

    Attributes:
        average_units_per_day (:obj:`int`): Average unit consumption per-day for the report window.
        pipeline_hours (:obj:`float`): Total pipeline hours consumed for the report window.
        clock_hours (:obj:`float`): Total clock hours consumed for the report window.
        total_units (:obj:`int`): Total units consumed for the report window.
    """

    _REPR_METADATA = ['start', 'end', 'total_units', 'pipeline_hours', 'clock_hours']
    _ATTRIBUTES_TO_IGNORE = ['version', 'data', 'status']
    _METRIC_LOOKUP = {'pipeline_hours': 'pipelineTime', 'clock_hours': 'clockTime', 'total_units': 'units'}

    def __init__(self, metering_data, start, end, control_hub):
        super().__init__(
            metering_data,
            attributes_to_ignore=MeteringReport._ATTRIBUTES_TO_IGNORE,
            repr_metadata=MeteringReport._REPR_METADATA,
        )
        self.start = start
        self.end = end
        self._control_hub = control_hub

    @property
    def average_units_per_day(self):
        # Needs to be inclusive of start and end days, so adding 1 to the difference of the two
        return round(self.total_units / (self.end - self.start).days + 1)

    @property
    def pipeline_hours(self):
        hours = 0
        pipeline_hours_index = self._data['data']['columnNames'].index('pipelineTime')
        for item in self._data['data']['report']:
            hours += item[pipeline_hours_index]
        return round(hours / MILLIS_IN_HOUR, 1)

    @property
    def clock_hours(self):
        hours = 0
        clock_hours_index = self._data['data']['columnNames'].index('clockTime')
        for item in self._data['data']['report']:
            hours += item[clock_hours_index]
        return round(hours / MILLIS_IN_HOUR, 1)

    @property
    def total_units(self):
        units = 0
        units_index = self._data['data']['columnNames'].index('units')
        for item in self._data['data']['report']:
            units += item[units_index]
        return units

    def get_usage(self, metric):
        """Get the usage breakdown of a metric for each day in the report window.

        Args:
            metric (:obj:`str`): The metric to use for comparison. Options: ``'pipeline_hours'``, ``'clock_hours'``,
                ``'total_units'``

        Returns:
            An :obj:`OrderedDict` in sorted, chronological order by day.
        """
        if metric not in ['pipeline_hours', 'clock_hours', 'total_units']:
            raise ValueError('The metric provided must be pipeline_hours, clock_hours, or total_units.')
        metric_by_datetime = {}
        metric_name_map = METERING_METRIC_LOOKUP[metric]
        datetime_index = self._data['data']['columnNames'].index('datetime')
        metric_index = self._data['data']['columnNames'].index(metric_name_map)
        engine_index = self._data['data']['columnNames'].index('engineType')
        for item in self._data['data']['report']:
            engine_type = self._data['data']['aliases'][item[engine_index]][0]
            if item[datetime_index] not in metric_by_datetime:
                metric_by_datetime.update(
                    {item[datetime_index]: {metric: item[metric_index], engine_type: item[metric_index]}}
                )
            else:
                metric_by_datetime[item[datetime_index]][metric] += item[metric_index]
                if engine_type in metric_by_datetime[item[datetime_index]]:
                    metric_by_datetime[item[datetime_index]][engine_type] += item[metric_index]
                else:
                    metric_by_datetime[item[datetime_index]][engine_type] = item[metric_index]
        return collections.OrderedDict(
            [
                (datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'), metrics)
                for timestamp, metrics in sorted(metric_by_datetime.items(), key=lambda key: key[0])
            ]
        )

    def get_top_deployments(self, metric):
        """Get the highest-consuming deployments based on the provided metric.

        Args:
            metric (:obj:`str`): The metric to use for comparison. Options: ``'pipeline_hours'``, ``'clock_hours'``,
                ``'total_units'``

        Returns:
            An :obj:`OrderedDict` instance in 'deployment_id: metric' format, sorted in order from highest consuming to
                lowest consuming.
        """
        return top_objects_by_metering_metric(self._data, 'deployment', metric)

    def get_top_environments(self, metric):
        """Get the highest-consuming environments based on the provided metric.

        Args:
            metric (:obj:`str`): The metric to use for comparison. Options: ``'pipeline_hours'``, ``'clock_hours'``,
                ``'total_units'``

        Returns:
            An :obj:`OrderedDict` instance in 'environment_id: metric' format, sorted in order from highest consuming to
                lowest consuming.
        """
        return top_objects_by_metering_metric(self._data, 'environment', metric)

    def get_top_jobs(self, metric):
        """Get the highest-consuming jobs based on the provided metric.

        Args:
            metric (:obj:`str`): The metric to use for comparison. Options: ``'pipeline_hours'``, ``'clock_hours'``,
                ``'total_units'``

        Returns:
            An :obj:`OrderedDict` instance in 'job_id: metric' format, sorted in order from highest consuming to
                lowest consuming.
        """
        return top_objects_by_metering_metric(self._data, 'job', metric)

    def get_top_users(self, metric):
        """Get the highest-consuming users based on the provided metric.

        Args:
            metric (:obj:`str`): The metric to use for comparison. Options: ``'pipeline_hours'``, ``'clock_hours'``,
                ``'total_units'``

        Returns:
            An :obj:`OrderedDict` instance in 'user_id: metric' format, sorted in order from highest consuming to
                lowest consuming.
        """
        return top_objects_by_metering_metric(self._data, 'user', metric)

    def view_job_runs(self, job_id):
        """Get a job's unit consumption, broken down for each run in the report window.

        Args: job_id (:obj:`str`): The ID of the job

        Returns:
            An :obj:`OrderedDict` instance of every job run, sorted in chronological order (oldest to newest).
        """
        response = self._control_hub.api_client.get_metering_report_for_job(
            job_id=job_id, start=int(self.start.timestamp() * 1000), end=int(self.end.timestamp() * 1000)
        ).response.json()
        if response['data']['report']:
            run_index = response['data']['columnNames'].index('run')
            unit_index = response['data']['columnNames'].index('units')
            start_index = response['data']['columnNames'].index('start')
            clock_time_index = response['data']['columnNames'].index('clockTime')
            pipeline_time_index = response['data']['columnNames'].index('pipelineTime')
            units_per_run = {}
            for item in response['data']['report']:
                run_id = response['data']['aliases'][item[run_index]][0]
                units_per_run[run_id] = {
                    'start_run_time': str(datetime.fromtimestamp(item[start_index] / 1000))[:-3],
                    'total_run_time': str(timedelta(milliseconds=item[pipeline_time_index]))[:-3],
                    'units': round(item[unit_index] / MILLIS_IN_HOUR, 3),
                    'clock_time': str(timedelta(milliseconds=item[clock_time_index]))[:-3],
                }
            return collections.OrderedDict(
                [(key, value) for key, value in sorted(units_per_run.items(), key=lambda key: key[1]['start_run_time'])]
            )
        else:
            return {}


@analytics_class_decorator
class Project(BaseModel):
    """Represents a Project.

    Args:
        project (:obj:`dict`): JSON representation of a Project.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.

    Attributes:
        id (:obj:`str`): ID of the project.
        name (:obj:`str`): Name of the project.
        description (:obj:`str`): Description of the project.
        users (:py:class:`streamsets.sdk.utils.SeekableList` of
               :py:class:`streamsets.sdk.sch_models.User` instances): Users belonging to this project.
        groups (:py:class:`streamsets.sdk.utils.SeekableList` of
                :py:class:`streamsets.sdk.sch_models.Group` instances): Groups belonging to this project.
        organization (:obj:`str`): Organization ID inside which this project exists.
    """

    _ATTRIBUTES_TO_IGNORE = ['containerUserXJoins']
    _ATTRIBUTES_TO_REMAP = {'organization': 'organizationId'}
    _REPR_METADATA = ['id', 'name', 'description']

    def __init__(self, project, control_hub):
        super().__init__(
            data=project,
            attributes_to_ignore=Project._ATTRIBUTES_TO_IGNORE,
            attributes_to_remap=Project._ATTRIBUTES_TO_REMAP,
            repr_metadata=Project._REPR_METADATA,
        )

        self._control_hub = control_hub

        # Private members for properties that will be initialized later
        self._users = None
        self._groups = None

    @property
    def users(self):
        if self._users is None:
            users = self._control_hub.api_client.get_all_users_in_project(project_id=self.id).response.json()['data']
            self._users = SeekableList()
            for user_data in users:
                self._users.append(User(user=user_data, roles=self._control_hub._roles, control_hub=self._control_hub))
        return self._users

    @users.setter
    def users(self, val):
        raise NotImplementedError(
            "Cannot set value to users property of a project, use `add_user` or `remove_user` instead."
        )

    @property
    def groups(self):
        if self._groups is None:
            groups = self._control_hub.api_client.get_all_groups_in_project(project_id=self.id).response.json()['data']
            self._groups = SeekableList()
            for group in groups:
                group_data = self._control_hub.api_client.get_group(
                    org_id=self._control_hub.organization, group_id=group['id']
                ).response.json()
                self._groups.append(
                    Group(group=group_data, roles=self._control_hub._roles, control_hub=self._control_hub)
                )
        return self._groups

    @groups.setter
    def groups(self, val):
        raise NotImplementedError(
            "Cannot set value to groups property of a project, use `add_group` or `remove_group` instead."
        )

    def _commit_users_to_control_hub(self):
        """Commits the current state of users to ControlHub.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """

        user_ids = [user.id for user in self.users]
        request_body = {'userIds': user_ids}

        try:
            update_users_command = self._control_hub.api_client.update_users_in_project(
                project_id=self.id, body=request_body
            )
        except HTTPError as e:
            # if an error occurs, we clear the _users attributes as we might not know the current state of users in the project
            self._users = None
            raise e

        return update_users_command

    def add_user(self, *users):
        """Add one or more users to the project.

        Args:
            *users (:py:class:`streamsets.sdk.sch_models.User`): One or more users to add to the project.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """

        if not all([isinstance(user, User) for user in users]):
            raise TypeError("users should be of type :py:class:`streamsets.sdk.sch_models.User`.")

        if not all([user.id is not None for user in users]):
            raise ValueError("User's ID should not be None, ensure the user is added to Control Hub.")

        existing_user_ids = set([existing_user.id for existing_user in self.users])

        for user in users:
            if user.id not in existing_user_ids:
                self.users.append(user)
                existing_user_ids.add(user.id)

        # finally, commit to control hub
        return self._commit_users_to_control_hub()

    def remove_user(self, *users):
        """Remove one of more users from the project.

        Args:
            *users (:py:class:`streamsets.sdk.sch_models.User`): One or more users to add to the project.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """

        if not all([isinstance(user, User) for user in users]):
            raise TypeError("users should be of type :py:class:`streamsets.sdk.sch_models.User`.")

        if not all([user.id is not None for user in users]):
            raise ValueError("User's ID should not be None, ensure the user is added to Control Hub.")

        # ensure all users exist in the project before removing
        for user in users:
            try:
                self.users.get(id=user.id)
            except ValueError:
                raise ValueError(f"User with ID {user.id} not found in project.")

        # since all users exist in the project, we can remove them
        for user in users:
            self.users.remove(user)

        # finally, commit to control hub
        return self._commit_users_to_control_hub()

    def _commit_groups_to_control_hub(self):
        """Commits the current state of groups to ControlHub.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """

        group_ids = [group.group_id for group in self.groups]
        request_body = {'groupIds': group_ids}

        try:
            update_groups_command = self._control_hub.api_client.update_groups_in_project(
                project_id=self.id, body=request_body
            )
        except HTTPError as e:
            # if an error occurs, we clear the _groups attributes as we might not know the current state of groups in the project
            self._groups = None
            raise e

        return update_groups_command

    def add_group(self, *groups):
        """Add one or more groups to the project.

        Args:
            *groups (:py:class:`streamsets.sdk.sch_models.Group`): One or more groups to add to the project.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """

        if not all([isinstance(group, Group) for group in groups]):
            raise TypeError("groups should be of type :py:class:`streamsets.sdk.sch_models.Group`.")

        if not all([group.group_id is not None for group in groups]):
            raise ValueError("Group's ID should not be None, ensure the group is added to Control Hub.")

        existing_group_ids = set([existing_group.group_id for existing_group in self.groups])

        for group in groups:
            if group.group_id not in existing_group_ids:
                self.groups.append(group)
                existing_group_ids.add(group.group_id)

        # finally, commit to control hub
        return self._commit_groups_to_control_hub()

    def remove_group(self, *groups):
        """Remove one of more groups from the project.

        Args:
            *groups (:py:class:`streamsets.sdk.sch_models.Group`): One or more groups to add to the project.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """

        if not all([isinstance(group, Group) for group in groups]):
            raise TypeError("groups should be of type :py:class:`streamsets.sdk.sch_models.Group`.")

        if not all([group.group_id is not None for group in groups]):
            raise ValueError("Group's ID should not be None, ensure the group is added to Control Hub.")

        # ensure all groups exist in the project before removing
        for group in groups:
            try:
                self.groups.get(group_id=group.group_id)
            except ValueError:
                raise ValueError(f"Group with ID {group.group_id} not found in project.")

        # since all groups exist in the project, we can remove them
        for group in groups:
            self.groups.remove(group)

        # finally, commit to control hub
        return self._commit_groups_to_control_hub()


@analytics_class_decorator
class Projects(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Project` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
    """

    def __init__(self, control_hub):
        super().__init__(control_hub)

    def _get_all_results_from_api(self, **kwargs):
        """
        Args:
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Project` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.User`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()

        response = self._control_hub.api_client.get_all_projects_in_org(
            offset=kwargs_unioned['offset'], len=kwargs_unioned['len']
        ).response.json()

        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Project, {'control_hub': self._control_hub})


@analytics_class_decorator
class ProjectBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Project`.

    Instead of instantiating this class directly, all users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_project_builder`.

    Args:
        project (:obj:`dict`): Python object built from our Swagger NewProject definition.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub.
    """

    def __init__(self, project, control_hub):
        self._project = project
        self._control_hub = control_hub

    def build(self, name, description=None):
        """Build the Project.

        Args:
            name (:obj:`str`): Name of the project.
            description (:obj:`str`, optional): Description of the project. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Project`.
        """
        self._project['name'] = name
        self._project['description'] = description

        return Project(project=self._project, control_hub=self._control_hub)


# We define module-level attributes to allow users to extend certain
# ControlHub classes and have them used by other classes without the need to override
# their methods (e.g. allow the Pipeline class to be extended and be built using a
# non-extended PipelineBuilder class).
_Pipeline = Pipeline
_SchSdcStage = SchSdcStage
_SchStStage = SchStStage

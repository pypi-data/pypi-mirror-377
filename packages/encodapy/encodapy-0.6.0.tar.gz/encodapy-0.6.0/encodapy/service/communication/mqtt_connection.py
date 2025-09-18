"""
Description: This file contains the class MqttConnection,
which is used to store the connection parameters for the MQTT broker.
Author: Maximilian Beyer
"""

import json
import os
import re
from datetime import datetime, timezone
from typing import Optional, Union

import paho.mqtt.client as mqtt
from loguru import logger
from paho.mqtt.enums import CallbackAPIVersion
from pandas import DataFrame

from encodapy.config import (
    ConfigModel,
    DataQueryTypes,
    DefaultEnvVariables,
    InputModel,
    Interfaces,
    OutputModel,
)
from encodapy.utils.error_handling import ConfigError, NotSupportedError
from encodapy.utils.models import (
    AttributeModel,
    InputDataAttributeModel,
    InputDataEntityModel,
    OutputDataEntityModel,
)


class MqttConnection:
    """
    Class for the connection to a MQTT broker.
    Only a helper class.
    """

    def __init__(self) -> None:
        """
        Constructor for the MqttConnection class.
        Initializes the MQTT parameters and the MQTT client.
        """
        self.mqtt_params: dict = {}
        self.config: ConfigModel
        self.mqtt_client: Optional[mqtt.Client] = None
        self.mqtt_message_store: dict[str, dict] = {}
        self._mqtt_loop_running = False

    def load_mqtt_params(self) -> None:
        """
        Function to load the MQTT parameters from the environment variables
        or use the default values from the DefaultEnvVariables class.
        """
        # the IP of the broker
        self.mqtt_params["host"] = os.environ.get(
            "MQTT_HOST", DefaultEnvVariables.MQTT_HOST.value
        )
        # the port of the broker
        self.mqtt_params["port"] = int(
            os.environ.get("MQTT_PORT", DefaultEnvVariables.MQTT_PORT.value)
        )
        # the username to connect to the broker
        self.mqtt_params["username"] = os.environ.get(
            "MQTT_USERNAME", DefaultEnvVariables.MQTT_USERNAME.value
        )
        # the password to connect to the broker
        self.mqtt_params["password"] = os.environ.get(
            "MQTT_PASSWORD", DefaultEnvVariables.MQTT_PASSWORD.value
        )
        # the topic prefix to use for the topics
        self.mqtt_params["topic_prefix"] = os.environ.get(
            "MQTT_TOPIC_PREFIX", DefaultEnvVariables.MQTT_TOPIC_PREFIX.value
        )

        if not self.mqtt_params["host"] or not self.mqtt_params["port"]:
            raise ConfigError("MQTT host and port must be set")

    def prepare_mqtt_connection(self) -> None:
        """
        Function to prepare the MQTT connection
        """
        # initialize the MQTT client
        if not self.mqtt_client:
            self.mqtt_client = mqtt.Client(
                callback_api_version=CallbackAPIVersion.VERSION2
            )

        # set username and password for the MQTT client
        self.mqtt_client.username_pw_set(
            username=self.mqtt_params["username"], password=self.mqtt_params["password"]
        )

        # try to connect to the MQTT broker
        try:
            self.mqtt_client.connect(
                host=self.mqtt_params["host"], port=self.mqtt_params["port"]
            )
        except Exception as e:
            raise ConfigError(
                f"Could not connect to MQTT broker {self.mqtt_params['host']}:"
                f"{self.mqtt_params['port']} with given login information - {e}"
            ) from e

        # prepare the message store
        self.prepare_mqtt_message_store()

        # subscribe to all topics in the message store
        self.subscribe_to_message_store_topics()

        # start the MQTT client loop
        self.start_mqtt_client()

    def prepare_mqtt_message_store(self) -> None:
        """
        Function to prepare the MQTT message store for all input entities and their attributes.
        Sets the optional default values for all attributes of the entities in the config.
        The Topic structure is defined as follows:
        <topic_prefix>/<entity_id(_interface)>/<attribute_id(_interface)>

        Format of the message store:
        {
            "topic": {
                "entity_id": "entity_id",
                "attribute_id": "attribute_id",
                "payload": value,
                "timestamp": datetime.now(),
            }
        }
        """
        if self.mqtt_message_store:
            logger.warning("MQTT message store is not empty and will be overwritten.")
            self.mqtt_message_store.clear()

        if self.config is None:
            raise ConfigError(
                "ConfigModel is not set. Please set the config before using the MQTT connection."
            )

        for entity in self.config.inputs:
            if entity.interface == Interfaces.MQTT:
                # add the entity itself to the message store
                topic = self.assemble_topic_parts(
                    [self.mqtt_params["topic_prefix"], entity.id_interface]
                )

                self._add_item_to_mqtt_message_store(
                    topic=topic,
                    entity_id=entity.id,
                )

                # iterate over all attributes of the entity and add them to the message store
                for attribute in entity.attributes:
                    topic = self.assemble_topic_parts(
                        [
                            self.mqtt_params["topic_prefix"],
                            entity.id_interface,
                            attribute.id_interface,
                        ]
                    )

                    # set the default value for the attribute
                    if hasattr(attribute, "value"):
                        default_value = attribute.value
                    else:
                        default_value = None

                    self._add_item_to_mqtt_message_store(
                        topic=topic,
                        entity_id=entity.id,
                        attribute_id=attribute.id,
                        payload=default_value,
                    )

    def assemble_topic_parts(self, parts: list[str | None]) -> str:
        """
        Function to build a topic from a list of strings.
        Ensures that the resulting topic is correctly formatted with exactly one '/' between parts.

        Args:
            parts (list[str|None]): List of strings to be joined into a topic.

        Returns:
            str: The correctly formatted topic.

        Raises:
            ValueError: If the list of parts is empty.
        """
        if not parts:
            raise ValueError("The list of parts cannot be empty.")

        # drop a part if it is None or empty
        parts = [part for part in parts if part not in (None, "")]

        # Join the parts with a single '/',
        # stripping only trailing slashes from each part to avoid double slashes in the topic
        topic = "/".join(part.rstrip("/") for part in parts if isinstance(part, str))

        return topic

    def _add_item_to_mqtt_message_store(
        self,
        *,
        topic: str,
        entity_id: str,
        attribute_id: Optional[str] = None,
        payload=None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Function to add an item to the MQTT message store.

        If the topic already exists, it will be overwritten and logs a warning.

        Args:
            topic (str): The topic to add the item to.
            entity_id (str): The ID of the entity.
            attribute_id (Optional[str]): The ID of the attribute (if applicable).
            payload: The default value of the message (if applicable).
            timestamp (Optional[datetime]): The initial timestamp of the message (if applicable).
        """
        if topic in self.mqtt_message_store:
            logger.warning(
                f"Topic {topic} from entity {entity_id} already exists in message store, "
                "overwriting it. This should not happen, check your configuration."
            )

        self.mqtt_message_store[topic] = {
            "entity_id": entity_id,
            "attribute_id": attribute_id,
            "payload": payload,
            "timestamp": timestamp,
        }

    def publish(
        self,
        topic: str,
        payload: Union[str, float, int, bool, dict, list, DataFrame, None],
    ) -> None:
        """
        Function to publish a message (payload) to a topic.

        Every payload is converted to a utf8 encoded string before publishing
        (at the latest from the paho-mqtt package used).

        Args:
            topic (str): The topic to publish the message to
            payload (Union[str, float, int, bool, dict, list, DataFrame, None]): payload to publish
        """
        if not self.mqtt_client:
            raise NotSupportedError(
                "MQTT client is not prepared. Call prepare_mqtt_connection() first."
            )

        payload = self.prepare_payload_for_publish(payload)
        self.mqtt_client.publish(topic, payload)
        logger.debug(f"Published to topic {topic}: {payload}")

    def prepare_payload_for_publish(
        self, payload: Union[str, float, int, bool, dict, list, DataFrame, None]
    ) -> Union[str, None]:
        """
        Function to prepare the payload for publishing.

        Converts the payload to a JSON string if it is a dict, list or DataFrame.
        If the payload is a string, float, int or bool, it is converted to a string.
        If the payload is None or an unsupported type, it is set to None.
        """
        try:
            if isinstance(payload, (dict, list)):
                payload = json.dumps(payload)
            elif isinstance(payload, DataFrame):
                payload = payload.to_json()
            elif isinstance(payload, (str, float, int, bool)):
                payload = str(payload)
            elif payload is None:
                pass
            else:
                logger.warning(
                    f"Unsupported payload type: {type(payload)}, set it to None"
                )
                payload = None

        except TypeError as e:
            logger.warning(f"Failed to convert payload: {e}, set it to None")
            payload = None

        return payload

    def subscribe_to_message_store_topics(self) -> None:
        """
        Function to subscribe to all topics in the message store.
        """
        if not self.mqtt_message_store:
            raise NotSupportedError(
                "MQTT message store is initialized, but empty. Cannot subscribe to topics."
            )

        for topic in self.mqtt_message_store:
            self.subscribe(topic)
            logger.debug(f"Subscribed to topic: {topic}")

    def subscribe(self, topic) -> None:
        """
        Function to subscribe to a topic
        """
        if not self.mqtt_client:
            raise NotSupportedError(
                "MQTT client is not prepared. Call prepare_mqtt_connection() first."
            )
        self.mqtt_client.subscribe(topic)

    def on_message(self, _, __, message):
        """
        Callback function for received messages.

        Stores the decoded message payload with its timestamp in the message store.
        If the message is from an entity, the payload is scanned for attributes and
        their values are stored in the message store, too.
        """
        if not hasattr(self, "mqtt_message_store"):
            raise NotSupportedError(
                "MQTT message store is not initialized. Call prepare_mqtt_connection() first."
            )

        current_time = datetime.now(timezone.utc)

        debug_message = (
            f"MQTT connection received message on {message.topic} at {current_time}."
        )

        if message.topic in self.mqtt_message_store:
            # decode the message payload
            try:
                payload = message.payload.decode("utf-8")
            except UnicodeDecodeError as e:
                logger.error(debug_message + f" Failed to decode message payload: {e}.")
                return

            # store payload and current time in the message store
            self.mqtt_message_store[message.topic]["payload"] = payload
            self.mqtt_message_store[message.topic]["timestamp"] = current_time

            debug_message += f" Updated MQTT message store with value: {payload}."

            # if the item in the store is from an entity, its attribute_id in the store must be None
            # and attribute values are possibly in payload
            if self.mqtt_message_store[message.topic]["attribute_id"] is None:
                # get the entity from the message store
                entity_id = self.mqtt_message_store[message.topic]["entity_id"]
                debug_message += (
                    f" Message is from entity {entity_id}, try to extract attributes."
                )
                # try to parse the payload as JSON
                try:
                    payload = json.loads(payload)
                    if isinstance(payload, dict):
                        # extract attributes from the payload and update the message store
                        logger.debug(debug_message)
                        self._extract_attributes_from_payload_and_update_store(
                            entity_id=entity_id, payload=payload, timestamp=current_time
                        )
                    else:
                        debug_message += (
                            f" Unexpected payload format, type={type(payload)}."
                        )
                        logger.warning(debug_message)
                except json.JSONDecodeError:
                    debug_message += (
                        f" Failed to decode JSON payload: type={type(payload)}."
                    )
                    logger.error(debug_message)
                    return
            else:
                logger.debug(debug_message)

    def _extract_attributes_from_payload_and_update_store(
        self,
        entity_id: str,
        payload: dict,
        timestamp: datetime = datetime.now(),
    ) -> None:
        """
        Function to extract attributes from the payload and update the message store.
        This is called when a message is received on a topic that corresponds to an entity.

        Args:
            entity_id (str): The ID of the entity the message is related to.
            payload (dict): The payload received from the MQTT broker.
            timestamp (datetime): The timestamp when the message was received.
        """
        if not hasattr(self, "mqtt_message_store"):
            raise NotSupportedError(
                "MQTT message store is not initialized. Call prepare_mqtt_connection() first."
            )

        debug_message = ""

        for key, value in payload.items():
            # search in the message store for a subtopic that matches the key and entity
            for topic, item in self.mqtt_message_store.items():
                # check if the item in the message store is from the entity
                if item["entity_id"] != entity_id:
                    continue

                # get subtopic (last part of the topic),
                # which could reference the attribute.id_interface
                subtopic = topic.split("/")[-1] if "/" in topic else topic

                # if subtopic matches key in the payload from entity, update the message store
                if subtopic == key:
                    item["payload"] = value
                    item["timestamp"] = timestamp
                    debug_message += (
                        f"Updated MQTT message store for topic {topic} with value: {value} "
                        f"and timestamp: {timestamp}"
                    )
                    continue

        if debug_message == "":
            debug_message += (
                f" No updates made to MQTT message store for entity {entity_id}."
            )

        logger.debug(debug_message)

    def start_mqtt_client(self):
        """
        Function to hang in on_message hook and start the MQTT client loop
        """
        if not hasattr(self, "mqtt_client") or self.mqtt_client is None:
            raise NotSupportedError(
                "MQTT client is not prepared. Call prepare_mqtt_connection() first."
            )

        if hasattr(self, "_mqtt_loop_running") and self._mqtt_loop_running:
            raise NotSupportedError("MQTT client loop is already running.")

        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.loop_start()
        self._mqtt_loop_running = True  # state variable to check if the loop is running

    def stop_mqtt_client(self):
        """
        Function to stop the MQTT client loop and clean up resources
        """
        if isinstance(self.mqtt_client, mqtt.Client) and self._mqtt_loop_running:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self._mqtt_loop_running = False

    def get_data_from_mqtt(
        self,
        method: DataQueryTypes,  # pylint: disable=unused-argument
        entity: InputModel,
    ) -> InputDataEntityModel:
        """
        Function to get the data from the MQTT broker.
        It checks the MQTT message store for the topics of the entity and its attributes.
        If the topic is found, it extracts the data from the message payload.
        If the topic is not found or the payload is not in the expected format,
        it sets the data to None and marks it as unavailable.


        Args:
            method (DataQueryTypes): The method is currently not used.
            entity (InputModel): Input entity

        Returns:
            InputDataEntityModel: Model with input data (data=None if no data available)
        """
        if not hasattr(self, "mqtt_message_store"):
            raise NotSupportedError(
                "MQTT message store is not initialized. Call prepare_mqtt_connection() first."
            )

        attributes_values = []

        for attribute in entity.attributes:
            # construct the topic for the attribute
            topic = self.assemble_topic_parts(
                [
                    self.mqtt_params["topic_prefix"],
                    entity.id_interface,
                    attribute.id_interface,
                ]
            )

            # if the topic is not in the message store, mark the data as unavailable
            if topic not in self.mqtt_message_store:
                logger.warning(
                    f"Topic {topic} not found in MQTT message store. Setting data as None and "
                    "unavailable. User should check for possible misconfiguration!"
                )
                data = None
                data_available = False
                timestamp = None

            # if the topic is in the message store, extract the data from message payload
            else:
                message_payload = self.mqtt_message_store[topic]["payload"]
                try:
                    data = self._extract_payload_value(message_payload)
                    data_available = True
                except ValueError as e:
                    logger.error(
                        f"Failed to extract payload value for topic {topic}: {e}. "
                        "Setting data as None and unavailable."
                    )
                    data = None
                    data_available = False

                # Get the timestamp from the message store
                timestamp = self.mqtt_message_store[topic]["timestamp"]

            attributes_values.append(
                InputDataAttributeModel(
                    id=attribute.id,
                    data=data,
                    data_type=attribute.type,
                    data_available=data_available,
                    latest_timestamp_input=timestamp,
                    unit=None,  # TODO MB: Add unit handling if necessary
                )
            )
        return InputDataEntityModel(id=entity.id, attributes=attributes_values)

    def _extract_payload_value(
        self, payload
    ) -> Union[str, float, int, bool, dict, list, DataFrame, None]:
        """
        Function to extract data from the payload as needed.
        # TODO MB: How to use pd.read_json here for Dataframes?
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_json.html
        """
        if payload is None or payload == "":
            return None

        # If the payload is not a string (maybe from other source), return it directly
        if not isinstance(payload, str):
            return payload

        # Try to parse JSON (automatically handles int, float, bool, dicts, lists)
        try:
            parsed = json.loads(payload)
            # If the payload is a valid dict, try to extract a value from it
            if isinstance(parsed, dict):
                # Ensure case-insensitive key check and return value of first found "value" key
                value = next((parsed[k] for k in parsed if k.lower() == "value"), None)
                if value is not None:
                    return value
            return parsed
        except json.JSONDecodeError:
            pass

        # If the payload is a string that starts with a number, try to extract it
        # This handles cases like "22.5 °C" or "6552.0 h" where we want to extract the number
        # and ignore the unit (if any).
        # The regex matches an optional leading '-' for negative numbers, followed by digits,
        # optionally with a decimal point and more digits.
        match = re.match(r"^\s*(-?\d+(\.\d+)?)", payload)
        if match:
            num_str = match.group(1)
            if "." in num_str:
                return float(num_str)
            return int(num_str)

        # if nothing else worked, return the payload as is
        return payload

    def send_data_to_mqtt(
        self,
        output_entity: OutputModel,
        output_attributes: list[AttributeModel],
        # output_commands: list[CommandModel],
    ) -> None:
        """
        Function to send the output data to MQTT (publish the data to the MQTT broker).

        Args:
            - output_entity: OutputModel with the output entity
            - output_attributes: list with the output attributes
        """
        if not hasattr(self, "mqtt_client"):
            raise NotSupportedError(
                "MQTT client is not prepared. Call prepare_mqtt_connection() first."
            )

        # check if the config is set
        if self.config is None:
            raise ConfigError(
                "ConfigModel is not set. Please set the config before using the MQTT connection."
            )

        # publish the data to the MQTT broker
        for attribute in output_attributes:
            topic = self.assemble_topic_parts(
                [
                    self.mqtt_params["topic_prefix"],
                    output_entity.id_interface,
                    attribute.id_interface,
                ]
            )
            payload = attribute.value
            self.publish(topic, payload)

    def _get_last_timestamp_for_mqtt_output(
        self, output_entity: OutputModel
    ) -> tuple[OutputDataEntityModel, Union[datetime, None]]:
        """
        Function to get the latest timestamps of the output entity from a MQTT message, if exists.

        Args:
            output_entity (OutputModel): Output entity

        Returns:
            tuple[OutputDataEntityModel, Union[datetime, None]]:
                - OutputDataEntityModel with timestamps for the attributes
                - the latest timestamp of the output entity for the attribute
                with the oldest value (None if no timestamp is available)
        """
        timestamps: list = []
        timestamp_latest_output = None

        return (
            OutputDataEntityModel(id=output_entity.id, attributes_status=timestamps),
            timestamp_latest_output,
        )

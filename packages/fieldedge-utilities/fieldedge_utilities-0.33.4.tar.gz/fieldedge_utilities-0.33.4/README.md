# Viasat FieldEdge Utilities

The FieldEdge project supports *Internet of Things* (**IoT**) using
satellite communications technology. Generally this library is meant to be used
on single board computers capable of running Debian Linux.

>*While the authors recognize Python has several shortcomings for embedded use,*
*it provides a useful learning template.*

This library available on [**PyPI**](https://pypi.org/project/fieldedge-utilities/)
provides:

* A common **`logger`** format and wrapping file facility with UTC timestamps.
* A **`timer.RepeatingTimer`** utility (thread) that can be started, stopped,
restarted, and interval changed.
* A simplified **`mqtt`** client that automatically (re)onnects
(by default to a local `fieldedge-broker`).
* Helper functions for managing files and **`path`** on different OS.
* An interface for the FieldEdge **`hostpipe`** or **`hostrequest`** service
for sending host commands from a Docker container, with request/result captured
in a logfile.
* Helper functions **`ip.interfaces`** for finding and validating IP interfaces
and addresses/subnets.
* A defined set of common **`ip.protocols`** used for packet analysis and
satellite data traffic optimisation.
* Helpers for managing **`serial`** ports on a host system.
* Utilities for converting **`timestamp`**s between unix and ISO 8601
* **`properties`** manipulation and conversion between JSON and PEP style,
and derived from classes or instances.
    * **`ConfigurableProperty`** for improved ISC configuration handling.
    * **`DelegatedProperty`** for subclass conversions of method to property
    with optional caching.
* Classes useful for implementing **`microservice`**s based on MQTT
inter-service communications and task workflows:
    * **`interservice`** communications tasks and searchable queue.
    * **`microservice`** class for consistent abstraction and interaction.
    * **`msproxy`** microservice proxy class form a kind of twin of another
    microservice, as a child of a microservice.
    * **`feature`** class as a child of a microservice, with routing of MQTT
    topics and messages and interaction with a simple task queue.
    * **`propertycache`** concept for caching frequently referenced object
    properties where the query may take time.
    * **`subscriptionproxy`** allows cascading of received MQTT messages to
    multiple modules within a project framing a microservice.

[Docmentation](https://inmarsat-enterprise.github.io/fieldedge-utilities/)

Rosbag module 
======================================


A ROS bag is a file format in ROS for storing ROS message data. The rapyuta.io platform allows you to record the ROS messages (ROS topics) for ROS enabled components deployed on the cloud.



.. toctree::
   :maxdepth: 1
   :caption: Contents:
   
Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, create_rosbag_job, list_rosbag_jobs, list_rosbag_jobs_in_project, stop_rosbag_jobs, list_rosbag_blobs, download_rosbag_blob, delete_rosbag_blob



Rosbag Module
-----------------


.. automodule:: rapyuta_io.clients.rosbag
    :members:
    :exclude-members: get_deserialize_map,get_serialize_map, is_ready, poll_till_ready


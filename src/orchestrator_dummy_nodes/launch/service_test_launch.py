from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node, SetParameter
from orchestrator.orchestrator_lib.remapping_generation import generate_remappings_from_config


def generate_launch_description():
    logger = LaunchConfiguration("log_level")

    remap_actions = generate_remappings_from_config("orchestrator_dummy_nodes", "service_test_launch_config.json")
    for r in remap_actions:
        r.__condition = IfCondition(LaunchConfiguration("intercepted"))

    return LaunchDescription([
        DeclareLaunchArgument(
            "log_level",
            default_value=["info"],
            description="Logging level",
        ),
        DeclareLaunchArgument(
            "intercepted",
            default_value='false'
        ),

        SetParameter(name="use_sim_time", value=True),

        *remap_actions,

        Node(
            package='orchestrator_dummy_nodes',
            executable='service_provider_node',
            name='SP',
            arguments=['--ros-args', '--log-level', ['SP:=', logger]],
        ),
        Node(
            package='orchestrator_dummy_nodes',
            executable='service_caller_node',
            name='C1',
            arguments=['--ros-args', '--log-level', ['C1:=', logger]],
        ),
        Node(
            package='orchestrator_dummy_nodes',
            executable='service_caller_node',
            name='C2',
            arguments=['--ros-args', '--log-level', ['C2:=', logger]],
        ),
    ])

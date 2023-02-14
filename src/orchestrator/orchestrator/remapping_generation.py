import sys

from orchestrator_dummy_nodes.orchestrator_lib.node_model import TopicInput
from orchestrator_dummy_nodes.orchestrator_lib.name_utils import intercepted_name
from .model_loader import *

from launch_ros.actions import SetRemap
from launch.substitutions import TextSubstitution


def _find_node_model(name: str, models: list[NodeModel]) -> NodeModel:
    for model in models:
        if name == model.get_name():
            return model

    raise RuntimeError(f"No model for node with name {name}")


def generate_remappings_from_config(package_name: str, launch_config_file: str) -> list[SetRemap]:
    """Generate remappings for topic interception by orchestrator."""
    launch_config = load_launch_config(package_name, launch_config_file, load_launch_config_schema())
    node_models = load_models(launch_config, load_node_config_schema())

    remap_actions = []

    for node_name, node in launch_config["nodes"].items():
        for internal_name, ros_name in node["remappings"].items():

            model = _find_node_model(node_name, node_models)
            if TopicInput(ros_name) not in model.get_possible_inputs():
                continue

            remap_src = f"{node_name}:{internal_name}"
            remap_dst = intercepted_name(node_name, ros_name)
            remap_actions.append(
                SetRemap(src=remap_src, dst=remap_dst)
            )

    return remap_actions


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <package_name> <launch_config_file_name>")
        exit(1)

    package_name = sys.argv[1]
    config_name = sys.argv[2]

    remappings = generate_remappings_from_config(package_name, config_name)
    for r in remappings:
        if len(r.src) == 0 or not isinstance(r.src[0], TextSubstitution):
            raise RuntimeError(f"Source is not a TextSubstitution, no idea how to print that nicely: {r.src}")
        if len(r.dst) == 0 or not isinstance(r.dst[0], TextSubstitution):
            raise RuntimeError(f"Destination is not a TextSubstitution, no idea how to print that nicely: {r.src}")
        print(f"Remap {r.src[0].text} to {r.dst[0].text}")


if __name__ == '__main__':
    main()
import time
import json


"""
WorldIO: Import/Export World Configurations for easy Reproducibility
[STATIC METHODS HOLDER] -- No instantiation Needed
"""
class WorldIO:
    @staticmethod
    def save_world(world, file_name=None):
        world_dict = world.as_config_dict()
        j_string = json.dumps(world_dict)
        if file_name is None:
            file_name = f"world_{int(time.time())}.json"
        with open(file_name, "w") as f:
            f.write(j_string)
        print(f"World data saved to {file_name}.")

    @staticmethod
    def load_world_dictionary(file_name):
        file = open(file_name, mode='r')
        contents = file.read()
        file.close()
        d = json.loads(contents)
        return d

    @staticmethod
    def sim_from_json(file_name):
        from src.swarmsim.config.WorldConfig import RectangularWorldConfig
        from src.swarmsim.world.simulate import main as sim

        d = WorldIO.load_world_dictionary(file_name)
        config = RectangularWorldConfig.from_dict(d)
        # for c in config.agentConfig.get_configs():
        #     c.body_filled = True
        #     c.agent_radius = 7
        sim(config)



"""
Given a File, JSON_WORLD, simulate the entire experiment with a single function call
"""
if __name__ == "__main__":
    JSON_WORLD = "../../../demo/results/experiments/heterogeneous_behaviors/goal_behaviors/leader_follower.json"
    # JSON_WORLD = "../../../demo/results/experiments/heterogeneous_behaviors/goal_behaviors/leader_follower_GMU_edition.json"
    WorldIO.sim_from_json(JSON_WORLD)

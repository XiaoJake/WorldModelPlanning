import time
from tqdm import tqdm
from tests_custom.base_planning_tester import BasePlanningTester, TEST_NAME, ELITES, CUSTOM_SEED, ACTION_HISTORY
from gym.envs.box2d.car_dynamics import Car

# custom args
OPTIMAL_STEPS = 'optimal_steps'
OPTIMAL_REWARD = 'optimal_reward'
RANDOM_REWARD = 'random_reward'
TILES_TO_COMPLETE = 'tiles_to_complete'
START_TRACK = 'start_track'
PRE_ACTIONS = 'pre_actions'

class PlanningTester(BasePlanningTester):
    def __init__(self, config, vae, mdrnn, preprocessor, planning_agent):
        super().__init__(config, vae, mdrnn, preprocessor, planning_agent)
        self.is_render_best_elite_only = self.config['visualization']['is_best_elite_trajectory_only']
        self.is_render_fitness = self.config['visualization']['is_render_fitness']
        self.is_render_trajectory = self.config['visualization']['is_render_trajectory']


    def get_test_functions(self):
        return {  # (test_func, args)
                "planning_whole_random_track": (self._planning_whole_random_track_test, {OPTIMAL_REWARD: 900, OPTIMAL_STEPS: 1000, RANDOM_REWARD: -3, TILES_TO_COMPLETE: 1200, CUSTOM_SEED: None, PRE_ACTIONS: None}),
                "planning_specific_track": (self._planning_specific_track_test, {OPTIMAL_REWARD: 900, OPTIMAL_STEPS: 1000, RANDOM_REWARD: -3, TILES_TO_COMPLETE: 1200, CUSTOM_SEED: 9214, PRE_ACTIONS: None}),
                "planning_whole_track_no_right_turns_test": (self._planning_whole_track_no_right_turns_test, {OPTIMAL_REWARD: 900, OPTIMAL_STEPS: 1000, RANDOM_REWARD: -32, TILES_TO_COMPLETE: 1200, CUSTOM_SEED: 30, PRE_ACTIONS: None}),
                "planning_forward_left_side": (self._planning_forward_left_side, {OPTIMAL_REWARD: 66, OPTIMAL_STEPS: 100, RANDOM_REWARD: -7, TILES_TO_COMPLETE: 25, CUSTOM_SEED: 9214, PRE_ACTIONS: None}),
                "planning_forward_right_side": (self._planning_forward_right_side, {OPTIMAL_REWARD: 66, OPTIMAL_STEPS: 100, RANDOM_REWARD: -7, TILES_TO_COMPLETE: 25, CUSTOM_SEED: 9214, PRE_ACTIONS: None}),
                "planning_head_to_grass_right": (self._planning_head_to_grass_right, {OPTIMAL_REWARD: 66, OPTIMAL_STEPS: 100, RANDOM_REWARD: -7, TILES_TO_COMPLETE: 25, CUSTOM_SEED: 9214, PRE_ACTIONS: None}),
                "planning_head_to_grass_left": (self._planning_head_to_grass_left, {OPTIMAL_REWARD: 66, OPTIMAL_STEPS: 100, RANDOM_REWARD: -7, TILES_TO_COMPLETE: 25, CUSTOM_SEED: 9214, PRE_ACTIONS: None}),
                "planning_forward_test": (self._planning_forward_test, {OPTIMAL_REWARD: 66, OPTIMAL_STEPS: 100, RANDOM_REWARD: -7, TILES_TO_COMPLETE: 25, CUSTOM_SEED: 9214, PRE_ACTIONS: None}),
                "planning_left_turn_test": (self._planning_left_turn_test, {OPTIMAL_REWARD: 23, OPTIMAL_STEPS: 100, RANDOM_REWARD: -3, TILES_TO_COMPLETE: 10, CUSTOM_SEED: 9214, PRE_ACTIONS: None}),
                "planning_right_turn_test": (self._planning_right_turn_test,{OPTIMAL_REWARD: 33, OPTIMAL_STEPS: 100, RANDOM_REWARD: -3, TILES_TO_COMPLETE: 11, CUSTOM_SEED: 2, PRE_ACTIONS: None}),
                "planning_s_turn_test": (self._planning_s_turn_test, {OPTIMAL_REWARD: 43, OPTIMAL_STEPS: 100, RANDOM_REWARD: -3, TILES_TO_COMPLETE: 16, CUSTOM_SEED: 9214, PRE_ACTIONS: None}),
                "planning_u_turn_test": (self._planning_u_turn_test, {OPTIMAL_REWARD: 40, OPTIMAL_STEPS: 280, RANDOM_REWARD: -5, TILES_TO_COMPLETE: 15, CUSTOM_SEED: 9214, PRE_ACTIONS: None}),
        }

    # TEST METHODS #######################################

    def _planning_forward_left_side(self, args):
        pre_actions = []
        pre_actions.extend([[-1, 0.1, 0] for _ in range(30)])
        pre_actions.extend([[1, 0.1, 0] for _ in range(5)])
        pre_actions.extend([[0.15, 0.1, 0] for _ in range(35)])
        pre_actions.extend([[0, 0.1, 0] for _ in range(30)])

        args[PRE_ACTIONS] = pre_actions
        args[TEST_NAME] = 'planning_forward_left_side'
        args[START_TRACK] = 25
        return self._run_plan_or_replay(args=args)

    def _planning_forward_right_side(self, args):
        pre_actions = []
        pre_actions.extend([[1, 0.1, 0] for _ in range(25)])
        pre_actions.extend([[-1, 0.1, 0] for _ in range(5)])
        pre_actions.extend([[-0.15, 0.1, 0] for _ in range(35)])
        pre_actions.extend([[0, 0.1, 0] for _ in range(30)])

        args[PRE_ACTIONS] = pre_actions
        args[TEST_NAME] = 'planning_forward_right_side'
        args[START_TRACK] = 25
        return self._run_plan_or_replay(args=args)

    def _planning_head_to_grass_left(self, args):
        pre_actions = []
        pre_actions.extend([[1, 0.1, 0] for _ in range(25)])
        pre_actions.extend([[-1, 0.1, 0] for _ in range(5)])
        pre_actions.extend([[-0.15, 0.1, 0] for _ in range(30)])
        pre_actions.extend([[0.05, 0.1, 0] for _ in range(20)])
        pre_actions.extend([[0.05, 0.1, 0] for _ in range(5)])
        pre_actions.extend([[-1, 0.0, 0] for _ in range(15)])
        pre_actions.extend([[-0.1, 0.0, 0.01] for _ in range(20)])
        args[PRE_ACTIONS] = pre_actions
        args[TEST_NAME] = 'planning_head_to_grass_left'
        args[START_TRACK] = 25
        return self._run_plan_or_replay(args=args)

    def _planning_head_to_grass_right(self, args):
        pre_actions = []
        pre_actions.extend([[-1, 0.1, 0] for _ in range(25)])
        pre_actions.extend([[0.15, 0.1, 0] for _ in range(30)])
        pre_actions.extend([[-0.05, 0.1, 0] for _ in range(20)])
        pre_actions.extend([[1, 0.0, 0] for _ in range(15)])
        pre_actions.extend([[0.1, 0.0, 0.01] for _ in range(10)])
        args[PRE_ACTIONS] = pre_actions
        args[TEST_NAME] = 'planning_head_to_grass_right'
        args[START_TRACK] = 25
        return self._run_plan_or_replay(args=args)

    def _planning_forward_test(self, args):
        args[TEST_NAME] = 'planning_forward_test'
        args[START_TRACK] = 25
        return self._run_plan_or_replay(args=args)

    def _planning_left_turn_test(self, args):
        args[TEST_NAME] = 'planning_left_turn_test'
        args[START_TRACK] = 14
        return self._run_plan_or_replay(args=args)

    def _planning_right_turn_test(self, args):
        args[TEST_NAME] = 'planning_right_turn_test'
        args[START_TRACK] = 222
        return self._run_plan_or_replay(args=args)

    def _planning_u_turn_test(self, args):
        args[TEST_NAME] = 'planning_u_turn_test'
        args[START_TRACK] = 103
        return self._run_plan_or_replay(args=args)

    def _planning_s_turn_test(self, args):
        args[TEST_NAME] = 'planning_s_turn_test'
        args[START_TRACK] = 250
        return self._run_plan_or_replay(args=args)

    def _planning_whole_track_no_right_turns_test(self, args):
        args[TEST_NAME] = 'planning_whole_track_no_right_turns_test'
        args[START_TRACK] = 1
        return self._run_plan_or_replay(args=args)

    def _planning_whole_random_track_test(self, args):
        args[TEST_NAME] = 'planning_whole_random_track'
        args[START_TRACK] = 1
        return self._run_plan_or_replay(args=args)

    def _planning_specific_track_test(self, args):
        args[TEST_NAME] = f'planning_specific_track - seed: {args[CUSTOM_SEED]}'
        # pre_actions = []
        # pre_actions.extend([[0, 1, 0] for _ in range(35)])
        # args[PRE_ACTIONS] = pre_actions
        # args[START_TRACK] = 67
        args[START_TRACK] = 1
        return self._run_plan_or_replay(args=args)

    # ######################################################

    def _run_trial(self, trial_i, args, seed):
        environment = self._get_environment()
        environment.is_random_inital_car_position = False
        current_state = environment.reset(seed)
        seed = environment.seed

        if args[CUSTOM_SEED] is not None:
            self._set_car_position(args[START_TRACK], environment)

        self.simulated_environment.reset()
        latent_state, _ = self._encode_state(current_state)
        hidden_state = self.simulated_environment.get_hidden_zeros_state()

        trial_results_dto = self._get_trial_results_dto(args)
        elites = []
        action_history = []
        start_time = time.time()
        total_reward = 0
        steps_ran = 0
        elapsed_time = 0

        negative_counter = 0
        is_done = False

        total_steps = args['optimal_steps']
        max_negative_count = self.config['test_suite']['car_racing']['max_negative_count']
        progress_bar = tqdm(total=total_steps)

        if args[PRE_ACTIONS] is not None:
            for action in args[PRE_ACTIONS]:
                current_state, reward, is_done, simulated_reward, simulated_is_done, latent_state, hidden_state = \
                    self._step(action, hidden_state, environment)

        for step in range(total_steps):
            action, step_elites = self._search_action(latent_state, hidden_state)
            elites.append(step_elites)

            self._render_fitness_and_trajory(current_state, step_elites, environment)

            if self.config['planning']['planning_agent'] != "RANDOM":
                self._simulate_dream(self.planning_agent.current_elite.action_sequence, current_state, hidden_state)

            if negative_counter == max_negative_count or total_reward > 900:
                break

            current_state, reward, is_done, simulated_reward, simulated_is_done, latent_state, hidden_state = \
                self._step(action, hidden_state, environment)

            negative_counter = 0 if reward > 0 else negative_counter + 1
            action_history.append(action)
            total_reward = environment.get_current_reward()
            steps_ran += 1
            elapsed_time = time.time() - start_time
            self._update_trial_results(trial_results_dto, reward, total_reward, steps_ran)

            progress_bar.set_postfix_str(f"action={action} | total_reward={round(total_reward,3)} | max_reward {round(trial_results_dto['max_reward'],3)} | negative_counter={negative_counter}/{max_negative_count}")
            progress_bar.update(n=1)

        progress_bar.close()
        custom_message = self._print_trial_results(trial_i, seed, elapsed_time, total_reward, steps_ran, trial_results_dto)
        environment.close()
        print(action_history[0], trial_results_dto['max_reward'], seed)
        return elites, action_history, total_reward, trial_results_dto['max_reward'], seed, custom_message

    def _replay_planning_test(self, args):
        actions = args[ACTION_HISTORY]
        elites = args[ELITES]
        seed = args[CUSTOM_SEED]
        environment = self._get_environment()
        _ = environment.reset(seed=seed)
        self.simulated_environment.reset()
        hidden_state = self.simulated_environment.get_hidden_zeros_state()
        self._set_car_position(args[START_TRACK], environment)

        if args[PRE_ACTIONS] is not None:
            for action in args[PRE_ACTIONS]:
                current_state, reward, is_done, simulated_reward, simulated_is_done, latent_state, hidden_state = \
                    self._step(action, hidden_state, environment)

        trial_results_dto = self._get_trial_results_dto(args)

        steps_ran = 0
        total_reward = 0
        for i, action in enumerate(actions):
            action = self._get_action(action)
            current_state, reward, is_done, simulated_reward, simulated_is_done, latent_state, hidden_state = self._step(action, hidden_state, environment)
            steps_ran += 1
            total_reward += reward
            self._update_trial_results(trial_results_dto, reward, total_reward, steps_ran)

            if elites:
                self._render_fitness_and_trajory(step_elites=elites[i], current_state=current_state, environment=environment)
                self._simulate_dream(elites[i][-1][2], current_state, hidden_state)
        environment.close()
        self._print_trial_results(None, seed, None, total_reward, steps_ran, trial_results_dto)

        return actions, total_reward

    def _render_fitness_and_trajory(self, current_state, step_elites, environment):
        if self.is_render_fitness:
            self.visualizer.show_fitness_plot(max_generation=len(step_elites)-1, elites=step_elites, agent=self.config['planning']['planning_agent'])

        if self.is_render_trajectory:
            self.visualizer.show_trajectory_plot(current_state, step_elites, self.config['planning']['planning_agent'],
                                                 environment.environment, self.is_render_best_elite_only)

    def _simulate_dream(self, action_sequence, current_state, hidden_state):
        action_sequence = [self._get_action(action) for action in action_sequence]
        if self.is_render_dream:
            self._step_sequence_in_dream(action_sequence, current_state, hidden_state)

    def _get_action(self, action):
        return action[0] if type(action) == tuple and len(action) == 2 else action

    def _set_car_position(self, start_track, environment):
        if start_track == 1:
            return
        environment.environment.env.car = Car(environment.environment.env.world, *environment.environment.env.track[start_track][1:4])

    def _reward_diff_percentage(self, actual, control):
        return round((actual-control) / 100) if abs(actual) == 0 else round((actual-control) / abs(actual) * 100)

    def _get_trial_results_dto(self, args):
        base_dto = super(PlanningTester, self)._get_trial_results_dto(args)
        base_dto['reward_at_success'] = 0
        base_dto['steps_at_success'] = 0
        base_dto['tiles'] = 0
        base_dto[OPTIMAL_STEPS] = args[OPTIMAL_STEPS]
        base_dto[OPTIMAL_REWARD] = args[OPTIMAL_REWARD]
        base_dto[RANDOM_REWARD] = args[RANDOM_REWARD]
        base_dto[TILES_TO_COMPLETE] = args[TILES_TO_COMPLETE]
        base_dto['reward_at_optimum_steps'] = 0
        return base_dto

    def _update_trial_results(self, trial_results_dto, reward, total_reward, steps_ran):
        tiles = trial_results_dto['tiles']
        tiles_to_complete = trial_results_dto['tiles_to_complete']
        reward_at_success = trial_results_dto['reward_at_success']
        reward_at_optimum_steps = trial_results_dto['reward_at_optimum_steps']
        optimal_steps = trial_results_dto[OPTIMAL_STEPS]

        trial_results_dto['max_reward'] = total_reward if total_reward > trial_results_dto['max_reward'] else trial_results_dto['max_reward']

        trial_results_dto['tiles'] = tiles + 1 if reward > 0 and tiles <= tiles_to_complete else tiles
        if tiles <= tiles_to_complete:
            trial_results_dto['test_success'] = tiles == tiles_to_complete
            trial_results_dto['steps_at_success'] = steps_ran if tiles_to_complete == tiles_to_complete else 0

        trial_results_dto['reward_at_success'] = total_reward if tiles == tiles_to_complete else reward_at_success
        trial_results_dto['reward_at_optimum_steps'] = total_reward if steps_ran == optimal_steps else reward_at_optimum_steps

    def _print_trial_results(self, trial, seed, elapsed_time, total_reward, steps_ran, trial_results_dto):
        test_name = trial_results_dto['test_name']
        optimal_steps = trial_results_dto['optimal_steps']
        optimal_reward = trial_results_dto[OPTIMAL_REWARD]
        random_reward = trial_results_dto[RANDOM_REWARD]
        test_success = trial_results_dto['test_success']
        steps_at_success = trial_results_dto['steps_at_success']
        reward_at_optimum_steps = round(trial_results_dto['reward_at_optimum_steps'], 2)
        reward_at_success = round(trial_results_dto['reward_at_success'], 2)

        optimal_reward_diff = self._reward_diff_percentage(reward_at_optimum_steps, optimal_reward)
        random_reward_diff = self._reward_diff_percentage(reward_at_optimum_steps, random_reward)

        trial_str = '' if trial is None else f'Planning trial: {trial}'
        elapsed_time_str = '' if elapsed_time is None else f'Elapsed_time: {round(elapsed_time,0)}'
        success_str = f'Test success: {test_success} | Reward at success: {reward_at_success} | Steps on Success: {steps_at_success}\n' \
            if test_success else f'Test success: {test_success}\n'
        message = f'Elapsed_time: {elapsed_time_str}\n | seed: {seed}' \
                  f'| Total reward: {round(total_reward, 2)} | Max reward: {round(trial_results_dto["max_reward"],2)} |  Steps on exit: {steps_ran}\n' \
                  f'| {success_str}' \
                  f'| Agent reward at optimal step {optimal_steps} : {reward_at_optimum_steps}\n' \
                  f'| Manual drive reward at  step {optimal_steps} : {optimal_reward} | Reward Diff: {optimal_reward_diff} %\n' \
                  f'| Random drive reward at  step {optimal_steps} : {random_reward}  | Reward Diff: {random_reward_diff} %'
        print(message)
        return message

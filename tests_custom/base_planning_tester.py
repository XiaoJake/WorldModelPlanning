import os
import pickle
import torch
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from pprint import pprint
from os.path import exists, join
from torch import multiprocessing
from datetime import date, datetime
from utility.visualizer import Visualizer
from tests_custom.base_tester import BaseTester
from planning.agent_factory import get_agent_parameters
from concurrent.futures.process import ProcessPoolExecutor
from utility.logging.planning_logger import PlanningLogger

# ARGS KEYS PLANNING
ACTION_HISTORY = 'action_history'
ELITES = 'elites'
CUSTOM_SEED = 'custom_seed'
TEST_NAME = 'test_name'

class BasePlanningTester(BaseTester):
    def __init__(self, config, vae, mdrnn, preprocessor, planning_agent):
        super().__init__(config, vae, mdrnn, preprocessor, trials=config["test_suite"]["trials"])
        self.is_ntbea_tuning = False
        self.is_multithread_tests = self.config['test_suite']['is_multithread_tests']
        self.is_multithread_trials = self.config['test_suite']['is_multithread_trials']
        self.planning_agent = planning_agent
        self.planning_dir = join('tests_custom', config['test_suite']['planning_test_log_dir'])
        self.visualizer = Visualizer()
        self.is_render = config['visualization']['is_render']
        self.is_render_dream = self.config['visualization']['is_render_dream']
        self.is_logging = self.config['test_suite']['is_logging']
        self.session_name = self._make_session_name()

        torch.set_num_threads(1)
        os.environ['OMP_NUM_THREADS'] = '1'

    def get_test_functions(self):
        return NotImplemented

    def _print_trial_results(self, trial, seed, elapsed_time, total_reward, steps_ran, trial_results_dto):
        return NotImplemented

    def _run_trial(self, trial_i, args, seed):
        return NotImplemented

    def _replay_planning_test(self, args):
        return NotImplemented

    def _get_trial_results_dto(self, args):
        return {
            'test_name': args[TEST_NAME],
            'test_success': False,
            'max_reward': 0,
        }

    def _run_new_session(self):
        print('\n--- RUNNING NEW PLANNING TESTS ---')
        return self._run_multithread_new_test_session() if self.is_multithread_tests else \
            self._run_singlethread_new_test_session()

    def run_tests(self, session_name=None):
        self.session_name = self._make_session_name(session_name)
        print('------- Planning Tests params --------')
        print(f'seed: {self.seed} | trials per test: {self.trials}')
        print(f'Planning Agent: {type(self.planning_agent)}')
        pprint(vars(self.planning_agent))  # Print agent params

        if self.config['test_suite']["is_reload_planning_session"] and self._is_session_exists():
            return self._run_cached_session()
        else:
            return self._run_new_session()

    def run_specific_test(self, test_name, session_name=None):
        self.session_name = self._make_session_name(session_name)
        test_func, args = self.get_test_functions()[test_name]
        trial_actions, trial_rewards, trial_elites, trial_max_rewards, trial_seeds = test_func(args=args)
        plt.close('all')
        return test_name, trial_actions, trial_rewards, trial_elites, trial_max_rewards, trial_seeds

    def _run_multithread_new_test_session(self):
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            tests = self.get_test_functions()
            thread_results = list(executor.map(self.run_specific_test, tests.keys()))
            test_results = {}
            for test_name, trial_actions, trial_rewards, trial_elites, trial_max_rewards, trial_seeds in thread_results:
                test_results[test_name] = (test_name, trial_actions, trial_rewards, trial_elites, trial_seeds)
                if len(trial_rewards) > 1:
                    print(f'{self.config["planning"]["planning_agent"]} - {test_name} - Average reward over {len(trial_rewards)} trials: {np.mean(trial_rewards)}')
            self._save_test_session(test_results)
            return self._get_session_total_best_reward(test_results)

    def _run_singlethread_new_test_session(self):
        test_results = {}
        tests = self.get_test_functions()
        for test_name in tests.keys():
            test_func, args = tests[test_name]
            trial_actions, trial_rewards, trial_elites, trial_max_rewards, trial_seeds = test_func(args=args)
            test_results[test_name] = (test_name, trial_actions, trial_rewards, trial_elites, trial_seeds)
            print(f'Average reward over {len(trial_rewards)} trials: {np.mean(trial_rewards)}')
        self._save_test_session(test_results)
        plt.close('all')
        return self._get_session_total_best_reward(test_results)

    def _run_plan_or_replay(self, args):
        print(args[TEST_NAME])
        if ACTION_HISTORY in args:
            return self._replay_planning_test(args)
        else:
            return self._run_planning_test(args)

    def _run_planning_test(self, args):
        trial_actions = []
        trial_rewards = []
        trial_max_rewards = []
        trial_elites = []
        trial_seeds = []
        seed = args[CUSTOM_SEED]
        logger = PlanningLogger(is_logging=self.is_logging)
        logger.start_log(name=self.session_name)
        logger.log_agent_settings(test_name=args[TEST_NAME], agent=self.config['planning']['planning_agent'], settings=f'{vars(self.planning_agent)}')

        if self.is_multithread_trials:
            func_input = [(trial_i, args, seed) for trial_i in range(self.trials)]

            with ProcessPoolExecutor(max_workers=self._get_threads()) as executor:
                thread_results = list(executor.map(self._run_trial_thread, func_input))
                trial_i = 0
                for elites, action_history, total_reward, max_reward, seed, custom_message in thread_results:
                    trial_actions.append(action_history)
                    trial_rewards.append(total_reward)
                    trial_max_rewards.append(max_reward)
                    trial_elites.append(elites)
                    trial_seeds.append(seed)
                    logger.log_trial_rewards(test_name=args[TEST_NAME], trial_idx=trial_i, total_reward=total_reward, max_reward=max_reward)
                    logger.log_custom_trial_results(test_name=args[TEST_NAME], trial_idx=trial_i, results=custom_message)
                    trial_i += 1
        else:
            for i in tqdm(range(self.trials), desc=f'Planning Test on {args[TEST_NAME]} with {self.trials} trials'):
                elites, action_history, total_reward, max_reward, seed, custom_message = self._run_trial(i, args, seed)
                trial_actions.append(action_history)
                trial_rewards.append(total_reward)
                trial_max_rewards.append(max_reward)
                trial_elites.append(elites)
                trial_seeds.append(seed)
                logger.log_trial_rewards(test_name=args[TEST_NAME], trial_idx=i, total_reward=total_reward, max_reward=max_reward)
                logger.log_custom_trial_results(test_name=args[TEST_NAME], trial_idx=i, results=custom_message)
        logger.log_reward_mean_std(args[TEST_NAME], trial_rewards)
        logger.end_log()
        return trial_actions, trial_rewards, trial_elites, trial_max_rewards, trial_seeds

    def _run_trial_thread(self, args):
        return self._run_trial(args[0], args[1], args[2])

    def _run_cached_session(self):
        print('--- RUNNING CACHED PLANNING TESTS ---')
        session = self._load_test_session(session_name=self.config['test_suite']['planning_session_to_load'])
        tests = self.get_test_functions()
        session_reward = 0
        for test_name in session.keys():
            best_trial, best_actions, best_reward, elites, seed = self._get_best_trial_action_and_reward(session[test_name])  # ONLY RUN BEST TRIALS
            print(f'Reload actions from {test_name}, trial {best_trial} with best reward {best_reward}')
            test_func, args = tests[test_name]
            args[ACTION_HISTORY] = best_actions
            args[ELITES] = elites
            args[CUSTOM_SEED] = seed if seed is not None else args[CUSTOM_SEED]
            _, reward = test_func(args=args)
            session_reward += reward
        print(f'Total session reward: {session_reward}')
        return self._get_session_total_best_reward(session)

    def _search_action(self, latent_state, hidden_state):
        if self.config['planning']['planning_agent'] == "MCTS":
            action = self.planning_agent.search(self.simulated_environment, latent_state, hidden_state)
            step_elites = []
        else:
            action, step_elites = self.planning_agent.search(self.simulated_environment, latent_state, hidden_state)

        return action, step_elites

    def _step(self, action, hidden_state, environment):
        current_state, reward, is_done, _ = environment.step(action, ignore_is_done=True)
        latent_state, _ = self._encode_state(current_state)
        latent_state, simulated_reward, simulated_is_done, hidden_state = self.simulated_environment.step(action,
                                                                                                          hidden_state,
                                                                                                          latent_state,
                                                                                                          is_simulation_real_environment=True)

        if self.is_render:
            environment.render()

        return current_state, reward, is_done, simulated_reward, simulated_is_done, latent_state, hidden_state

    def _step_sequence_in_dream(self, actions, current_state, hidden):
        latent, _ = self._encode_state(current_state)
        total_reward = 0

        for action in actions:
            latent, simulated_reward, simulated_is_done, hidden = self.simulated_environment.step(action, hidden,
                                                                                                  latent,
                                                                                                  is_simulation_real_environment=True)
            total_reward += simulated_reward
            self.simulated_environment.render()
        print(f'expected dream reward: {round(total_reward, 2)}')
        return total_reward

    def _save_test_session(self, test_results):
        save_data = {
            'agent_type': self.config['planning']['planning_agent'],
            'agent_params': self._get_agent_parameters(self.config['planning']['planning_agent']),
            'test_results': test_results
        }
        if not exists(self.planning_dir):
            os.mkdir(self.planning_dir)
        session_reward = round(self._get_session_total_best_reward(test_results), 4)
        session_date = date.today().strftime('%Y-%m-%d-%H.%M')

        file_name = f'{self.config["game"]}_{"NTBEA_" if self.is_ntbea_tuning else ""}{save_data["agent_type"]}_{self.config["experiment_name"]}_planning_session_{session_date}_total_session_best_reward_{session_reward}'
        path = join(self.planning_dir, file_name)
        with open(f'{path}.pickle', 'wb') as file:
            pickle.dump(save_data, file, protocol=pickle.HIGHEST_PROTOCOL)
            print(f'results saved at: {path}.pickle')

    def _load_test_session(self, session_name):
        file_name = join(self.planning_dir, session_name)
        with open(f'{file_name}.pickle', 'rb') as file:
            save_data = pickle.load(file)
            print(save_data['agent_params'])
            test_results = save_data['test_results']
            return test_results

    def _get_agent_parameters(self, agent_type):
        params = {'agent_parameters': get_agent_parameters(self.config)}
        if agent_type == 'RHEA' or agent_type == 'RMHC':
            params['evolution_settings'] = self.config['evolution_handler']
        return params

    def _is_session_exists(self):
        filename = join(self.planning_dir, self.config['test_suite']['planning_session_to_load'])+'.pickle'
        is_exists = exists(filename)
        print(f'\nFOUND SESSION: {filename}') if is_exists else print(f'COULD NOT FIND SESSION {filename}')
        return is_exists

    def _get_session_total_best_reward(self, test_results):
        total_reward = 0
        for test_name, actions, rewards, elites, seed in test_results.values():
            total_reward += np.amax(rewards)
        return total_reward

    def _get_best_trial_action_and_reward(self, test_result):
        trial_seeds = None
        if len(test_result) is 5:  # 5 = testname, actions, finalrewards, elites, seeds
            test_name, trial_actions, trial_rewards, trial_elites, trial_seeds = test_result
        else:
            test_name, trial_actions, trial_rewards, trial_elites = test_result

        index_max = np.argmax(trial_rewards)
        return index_max+1, trial_actions[index_max], trial_rewards[index_max], trial_elites[index_max], trial_seeds[index_max] if trial_seeds else None

    def _make_session_name(self, custom_name=None):
        config_name = self.config['experiment_name']
        agent_name = self.config['planning']['planning_agent']
        date = datetime.now().strftime("%Y_%m_%d_%H_%M")
        return custom_name if custom_name else f'{config_name}_{date}_{agent_name}_h{self.planning_agent.horizon}_g{self.planning_agent.max_generations}_sb{self.planning_agent.is_shift_buffer}'

    def _get_threads(self):
        fixed_cores = self.config['test_suite']['fixed_cores']
        return fixed_cores if fixed_cores is not None and fixed_cores <= multiprocessing.cpu_count() else multiprocessing.cpu_count()

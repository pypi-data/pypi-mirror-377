# -----------------------------------------------------------------------------------
# ObjectRL: An Object-Oriented Reinforcement Learning Codebase
# Copyright (C) 2025 ADIN Lab

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------------

import time

import numpy as np
import torch
from tqdm import tqdm

from objectrl.config.config import MainConfig
from objectrl.experiments.base_experiment import Experiment
from objectrl.utils.utils import tonumpy, totorch


class ControlExperiment(Experiment):
    """
    The Experiment class for training and evaluating.
    This class defines the core training loop, manages interaction with the environment,
    performs evaluations at regular intervals, and handles model saving and logging.

    Args:
    max_steps : int
        Maximum number of training steps.
    warmup_steps : int
        Number of initial steps using random actions before policy-based action selection.
    device : torch.device
        Device (CPU/GPU) used for tensor computations.
    """

    def __init__(self, config: "MainConfig"):
        super().__init__(config)

        # Retrieve training parameters from the configuration
        self.max_steps: int = self.config.training.max_steps
        self.warmup_steps: int = self.config.training.warmup_steps
        self.device = torch.device(config.system.device)
        self._vectorized_eval = self.config.training.parallelize_eval
        self.verbose = self.config.verbose

    def train(self) -> None:
        """
        Runs the training loop for the agent, managing interactions with the environment,
        learning updates, evaluations, and logging.

        Args:
            None
        Returns:
            None
        """
        time_start = time.time()

        # Dictionary to store rewards and steps for logging
        information_dict = {
            "episode_rewards": torch.zeros(self.max_steps),
            "episode_steps": torch.zeros(self.max_steps),
            "step_rewards": np.empty((2 * self.max_steps), dtype=object),
        }

        # Initialize the environment and state
        state, _ = self.env.reset()
        state = totorch(state, device=self.device)
        r_cum = np.zeros(1)
        episode = 0
        e_step = 0

        # Training loop
        for step in tqdm(
            range(self.max_steps),
            leave=True,
            disable=not self.config.progress,
        ):
            e_step += 1

            # Reset agent periodically if configured
            if (
                step > self.warmup_steps
                and self.config.training.reset_frequency > 0
                and step % self.config.training.reset_frequency == 0
            ):
                self.agent.reset()

            # Evaluate the agent at specified intervals
            if step % self.config.training.eval_frequency == 0:
                self.eval(step)

            # Select an action (random during warmup, policy-based afterward)
            if step < self.warmup_steps:
                action = self.env.action_space.sample()
                action = totorch(np.clip(action, -1.0, 1.0), device=self.device)
                act_dict = {"action": action}
            else:
                act_dict = self.agent.select_action(state)
                action = act_dict["action"].clip(-1.0, 1.0)

            # Take a step in the environment
            next_state, reward, terminated, truncated, info = self.env.step(
                int(action) if self._discrete_action_space else tonumpy(action)
            )
            next_state = totorch(next_state, device=self.device)

            transition_kwargs = {
                **act_dict,
                "state": state,
                "next_state": next_state,
                "reward": reward,
                "terminated": terminated,
                "truncated": truncated,
                "step": step + 1,
            }
            transition = self.agent.generate_transition(**transition_kwargs)

            # Store the transition in replay buffer
            self.agent.store_transition(transition)

            # Log per-step reward
            information_dict["step_rewards"][self.n_total_steps + step] = (
                episode,
                step,
                reward,
            )

            state = next_state  # Update state
            r_cum += reward  # Update cumulative reward

            # Perform learning updates at specified intervals
            if (
                step >= self.warmup_steps
                and (step % self.config.training.learn_frequency) == 0
            ):
                self.agent.learn(
                    max_iter=self.config.training.max_iter,
                    n_epochs=self.config.training.n_epochs,
                )

            # Episode termination
            if terminated or truncated:
                information_dict["episode_rewards"][episode] = r_cum.item()
                information_dict["episode_steps"][episode] = step

                # Save episode summary
                self.agent.logger.episode_summary(episode, step, information_dict)

                # Reset the environment for the next episode
                state, _ = self.env.reset()
                state = totorch(state, device=self.device)
                r_cum = np.zeros(1)
                episode += 1
                e_step = 0

            # Save model and logs at specified intervals
            if step % self.config.logging.save_frequency == 0:
                self.agent.logger.save(information_dict, episode, step)
                self.agent.save()

        # Final evaluation after training
        self.eval(step)
        time_end = time.time()
        self.agent.save()
        self.agent.logger.save(information_dict, episode, step)
        self.agent.logger.log(f"Training time: {time_end - time_start:.2f} seconds")

    # ruff: noqa: C901
    @torch.inference_mode()
    def eval(self, n_step: int) -> None:
        """
        Evaluates the agent over multiple episodes in the evaluation environment.

        Args:
            n_step (int): The current training step at which evaluation is performed.
        Returns:
            None
        """
        self.agent.eval()  # Set agent to evaluation mode

        # Save RNG states
        torch_rng_state = torch.get_rng_state()
        if torch.cuda.is_available():
            cuda_rng_state = torch.cuda.get_rng_state_all()

        # Set deterministic seed for eval
        eval_seed = self.config.system.seed + 12345
        torch.manual_seed(eval_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(eval_seed)
            torch.cuda.manual_seed_all(eval_seed)

        # Store rewards for evaluation episodes
        results = torch.zeros(self.config.training.eval_episodes)

        if self._vectorized_eval:
            states, _ = self.eval_env.reset()
            states = totorch(states, device=self.device)

            dones = torch.zeros(self.config.training.eval_episodes, dtype=torch.bool)
            while not torch.all(dones):
                actions = self.agent.select_action(states, is_training=False)["action"]

                if self._discrete_action_space:
                    actions = actions.int()

                next_states, rewards, term, trunc, _ = self.eval_env.step(
                    tonumpy(actions)
                )

                done = torch.tensor(term) | torch.tensor(trunc)
                results += torch.tensor(rewards) * (
                    ~done
                )  # only add reward to running environments
                dones |= done

                states = totorch(next_states, device=self.device)

        else:
            # Run multiple evaluation episodes
            for episode in range(self.config.training.eval_episodes):
                state, info = self.eval_env.reset()
                state = totorch(state, device=self.device)

                done = False

                while not done:
                    # Select action using the agent's policy (without exploration)
                    action = self.agent.select_action(state, is_training=False)[
                        "action"
                    ]

                    # Execute action in the environment
                    next_state, reward, term, trunc, info = self.eval_env.step(
                        int(action) if self._discrete_action_space else tonumpy(action)
                    )

                    # Check termination condition
                    done = term or trunc
                    # Update state and record reward
                    state = totorch(next_state, device=self.device)
                    results[episode] += reward

                # If using Sparse MetaWorld env, adjust reward to reflect success
                # mean_reward in save_eval_results will be equal to success rate
                if "success" in info and self.config.env.sparse_rewards:
                    results[episode] = reward + 1.0

        self.agent.logger.save_eval_results(n_step, results)
        if self.verbose:
            tqdm.write(f"{n_step}: {results.mean():.4f} +/- {results.std():.4f}")
        self.agent.train()

        # Restore RNG states
        torch.set_rng_state(torch_rng_state)
        if torch.cuda.is_available():
            torch.cuda.set_rng_state_all(cuda_rng_state)

import typing
from typing import Dict, List

import torch
import torch.nn as nn

from .game import Action


class NetworkOutput(typing.NamedTuple):
    value: float
    reward: float
    policy_logits: Dict[Action, float]
    hidden_state: List[float]


class BaseMuZeroNet(nn.Module):
    def __init__(self, input_size, action_space_n):
        super(BaseMuZeroNet, self).__init__()

    def prediction(self, state):
        raise NotImplementedError

    def representation(self, obs_history):
        raise NotImplementedError

    def dynamics(self, state, action):
        raise NotImplementedError

    def initial_inference(self, obs) -> NetworkOutput:
        state = self.representation(obs)
        actor_logit, value = self.prediction(state)
        value = self._value_transformation(value)
        return NetworkOutput(value, 0, actor_logit, state)

    def recurrent_inference(self, hidden_state, action) -> NetworkOutput:
        state, reward = self.dynamics(hidden_state, action)
        actor_logit, value = self.prediction(state)
        value = self._value_transformation(value)
        reward = self._reward_transformation(reward)
        return NetworkOutput(value, reward, actor_logit, state)

    def get_weights(self):
        return {k: v.cpu() for k, v in self.state_dict().items()}

    def set_weights(self, weights):
        self.load_state_dict(weights)

    def get_gradients(self):
        grads = []
        for p in self.parameters():
            grad = None if p.grad is None else p.grad.data.cpu().numpy()
            grads.append(grad)
        return grads

    def set_gradients(self, gradients):
        for g, p in zip(gradients, self.parameters()):
            if g is not None:
                p.grad = torch.from_numpy(g)

    def _value_transformation(self, value):
        """ Reference : Appendix F => Network Architecture
        As of now, we are keeping this transformation as identity fun.
        """

        return value

    def _reward_transformation(self, reward):
        """ Reference : Appendix F => Network Architecture
        As of now, we are keeping this transformation as identity fun.
        """
        return reward

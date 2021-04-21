import math
import types
import random
import numpy as np
import tensorflow as tf

from Memory import Memory
from Model import Model
from selector import Action
from warehouse import Warehouse

MAX_EPSILON = 1
MIN_EPSILON = 0.01
LAMBDA = 0.00001
GAMMA = 0.99
BATCH_SIZE = 50

class Policy:

    model = Model(3, 2, BATCH_SIZE)
    _sess = None
    _eps = MAX_EPSILON
    _memory = Memory(50000)
    _steps = 0
    _tot_reward = 0
    _loss = None

    def __init__(self, sess):
        self._sess = sess
        sess.run(self.model.var_init)

    def select(self, robot):
        action = 0
        state = robot.get_state()
        if state[0] < 0 and state[2] <= 0:
            return Action.IDLE
        if state[0] < 0:
            action = 0
        elif random.random() < self._eps:
            action = random.randint(0, self.model.num_actions - 1)
        else:
            action = np.argmax(self.model.predict_one(np.array(state), self._sess))
        action = Action(action + 1)
        if action == Action.CHARGE and state[2] <= 0:
            if state[0] < 0:
                return Action.IDLE
            action = action.FETCH_ITEM
        next_state, reward = robot.calc_step(action)
        if action == Action.FETCH_ITEM and next_state[0] < 0:
            if state[2] <= 0:
                return Action.IDLE
            action = Action.CHARGE
            next_state, reward = robot.calc_step(action)
        self._memory.add_sample((state, action.value - 1, reward, next_state))
        self._replay()
        self._steps += 1
        self._eps = MIN_EPSILON + (MAX_EPSILON - MIN_EPSILON) * math.exp(-LAMBDA * self._steps)
        self._tot_reward += reward

        return action

    def run(self):
        warehouse = Warehouse(self.select)
        self._tot_reward = 0
        i = 0
        last_damage = [robot.battery.lost_capacity for robot in warehouse.robots]
        while warehouse.time < 525600:
            warehouse.tick()
            if warehouse.time // 1440 > i:
                new_damage = [robot.battery.lost_capacity for robot in warehouse.robots]
                avg_damage = sum(n - o for n, o in zip(new_damage, last_damage)) / len(new_damage)
                print("Day {}, today's reward is {}, average damage is {}, loss {}".format(i, self._tot_reward, avg_damage, self._loss))
                i += 1
                self._tot_reward = 0
                self._loss = None
                last_damage = new_damage

        print("Ran for {} days".format(math.ceil(warehouse.time / 1440)))
        print("Picked {} items with {} robots and {} chargers".format(warehouse.items_picked, len(warehouse.robots),
                                                                      len(warehouse.chargers)))
        for robot in warehouse.robots:
            print("Battery Health: {}".format(math.floor((1 - robot.battery.lost_capacity) * 100)))

    def _replay(self):
        batch = self._memory.sample(self.model.batch_size)
        states = np.array([val[0] for val in batch])
        next_states = np.array([(np.zeros(self.model.num_states) if val[3] is None else val[3]) for val in batch])
        q_s_a = self.model.predict_batch(states, self._sess)
        q_s_a_d = self.model.predict_batch(next_states, self._sess)
        x = np.zeros((len(batch), self.model.num_states))
        y = np.zeros((len(batch), self.model.num_actions))
        for i, b in enumerate(batch):
            state, action, reward, next_state = b[0], b[1], b[2], b[3]
            current_q = q_s_a[i]
            if next_state is None:
                current_q[action] = reward
            else:
                current_q[action] = reward + GAMMA * np.amax(q_s_a_d[i])
            x[i] = state
            y[i] = current_q
        loss = self.model.train_batch(self._sess, x, y)
        if self._loss is None or self._loss > loss:
            self._loss = loss

if __name__ == '__main__':
    with tf.Session() as sess:
        p = Policy(sess)
        p.run()

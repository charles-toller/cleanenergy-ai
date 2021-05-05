import math
import types
import random
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from Memory import Memory
from Model import Model
from selector import Action
from warehouse import Warehouse

MAX_EPSILON = 1
MIN_EPSILON = 0.01
LAMBDA = 0.00001
GAMMA = 0.99
BATCH_SIZE = 50

plt.rcParams['figure.figsize'] = (16, 9)


class Policy:
    model = Model(3, 2, BATCH_SIZE)
    _sess = None
    _eps = MAX_EPSILON
    _memory = Memory(50000)
    _steps = 0
    _tot_reward = 0
    _loss = None
    _is_training = False

    def __init__(self, sess):
        self._sess = sess

    def select(self, robot):
        if not self._is_training:
            self._eps = 0
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
        if self._is_training:
            self._memory.add_sample((state, action.value - 1, reward, next_state))
            self._replay()
            self._eps = MIN_EPSILON + (MAX_EPSILON - MIN_EPSILON) * math.exp(-LAMBDA * self._steps)
            self._steps += 1
        self._tot_reward += reward

        return action

    def train(self, write_to_file=False):
        sess.run(self.model.var_init)
        self._is_training = True
        self._inner_run(write_to_file)
        self.model.save_model(self._sess)

    def run(self, load=False, models_dir="", name="final", write_to_file=False):
        self._is_training = False
        if load:
            self.model.restore_model(self._sess, models_dir=models_dir, name=name)
        self._inner_run(write_to_file, run_for_time=150, show_graphs=False)

    def _inner_run(self, write_to_file, run_for_time=90*1440, show_graphs=True):
        warehouse = Warehouse(self.select, write_to_file=write_to_file)
        self._tot_reward = 0
        i = 0
        last_damage = [robot.battery.lost_capacity for robot in warehouse.robots]
        x = []
        loss_y = []
        damage_y = []
        reward_y = []
        low_y = []
        high_y = []
        while warehouse.time < run_for_time:
            warehouse.tick()
            if warehouse.time // 1440 > i:
                new_damage = [robot.battery.lost_capacity for robot in warehouse.robots]
                avg_damage = sum(n - o for n, o in zip(new_damage, last_damage)) / len(new_damage)
                print("Day {}, today's reward is {}, average damage is {}, loss {}".format(i, self._tot_reward,
                                                                                           avg_damage, self._loss))
                if self._is_training:
                    self.model.save_model(self._sess, name="day{}".format(i))
                x.append(i)
                loss_y.append(self._loss)
                damage_y.append(avg_damage)
                reward_y.append(self._tot_reward)
                lows_total = 0
                highs_total = 0
                count = 0
                for robot in warehouse.robots:
                    lows_total += sum(robot.battery.lows)
                    highs_total += sum(robot.battery.highs)
                    count += len(robot.battery.lows)
                low_y.append(lows_total / count)
                high_y.append(highs_total / count)
                i += 1
                self._tot_reward = 0
                self._loss = None
                last_damage = new_damage
        if write_to_file:
            for robot in warehouse.robots:
                robot.file.close()
        if self._is_training:
            loss_y = np.clip(loss_y, None, 1)
        if show_graphs:
            if self._is_training:
                plt.plot(x, loss_y, 'bo', x, loss_y, 'k')
                plt.xlabel('Days')
                plt.ylabel('Loss')
                plt.title('Loss over Time (Lower is "Better")')
                plt.show()
            plt.plot(x, damage_y, 'bo', x, damage_y, 'k')
            plt.xlabel('Days')
            plt.ylabel('Battery Damage')
            plt.title('Additional Battery Damage over Time (Lower is Better)')
            plt.show()
            plt.plot(x, reward_y, 'bo', x, reward_y, 'k')
            plt.xlabel('Days')
            plt.ylabel('Profit/Reward')
            plt.title('Reward/Profit over Time (Higher is Better)')
            plt.show()
            plt.plot(x, low_y, 'bo', x, low_y, 'k')
            plt.plot(x, high_y, 'ro', x, high_y, 'k')
            plt.xlabel('Days')
            plt.ylabel('Charge Range')
            plt.title('Charge High/Low over Time (Closer to 0.5 is better)')
            plt.show()

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
        p.run(models_dir="_10", write_to_file=True, load=True, name="day89")
        # p.train(write_to_file=False)

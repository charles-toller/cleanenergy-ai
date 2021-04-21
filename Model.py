import tensorflow as tf


## In the mountain car game, the number of states is 2 (position, velocity) and
## num of actions is 3 (push left, no push, push right).

class Model:
    def __init__(self, num_states, num_actions, batch_size):
        self._num_states = num_states
        self._num_actions = num_actions
        self._batch_size = batch_size
        # define the placeholders
        self._states = None
        self._actions = None
        self._loss = None
        # the output operations
        self._logits = None  # this is the output of an ANN.
        self._optimizer = None
        self._var_init = None
        self._fc1 = None
        self._fc2 = None
        self._fc3 = None
        # now setup the model
        self._define_model()

    def _define_model(self):
        self._define_model_2()

    ## 2-layer model.
    def _define_model_2(self):
        self._states = tf.placeholder(shape=[None, self._num_states],
                                      dtype=tf.float32)
        ## This is the Q(s, a) table.
        ## The number of columns is determined by the input fed to it
        ## The number of actions is 3. So, the size of _q_s_a is ? x 3,
        ## because there are 3 actions in the game.
        self._q_s_a = tf.placeholder(shape=[None, self._num_actions],
                                     dtype=tf.float32)
        # create two fully connected hidden layers
        self._fc1 = tf.layers.dense(self._states, 50, activation=tf.nn.relu)
        self._fc2 = tf.layers.dense(self._fc1, 50, activation=tf.nn.relu)
        self._logits = tf.layers.dense(self._fc2, self._num_actions)
        self._loss = tf.losses.mean_squared_error(self._q_s_a, self._logits)
        self._optimizer = tf.train.AdamOptimizer().minimize(self._loss)
        self._var_init = tf.global_variables_initializer()

    ## your 3-layer model
    def _define_model_3(self):
        self._states = tf.placeholder(shape=[None, self._num_states],
                                      dtype=tf.float32)
        ## This is the Q(s, a) table.
        ## The number of columns is determined by the input fed to it
        ## The number of actions is 3. So, the size of _q_s_a is ? x 3,
        ## because there are 3 actions in the game.
        self._q_s_a = tf.placeholder(shape=[None, self._num_actions],
                                     dtype=tf.float32)
        # create two fully connected hidden layers
        self._fc1 = tf.layers.dense(self._states, 50, activation=tf.nn.relu)
        self._fc2 = tf.layers.dense(self._fc1, 50, activation=tf.nn.relu)
        self._fc3 = tf.layers.dense(self._fc2, 50, activation=tf.nn.relu)
        self._logits = tf.layers.dense(self._fc3, self._num_actions)
        self._loss = tf.losses.mean_squared_error(self._q_s_a, self._logits)
        self._optimizer = tf.train.AdamOptimizer().minimize(self._loss)
        self._var_init = tf.global_variables_initializer()

    ## your 4-layer model
    def _define_model_4(self):
        self._states = tf.placeholder(shape=[None, self._num_states],
                                      dtype=tf.float32)
        ## This is the Q(s, a) table.
        ## The number of columns is determined by the input fed to it
        ## The number of actions is 3. So, the size of _q_s_a is ? x 3,
        ## because there are 3 actions in the game.
        self._q_s_a = tf.placeholder(shape=[None, self._num_actions],
                                     dtype=tf.float32)
        # create two fully connected hidden layers
        self._fc1 = tf.layers.dense(self._states, 50, activation=tf.nn.relu)
        self._fc2 = tf.layers.dense(self._fc1, 60, activation=tf.nn.relu)
        self._fc3 = tf.layers.dense(self._fc2, 60, activation=tf.nn.relu)
        self._fc4 = tf.layers.dense(self._fc3, 9, activation=tf.nn.relu)
        self._logits = tf.layers.dense(self._fc4, self._num_actions)
        self._loss = tf.losses.mean_squared_error(self._q_s_a, self._logits)
        self._optimizer = tf.train.AdamOptimizer().minimize(self._loss)
        self._var_init = tf.global_variables_initializer()

    ## your 5-layer model
    def _define_model_5(self):
        self._states = tf.placeholder(shape=[None, self._num_states],
                                      dtype=tf.float32)
        ## This is the Q(s, a) table.
        ## The number of columns is determined by the input fed to it
        ## The number of actions is 3. So, the size of _q_s_a is ? x 3,
        ## because there are 3 actions in the game.
        self._q_s_a = tf.placeholder(shape=[None, self._num_actions],
                                     dtype=tf.float32)
        # create two fully connected hidden layers
        self._fc1 = tf.layers.dense(self._states, 51, activation=tf.nn.relu)
        self._fc2 = tf.layers.dense(self._fc1, 102, activation=tf.nn.relu)
        self._fc3 = tf.layers.dense(self._fc2, 102, activation=tf.nn.relu)
        self._fc4 = tf.layers.dense(self._fc3, 30, activation=tf.nn.relu)
        self._fc5 = tf.layers.dense(self._fc4, 18, activation=tf.nn.relu)
        self._logits = tf.layers.dense(self._fc5, self._num_actions)
        self._loss = tf.losses.mean_squared_error(self._q_s_a, self._logits)
        self._optimizer = tf.train.AdamOptimizer().minimize(self._loss)
        self._var_init = tf.global_variables_initializer()

    # take a state and a session and use the network to predict
    # the next state. state is a vector of 2 floats, e.g., [-0.61506952 -0.00476815].
    def predict_one(self, state, sess):
        # print('predict_one: state={}'.format(state))
        next_state = sess.run(self._logits, feed_dict={self._states:
                                                           state.reshape(1,
                                                                         self.num_states)})
        # print('predict_one: next_state={}'.format(next_state))
        # next_state is a vector state predicted by the network (e.g., [[-53.998287 -53.755825 -53.867805]])
        return next_state

    # sess is tf.Session.
    def predict_batch(self, states, sess):
        return sess.run(self._logits, feed_dict={self._states: states})

    def train_batch(self, sess, x_batch, y_batch):
        return sess.run([self._loss, self._optimizer], feed_dict={self._states: x_batch, self._q_s_a: y_batch})[0]

    def set_fc1(self, fc1):
        self._fc1 = fc1

    def set_fc2(self, fc2):
        self._fc2 = fc2

    def set_logits(self, logits):
        self._logits = logits

    @property
    def fc1(self):
        return self._fc1

    @property
    def fc2(self):
        return self._fc2

    @property
    def logits(self):
        return self._logits

    @property
    def b(self):
        return self._b

    @property
    def num_states(self):
        return self._num_states

    @property
    def num_actions(self):
        return self._num_actions

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def var_init(self):
        return self._var_init

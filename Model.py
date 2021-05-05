import tensorflow as tf

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
        self.saver = tf.train.Saver(max_to_keep=100)

    def save_model(self, sess, name="final"):
        path = self.saver.save(sess, "/home/charles/projects/cleanenergy-ai/models/{}/model.ckpt".format(name))
        print("Model saved at path: %s" % path)

    def restore_model(self, sess, models_dir="", name="final"):
        self.saver.restore(sess, "/home/charles/projects/cleanenergy-ai/models{}/{}/model.ckpt".format(models_dir, name))

    ## 2-layer model.
    def _define_model_2(self):
        self._states = tf.placeholder(shape=[None, self._num_states],
                                      dtype=tf.float32)
        ## This is the Q(s, a) table.
        self._q_s_a = tf.placeholder(shape=[None, self._num_actions],
                                     dtype=tf.float32)
        # create two fully connected hidden layers
        self._fc1 = tf.layers.dense(self._states, 50, activation=tf.nn.relu)
        self._fc2 = tf.layers.dense(self._fc1, 50, activation=tf.nn.relu)
        self._logits = tf.layers.dense(self._fc2, self._num_actions)
        self._loss = tf.losses.mean_squared_error(self._q_s_a, self._logits)
        self._optimizer = tf.train.AdamOptimizer().minimize(self._loss)
        self._var_init = tf.global_variables_initializer()

    def predict_one(self, state, sess):
        # print('predict_one: state={}'.format(state))
        next_state = sess.run(self._logits, feed_dict={self._states:
                                                           state.reshape(1,
                                                                         self.num_states)})
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

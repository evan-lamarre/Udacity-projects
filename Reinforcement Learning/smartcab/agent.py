from __future__ import division
import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.75):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        self.step = 1

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)

        ###########
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice

        # self.epsilon = self.epsilon - 0.005
        # self.epsilon = 1 / ((self.step) ** 2)
        # self.epsilon = (0.99) ** self.step
        self.epsilon = math.exp(-0.006 * self.step)

        # self.epsilon = math.cos(0.01 * self.step) # 0.01 results in 150ish trials
        # Update additional class parameters as needed
        self.step = self.step + 1
        #self.alpha = self.alpha - 0.0005
        # If 'testing' is True, set epsilon and alpha to 0
        if testing:
            self.epsilon = 0
            self.alpha = 0

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the
            environment. The next waypoint, the intersection inputs, and the deadline
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ###########
        ## TO DO ##
        ###########
        # Set 'state' as a tuple of relevant data for the agent
        state = (waypoint, inputs['light'], inputs['oncoming'], inputs['left'], inputs['right'])

        return state


    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ###########
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state
        if state in self.Q:
            possible_actions = self.Q[state]
            max_value = -999999
            for action in possible_actions:
                if possible_actions[action] > max_value:
                    max_value = possible_actions[action]


        else:
            max_value = None

        return max_value


    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ###########
        ## TO DO ##
        ###########

        if (self.learning) and (state not in self.Q):
            # Bellow dict comprehension taken from review feedback
            self.Q[state] = {action: 0 for action in self.valid_actions}


        return


    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        ###########
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        if not self.learning:
            action = random.choice(self.valid_actions)

        elif self.learning:
        # When learning, choose a random action with 'epsilon' probability
            if self.epsilon > random.random():
                aciton = random.choice(self.valid_actions)
            else:
        #   Otherwise, choose an action with the highest Q-value for the current state
                highestQ = self.get_maxQ(state)
                state_actions = self.Q[state]
                maxQ_actions = []

                for action in state_actions:
                    if state_actions[action] == highestQ:
                        maxQ_actions.append(action)

                action = random.choice(maxQ_actions)

        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards
            when conducting learning. """

        ###########
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        if self.learning:
            # If current value is not zero then use the current learning rate
            if self.Q[state][action] != 0:
                self.Q[state][action] = self.Q[state][action] * (1 - self.alpha) + reward * self.alpha
            # If the current value is zero then assume this is the first entry
            # don't use learning rate. Ths should allow the agent to learn faster.
            # Without this the agent assumes it has prior information and discounts
            # the reward it just received. 0 was an arbitrary initial pick so we don't want
            # to retain any of that information.
            else:
                self.Q[state][action] = reward
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')

        return


    def update(self):
        """ The update function is called when a time step is completed in the
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return


def run():
    """ Driving function for running the simulation.
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment(verbose=True)

    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent, learning = True)

    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, update_delay=0.000000001, log_metrics=True, optimized=True, display=False)

    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test=20, tolerance=0.008)


if __name__ == '__main__':
    run()

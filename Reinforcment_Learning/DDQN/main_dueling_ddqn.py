import gym
from gym import envs
from gym import wrappers 
import numpy as np
from dueling_ddqn_agent import DuelingDDQNAgent
from utils import plot_learning_curve, make_env
import custom_spaceship

if __name__ == '__main__':
    env = make_env('CustomSpaceShip-v0')
    best_score = 0
    load_checkpoint = True
    n_games = 5000
    agent = DuelingDDQNAgent(gamma=0.99, epsilon=1.0, lr=0.0001,
                     input_dims=(env.observation_space.shape),
                     n_actions=env.action_space.n, mem_size=11000, eps_min=0.1,
                     batch_size=32, replace=1000, eps_dec=1e-5,
                     chkpt_dir='models/', algo='DuelingDDQNAgent',
                     env_name='CustomSpaceShip-v0')


    if load_checkpoint:
        agent.load_models()

    fname = agent.algo + '_' + agent.env_name + '_lr' + str(agent.lr) +'_' \
            + str(n_games) + 'games'
    figure_file = 'plots/' + fname + '.png'

    n_steps = 0
    scores, eps_history, steps_array = [], [], []

    for i in range(n_games):
        done = False
        observation = env.reset()
        score = 0
        while not done:
            action = agent.choose_action(observation)
            observation_, reward, done, info = env.step(action)
            score += reward
            env.render()
            #if not load_checkpoint:
            agent.store_transition(observation, action,
                                   reward, observation_, int(done))
            agent.learn()
            observation = observation_
            n_steps += 1
        scores.append(score)
        steps_array.append(n_steps)

        avg_score = np.mean(scores[-100:])
        max_score = np.max(scores)
        print('episode: ', i,'score: ', score,
             ' average score %.1f' % avg_score, 'best score %.2f' % best_score,
            'epsilon %.2f' % agent.epsilon, 'steps', n_steps)
        # change avg_score to score
        if avg_score > best_score:
            print("******  Saving new model ******")
            #if not load_checkpoint:
            agent.save_models()
            best_score = avg_score

        eps_history.append(agent.epsilon)
        if load_checkpoint and n_steps >= 60000:
            break
    print("Max Score: ",max_score)
    env.close()
    x = [i+1 for i in range(len(scores))]
    plot_learning_curve(steps_array, scores, eps_history, figure_file)

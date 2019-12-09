{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 34
    },
    "colab_type": "code",
    "id": "ZLX5bfvuvJBg",
    "outputId": "7d71368e-d091-484f-b07e-1bf29b0ccf22"
   },
   "outputs": [],
   "source": [
    "# !unzip robohearts.zip\n",
    "#%cd robohearts/"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "LQFmIAWEj30z"
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "WARNING:root:This caffe2 python run does not have GPU support. Will run in CPU only mode.\n"
     ]
    }
   ],
   "source": [
    "import gym\n",
    "import multiprocessing\n",
    "from gymhearts.Hearts import *\n",
    "from gymhearts.Agent.human import Human\n",
    "from gymhearts.Agent.random_agent import RandomAgent\n",
    "from gymhearts.Agent.monte_carlo_nn import MonteCarloNN\n",
    "from gymhearts.Agent.agent_utils import save_model\n",
    "from tqdm import tqdm_notebook"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 62
    },
    "colab_type": "code",
    "id": "xsPqUNz_j307",
    "outputId": "c1591ddd-a48d-4aed-bc1b-64c392711308"
   },
   "outputs": [],
   "source": [
    "# ----------- TRAINING CONFIGURATION -------------\n",
    "# Number of games to train on \n",
    "TRAINING_ITERS = 1000\n",
    "\n",
    "# Number of episodes to run during model evaluation\n",
    "NUM_EPISODES = 10\n",
    "\n",
    "# Number of model evaluations to average together\n",
    "NUM_TESTS = 10\n",
    "\n",
    "# Max score for players to win the game\n",
    "MAX_SCORE = 100\n",
    "\n",
    "# Set to false to skip training\n",
    "run_train = False\n",
    "\n",
    "# Set to true to resume training from an existing model\n",
    "continue_train = False\n",
    "\n",
    "# Run testing on a random agent for comparison\n",
    "run_random = False\n",
    "\n",
    "# Features to include in model :: [in_hand, in_play, played_cards, won_cards, scores]\n",
    "feature_list = ['in_hand', 'in_play', 'played_cards']\n",
    "\n",
    "# Name of the file that is saved :: {model_name}.th\n",
    "model_name = 'mlp'\n",
    "\n",
    "# Configuration parameters for the model\n",
    "mc_config = {\n",
    "    'print_info' : False,\n",
    "    'epsilon' : .01,\n",
    "    'gamma' : 1.0,\n",
    "    'alpha': 1e-2,\n",
    "    'feature_list' : feature_list\n",
    "}\n",
    "\n",
    "if continue_train:\n",
    "    mc_config['load_model'] = model_name\n",
    "\n",
    "playersNameList = ['MonteCarlo', 'Rando', 'Randy', 'Randall']\n",
    "agent_list = [0, 0, 0, 0]\n",
    "\n",
    "agent_list[0] = MonteCarloNN(playersNameList[0], mc_config)\n",
    "agent_list[1] = RandomAgent(playersNameList[1], {'print_info' : False})\n",
    "agent_list[2] = RandomAgent(playersNameList[2], {'print_info' : False})\n",
    "agent_list[3] = RandomAgent(playersNameList[3], {'print_info' : False})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "Pt8mEPEQj31D"
   },
   "outputs": [],
   "source": [
    "# TRAIN THE MONTE CARLO AGENT\n",
    "env = gym.make('Hearts_Card_Game-v0')\n",
    "env.__init__(playersNameList, MAX_SCORE)\n",
    "if run_train:\n",
    "    for trn_episode in tqdm_notebook(range(TRAINING_ITERS)):\n",
    "        # Save the model every 50 steps\n",
    "        if trn_episode % 50 == 0:\n",
    "            save_model(agent_list[0].nn, model_name)\n",
    "        observation = env.reset()\n",
    "        history = []\n",
    "        while True:\n",
    "            #env.render()\n",
    "\n",
    "            now_event = observation['event_name']\n",
    "            IsBroadcast = observation['broadcast']\n",
    "            # update my agent before clearing state\n",
    "            if now_event == 'RoundEnd':\n",
    "                agent_list[0].update_weights(history, -reward['MonteCarlo'])\n",
    "                history = []\n",
    "            if now_event == 'GameOver':\n",
    "                  break\n",
    "            if observation['event_name']=='PlayTrick' and observation['data']['playerName'] == 'MonteCarlo':\n",
    "                # don't add score, they don't change till at end of round\n",
    "                history.append((observation, agent_list[0].played_cards, agent_list[0].won_cards))\n",
    "\n",
    "            action = None\n",
    "            if IsBroadcast == True:\n",
    "                for agent in agent_list:\n",
    "                    agent.Do_Action(observation)\n",
    "            else:\n",
    "                playName = observation['data']['playerName']\n",
    "                for agent in agent_list:\n",
    "                    if agent.name == playName:\n",
    "                        action = agent.Do_Action(observation)\n",
    "\n",
    "            observation, reward, done, info = env.step(action)\n",
    "    save_model(agent_list[0].nn, model_name)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "ZX6qQi9blVFk"
   },
   "outputs": [],
   "source": [
    "# Function to test model, meant to be passed into multiprocessing pool\n",
    "def run_test(num_won):\n",
    "    # Weird hack to make progress bars render properly\n",
    "    print(' ', end='', flush=True)\n",
    "    for i_ep in tqdm_notebook(range(NUM_EPISODES)):\n",
    "        observation = env.reset()\n",
    "        while True:\n",
    "            now_event = observation['event_name']\n",
    "            IsBroadcast = observation['broadcast']\n",
    "            action = None\n",
    "            if IsBroadcast == True:\n",
    "                for agent in agent_list:\n",
    "                    agent.Do_Action(observation)\n",
    "            else:\n",
    "                playName = observation['data']['playerName']\n",
    "                for agent in agent_list:\n",
    "                    if agent.name == playName:\n",
    "                        action = agent.Do_Action(observation)\n",
    "            if now_event == 'GameOver':\n",
    "                num_won += int(observation['data']['Winner'] == 'MonteCarlo')\n",
    "                break\n",
    "            observation, reward, done, info = env.step(action)\n",
    "    return num_won"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 50
    },
    "colab_type": "code",
    "id": "Qn-MK5D5pBUw",
    "outputId": "24766394-6d68-4b8b-b7f9-8d058443c268"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "loaded from /Users/akwatra/repos/robohearts/gymhearts/Agent/mlp.th\n",
      "          "
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "a7434418e733497a9945c583ec89fb21",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "85f0253606e04d85b9b7d4cd1dc0a38a",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "2b06da621d49456dbec032492c65055c",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "acf920d7f22a4e1698d2bcb6bf872d9d",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "6e0b3a4f86f3486e9ca99b1d18272c65",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "47338310d6c94420a935e94bff23e220",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "326d27cde83c4ad690dcd03b11ac3ddb",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "65ccb972fbd84c658a7d54dde894327e",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "ab82945e6d0747b983f7b5f6eba9d9fc",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "87064928a18a45778a98f0c0083d2d7a",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "[3, 3, 4, 3, 3, 5, 5, 0, 2, 3]\n"
     ]
    }
   ],
   "source": [
    "# EVALUATE THE MONTE CARLO AGENT\n",
    "    \n",
    "env = gym.make('Hearts_Card_Game-v0')\n",
    "env.__init__(playersNameList, MAX_SCORE)\n",
    "\n",
    "# Evaluation parameters for testing\n",
    "mc_config = {\n",
    "    'print_info' : False,\n",
    "    'load_model' : model_name,\n",
    "    'feature_list' : feature_list\n",
    "}\n",
    "agent_list[0] = MonteCarloNN(playersNameList[0], mc_config)\n",
    "mc_wins = [0] * NUM_TESTS        \n",
    "pool = multiprocessing.Pool(processes=NUM_TESTS)\n",
    "mc_wins = pool.map(run_test, mc_wins)\n",
    "print(mc_wins)\n",
    "pool.close()\n",
    "pool.join()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "7y1WTLbOEYw-"
   },
   "outputs": [],
   "source": [
    "def run_test_random(num_won):\n",
    "    # Weird hack to make progress bars render properly\n",
    "    print(' ', end='', flush=True)\n",
    "    for i_ep in tqdm_notebook(range(NUM_EPISODES)):\n",
    "        observation = env.reset()\n",
    "        while True:\n",
    "            now_event = observation['event_name']\n",
    "            IsBroadcast = observation['broadcast']\n",
    "            action = None\n",
    "            if IsBroadcast == True:\n",
    "                for agent in agent_list:\n",
    "                    agent.Do_Action(observation)\n",
    "            else:\n",
    "                playName = observation['data']['playerName']\n",
    "                for agent in agent_list:\n",
    "                    if agent.name == playName:\n",
    "                        action = agent.Do_Action(observation)\n",
    "            if now_event == 'GameOver':\n",
    "                num_won += int(observation['data']['Winner'] == 'Randman')\n",
    "                break\n",
    "            observation, reward, done, info = env.step(action)\n",
    "    return num_won"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "-b3qOJsbh9pf"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "          "
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "8917489dca5648c584b2ee699647e54e",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "3988338ae30e424aaca68364aacc4c22",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "bb80c8494c1442dfa79e477aef15f532",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "db9eece8fbc148fcb3668a6f36376514",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "9d9c4441259b4faeb924eb723edc3e97",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "5e157b74560f4c78931dedb40d3ad447",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "729cc16dc6c64905ad21134b35ad635e",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "d2f53090615b486cb9b919e9ac738b44",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "a929088d5a2a47ebaedef89ae6a6fd85",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "e8d0fa9f1849445d8a63f14b57e6a3cd",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "[5, 0, 3, 3, 3, 4, 4, 5, 2, 4]\n"
     ]
    }
   ],
   "source": [
    "# EVALUATE THE RANDOM AGENT\n",
    "if run_random:\n",
    "    env = gym.make('Hearts_Card_Game-v0')\n",
    "    env.__init__(playersNameList, MAX_SCORE)\n",
    "    playersNameList[0] = 'Randman'\n",
    "    agent_list[0] = RandomAgent(playersNameList[0])\n",
    "    rand_wins = [0] * NUM_TESTS\n",
    "\n",
    "    pool = multiprocessing.Pool(processes=NUM_TESTS)\n",
    "    rand_wins = pool.map(run_test_random, rand_wins)\n",
    "    print(rand_wins)\n",
    "    pool.close()\n",
    "    pool.join()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "3kXj1tPLnR7F"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Monte Carlo won 3.1 times on average :: [3, 3, 4, 3, 3, 5, 5, 0, 2, 3]\n",
      "3\n",
      "3\n",
      "4\n",
      "3\n",
      "3\n",
      "5\n",
      "5\n",
      "0\n",
      "2\n",
      "3\n",
      "Random won 3.3 times on average :: [5, 0, 3, 3, 3, 4, 4, 5, 2, 4]\n"
     ]
    }
   ],
   "source": [
    "print(f\"Monte Carlo won {sum(mc_wins)/len(mc_wins)} times on average :: {str(mc_wins)}\")\n",
    "for win in mc_wins:\n",
    "    print(win)\n",
    "if run_random:\n",
    "    print(f\"Random won {sum(rand_wins)/len(rand_wins)} times on average :: {str(rand_wins)}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "colab": {
   "collapsed_sections": [],
   "name": "mc_nn.ipynb",
   "provenance": []
  },
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 1
}
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
    "outputId": "549b447d-bf92-4e93-bfda-6edbbe2c6ff8"
   },
   "outputs": [],
   "source": [
    "# !unzip robohearts.zip\n",
    "#%cd robohearts/"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import gym\n",
    "import multiprocessing\n",
    "from gymhearts.Hearts import *\n",
    "from gymhearts.Agent.human import Human\n",
    "from gymhearts.Agent.random_agent import RandomAgent\n",
    "from gymhearts.Agent.monte_carlo import MonteCarlo\n",
    "from tqdm import tqdm_notebook"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "NUM_TESTS = 25\n",
    "NUM_EPISODES = 1000\n",
    "TRAINING_ITERS = 10000\n",
    "MAX_SCORE = 100\n",
    "\n",
    "run_train = True\n",
    "\n",
    "playersNameList = ['MonteCarlo', 'Rando', 'Randy', 'Randall']\n",
    "agent_list = [0, 0, 0, 0]\n",
    "\n",
    "# Human vs Random\n",
    "mc_config = {\n",
    "    'print_info' : False,\n",
    "    'epsilon' : 0.00005,\n",
    "    'gamma' : 1,\n",
    "    'alpha': 0.01\n",
    "}\n",
    "agent_list[0] = MonteCarlo(playersNameList[0], mc_config)\n",
    "agent_list[1] = RandomAgent(playersNameList[1], {'print_info' : False})\n",
    "agent_list[2] = RandomAgent(playersNameList[2], {'print_info' : False})\n",
    "agent_list[3] = RandomAgent(playersNameList[3], {'print_info' : False})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "0d99d689ddc34b2f92ec70ea1d052062",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=10000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n"
     ]
    }
   ],
   "source": [
    "# TRAIN THE MONTE CARLO AGENT\n",
    "env = gym.make('Hearts_Card_Game-v0')\n",
    "env.__init__(playersNameList, MAX_SCORE)\n",
    "weights = []\n",
    "if run_train:\n",
    "    for trn_episode in tqdm_notebook(range(TRAINING_ITERS)):\n",
    "        observation = env.reset()\n",
    "        history = []\n",
    "        while True:\n",
    "            #env.render()\n",
    "\n",
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
    "\n",
    "            # update my agent\n",
    "            if now_event == 'RoundEnd':\n",
    "                errors = agent_list[0].update_weights(history, -reward['MonteCarlo'])\n",
    "                history = []\n",
    "                weights = agent_list[0].weight_vec\n",
    "                #print(sum(errors) / len(errors))\n",
    "            if now_event == 'GameOver':\n",
    "                  break\n",
    "            if not IsBroadcast and observation['data']['playerName'] == 'MonteCarlo':\n",
    "                history.append(observation)\n",
    "            observation, reward, done, info = env.step(action)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 185
    },
    "colab_type": "code",
    "id": "Qn-MK5D5pBUw",
    "outputId": "2d5fa5ed-87d6-4c10-aaf7-cb7e6e5883c1"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                         "
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "4a0972c739c944359149303c9f5b9017",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "40c78f85a8624f5eb41081e0911d5735",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "5bf3654710614ec1a791fea610c3ad08",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "c9926cbd7a324fd189dcd3eaff0056ae",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "422bf78abc6c43a98bd0ee9234fd7166",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "546b0092ea66460a9af7c6c418c05d39",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "6731fb21da044693ad660182582741eb",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "aae7cb5b725f45a4822261d19496b2b3",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "5cfe237d77374e9184196fe2a85e0cb5",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "35d98eb04ddf4aca805da78012bf4e57",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "f48ed145cce34369a0464cd8aba82d11",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "a20549383f0941cfb57edce801386608",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "64ea4683242f46219ebe0dba0fd350ce",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "48bf8e91dcd847238127a97a61926377",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "8c6a0ead902640448fe53409ff45a4cb",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "72bf6deb8dbe4b8593d4383dcfe2387c",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "9ac8acf71bf84abc83a7e2c9b2c09afe",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "78f69c95e0074649a3b676d3661897ab",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "3340b198ce5c48de87fcb8f66a8cc8ab",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "55cc7c4941014c8a88ef8b011fe003a3",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "ad14ceba776b425c8ed40e420c3ddb20",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "d08c1b720f4b4486a6e33751c4dbdf90",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "50999dc7e0284ba88a03e64d66df31dd",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "ebe9e7e8f7884bdc9884db640ef05e69",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "85c092d289ab4c9eabf632b5c1810f80",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
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
      "\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "[248, 262, 257, 248, 223, 225, 250, 260, 257, 247, 234, 237, 215, 237, 250, 256, 223, 222, 236, 232, 236, 238, 227, 210, 228]\n"
     ]
    }
   ],
   "source": [
    "# weights = [2.576861053203586, 0.0746679771208893, -1.0812505668744499, -0.7988069051959343, -0.18287651208895211, -1.3484899819506349, -0.7738220160521773, -0.5906825585410745, -0.8971680184937948, -0.885565000008097, -1.3417259322269985, 0.2535853856420063, -1.441329568781756, -1.626241953689169, -0.4520713221939589, -0.6678954038095386, -2.25007892981782, -2.431379022777693, -1.567284905178469, -0.490646940611233, 0.34596233132385223, -1.3335021078350033, -0.7279177782535996, -1.779761417596184, -0.05179903215749995, -1.5942588118086698, -0.7143773868101742, -0.41782520640881626, -0.6012057234741566, -0.1547484832852079, -1.3914770806800125, -1.698230349430356, -0.524848250080739, -1.5398434930711828, -0.9721881808831833, -0.5133157337051545, -1.8444207319021027, -1.6356606139213474, -1.7030771121557624, -0.33409359803424515, -2.0573741435708257, -1.3594361478746861, 0.34910201903712196, -2.0820589269098035, -0.7468014984012109, -0.384112150138625, -1.626876697152019, -1.3726614211322747, -1.3817587383450798, -2.0699660501885186, -0.711128850022648, -1.9758887630510917]\n",
    "\n",
    "# EVALUATE THE MONTE CARLO AGENT\n",
    "    \n",
    "env = gym.make('Hearts_Card_Game-v0')\n",
    "env.__init__(playersNameList, MAX_SCORE)\n",
    "agent_list[0] = MonteCarlo(playersNameList[0], params={'weight_vec' : weights})\n",
    "mc_wins = [0] * NUM_TESTS\n",
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
    "    return num_won\n",
    "        \n",
    "pool = multiprocessing.Pool(processes=NUM_TESTS)\n",
    "mc_wins = pool.map(run_test, mc_wins)\n",
    "print(mc_wins)\n",
    "pool.close()\n",
    "pool.join()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 185
    },
    "colab_type": "code",
    "id": "-b3qOJsbh9pf",
    "outputId": "1d699944-7e94-4730-8a4e-69c99f3e30a7"
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
       "model_id": "e21897c47b0d435cb2f9c40bb95a0057",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "f260399ed1b840ab8a559abf0bba9837",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "fda44251bc5949bbaacc067c4c9c4b32",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "5915e84ac91a4587b63a676860153781",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "e1bc4dedffd94cc78ffb065bdf317948",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "bc66e53be6234646afad2f95cc50c1ec",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "bbb8169c53c14b509930fff49e3e3aa9",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "a4fe883d6fbe4075b48ff12f6734913a",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "2e4f375baf80477c86fbfb6f5a57badb",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "a49f07473be445d685f81ed238d6e5bd",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HBox(children=(IntProgress(value=0, max=1000), HTML(value='')))"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[244, 278, 237, 258, 237, 253, 258, 275, 274, 248]\n"
     ]
    }
   ],
   "source": [
    "# EVALUATE THE RANDOM AGENT\n",
    "env = gym.make('Hearts_Card_Game-v0')\n",
    "env.__init__(playersNameList, MAX_SCORE)\n",
    "playersNameList[0] = 'Randman'\n",
    "agent_list[0] = RandomAgent(playersNameList[0])\n",
    "rand_wins = [0] * NUM_TESTS\n",
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
    "                num_won += int(observation['data']['Winner'] == 'Randman')\n",
    "                break\n",
    "            observation, reward, done, info = env.step(action)\n",
    "    return num_won\n",
    "        \n",
    "pool = multiprocessing.Pool(processes=NUM_TESTS)\n",
    "rand_wins = pool.map(run_test, rand_wins)\n",
    "print(rand_wins)\n",
    "pool.close()\n",
    "pool.join()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 202
    },
    "colab_type": "code",
    "id": "3kXj1tPLnR7F",
    "outputId": "6ea21659-4bce-4baf-9e89-b995889ddad2"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Monte Carlo won 238.32 times on average :: [248, 262, 257, 248, 223, 225, 250, 260, 257, 247, 234, 237, 215, 237, 250, 256, 223, 222, 236, 232, 236, 238, 227, 210, 228]\n",
      "248\n",
      "262\n",
      "257\n",
      "248\n",
      "223\n",
      "225\n",
      "250\n",
      "260\n",
      "257\n",
      "247\n",
      "234\n",
      "237\n",
      "215\n",
      "237\n",
      "250\n",
      "256\n",
      "223\n",
      "222\n",
      "236\n",
      "232\n",
      "236\n",
      "238\n",
      "227\n",
      "210\n",
      "228\n",
      "\n",
      "\n",
      "The Monte Carlo weights are: [2.576861053203586, 0.0746679771208893, -1.0812505668744499, -0.7988069051959343, -0.18287651208895211, -1.3484899819506349, -0.7738220160521773, -0.5906825585410745, -0.8971680184937948, -0.885565000008097, -1.3417259322269985, 0.2535853856420063, -1.441329568781756, -1.626241953689169, -0.4520713221939589, -0.6678954038095386, -2.25007892981782, -2.431379022777693, -1.567284905178469, -0.490646940611233, 0.34596233132385223, -1.3335021078350033, -0.7279177782535996, -1.779761417596184, -0.05179903215749995, -1.5942588118086698, -0.7143773868101742, -0.41782520640881626, -0.6012057234741566, -0.1547484832852079, -1.3914770806800125, -1.698230349430356, -0.524848250080739, -1.5398434930711828, -0.9721881808831833, -0.5133157337051545, -1.8444207319021027, -1.6356606139213474, -1.7030771121557624, -0.33409359803424515, -2.0573741435708257, -1.3594361478746861, 0.34910201903712196, -2.0820589269098035, -0.7468014984012109, -0.384112150138625, -1.626876697152019, -1.3726614211322747, -1.3817587383450798, -2.0699660501885186, -0.711128850022648, -1.9758887630510917]\n"
     ]
    }
   ],
   "source": [
    "print(f\"Monte Carlo won {sum(mc_wins)/len(mc_wins)} times on average :: {str(mc_wins)}\")\n",
    "for item in mc_wins:\n",
    "    print(item)\n",
    "#print(f\"Random won {sum(rand_wins)/len(rand_wins)} times on average :: {str(rand_wins)}\")\n",
    "print(f\"\\n\\nThe Monte Carlo weights are: {str(list(weights))}\")"
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
   "name": "mc_simple.ipynb",
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
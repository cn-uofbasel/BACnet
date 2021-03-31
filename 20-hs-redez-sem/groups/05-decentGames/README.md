# 05 - Decent Games

## Introduction
*Many turn-based games exist on the Web where a game server keeps thegame’s state and permits (or prevents) the players/clients to make their move. In this proposed project, a turn-based game like chess should be implemented in orde to learn about the state management, starting from opening a game (where both players have to first agree) to validating each move, ending or aborting a game, as well as having a list of all pending games. In a second step, this should be expanded to a turn-based game with three players. In both steps it is assumed that structuring the game by representing moves as “remote procedure calls” helps to come up with a clean implementation strategy*

In this project, we implemented two classic turned-based board games:
- Chess
- Don't get angry! (3 player version)

The purpose of the project was to create decentralized games with append-only logs. The main problems were, how do we assure that a game is being fair without anyone being cheating and how do we update the games correctly when there is no server. In addition, we used RPC (Remote Procedure Calls) to be able to communicate between machines. The game is played on the terminal with different commands.

## Requirements

```
pip install Chessnut
pip install getmac
pip install pygame
```

## Create and join a game

### Chess & RCP AergereDicht:
1. Start with:
```
python main.py <type of game> <ip address 1> <ip address 2>
```
**Note**: <Type of game> is either chess or dga and the amount of ip addresses depend on the number of players. Also, if you are playing on a Linux machine, you may have to enter your own IP address too (the program the tells you when to) because the program wants you to use the localhost. 
2. A menu will show up and since we want to create a game we type:
```
/create <file name>
```

3. Since our RPC server is running in the background, we are listening to special requests of other machines. The machines request by targeting the IP address of the game creator (it is always the first entered IP address). It will automatically add the file into the corresponding directory.
```
/request <file name> 
```
4. We need to open the game and decide if we want to join the game (we will be asked first). **Note**: Same for the Don't get angry game, but for 3 people.
```
/play <file name>
```
5. Since the game was accepted, all are ready now to play the game by typing again:
```
/play <file name>
```

Enjoy playing!

### Bacnet AergereDichNicht: (Due to the nature of Bacnet, recreation of these steps might be difficult)
1. Masterfeed setup

Start with no key files or cborDatabase / eventDatabase in your directory. 

For each client: Launch feed_control.py, choose a username and press update username (feed_control does not act correctly on Mac OS, linux is recommended)

2. Masterfeed trusting 

Every client has to trust all other master feeds. You can share masterfeeds with 
```
python SyncFeeds.py --client [port]
```
And you can receive feeds with
```
python SyncFeeds.py --server [port]
```
After receiving a feed, trust it with feed_control.py (click on the feed, click trust). This is an unavoidable hassle with 4 players.

3. Taking turns

After trusting the masterfeeds, it is time to start the actual game feed. Launch the game AergereDichNicht.py, chose a colour, and the first player takes a turn by clicking on the dice by his colour.
   Sharing and receiving the game feed is easier now, simply press LEFT KEY to share and the next player presses RIGHT KEY to receive the feed.
   After receiving the feed, the game will automatically update all the pieces on the board. Take your turn then by clicking on your dice, and repeat this step.

##The game
### How to play
There are different commands to make the game playable:
```
In chess: /move <piece position/destination>    #e.g. /move e2e4
In Dga: /move                                   # Randomly chooses a number like a dice (1-6)
/display                                        # Display the board
/turnof                                         # Check who's turn it is
/whoami                                         # Which color/piece you have and which player you are
/ff                                             # Forfeit (not possible in Don't get angry)
/status                                         # Get information if game is over or going on
/refresh                                        # Refresh your game board after somebody made a move
/fetch                                          # If you lost the connection and others made already move, you can fetch it
```

### Game states

To be able to play, we need different game states and permanent assignments. Every game has board (information), roles assignment, game status, player identification and sequence number. If more games will be added with this system, they must mostly look like the examples below, nevertheless, one could add an arbitrary amount of other important states for the game. Momentary (and actually only for demonstration purposes), all players are identified by their MAC address. For the integration into BACnet, we may could use the FeedIDs. The role assignment happens randomly, when all players are registered. The status shows us 3 respectively 4 states: FF, GOINGON, FINISHED, CHEATED. If somebody forfeits in chess, the status adapts to it and sets also winner/loser. The same applies when the game is finished. CHEATED is more an overall status. If the board/game information is manipulated, it will be recognised as cheating by controlling previous and current game board.
Chess:
```
base_info = {
            'fen': game_fen,    # The game board, whose turn is it, other information
            'p1': gma(),        # Identification of machine 1
            'p2': None,         # Identification of machine 2
            'w': None,          # Which player is assigned to this role
            'b': None,          # Which player is assigned to this role
            'status': State.ONGOING,    # Game status (FF, ONGOING, FINISHED, CHEATED)
            'win': None,        # Assigning of p1 or p2
            'lose': None,       # Assigning of p1 or p2
            'seq': -1           # Sequence number
        }
```

DGA:
```
start_board = {
        'fen': {0: 'B', 1: 'O', 2: 'O', 3: 'O', 4: 'O', 5: 'O', 6: 'O', 7: 'O', 8: 'O',
                9: 'R', 10: 'O', 11: 'O', 12: 'O', 13: 'O', 14: 'O', 15: 'O', 16: 'O', 17: 'O',
                18: 'Y', 19: 'O', 20: 'O', 21: 'O', 22: 'O', 23: 'O', 24: 'O', 25: 'O', 26: 'O',
                27: 'x', 28: 'x', 29: 'x', 30: 'x',
                31: 'x', 32: 'x', 33: 'x', 34: 'x',
                35: 'x', 36: 'x', 37: 'x', 38: 'x',
                39: 'X'},                       # The game board
        'counter': {'B': 0, 'R': 0, 'Y': 0},    # Steps counter
        'status': 'normal',                     # Game status
        'turn': 'B',                            # Whose turn is it
        'p1': gma(),                            # Player 1 Identification
        'p2': None,                             # Player 2 Identification
        'p3': None,                             # Player 3 Identification
        'B': None,                              # Role assignment
        'R': None,                              # Role assignment
        'Y': None,                              # Role assignment
        'seq': -1                               # Sequence number
    }
```
### The composition
One game contains actuallyof 4 types of objects: Outer Loop, Inner Loop, the game itself and its game information. The classes for the game information handle the different states, assign roles, store the identifications, etc. Every game has its own "Manager". The main class of a game checks the validation by using tools of the game information class. Additionally, it has the interfaces to interact with the user (the commands in the inner loop). The outer loop is there for the creation/joining of game.

## Features
### Append-only logs
Thers is one file with the current game states and all previous games states including a time stamp. The current or new received game state gets compared with the previous state. Depending on the game, sequences are controlled by checking the numbers. In a turned-based game, all next possible game states are finite (mostly a small number of states). Therefore, it is easy to tell if the new game state is a sequence of the previous game state and that nobody is cheating or anything like that.

### Only one player is allowed to make a move
Roles/Pieces are assigned to only one machine when the game is joined. The game recognises the machine when the program start and must wait until it is its turn to make a move. Other machines cannot open the file in the programs and do anything, since the game file is restricted to only players' machines.

### RPC
During a game session, a RPC server must be running in the background to be able to play the game. Everytime somebody makes a move, the server pings every machine to tell them that a move/update was made. The ping triggers a request on all other machines to obtain the newest game state. That happens automatically, nevertheless, the program must be "refreshed" manually (command in-game).

### Connection loss
If somebody somehow disconnected and moves were made, there is a possibility in-game '/fetch' to fetch the newest moves (even if it is not only the last one).


## Pictures
Chess:

![alt text](https://github.com/cn-uofbasel/BACnet/blob/redez_games/redez-sem-hs20/groups/05-decentGames/res/chess.png)

Don't get angry:

![alt text](https://github.com/cn-uofbasel/BACnet/blob/redez_games/redez-sem-hs20/groups/05-decentGames/res/dga.png)

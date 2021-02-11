# 05 - Decent Games

## Introduction
*Many turn-based games exist on the Web where a game server keeps thegame’s state and permits (or prevents) the players/clients to make their move. In this proposed project, a turn-based game like chess should be implemented in orde to learn about the state management, starting from opening a game (where both players have to first agree) to validating each move, ending or aborting a game, as well as having a list of all pending games. In a second step, this should be expanded to a turn-based game with three players. In both steps it is assumed that structuring the game by representing moves as “remote procedure calls” helps to come up with a clean implementation strategy*

In this project, we implemented two classic turned-based board games:
- Chess
- Don't get angry! (3 player version)

The purpose of the project was to create decentralized games with append-only logs. The main problems were, how do we assure that a game is being fair without anyone being cheating and how do we update the games correctly when there is no server. In addition, we used RPC (Remote Procedure Calls) to be able to communicate between machines. The game is played on the console with different commands.

## Requirements

```
pip install Chessnut
pip install getmac
```

## Create and join a game
0. We start with an RPC server.
```
python RPC.py
```
1. Start with:
```
python main.py
```
2. A menu will show up and since we want to create a game we type:
```
/create <type of game> <file name>
```
Note: type of games are either *chess* or *dga*
3. Since our RPC server is running in the background, we are listening to special requests of other machines. We request by targeting the IP address of the game creator. It will automatically add the file in the corresponding directory.
```
/request <type of game> <file name> <target machine>
```
4. We need to open the game and decide if we want to join the game (we will be asked first). The game will restart after accepting to join the game.
```
/play <type of game> <file name>
```
5. Now, also the creator must request the same game on the joiner's machine to get the update. Therefore, same command will be used as above. **Note**: Same for the Don't get angry game. All 3 machines need the updated files. Some communication between players will be needed.
6. Since the game was accepted, all are ready now to play the game by typing (target machine 2 only needed in Don't get angry):
```
/play <type of game> <file name> <target machine 1> <target machine 2>
```

Enjoy playing!
## How to play
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
```

## Pictures
Chess:

![alt text](https://github.com/cn-uofbasel/BACnet/blob/redez_games/redez-sem-hs20/groups/05-decentGames/res/chess.png)

Don't get angry:

![alt text](https://github.com/cn-uofbasel/BACnet/blob/redez_games/redez-sem-hs20/groups/05-decentGames/res/dga.png)

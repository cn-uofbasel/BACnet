# IaS Project Group 7: Social Graph Explorer - BackEnd

##Goal
The goal of the project is to represent the social network of BACnet. 
The project was split into two groups: FrontEnd and BackEnd.
We are the BackEnd group, and our main goal is to provide the data needed to represent the graph in a GUI. 
The module "Person.py" and the Json-file "loadedData.json" are interfaces that are provided for the FrontEnd group.

##Interfaces
The following two interfaces are provided:
### Json: loadedData.json
This file is saved in "FrontEnd/socialgraph/static/socialgraph", and it is an interface to save the nodes and edges in the graph. 
First, there is a list of nodes, followed by a list of edges. 

For each node, the attributes of the user are saved. 
The attributes are: gender, birthday, country, town, language, status etc.. We also compute an activity level and an influencer status.

For each edge the start and end user-ID are saved.

###Person
This module can be used for changes in the graph while the user is online. The module provides methods to 
change the attributes and methods that handle following and unfollowing. 

## run code
Run "main.py".
Afterwards, a data order that includes an order for each user will be generated. Also, the Json-file will be current after.
  
To look at the GUI of the graph read the readme of the FrontEnd group.

![Logo](Documents/logo.png "Logo")
# BACnetCore
### A python-package to enter the world of BACnet!
  
  
We collected and expanded the core features of the BACnet and put them in a package. Our main goal was to present a
well structured, modular library that tackles the most important functions that need to exist on a node of the BACnet.
Prior to this package, several variants of the different modules were implemented by different groups and it was hard
to get an overview.  

Future BACnet developers may use this package as a quick way to get started with the BACnet. In our 
[Documentation](Documents/BACnet-Core-Documentation.pdf) or the [Report](Documents/BACnet-Core-Report.pdf), one can find
all the information needed to get to know the structure of the BACnet and more specifically of our core, as well as
some sample programms on how to use it. For a quick overview, we refer to the [Class Diagramm](Documents/libStructure/BACnetCore_classDiagram.pdf).  
The datastructures and functionalities provided should make it easy to implement new features of the BACnet. Simply add
your own Channel variant and connect it to the core, choosing the synchronisation mode you want. The rest should be handled
automatically.  
If there exists the need for more functionalities, the modular architecture of the core should make it easy to navigate
and find the right part to make adjustments.  
For even more information on how to work with the package or explanations for different classes and methods, please refer
to the codebase itself. It is well documented and commented.



### Future Expansion and Improvement Ideas

Down below are some ideas for future developers who may want to further improve our core implementations by adding new
features:
- Implement the ability to not trust a feed again
- Implement the ability to unblock a feed again
- Add some more channels to improve core compatibility with further projects



This is a project executed during the spring semester 2021 as part of the lecture "Introduction to Internet and Security", 
led by Professor Tschudin.  
Group Members: Raphael Kreft, Tim Bachmann, Nico Aebischer

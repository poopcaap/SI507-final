# SI507-final
To begin this program, you can download search.py and the json directory. command 'python search.py' to start the program.
The program will show:
Select option (1: Route Search, 2: Airline Code Search, 3: Airport Code Search, 4: Exit):

The first function is the main function of the program. It search the airline code, departure code, the plane model and distance range. And it will output all the route that fit the result.
<img width="791" alt="search1" src="https://github.com/poopcaap/SI507-final/assets/143746602/43de8357-c750-49dd-87ed-2941a67c5e37">
For example, in this picture it shows all the flight that is operated by Emirates(code ek), depart from Dubai(code dxb), use Boeing 777 plane and distance from 2001-4000 miles. 
You can also use fuzzy search. For example, you can type 'any' on certain place to get all result of this search.
<img width="809" alt="search2" src="https://github.com/poopcaap/SI507-final/assets/143746602/931c1031-2d6e-4ac0-b647-db98c96d9da0">
After forming the result, you can do following option:
1 return to start
2 sort by other factor(default:distance, you can also choose to sort by airline, departure, plane model)
3 turn mile to km
4 create a map showing routes
5 exit the program.

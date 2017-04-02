def task3():
    my_file = open("task3.data", "w")
    my_file.write("1 2 3 4 5 6 7 8 9 10")
    my_file.close()
    
    read_file = open("task3.data", "r")
    items = read_file.read().split(' ')
    read_file.close()
    
    items1 = []
    items2 = []
    
    for i in range(len(items)/2):
        items1.append(int(items[i]))
        items2.append(int(items[i+5]))
        
    print items1
    print items2
    
task3()
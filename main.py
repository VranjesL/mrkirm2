import sys
from multiprocessing import Process, Queue
from msg_passing_api import *

class Processor():

    def __init__(self, id, neighbours):
        self.parent = None
        self.children = []
        self.other = []
        self.id = id
        self.neighbours = neighbours
        self.root = True if self.id == 0 else False

def main():
    if len(sys.argv) != 3 :
        print("Invalid number of arguments!")
        print("Usage example: python.exe main.py 0 8") # 0 is id of processor, 8 is number of processors
        exit()

    id = int(sys.argv[1])
    num_of_processors = int(sys.argv[2])
    print(f"Enter neighbours for processor {id} (put space between neigbours)):")
    neighbours_input = input()
    neighbours = list(map(int, neighbours_input.split()))
    
    p = Processor(id=id, neighbours=neighbours)
    print("Processor " + str(p.id))

    allPorts = [6000+i for i in range(num_of_processors)]
    localPort = allPorts[id]
    remotePorts = [x+6000 for x in p.neighbours if x != p.id]

    queue = Queue()
    
    # Create and start server process
    server = Process(target=server_fun, args=(localPort,queue))
    server.start()
    
    # Set the lst of the addresses of the peer node's servers
    remote_server_addresses = [('localhost', port) for port in remotePorts]

    # Comunication starts when root processor manually starts it
    if p.root:
        while True:
            msg = input("Input 'start': ")
            if msg == 'start':
                break

    while True:
        if (p.root and p.parent == None):                               # if pi = pr and parent = NIL then   // koren još nije poslao <M>
            broadcastMsg(remote_server_addresses, (p.id, 'Hello'))      # pošalji <M> svim susedima
            p.parent = p.id                                             # parent := pi

        msg = rcvMsg(queue)
        sender_id = int(msg[0])
        received_msg = msg[1]
        sender = ('localhost', 6000 + sender_id)

        if received_msg == 'Hello':                                     # po prijemu <M> od suseda pj
            if p.parent == None:                                        # if parent = NIL then   // pi još nije bio primo <M>
                p.parent = sender_id                                    # parent := pj
                sendMsg(sender, (p.id, 'parent'))                       # pošalji <parent> ka pj

                if len(p.neighbours) > 1:                               # if postoje susedi osim pj ... 
                    addresses = [('localhost', port) for port in remotePorts if port != sender_id+6000]
                    broadcastMsg(addresses, (p.id, 'Hello'))            # ... then pošalji im <M> ... 
                else:
                    break                                               # ... else terminate
            else:
                sendMsg(sender, (p.id, 'already'))                      # else posalji <already> ka pj

        elif received_msg == 'parent':                                  # po prijemu <parent> od suseda pj:
            p.children.append(sender_id)                                # dodaj pj u children
            if set(p.children).union(p.other) == set(p.neighbours) - {p.parent}:    #if children + other sadrže sve susede osim parent then terminate

                break

        elif received_msg == 'already':                                 # po prijemu <already> od suseda pj:
            p.other.append(sender_id)                                   # dodaj pj u other
            if set(p.children).union(p.other) == set(p.neighbours) - {p.parent}:    #if children + other sadrze sve susede osim parent then terminate
                break
    
    print("Parent: " + str(p.parent))
    print("Children: " + str(p.children))
    print("Other: " + str(p.other))

    server.join()
    
    # Delete queue and server
    del queue
    del server

if __name__ == '__main__':
    main()
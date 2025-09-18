import multiprocessing as mp
from manager_factory import QueueManager
import uuid

def main() -> None:
    # Create a unique queue ID for this server instance
    queue_id = str(uuid.uuid4())
    
    # Create and start the manager
    manager = QueueManager(address=('localhost', 50000), authkey=b'abcdefg')
    manager.start()
    
    # Get the queue from the manager (this creates it in the manager process)
    queue = manager.get_queue(queue_id)

    with open("queue_address.txt", "w") as f:
        print(f"writing address {manager.address} with queue_id {queue_id}")
        # Write both address and queue_id
        f.write(f"{repr(manager.address)}\n{queue_id}")

    # Use the queue through the proxy
    print("waiting for input")
    print(queue.get())

if __name__ == "__main__":
   main()
# end main

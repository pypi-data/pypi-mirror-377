import multiprocessing as mp
from manager_factory import QueueManager
import ast

def main() -> None:
    with open("queue_address.txt", "r") as f:
        lines = f.read().strip().split('\n')
        # Parse the address tuple
        address = ast.literal_eval(lines[0])
        queue_id = lines[1]

    print(f"read address {address} with queue_id {queue_id}")

    # Connect to the manager
    manager = QueueManager(address=address, authkey=b'abcdefg')
    manager.connect()
    
    # Get the specific queue by ID (same method as server)
    q = manager.get_queue(queue_id)
    
    print("Sending item")
    q.put(10)
    print("done")

if __name__ == "__main__":
   main()
# end main

class Node:
    def __init__(self, price, quantity, order_type):
        self.price = price
        self.quantity = quantity
        self.order_type = order_type  # 'buy' or 'sell'
        self.next = None
        self.prev = None

    def to_dict(self):
        return {"price": self.price, "quantity": self.quantity}

class SortedDoublyLinkedList:
    def __init__(self, descending=False):
        self.head = None
        self.tail = None
        self.descending = descending

    def insert_or_merge(self, price, quantity):
        """Insert a new price level or merge with existing one."""
        new_node = Node(price, quantity, self.descending)

        # Empty list case
        if not self.head:
            self.head = self.tail = new_node
            return

        # Traverse to find the appropriate position
        current = self.head
        while current:
            if (self.descending and price > current.price) or (not self.descending and price < current.price):
                # Insert new node in sorted order
                if current.prev:
                    current.prev.next = new_node
                    new_node.prev = current.prev
                else:
                    self.head = new_node
                new_node.next = current
                current.prev = new_node
                return
            elif price == current.price:
                # Merge quantities at the same price level
                current.quantity += quantity
                return
            previous = current
            current = current.next

        # Insert at the end if no position found
        previous.next = new_node
        new_node.prev = previous
        self.tail = new_node

    def remove_node(self, node):
        """Remove a node from the linked list."""
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

    def to_list(self):
        """Convert the linked list to a list for easy serialization."""
        result = []
        current = self.head
        while current:
            result.append(current.to_dict())
            current = current.next
        return result

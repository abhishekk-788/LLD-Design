class LFUCache 
{
    class Node {
        int key, value, count;
        Node next, prev;

        Node(int key, int value, int count) {
            this.key = key;
            this.value = value;
            this.count = 1;
        }
    }

    private int capacity, totalNodes, minFreq;
    private Map<Integer, Node> hash;
    private Map<Integer, LinkedHashSet<Node>> counterMap;

    public LFUCache(int capacity) {
        this.capacity = capacity;
        this.totalNodes = 0;
        this.minFreq = 0;
        hash = new HashMap<>();
        counterMap = new HashMap<>();
    }

    public int get(int key) {
        if (!hash.containsKey(key)) return -1;

        Node node = hash.get(key);
        removeNode(node.count, node);
        addToHead(node.count + 1, node);
        return node.value;
    }

    public void put(int key, int value) {
        if (capacity == 0) return;

        if (hash.containsKey(key)) {
            Node node = hash.get(key);
            node.value = value;
            removeNode(node.count, node);
            addToHead(node.count + 1, node);
        } else 
        {
            if (totalNodes >= capacity) {
                removeLFU();
            }

            Node node = new Node(key, value, 1);
            addToHead(1, node);
            hash.put(key, node);
            totalNodes++; minFreq = 1;
        }
    }

    private void removeNode(int count, Node node) {
        counterMap.get(count).remove(node);

        if (counterMap.get(count).isEmpty()) {
            counterMap.remove(count);
            if (count == minFreq) {
                minFreq++;
            }
        }
    }

    private void addToHead(int count, Node node) {
        node.count = count;
        counterMap.computeIfAbsent(count, k -> new LinkedHashSet<>()).add(node);
        hash.put(node.key, node);
    }

    private void removeLFU() {
        LinkedHashSet<Node> nodes = counterMap.get(minFreq);
        Node evictNode = nodes.iterator().next();
        nodes.remove(evictNode);

        if (nodes.isEmpty()) {
            counterMap.remove(minFreq);
        }

        hash.remove(evictNode.key);
        totalNodes--;
    }
}

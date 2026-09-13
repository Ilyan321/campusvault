import logging
from typing import Dict, Any, List
from services.embedder_service import get_embeddings_batch
from services.supabase_service import insert_note_chunks, get_supabase_client
from utils.chunker import semantic_chunk

logger = logging.getLogger("campusvault.seed")

SEED_NOTES = [
    # --- 1. CSE-212: Data Structures & Algorithms ---
    {
        "course_id": "CSE-212",
        "week_number": 1,
        "topic": "Pointers, Dynamic Memory Allocation and Arrays",
        "file_name": "pointers_and_memory_management.cpp",
        "content": (
            "QUEST Nawabshah CSE-212 DSA Week 1: Pointers and Dynamic Memory Allocation in C/C++\n"
            "Key Concept: A pointer stores the memory address of another variable. Dereferencing `*ptr` accesses or modifies the value at that address.\n\n"
            "Memory Segments:\n"
            "- Stack: Fast, automatic allocation/deallocation for local variables and function call frames.\n"
            "- Heap: Manual dynamic allocation at runtime (`malloc`, `calloc`, `new`). Unfreed heap memory causes memory leaks.\n\n"
            "Dynamic Memory Functions:\n"
            "- `malloc(size_t bytes)`: Allocates uninitialized memory. Returns `void*` or `NULL`.\n"
            "- `calloc(num, size_t bytes)`: Allocates and zero-initializes memory for `num` elements.\n"
            "- `free(ptr)`: Releases heap memory. Set `ptr = NULL` immediately to avoid dangling pointer vulnerabilities.\n\n"
            "Pointer Arithmetic:\n"
            "Adding `ptr + 1` advances the address by `sizeof(*ptr)` bytes. For any array `arr[i] == *(arr + i)`."
        )
    },
    {
        "course_id": "CSE-212",
        "week_number": 3,
        "topic": "Singly and Doubly Linked Lists",
        "file_name": "linked_list_traversal_lab.cpp",
        "content": (
            "QUEST Nawabshah CSE-212 DSA Lab #3: Singly and Doubly Linked List Implementation in C++\n"
            "Node Definition:\n"
            "```cpp\n"
            "struct Node {\n"
            "    int data;\n"
            "    Node* next;\n"
            "    Node* prev; // Doubly linked list\n"
            "    Node(int val) : data(val), next(nullptr), prev(nullptr) {}\n"
            "};\n"
            "```\n\n"
            "Core Operations & Complexities:\n"
            "1. Insert at Head: O(1) — `newNode->next = head; if(head) head->prev = newNode; head = newNode;`\n"
            "2. Insert at Tail: O(N) without tail pointer, O(1) with tail pointer.\n"
            "3. Delete Node: O(1) given node pointer — `node->prev->next = node->next; node->next->prev = node->prev; delete node;`\n"
            "4. Search: O(N) linear traversal.\n\n"
            "Exam Viva Tip: Linked lists eliminate contiguous memory requirements of arrays, enabling dynamic growth without re-allocation overhead."
        )
    },
    {
        "course_id": "CSE-212",
        "week_number": 4,
        "topic": "Stack Data Structure & Expression Parsing",
        "file_name": "stack_operations_and_postfix_lab.cpp",
        "content": (
            "QUEST Nawabshah CSE-212 DSA Lab #4: Stack (LIFO) & Infix to Postfix Expression Parsing in C++\n"
            "Principles: Last-In, First-Out (LIFO). Elements are pushed and popped exclusively at the `top`.\n\n"
            "Infix to Postfix Conversion Algorithm:\n"
            "1. Operands (e.g. A, B, 5) -> Append directly to output string.\n"
            "2. Left Parenthesis `(` -> Push onto operator stack.\n"
            "3. Right Parenthesis `)` -> Pop and append to output until `(` is popped.\n"
            "4. Operators (+, -, *, /, ^) -> While stack not empty and `precedence(stack.top()) >= precedence(current)`, pop stack to output. Then push current operator.\n\n"
            "Precedence Order: `^` (3, Right-to-Left) > `*`, `/` (2, Left-to-Right) > `+`, `-` (1, Left-to-Right)."
        )
    },
    {
        "course_id": "CSE-212",
        "week_number": 5,
        "topic": "Queue Data Structure & Circular Implementations",
        "file_name": "circular_queue_lab.cpp",
        "content": (
            "QUEST Nawabshah CSE-212 DSA Lab #5: Circular Queue Implementation in C++\n"
            "Key Concept: In a standard linear array queue, once rear reaches MAX-1, we cannot insert even if front has moved, causing false overflow. "
            "A Circular Queue solves this by wrapping indices around using modulo arithmetic: `rear = (rear + 1) % MAX_SIZE`.\n\n"
            "Conditions:\n"
            "1. IsEmpty: `front == -1 && rear == -1`\n"
            "2. IsFull: `(rear + 1) % MAX_SIZE == front`\n"
            "3. Enqueue: if empty, set `front = rear = 0`. Else `rear = (rear + 1) % MAX_SIZE`. Array[rear] = item.\n"
            "4. Dequeue: item = Array[front]. If `front == rear`, queue becomes empty, set `front = rear = -1`. Else `front = (front + 1) % MAX_SIZE`.\n\n"
            "C++ Snippet:\n"
            "```cpp\n"
            "#define MAX 5\n"
            "int queue[MAX], front = -1, rear = -1;\n"
            "void enqueue(int val) {\n"
            "    if ((rear + 1) % MAX == front) { cout << \"Queue Overflow!\\n\"; return; }\n"
            "    if (front == -1) front = 0;\n"
            "    rear = (rear + 1) % MAX;\n"
            "    queue[rear] = val;\n"
            "}\n"
            "int dequeue() {\n"
            "    if (front == -1) { cout << \"Queue Underflow!\\n\"; return -1; }\n"
            "    int val = queue[front];\n"
            "    if (front == rear) front = rear = -1;\n"
            "    else front = (front + 1) % MAX;\n"
            "    return val;\n"
            "}\n"
            "```\n"
            "Viva Tip: Time complexity for both Enqueue and Dequeue in Circular Queue is strictly O(1)."
        )
    },
    {
        "course_id": "CSE-212",
        "week_number": 8,
        "topic": "Binary Search Trees & Tree Traversals",
        "file_name": "binary_search_tree_traversals.cpp",
        "content": (
            "QUEST Nawabshah CSE-212 DSA Week 8: Binary Search Tree (BST) & Tree Traversals in C++\n"
            "BST Property: For every node $N$, all nodes in left subtree have keys $< N.key$, and all nodes in right subtree have keys $> N.key$.\n\n"
            "Depth-First Traversals:\n"
            "1. Inorder (Left -> Root -> Right): Always produces strictly SORTED output for a valid BST.\n"
            "2. Preorder (Root -> Left -> Right): Used for serializing/copying trees.\n"
            "3. Postorder (Left -> Right -> Root): Used for deleting/freeing tree nodes (bottom-up).\n\n"
            "Time Complexity:\n"
            "- Balanced BST (AVL/Red-Black): Search, Insert, Delete = $O(\\log N)$.\n"
            "- Degenerate Skewed BST: Search, Insert, Delete degrades to $O(N)$ (linked list behavior)."
        )
    },
    {
        "course_id": "CSE-212",
        "week_number": 12,
        "topic": "Graph Traversals and Shortest Path Optimization",
        "file_name": "dijkstra_shortest_path_notes.cpp",
        "content": (
            "QUEST Nawabshah CSE-212 DSA Week 12: Dijkstra's Single Source Shortest Path Algorithm\n"
            "Concept: Dijkstra finds shortest paths from a single source node to all other vertices in a weighted graph with non-negative edge weights.\n\n"
            "Greedy Strategy & Relaxation:\n"
            "Maintain a min-priority queue of `(distance, u)` pairs. Initially, `dist[source] = 0` and all other `dist[v] = infinity`.\n"
            "For edge (u, v) with weight w: If `dist[u] + w < dist[v]`, update `dist[v] = dist[u] + w` (Relaxation step) and push `(dist[v], v)` into the priority queue.\n\n"
            "Complexity:\n"
            "- Using Adjacency Matrix: O(V^2)\n"
            "- Using Adjacency List + Min-Heap/Priority Queue: O((V + E) log V)\n\n"
            "Exam Pitfall: Dijkstra FAILS on graphs with negative weight edges or negative cycles. For negative weights, use Bellman-Ford algorithm (O(V*E))."
        )
    },

    # --- 2. CSE-305: Data & Computer Networks ---
    {
        "course_id": "CSE-305",
        "week_number": 2,
        "topic": "OSI 7-Layer Architecture & TCP/IP Model",
        "file_name": "osi_and_tcp_ip_layered_model.txt",
        "content": (
            "QUEST CSE-305 Computer Networks Week 2: OSI 7-Layer vs TCP/IP Architecture\n"
            "OSI Layers & Protocol Data Units (PDUs):\n"
            "1. Physical (Bits): Hubs, cables, modulation, bit timing.\n"
            "2. Data Link (Frames): Switches, MAC addressing, framing, error detection (CRC).\n"
            "3. Network (Packets): Routers, IPv4/IPv6 logical addressing, path routing.\n"
            "4. Transport (Segments): TCP/UDP, port numbers, end-to-end reliability, flow control.\n"
            "5. Session (Data): Session establishment, checkpointing, token management.\n"
            "6. Presentation (Data): Encryption (TLS), data translation, compression.\n"
            "7. Application (Data): User interface protocols (HTTP, DNS, SMTP, SSH).\n\n"
            "TCP/IP Mapping: Application (combines 5, 6, 7), Transport (4), Internet (3), Network Access (1, 2)."
        )
    },
    {
        "course_id": "CSE-305",
        "week_number": 5,
        "topic": "IP Addressing, CIDR & Subnetting Calculations",
        "file_name": "subnetting_and_cidr_guide.pdf",
        "content": (
            "QUEST CSE-305 Networks Lab #5: IP Addressing & Subnetting Guide\n"
            "IPv4 address is 32 bits divided into 4 octets. Default classes:\n"
            "- Class A: /8 (1.0.0.0 to 126.0.0.0)\n"
            "- Class B: /16 (128.0.0.0 to 191.255.0.0)\n"
            "- Class C: /24 (192.0.0.0 to 223.255.255.0)\n\n"
            "CIDR (Classless Inter-Domain Routing) & Usable Hosts Formula:\n"
            "Host bits = 32 - prefix_length\n"
            "Total IP addresses = 2^(Host bits)\n"
            "Usable host IP addresses = 2^(Host bits) - 2 (Subtracting Network ID and Broadcast IP).\n\n"
            "Example /26 Subnet:\n"
            "Prefix = /26 -> Host bits = 32 - 26 = 6 bits.\n"
            "Total addresses = 2^6 = 64.\n"
            "Usable hosts per subnet = 64 - 2 = 62 hosts.\n"
            "Subnet mask = 255.255.255.192 (/26 = 11000000 = 128 + 64 = 192)."
        )
    },
    {
        "course_id": "CSE-305",
        "week_number": 9,
        "topic": "Routing Protocols (OSPF & RIP)",
        "file_name": "routing_protocols_ospf_rip.txt",
        "content": (
            "QUEST CSE-305 Networks Week 9: Dynamic Routing Protocols — Distance Vector vs Link State\n"
            "1. RIP (Routing Information Protocol - Distance Vector):\n"
            "- Algorithm: Bellman-Ford.\n"
            "- Metric: Hop count (Max allowed = 15; 16 represents infinity/unreachable).\n"
            "- Updates: Periodic broadcasts every 30 seconds. Slow convergence and prone to count-to-infinity problem.\n\n"
            "2. OSPF (Open Shortest Path First - Link State):\n"
            "- Algorithm: Dijkstra's Shortest Path First (SPF).\n"
            "- Metric: Cost (calculated as $10^8 / \\text{Bandwidth in bps}$).\n"
            "- Updates: Event-triggered Link State Advertisements (LSAs). Fast convergence, hierarchical area design (Area 0 Backbone)."
        )
    },
    {
        "course_id": "CSE-305",
        "week_number": 11,
        "topic": "Transport Layer Protocols: TCP vs UDP & Handshake",
        "file_name": "tcp_vs_udp_handshake_flow_control.txt",
        "content": (
            "QUEST CSE-305 Networks Week 11: Transport Layer — TCP 3-Way Handshake & Flow Control\n"
            "TCP 3-Way Handshake (Connection Establishment):\n"
            "1. Client -> Server: `SYN` (Seq = $x$)\n"
            "2. Server -> Client: `SYN-ACK` (Seq = $y$, Ack = $x + 1$)\n"
            "3. Client -> Server: `ACK` (Seq = $x + 1$, Ack = $y + 1$)\n\n"
            "TCP 4-Way Teardown: `FIN` -> `ACK` -> `FIN` -> `ACK`.\n\n"
            "Flow Control vs Congestion Control:\n"
            "- Flow Control: Uses Sliding Window (Receive Window `rwnd`) to prevent sender from overwhelming the receiver's buffer.\n"
            "- Congestion Control: Uses Congestion Window (`cwnd`) with Slow Start, Congestion Avoidance, Fast Retransmit, and Fast Recovery."
        )
    },

    # --- 3. CSE-310: Operating Systems ---
    {
        "course_id": "CSE-310",
        "week_number": 3,
        "topic": "CPU Scheduling Algorithms (FCFS, SJF, Round Robin)",
        "file_name": "cpu_scheduling_algorithms_notes.cpp",
        "content": (
            "QUEST Nawabshah CSE-310 Operating Systems Week 3: CPU Scheduling Algorithms & Gantt Charts\n"
            "Metrics:\n"
            "- Turnaround Time ($TAT$) = $\\text{Completion Time} - \\text{Arrival Time}$\n"
            "- Waiting Time ($WT$) = $TAT - \\text{Burst Time}$\n"
            "- Response Time = $\\text{First CPU allocation time} - \\text{Arrival Time}$\n\n"
            "Scheduling Algorithms:\n"
            "1. FCFS (First-Come, First-Served): Non-preemptive. Suffers from Convoy Effect (short processes waiting behind long ones).\n"
            "2. SJF (Shortest Job First): Optimal minimum average waiting time. Preemptive version is called SRTF (Shortest Remaining Time First).\n"
            "3. Round Robin (RR): Preemptive using fixed Time Quantum ($Q$). If $Q$ is too large, behaves like FCFS; if $Q$ is too small, excessive context-switch overhead occurs."
        )
    },
    {
        "course_id": "CSE-310",
        "week_number": 6,
        "topic": "Process Synchronization, Mutex & Semaphores",
        "file_name": "process_synchronization_and_semaphores.cpp",
        "content": (
            "QUEST Nawabshah CSE-310 Operating Systems Week 6: Process Synchronization & Classic Problems\n"
            "Critical Section Requirements:\n"
            "1. Mutual Exclusion: Only one process can execute in critical section at any instant.\n"
            "2. Progress: Decision on who enters next cannot be postponed indefinitely by processes outside critical section.\n"
            "3. Bounded Waiting: Bound on number of times other processes enter before a request is granted.\n\n"
            "Semaphores (Dijkstra):\n"
            "- `wait(S)` / `P(S)`: `while(S <= 0); S--;` (Decrements semaphore, blocks if $\\le 0$).\n"
            "- `signal(S)` / `V(S)`: `S++;` (Increments semaphore and wakes waiting process).\n\n"
            "Classic Problems: Producer-Consumer (Bounded Buffer), Reader-Writer (Starvation prevention), Dining Philosophers (Deadlock avoidance using resource hierarchy)."
        )
    },
    {
        "course_id": "CSE-310",
        "week_number": 8,
        "topic": "Deadlocks & Banker's Safety Algorithm",
        "file_name": "deadlock_bankers_safety_algorithm.cpp",
        "content": (
            "QUEST Nawabshah CSE-310 Operating Systems Week 8: Deadlocks & Banker's Safety Algorithm\n"
            "Coffman 4 Deadlock Conditions (All 4 must hold simultaneously):\n"
            "1. Mutual Exclusion\n"
            "2. Hold and Wait\n"
            "3. No Preemption\n"
            "4. Circular Wait\n\n"
            "Banker's Algorithm Matrices:\n"
            "- $\\text{Available}[m]$: Available instances of resource $R_j$.\n"
            "- $\\text{Max}[n][m]$: Max demand of process $P_i$.\n"
            "- $\\text{Allocation}[n][m]$: Currently allocated resources.\n"
            "- $\\text{Need}[n][m] = \\text{Max}[i][j] - \\text{Allocation}[i][j]$.\n\n"
            "Safety Check: Find process $P_i$ where $\\text{Need}_i \\le \\text{Work}$. Set $\\text{Work} = \\text{Work} + \\text{Allocation}_i$, mark finished. If all processes finish, state is SAFE."
        )
    },
    {
        "course_id": "CSE-310",
        "week_number": 12,
        "topic": "Virtual Memory, Paging & Page Replacement (LRU, FIFO)",
        "file_name": "virtual_memory_paging_and_lru.txt",
        "content": (
            "QUEST Nawabshah CSE-310 Operating Systems Week 12: Virtual Memory, Paging & Page Replacement\n"
            "Paging Architecture:\n"
            "- Logical Address: Split into Page Number ($p$) and Offset ($d$).\n"
            "- TLB (Translation Lookaside Buffer): High-speed associative cache for Page Table entries.\n"
            "- Effective Memory Access Time: $EAT = \\text{HitRate} \\times (t_{tlb} + t_{mem}) + (1 - \\text{HitRate}) \\times (t_{tlb} + 2 \\times t_{mem})$.\n\n"
            "Page Replacement Algorithms:\n"
            "1. FIFO: Replaces oldest loaded page. Suffers from Belady's Anomaly (more frames $\\rightarrow$ more page faults).\n"
            "2. Optimal (OPT): Replaces page not used for longest future duration (theoretical benchmark).\n"
            "3. LRU (Least Recently Used): Replaces page not used for longest past duration (stack property, immune to Belady's anomaly)."
        )
    },

    # --- 4. CSE-315: Database Systems & SQL ---
    {
        "course_id": "CSE-315",
        "week_number": 3,
        "topic": "Relational Algebra & Advanced SQL Queries",
        "file_name": "relational_algebra_and_advanced_sql.sql",
        "content": (
            "QUEST Nawabshah CSE-315 Database Systems Week 3: Relational Algebra & Advanced SQL Joins\n"
            "Relational Algebra Operators:\n"
            "- Selection ($\\sigma_{\\text{condition}}(R)$): Filters rows.\n"
            "- Projection ($\\pi_{\\text{columns}}(R)$): Filters columns / attributes.\n"
            "- Cartesian Product ($R \\times S$): All ordered pairs.\n"
            "- Natural Join ($R \\bowtie S$): Equi-join on matching attribute names.\n\n"
            "SQL Example — Department Salary Aggregations:\n"
            "```sql\n"
            "SELECT d.dept_name, COUNT(e.emp_id) AS total_employees, AVG(e.salary) AS avg_salary\n"
            "FROM departments d\n"
            "LEFT JOIN employees e ON d.dept_id = e.dept_id\n"
            "GROUP BY d.dept_name\n"
            "HAVING AVG(e.salary) > 75000\n"
            "ORDER BY avg_salary DESC;\n"
            "```\n"
            "Rule: `WHERE` filters rows BEFORE grouping; `HAVING` filters aggregate groups AFTER `GROUP BY`."
        )
    },
    {
        "course_id": "CSE-315",
        "week_number": 6,
        "topic": "Database Normalization (1NF, 2NF, 3NF & BCNF)",
        "file_name": "database_normalization_1nf_to_bcnf.txt",
        "content": (
            "QUEST Nawabshah CSE-315 Database Systems Week 6: Database Normalization (1NF to BCNF)\n"
            "Purpose: Eliminate insertion, deletion, and update anomalies and reduce data redundancy.\n\n"
            "Normal Forms Hierarchy:\n"
            "1. 1NF (First Normal Form): All column values must be atomic (no multi-valued attributes or repeating groups).\n"
            "2. 2NF (Second Normal Form): Must be in 1NF + NO Partial Dependencies (no non-prime attribute can depend on a proper subset of any candidate key).\n"
            "3. 3NF (Third Normal Form): Must be in 2NF + NO Transitive Dependencies ($X \\rightarrow Y$, where neither $X$ is superkey nor $Y$ is prime attribute).\n"
            "4. BCNF (Boyce-Codd Normal Form): For EVERY functional dependency $X \\rightarrow Y$, $X$ MUST be a Super Key."
        )
    },
    {
        "course_id": "CSE-315",
        "week_number": 10,
        "topic": "Transactions, ACID Properties & Concurrency Control (2PL)",
        "file_name": "acid_transactions_and_2pl_concurrency.sql",
        "content": (
            "QUEST Nawabshah CSE-315 Database Systems Week 10: ACID Properties & 2-Phase Locking (2PL)\n"
            "ACID Guarantees:\n"
            "- Atomicity: All operations in transaction succeed or none execute (All-or-Nothing via Rollback).\n"
            "- Consistency: Database transitions from one valid state satisfying all constraints to another.\n"
            "- Isolation: Concurrent transactions execute without interfering with each other.\n"
            "- Durability: Committed updates persist permanently on disk even during power failures (WAL / Write-Ahead Logging).\n\n"
            "Two-Phase Locking (2PL):\n"
            "1. Growing Phase: Transaction may acquire locks but cannot release any lock.\n"
            "2. Shrinking Phase: Transaction may release locks but cannot acquire new locks.\n"
            "Strict 2PL: All exclusive (X) locks held until transaction commits/aborts (prevents cascading aborts)."
        )
    },

    # --- 5. CSE-204: Digital Logic & Computer Architecture ---
    {
        "course_id": "CSE-204",
        "week_number": 2,
        "topic": "Boolean Algebra & Karnaugh Maps (K-Maps)",
        "file_name": "boolean_algebra_and_karnaugh_maps.txt",
        "content": (
            "QUEST CSE-204 Digital Logic Design Week 2: Boolean Minimization & Karnaugh Maps (K-Maps)\n"
            "Gray Code Ordering: 00, 01, 11, 10 (Adjacent cells differ by exactly ONE bit).\n\n"
            "K-Map Grouping Rules:\n"
            "1. Groups must contain $2^n$ cells (1, 2, 4, 8, 16).\n"
            "2. Group sizes must be maximized to eliminate the maximum number of variables.\n"
            "3. Groups can wrap around boundaries (corners and edges are adjacent).\n"
            "4. Don't-Care conditions ($d$ or $X$) can be treated as 1 if they enlarge a group, or 0 otherwise.\n\n"
            "De Morgan's Laws: $\\overline{A + B} = \\bar{A} \\cdot \\bar{B}$ and $\\overline{A \\cdot B} = \\bar{A} + \\bar{B}$."
        )
    },
    {
        "course_id": "CSE-204",
        "week_number": 9,
        "topic": "CPU Pipelining & Pipeline Hazards",
        "file_name": "cpu_pipelining_and_hazard_resolution.txt",
        "content": (
            "QUEST CSE-204 Computer Architecture Week 9: Classic 5-Stage RISC CPU Pipeline & Hazards\n"
            "5 Pipeline Stages: IF (Instruction Fetch) -> ID (Decode/Reg Read) -> EX (Execute/ALU) -> MEM (Memory Access) -> WB (Write Back).\n\n"
            "Pipeline Hazards & Solutions:\n"
            "1. Structural Hazard: Hardware resource conflict (e.g. unified memory accessed by IF and MEM simultaneously). Solution: Separate Instruction and Data Caches (Harvard Architecture).\n"
            "2. Data Hazard (RAW - Read After Write): Instruction depends on result of prior instruction still in pipeline. Solution: Data Forwarding / Bypassing or Pipeline Stall (Bubble Insertion).\n"
            "3. Control Hazard: Branch/jump instructions alter Program Counter. Solution: Dynamic Branch Prediction (2-bit saturating counter) and Delayed Branching."
        )
    },

    # --- 6. MATH-201: Linear Algebra & Applied Mathematics ---
    {
        "course_id": "MATH-201",
        "week_number": 2,
        "topic": "Matrices, Gaussian Elimination & System of Linear Equations",
        "file_name": "gaussian_elimination_and_linear_systems.txt",
        "content": (
            "QUEST MATH-201 Linear Algebra Week 2: Gaussian Elimination & System of Linear Equations\n"
            "System representation: $A \\mathbf{x} = \\mathbf{b}$, Augmented matrix $[A | \\mathbf{b}]$.\n\n"
            "Elementary Row Operations:\n"
            "1. $R_i \\leftrightarrow R_j$ (Row interchange)\n"
            "2. $R_i \\rightarrow k R_i$ ($k \\neq 0$, scalar multiplication)\n"
            "3. $R_i \\rightarrow R_i + k R_j$ (Row addition)\n\n"
            "Consistency Criteria (Rouché-Capelli Theorem):\n"
            "- Unique Solution: $\\text{Rank}(A) = \\text{Rank}([A|\\mathbf{b}]) = n$ (number of unknowns).\n"
            "- Infinitely Many Solutions: $\\text{Rank}(A) = \\text{Rank}([A|\\mathbf{b}]) < n$ ($n - r$ free variables).\n"
            "- Inconsistent / No Solution: $\\text{Rank}(A) < \\text{Rank}([A|\\mathbf{b}])$."
        )
    },
    {
        "course_id": "MATH-201",
        "week_number": 10,
        "topic": "Eigenvalues, Eigenvectors & Matrix Diagonalization",
        "file_name": "eigenvalues_eigenvectors_and_diagonalization.txt",
        "content": (
            "QUEST MATH-201 Linear Algebra Week 10: Eigenvalues, Eigenvectors & Diagonalization\n"
            "Definition: For square matrix $A_{n \\times n}$, scalar $\\lambda$ is an eigenvalue if there exists non-zero vector $\\mathbf{v}$ such that:\n"
            "$$A \\mathbf{v} = \\lambda \\mathbf{v} \\iff (A - \\lambda I)\\mathbf{v} = \\mathbf{0}$$\n\n"
            "Characteristic Equation: $\\det(A - \\lambda I) = 0$.\n\n"
            "Properties:\n"
            "1. $\\text{Trace}(A) = \\sum \\lambda_i$ (Sum of eigenvalues equals sum of main diagonal elements).\n"
            "2. $\\det(A) = \\prod \\lambda_i$ (Product of eigenvalues equals determinant).\n"
            "3. Matrix $A$ is diagonalizable if $A$ has $n$ linearly independent eigenvectors: $A = P D P^{-1}$, where $D$ is diagonal matrix of eigenvalues and $P$ is matrix of eigenvectors."
        )
    }
]

def seed_database() -> Dict[str, Any]:
    """
    Seeds the Supabase database with high-yield university peer notes across multiple engineering subjects.
    """
    total_indexed = 0

    for note in SEED_NOTES:
        chunks = semantic_chunk(note["content"], max_chars=450, overlap=80)
        embeddings = get_embeddings_batch(chunks)
        
        records = []
        for idx, (chunk_text, emb) in enumerate(zip(chunks, embeddings)):
            records.append({
                "content": chunk_text,
                "embedding": emb,
                "file_url": f"/api/notes/raw/{note['file_name']}",
                "file_name": note["file_name"],
                "course_id": note["course_id"],
                "week_number": note["week_number"],
                "topic": note["topic"],
                "chunk_index": idx,
                "metadata": {
                    "is_seed": True,
                    "total_chunks": len(chunks)
                }
            })
        
        inserted = insert_note_chunks(records)
        total_indexed += len(inserted) if inserted else len(records)

    return {
        "success": True,
        "message": f"Successfully seeded {total_indexed} high-yield note chunks across {len(SEED_NOTES)} university topics.",
        "seeded_topics": [f"[{n['course_id']}] {n['topic']}" for n in SEED_NOTES],
        "total_chunks": total_indexed
    }

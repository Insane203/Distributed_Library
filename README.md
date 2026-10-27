# Distributed Library Management System with Replication

A distributed library management application developed as part of the **M.Tech Computer Science and Engineering** program. The project explores distributed database concepts including data fragmentation, replication, distributed query processing, ACID transactions, and the CAP theorem.

## 📌 Project Overview

Traditional library management systems often store all information in a single database, which can create scalability, availability, and performance challenges as the system grows.

The **Distributed Library Management System** aims to organize library data across multiple database nodes while providing a centralized interface for managing students, books, and borrowing records.

The project demonstrates how distributed database techniques can improve data organization, availability, fault tolerance, and query performance.

## 🎯 Objectives

- Design a distributed database system for library management.
- Maintain student, book, and borrowing information.
- Implement data fragmentation across library nodes.
- Explore database replication and synchronization.
- Apply ACID properties to book issuing and returning transactions.
- Demonstrate CAP theorem trade-offs during network partitions.
- Implement distributed queries across data partitions.
- Develop a web-based interface for library operations.
- Evaluate query performance, consistency, and fault tolerance.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Flask | Backend web framework and API |
| MongoDB | Document database |
| PyMongo | Python–MongoDB connectivity |
| HTML, CSS, JavaScript | Frontend development |
| MongoDB Compass | Database inspection and management |
| Git and GitHub | Version control and project hosting |

## ✨ Planned Features

### 1. Student Management
- Store student ID, name, email, department, and contact details.
- Search and retrieve student records.
- Maintain borrowing history.

### 2. Book Management
- Store book IDs, titles, authors, categories, and copy counts.
- Search books by title, author, or category.
- Track available and borrowed copies.

### 3. Borrower Management
- Associate borrowing records with students and books.
- Maintain borrowing dates, due dates, and return status.
- Update book availability during issuing and returning.

### 4. Data Fragmentation
Divide library records into smaller logical partitions across database nodes.

Possible strategies include:
- **Horizontal fragmentation:** Divide records by branch, category, or another selection condition.
- **Vertical fragmentation:** Separate groups of attributes when appropriate.
- **Hybrid fragmentation:** Combine horizontal and vertical strategies.

The final fragmentation strategy will be determined by the implemented database design.

### 5. Database Replication
Maintain copies of data across database nodes to study:
- Data synchronization.
- Replication behavior.
- Read availability.
- Recovery after node failures.

MongoDB replica-set configuration and replication testing are required to demonstrate actual database replication.

### 6. ACID Transactions

The project will examine the four ACID properties:

- **Atomicity:** A book-issuing operation should either complete all required updates or roll back.
- **Consistency:** Database constraints and library rules should remain valid.
- **Isolation:** Concurrent borrowing operations should not incorrectly issue the same available copy.
- **Durability:** Committed transactions should persist according to the configured database durability guarantees.

Multi-document MongoDB transactions require a replica set or sharded cluster.

### 7. CAP Theorem Analysis

The project will examine the relationship between:

- **Consistency (C):** Whether reads observe the latest committed updates according to the selected consistency guarantees.
- **Availability (A):** Whether requests receive responses from available nodes.
- **Partition Tolerance (P):** Whether the system can handle communication failures between nodes.

A controlled network-partition experiment will be used to analyze consistency and availability trade-offs. The observed behavior will depend on the MongoDB deployment, read concern, write concern, and application design.

### 8. Distributed Query Processing
- Retrieve book records from multiple fragments.
- Combine results from different database nodes.
- Measure query execution time.
- Compare local and distributed query performance.

### 9. Web Interface
The planned interface will provide access to student records, book management, borrowing operations, and distributed database demonstrations.



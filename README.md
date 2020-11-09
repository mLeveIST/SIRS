# Ransomware-resistant remote documents

## Scenario

Collaborative applications allow groups of users to create and edit documents remotely. These documents are regularly synchronized between personal devices and the remote servers. In these applications, a user, owner of the document, can select contributors which have access to the document. Documents should not be accessed by unauthorized parties. If an attacker accesses the servers storing the documents he must not be able to view the documents and if he tries to edit any document, there must be a way to detect the illegal modifications.

A ransomware attack happens when a system is breached and the attacker encrypts the user files and asks for a ransom to provide the decryption key. If properly implemented, recovering the files without the decryption key is an intractable problem. Also, the identification of the attackers can be difficult with the use of cryptocurrencies like BitCoin.
Organizations must have backups, with version history, to allow recovery in the case of ransomware attacks.

In this topic, the solution should allow documents to be shared over a public network in a secure fashion. It should allow authenticated users to access local and remote files in a transparent way. Data confidentiality must be assured even in the case where an attacker gains physical access to the data storage devices. Illegal modification of the documents by unauthorized users must be detected. The document system should resist ransomware attacks.

## 1. Identified Problem

The given scenario depends heavily on the reliable communication between a central server and a set of client machines, and thus suffers from the possibility of attacks to this channel, such as spoofing, replay, man-in-the-middle, and others.

Another worry to take into account is the threat of ransomware, since the main server will function as a storage for potentially shared files and documents, susceptible to malicious code. This code can propagate through the network and encrypt the files of users and servers, offering the key for decryption for a hefty amount, usually through the use of cryptocurrency such as Bitcoin.

Finally, there is also the possibility of a physical attack to the servers, where an intruder (attacker) might access the data servers and attempt to read or modify a document to which he has no permissions.

These are considered to be the three main points where security problems may arise and where security mechanisms will need to be implemented in order to guarantee a secure environment. Additionally, in this manner, not only is the risk of an attack minimized, but also the impact and damage of a successful one is mitigated through the recovery of documents.

### 1.1. Requirements

- Authenticity, Integrity, Confidentiality and Freshness in communications between all parties;
- Client group key generation and sharing;
- Recovery from ransomware attacks to the shared documents;

### 1.2. Trust Assumptions

- We won't trust users if they don’t have the correct permissions for a specified document or whose requests don’t assure authenticity, integrity, confidentiality and freshness;
- We won’t trust anyone with physical access to the servers in terms of both read access and write access;
- We will trust that the servers won’t become unavailable, due to malfunction or denial of service.
- We will trust that there will be no malicious physical access to the backup servers.

## 2. Proposed Solution

### 2.1. Overview

The solution will follow the diagram below in terms of structure:

![](/images/SIRS_structure_diagram.png)

We will fork the NextCloud open source project and implement the following security features on top of the file sharing functionalities:

- TLS will be used in all communications between Clients and the File Server for accessing files, and between File Server and Backup Server to preform backups or recover files;
- The main File Server and the Backup Servers will all be in separate private networks
- The File Server files will be stored encrypted. The encryption will be made by the Client
Group (using PGP & Diffie-Hellman) that has access to the file;
- We will protect the system from ransomware with redundancy, by having a 3-2 system, 3
servers/databases, 2 of them for backups online in different networks;

### 2.2. Deployment

VirtualBox will be used to deploy each machine as a VM:

- The File Server machine will manage all files and users;
- Two other servers, in different networks, that will serve as backup servers for the main
server machine;
- Four Client machines that will connect to the main server;
- Three Client machines accessing files, two of them sharing;
- One client machine performing attacks (connections and ransomware);

### 2.3. ​Secure channel(s) to configure

The communication between the file server and the clients will be made using TLS (HTTPS), therefore, there will exist a certificate for the server (public and private keys).

### 2.4. ​Secure protocol(s) to develop

#### 2.4.1. Group Diffie-Hellman (Station-to-Station)

- Used for generating a shared group key between all users with read/write permissions to a certain file
- There is PFS between shared files, but not in different accesses to the same file
- To guarantee authentication between communications, the Station-to-Station variant will be used
  OR
- Use TLS for authentication

##### Protocol Specification

- Number of client participants does not have a hard limit
- Exchange of intermidiate values can be done on the open
- A circular approach would entail:
  - Number of exchanges: O(N^2)
  - Number of exponentiations: O(N^2)
- The Divide-and-Conquer approach defined bellow will require:
  - Number of exchanges: O(N)
  - Number of exponentiations: O(Nlog2(N))

Given:
- 4 clients A, B, C and D
- Client A created a file F, and choose to share it with B, C and D

1. Define protocol parameters:
  - A will generate a prime modulus (p) and a generator (g)
  - All clients will generate random private numbers (a), (b), (c) and (d)
  - A will send p and g to B, C and D
  - A will also send client group partition rules

2. Key intermidiate values exchange:
  - Split clients in two groups of equal size G1 = (A, B) and G2 = (C, D)

  - A will compute g^a mod p and send it to B
  - C will compute g^c mod p and send it to D

  - B will compute g^ab mod p and send it to C and D (partion of G2 into G21 = (C) and G22 = (D))
  - D will compute g^cd mod p and send it to A and B (partion of G1 into G11 = (A) and G12 = (B))

  - A will compute g^cda mod p and send it to B
  - B will compute g^cdb mod p and send it to A
  - C will compute g^abc mod p and send it to D
  - D will compute g^abd mod p and send it to C

3. Group key calculation:
  - A will compute K = g^cdba mod p
  - B will compute K = g^cdab mod p
  - C will compute K = g^abdc mod p
  - D will compute K = g^abcd mod p

#### 2.4.2. PGP using DH group key

- Used to encrypt files so they can be sent and stored with security on the server
- Used to decrypt files that a client has access to (at client side)
- Can be used only after file premissions setup is concluded (group key (K) already generated)
- Files are sent using TLS

##### Protocol Specification

The following diagram specidies how the protocol will work:

![](/images/SIRS_PGP_diagram.png)

1. Encryption:
  - Client generates a random key (KR) and encrypts file P with it using AES, producing C;
  - Client encrypts KR with shared group key KG using AES, producing CK;
  - Client sends C and CK to the server over TLS;

#### 2.4.3. Storage Integrity (much to do)

The main server will occasionally communicate with backup servers to perform backups of the file system, or to recover from a possible attack to the files.

We will use the following languages:
- Python
- Javascript​
- P​HP

What keys will exist and how will they be distributed?
- Each user will have its own pair of RSA keys. The server will store the public key of each user, which will be transferred by https in the user registration.
- For each file there will be a generated client group key to be distributed using PGP & Diffie-Hellman;
- For each communication between backup server and the file server an AES key will be generated, therefore the main server will have an RSA key pair.

## 3. Plan

### 3.1. Versions

- **Basic**​ - Add secure communication between machines configuring TLS for client - server and server - backup communications (Based on 3-2 backup rule). Files are stored in plain text.
- **Intermediate**​ - Add PGP protocol at client side for file encryption and storage at server.
- **Advanced**​ - Add Diffie-Hellman protocol on top of PGP for client group key sharing.

### 3.1. Effort Commitments

| Semanas       | Manuel Mascarenhas             | Miguel Levezinho               | Ricardo Fernandes               |
| :------------ | :----------------------------- | :----------------------------- | :------------------------------ |
| Nov 02-08     | Custom Protocol Design         | Custom Protocol Design         | Custom Protocol Design          |
| Nov 09-15     | NextCloud Server Configuration | NextCloud Server Configuration | NextCloud Server Configuration  |
| Nov 16-22     | NextCloud Server Configuration | Configure Infrastructure       | Configure TLS for communication |
| Nov 23-29     | Implement PGP protocol         | Implement PGP protocol         | Configure TLS for communication |
| Nov/Dec 30-06 | Implement PGP protocol         | Implement Group DH protocol    | Implement PGP protocol          |
| Dec 07-12     | Implement Group DH protocol    | Implement Group DH protocol    | Implement Group DH protocol     |

## 4. References

NextCloud​, ​Apache,​ P​GP​, ​Diffie-Hellman



















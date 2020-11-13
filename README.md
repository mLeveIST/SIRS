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
- Client side file encryption;
- Recovery from ransomware attacks to the shared documents;

### 1.2. Trust Assumptions

- We won't trust users if they don’t have the correct permissions for a specified document or whose requests don’t assure authenticity, integrity, confidentiality and freshness;
- We won’t trust anyone with physical access to the file server in terms of both read access and write access;
- We will trust that the servers won’t become unavailable, due to malfunction or denial of service;
- We will trust that there will be no malicious physical access to the backup servers or logs server;

## 2. Proposed Solution

### 2.1. Overview

The solution will follow the diagram below in terms of system structure:

![](/images/SIRS_IT_diagram.png)

We will implement the file sharing system ourselves. The Django REST Framework python package will be used for realizing the database, application server-side and client-side, and for the comunnications between machines. Naturaly, TLS will be used in all these communications. The application will use the rsync command to syncronize files between parties.

The File Server files will be stored encrypted. The encryption will be made by the Client Group that has access to the file, using the PGP protocol. To use the system, clients will need to register themselves through the Logs Server.

We will protect the system from ransomware using a custom made protocol, which we will call Ransomware Recovery Protocol (RRP) that will work in two phases:
  - Detection, where illegal changes to files are detected using a log system stored in the Logs Server;
  - Recovery, that will use redundancy by having the infrastructure setup in a 3-2 system way: 3 servers/databases, 2 of them for backups online, all of them in different private networks;

### 2.2. Deployment

VirtualBox will be used to deploy each machine in the system as a VM:

- The File Server machine will store and manage all files;
- The Logs Server machine will act as the entryway to the FS network. It will be split into:
  - A user registry system;
  - A log system for every file update;
- The Backup Server 1 and 2 will serve as backup servers for the files in the File Server machine;
- Four Client machines that will connect to the main server:
  - Three Client machines accessing files, two of them sharing;
  - One Client machine performing attacks (communications and ransomware);

### 2.3. ​Secure channel(s) to configure

Communication between machines will be made using TLS (HTTPS). Therefore, there will exist a certificate for all of them (public and private keys).

### 2.4. ​Secure protocol(s) to develop

### 2.4.1. PGP Protocol

- Used to encrypt files, so they can be securely stored at the File Server;
- Used to decrypt files that a client has access to (decryption at client side);
- Files are sent using TLS;

#### Protocol Specification

The following diagram specifies how the protocol will work:

![](/images/SIRS_PGP_diagram.png)

Where N is the number of clients that share file P

1. Encryption:
  - Client generates a random key (KR) and encrypts file P with it using AES, producing C;
  - Client encrypts KR N times with the other N file contributers public keys, producing CK1 to CKN;
  - Client sends C and CK1 to CKN to the server over TLS;

2. Decryption:
  - Client receives C and CK;
  - Client decrypts CK using its private key, producing key KR;
  - Client decrypts C using KR, producing file P;

### 2.4.3. RRP Protocol

- Used to detect data integrity attacks to the files at the File Server, by using a log system;
- Used to recover from data integrity attacks by use of redundancy, using backups (3-2 rule);
- Communications use TLS;

#### Protocol Specification (TODO)

The following diagram specifies how the protocol will work: (TODO)

(TODO)

```
The main server will occasionally communicate with backup servers to perform backups of the file system, or to recover from a possible attack to the files.

We will use the following languages:
- Python;

What keys will exist and how will they be distributed?
- Each user will have its own pair of RSA keys. The server will store the public key of each user, which will be transferred by https in the user registration.
- For each communication between backup server and the file server an AES key will be generated, therefore the main server will have an RSA key pair.
```

## 3. Plan

### 3.1. Versions

- **Basic**​ - Setup infrastucture and add secure communication between machines, configuring TLS for all communications. Files are stored in plain text.
- **Intermediate**​ - Add PGP protocol at client side for file encryption and storage at server.
- **Advanced**​ - Add RRP protocol for ransomware detection and recovery.

### 3.1. Effort Commitments

| Semanas       | Manuel Mascarenhas             | Miguel Levezinho               | Ricardo Fernandes               |
| :------------ | :----------------------------- | :----------------------------- | :------------------------------ |
| Nov 02-08     | Custom Protocol Design         | Custom Protocol Design         | Custom Protocol Design          |
| Nov 09-15     | Django System Configuration    | Django System Configuration    | Django System Configuration     |
| Nov 16-22     | Configure Infrastructure       | Configure Infrastructure       | Configure TLS for communication |
| Nov 23-29     | Implement PGP protocol         | Implement PGP protocol         | Configure TLS for communication |
| Nov/Dec 30-06 | Implement RRP protocol         | Implement RRP protocol         | Implement RRP protocol          |
| Dec 07-12     | Implement RRP protocol         | Implement RRP protocol         | Implement RRP protocol          |

## 4. References

[Django](https://www.djangoproject.com/)
[Django REST Framework](https://www.django-rest-framework.org/)
[PGP](https://en.wikipedia.org/wiki/Pretty_Good_Privacy)
[3-2-1 Backup Stategy for ransomeware](https://www.titanhq.com/blog/ransomware-protection-why-the-3-2-1-backup-strategy-works/)



















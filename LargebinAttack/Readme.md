# Largebin Attack

Today we'll be talking about large bin attacks which was one of the first heap challenges i solved. 
**Note** : this writeup isn't perfect am just putting in stuff that helps me analyze the concept.

# Introduction :
The largebin attack is considred to be one of the still on going vulnrabilities from **glibc 2.25** and going.
This vulnrability allows an attacker to write a heap address to an arbitrary memory location which can be possible only after bypassing glibc's malloc checks.

1) Largebin structures :
LargeBins are used for managing free chunks larger than 1024 bytes (on 64-bit systems)
<img width="852" height="232" alt="image" src="https://github.com/user-attachments/assets/260587f6-85bc-40fd-bfd0-a61b37e91476" />
<img width="549" height="341" alt="image" src="https://github.com/user-attachments/assets/1675bb6d-abf0-4653-b2af-b98c5812f915" />

**You might ask where does these pointers take us to?**
Depending on the size of the chunk large bins will be classified based on their size for example : 0x400-0x440 / 0x441-0x480 ...
and in the same pool we will arrange the freed chunks based on who was freed first

- fd_nextsize points to its next smaller chunk, bk_nextsize points to its larger chunk.
- fd, bk pointers points to the **same-size chunks** following by the inserted time sequence.
So overall our largebin will like this

<img width="978" height="694" alt="image" src="https://github.com/user-attachments/assets/04b4b7c0-d482-44c3-bc0f-bbe388cd4c4f" />



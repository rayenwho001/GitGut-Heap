# Largebin Attack

Today we'll be talking about large bin attacks which was one of the first heap challenges i solved. 
**Note** : this writeup isn't perfect am just putting in stuff that helps me analyze the concept.

# Introduction :
The largebin attack is considred to be one of the still on going vulnrabilities from **glibc 2.25** and going.
This vulnrability allows an attacker to write a heap address to an arbitrary memory location which can be possible only after bypassing glibc's malloc checks.

**1) Largebin structures :**

LargeBins are used for managing free chunks larger than 1024 bytes (on 64-bit systems) and they are set this way:
<img  alt="image" src="https://github.com/user-attachments/assets/260587f6-85bc-40fd-bfd0-a61b37e91476" width="50%" />
<img alt="image" src="https://github.com/user-attachments/assets/1675bb6d-abf0-4653-b2af-b98c5812f915" width="50%"  />

**You might ask where does these pointers take us to?**
Since largebins are managed in a way thats lets them be classified into groups based on their size. for example : (0x400-0x440 / 0x441-0x480 ...) 
So We need pointers to navigate through these different-sized groups and within the same group too.

- fd points to the next recent chunk in the same sized-list (in direction of the most recent chunk)
- bk points to the previous chunk in the same sized-list
- fd_nextsize points to its next smaller chunk, bk_nextsize points to its larger chunk.
- fd, bk pointers points to the **same-size chunks** following by the inserted time sequence.
So overall our largebin will look like this

<img width="978" height="694" alt="image" src="https://github.com/user-attachments/assets/04b4b7c0-d482-44c3-bc0f-bbe388cd4c4f" />

**2) Malloc's checks and constraints**

The attack happens in the process when a chunk is inserted into large bin, which triggers unlink action and changes existing pointers. 
It's not obligatory to look into malloc.c but i really recommend it since it made the rest of the exploit easier to understand :

<img width="702" height="776" alt="image" src="https://github.com/user-attachments/assets/4de9c527-919e-499a-9e96-3239d44c1c03" />

So directly modifying fd and bk chunks wont work because of these checks : 

// Before any largebin manipulation, malloc performs:
if (__builtin_expect(victim->fd->bk != victim || victim->bk->fd != victim, 0)) {
    errstr = "malloc(): corrupted double-linked list";
    malloc_printerr(errstr);
}

Is this a problem? Of course no! Because we can still play with value of bk_nextsize since :
-  There is no integrity check for bk_nextsize (when the corrupted chunk is the smallest)
-  And there's vulnrable line that allows us to write arbitrary value : **victim->bk_nextsize->fd_nextsize = victim**

Translation:

victim->bk_nextsize = our controlled pointer (target - 0x20)
fd_nextsize offset = +0x20 bytes from chunk start (fd=+0x10, bk=+0x18, fd_nextsize=+0x20)

Remember this : 
struct malloc_chunk {
    size_t prev_size;      // offset 0x00
    size_t size;           // offset 0x08
    malloc_chunk* fd;      // offset 0x10  
    malloc_chunk* bk;      // offset 0x18
    malloc_chunk* fd_nextsize; // offset 0x20  ← This is key!
    malloc_chunk* bk_nextsize; // offset 0x28
};

Result: writes victim address to (target - 0x20) + 0x20 = target
<img width="1015" height="518" alt="image" src="https://github.com/user-attachments/assets/d29bf98d-f196-4384-87c9-b5caa56c584f" />

Now we're ready let's get into practice!! 

**#Proof of Concept **
You can practice everything you see here at : https://wargames.ret2.systems/level/how2heap_large_bin_attack_2.34 , every demonstration is better when you do it
You can use commands to better visualise your problem : b * malloc ; b * free ; heap large ; heap chunks ; vmmap ; or x/20gx {chunk_pointer} 

First thing we will be doing is to create two large-sized chunks p1(0x428) and p2(0x418) smaller than p1 , then we free p1

<img width="678" height="122" alt="image" src="https://github.com/user-attachments/assets/388c2f34-f2ff-4696-a608-4a3163cb9d30" />

The freed chunk is in the unsorted bin list , to be able to move it to largebins we gotta allocate a larger chunk g3(0x438)  (malloc says "these chunks in unsorted bin are too small for this request, let me move them to their proper largebins so next time i can easily find large-sized freed chunks there)

<img width="650" height="301" alt="image" src="https://github.com/user-attachments/assets/4cbd7d14-8285-48e8-9e25-4a752baf3f4a" />

Then we free p2 , and at this point we have one chunk in large bin [p1], and one chunk in unsorted bin [p2]

<img width="472" height="230" alt="image" src="https://github.com/user-attachments/assets/e5a4de47-54af-445c-b4ea-8e3f522d83b3" />

And now as explained earlier by modifying the p1-> bk_nextsize to target-0x20 we will be able to modify target address.
Since Glibc does not check chunk->bk_nextsize if the newly inserted chunk is smaller than smallest, the modified p1->bk_nextsize does not trigger any error. 

<img width="618" height="268" alt="image" src="https://github.com/user-attachments/assets/d58c1fac-9bd2-4bd5-b195-7d2983da34bd" />

Finally, allocate another dummy chunk  g4(0x438) larger than [p2] to place [p2] (who is smaller than [p1]) into large bin

<img width="517" height="141" alt="image" src="https://github.com/user-attachments/assets/1deda972-bc22-42fd-a736-0eb4a53b64e2" />

He is treating our target like it's p2 because of the modified bk_nextsize.
And like that we succeded at modifying our target. Good Job! 
You can try and practice the same concept with the challenge attached. GL HF!
<img width="481" height="581" alt="image" src="https://github.com/user-attachments/assets/23a7f5ad-673c-4078-9794-103532f412b3" />






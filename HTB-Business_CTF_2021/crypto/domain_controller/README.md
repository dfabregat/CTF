# Files

In case you are tempted to open the files in the repo and possibly spoil yourself, here a list of files and what each one contains.

* app.py: server (provided by HTB)
* secret.py: dummy flag to be able to run the server
* bruteforce.py: my solution

# Exploration phase

The name of the challenge hints at some sort of authentication challenge. When we open the file app.py, we see it implements a server whose API offers two functionalities: reset a password, and login with a password.

We see that when a user tries to log in, the code simply compares the given password with the one stored in the variable crypto (```crypto.password```), which originally is a 53-byte random value.

The reset functionality allows us to reset this original random password. The code
1. Grabs the given token (at least 69 bytes long)
2. Splits it into two parts: a 16-byte long IV and an encrypted password
3. Decrypts the encrypted password and stores it in ```crypto.password```

The decryption happens with a random 128-bit key, from which we know nothing.

As for the cryptographic system, the challenge relies on AES CFB-8, with the aforementioned random 128-bit key. If you don't remember how CFB works, here a diagram from Wikipedia:

![Cipher Feedback (CFB) Mode](https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/CFB_decryption.svg/902px-CFB_decryption.svg.png)

# Exploitation phase

It looks like the entry point for our attack is the reset functionality. We must pass a token of at least 69 bytes, and somehow infer knowledge from the decrypted password.

A first thought is often passing a token of all zeros. Let's think for a second what that implies. Look at the diagram above. If the IV and all blocks of the ciphertext are 0, we are encrypting the 0 array multiple times, which results in a plaintext consisting of a concatenation of the same 128-bit pattern corresponding to ```E_k(0)``` (encrypt with key ```k``` the all-0 array).

Well, sure, still a random 128-bit pattern. A tough nut to crack. But, wait a second, what I described above is AES CFB-128. The code is using CFB-8, which means a slightly different computation. In CFB-8, we consume and produce 8-bit segments per iteration. That is:

```
I_0 = IV
I_j = LSB_120(I_(j-1)) | C_(j-1)
O_j = E_k(I_j)
P_j = C_j xor MSB_8(O_j)
```

where the Cipher inputs and outputs (```I``` and ```O```) are 128-bit long, and, as mentioned before, the plaintext and ciphertext segments (```C``` and ```P```) are 8-bit long.

If we look at those formulas carefully, we see that each 128-bit block in the sequence of ```I```s is an all-0 array. Thus, the sequence of ```O```s is still the same 128-bit pattern each time, with the difference that now the produced segments of plaintexts consist of the 8 most-significant bits of that 128-bit pattern (xor'd with 0, the identity element). This 8-bit pattern is now replicated to produce the final plaintext, that is, our password.

In short, when passing an all-0 69-byte token to the reset functionality, we will be storing a password consisting of 53 repeated bytes (e.g., 0F0F0...0F0F or ABAB...ABAB). We just need to try and bruteforce the 256 possibilities with a simple script, and we're good.

# Running the code

1. Run the server code on a terminal: python3 app.py
2. Run the attack on another terminal: python3 brutefoce.py

Example output:

```
$ python3 bruteforce.py
flag: HTB{Just_a_dummy_flag}
```

Feel free to add a couple of print statements here and there to better understand the code and the intermediate steps.

# References

[1] [Wikipedia - Block cipher mode: CFB mode](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher_feedback_(CFB))

[2] [NIST SP 800-38A - Recommendation for Block Cipher Modes of Operation: Methods and Techniques](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38a.pdf)

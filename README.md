CSIDH Analysis

Overview

This repository provides implementations and analysis of the CSIDH algorithm. CSIDH (short for Commutative Supersingular Isogeny Diffie-Hellman) is a cryptographic protocol designed for post-quantum key exchange, leveraging the mathematical structure of isogeny graphs of supersingular elliptic curves. The repository contains both a standard implementation of CSIDH and a constant-time variant designed to mitigate certain attack vectors.

Files and Directory Structure

csidh.py: This file contains a standard implementation of the CSIDH algorithm. The implementation is based on the group action described in the paper by Castryck, Lange, Martindale, Panny, and Renes, which introduced the protocol (see [Castryck et al., 2018]). Additionally, this repository was used as a reference for implementation details.

csidh_ct.py: This file provides a constant-time implementation of CSIDH, incorporating "dummy isogenies" to make computation time independent of private information. This variant is inspired by the work of Meyer, Campos, and Reith (see [Meyer et al., 2018]). The approach is designed to counteract potential side-channel attacks.

/Tests: This directory contains various test programs to validate the correctness and evaluate the performance of the csidh.py and csidh_ct.py modules. Each test includes documentation explaining its purpose and methodology.

/Results: This directory stores the results obtained from the tests in the /Tests directory. Each result file corresponds to a specific test, with detailed documentation included in the associated test program.

The Algorithms

Standard CSIDH

The CSIDH algorithm was introduced in the 2018 paper by Castryck, Lange, Martindale, Panny, and Renes (see [Castryck et al., 2018]). The algorithm defines a group action over supersingular elliptic curves and uses this action to facilitate a post-quantum key exchange protocol. Below is a representation of the group action in pseudocode, as described in the original paper, which is implemented in the csidh.py file.

Constant-Time CSIDH

The constant-time variant of CSIDH was proposed to address vulnerabilities related to timing attacks. This approach introduces "dummy isogenies" to ensure that the runtime does not vary based on secret inputs. The algorithm and its analysis are detailed in the paper by Meyer, Campos, and Reith (see [Meyer et al., 2018]). Below is the pseudocode for the modified algorithm, which forms the basis of the implementation in csidh_ct.py.

References

Castryck, W., Lange, T., Martindale, C., Panny, L., & Renes, J. (2018). CSIDH: An Efficient Post-Quantum Commutative Group Action. Retrieved from https://eprint.iacr.org/2018/383.pdf

Meyer, M., Campos, F., & Reith, S. (2018). Towards Constant-Time CSIDH. Retrieved from https://eprint.iacr.org/2018/1198.pdf


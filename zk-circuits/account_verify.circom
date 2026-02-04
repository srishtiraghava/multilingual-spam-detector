pragma circom 2.0.0;
include "node_modules/circomlib/circuits/poseidon.circom";

template AccountVerify() {
    signal input accountNum; // Private: The actual number
    signal input expectedHash; // Public: The hash we expect
    signal output isValid;

    component hasher = Poseidon(1);
    hasher.inputs[0] <== accountNum;
    
    // Constraint: The hash of the private accountNum must match the public expectedHash
    expectedHash === hasher.out;
    isValid <== 1;
}

component main {public [expectedHash]} = AccountVerify();
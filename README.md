# Gone compiler from David Beasley class.

http://dabeaz.com/chicago/compiler.html

The language is loosely based around go. 

The compiler runs in a few stages:
* Tokenizer - Breaks the progam into tokens
* Parser - Uses the tokenizer to parse the program
* Checker - Checks the parsed syntax
* IRCode - Creates intermediate code
* LLVMgen - Converts the intermediate code to LLVM instructions
* Compile - Compiles the code using LLVM (Optionally, there is a run that can
            work line a JIT manner.)

## Compile the program

`python -m gone.compile Programs/mandel.g`

## Execute the compiled program
`./a.out`

## View the tokenizer output
`python -m gone.tokenizer Programs/mandel.g`

## Parse the program
`python -m gone.parser Programs/mandel.g`

## Check the syntax of the program
`python -m gone.checker Programs/mandel.g`

## Build the intermediate code
`python -m gone.ircode Programs/mandel.g`

## Convert the IRCode to LLVM instructions
`python -m gone.llvmgen Programs/mandel.g`

## Run (JIT) the program and run it.
`python -m gone.run Programs/mandel.g`

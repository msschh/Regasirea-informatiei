dynamically generate code for the identity function include assert h include stdio h include sys mman h include unistd h include malloc h include stdlib h include errno h using objdump disassemble a out gives 080483c4 g 80483c4 55 push ebp 80483c5 89 e5 mov esp ebp 80483c7 8b 45 08 mov 0x8 ebp eax 80483ca 5d pop ebp 80483cb c3 ret int g int x return x simple program to demonstrate dynamic code generation on the x86 architecture note very very machine dependent int main int f int ugh linux tries to be clever and prevent you from executing heap stuff int pagesize sysconf _sc_page_size char buf memalign pagesize pagesize if mprotect buf pagesize prot_read prot_write prot_exec 1 perror failed assert 0 dynamically generate code equivalent to int f int x return x into buf buf 0 0x55 buf 1 0x89 buf 2 0xe5 buf 3 0x8b buf 4 0x45 buf 5 0x8 buf 6 0x5d buf 7 0xc3 cast buf's address to a function pointer f int int buf check that generated code returns right answer printf d d n 10 f 10 printf d d n 20 f 20 return 0
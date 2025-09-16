#include <iostream>
#include <cstdint>
#include "rasm/rasm.h"

#if defined(_WIN32)

extern "C" {
    __declspec(dllexport) long myputs(const char* s) {
        return std::puts(s);
    }
}

extern "C" {
    __declspec(dllexport) long _asm_(const char* code) {
        return ::_asm(code);
    }
}

#else

using namespace std;

extern "C" long myputs(const char* s) {
    return puts(s);
}

extern "C" {
    long _asm_(const char* code) {
        return _asm(code);
    }
}

#endif
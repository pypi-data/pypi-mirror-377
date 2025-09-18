# mp_reader: an analyzer for [mem_profile](https://github.com/codeinred/mem_profile)

This repo holds the implementation of `mp_reader`, which is an analyzer for the
files output by `mem_profile`.

## mem_profile: an Ownership-Aware Memory Profiler

mem_profile is an ownership-aware memory profiler, designed for direct
measurement of objects and their members.

What does this mean?

When a program is executed with mem_profile, we can see the number of bytes
allocated by types within the program.

![alt text](https://raw.githubusercontent.com/codeinred/mp_reader/main/images/objects_output.png)

Above is some sample output, produced by the analyzer (mp_reader, this project).

This is a toy example, but mem_profile is designed for use with complex
workloads, and has been tested on projects involving hundreds or even thousands
of translation units.

For instance, here's an output of type-level stats from profiling an FTXUI demo
application:

![alt text](https://raw.githubusercontent.com/codeinred/mp_reader/main/images/ftxui-demo.png)

And here's output from profiling CMake:

![alt text](https://raw.githubusercontent.com/codeinred/mp_reader/main/images/cmake-demo-types.png)

For more information, see the
[mem_profile repo](https://github.com/codeinred/mem_profile)!

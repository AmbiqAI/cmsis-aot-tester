# Modules Directory

This directory contains git submodules for the CMSIS-NN testing project.

## Current Submodules

- `neuralSPOT` - NeuralSPOT framework for embedded AI development

## Setting up submodules

To initialize and update all submodules:

```bash
git submodule update --init --recursive
```

To add a new submodule:

```bash
git submodule add <repository-url> modules/<module-name>
```

## Missing Submodules

The following submodules need to be added when network access is available:

- `helia-aot` - Helia AOT (Ahead-of-Time) compilation tool
- `ns-cmsis-nn` - NeuralSPOT CMSIS-NN implementation

To add them:

```bash
git submodule add https://github.com/AmbiqAI/helia-aot.git modules/helia-aot
git submodule add https://github.com/AmbiqAI/ns-cmsis-nn.git modules/ns-cmsis-nn
```
